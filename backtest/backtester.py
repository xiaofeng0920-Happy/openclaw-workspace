# -*- coding: utf-8 -*-
"""
巴菲特策略回测系统
==================

对巴菲特价值投资策略进行历史回测，验证策略有效性。

功能:
1. 历史数据获取
2. 策略信号生成
3. 交易模拟执行
4. 绩效统计分析
5. 可视化报告

使用方法:
    python3 backtest/backtester.py --code HK.00700 --start 2023-01-01 --end 2026-03-21
"""

import sys
sys.path.insert(0, '/home/admin/openclaw/workspace')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.font_manager import FontProperties
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

from data.financial_data import FinancialData
from strategies.buffett_strategy import BuffettStrategy


@dataclass
class Trade:
    """交易记录"""
    date: datetime
    code: str
    action: str  # 'BUY' or 'SELL'
    price: float
    shares: int
    value: float
    reason: str


@dataclass
class BacktestResult:
    """回测结果"""
    # 基本信息
    code: str
    name: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    
    # 收益指标
    final_capital: float
    total_return: float  # 总收益率
    annual_return: float  # 年化收益率
    benchmark_return: float  # 基准收益（买入持有）
    alpha: float  # 超额收益
    
    # 风险指标
    max_drawdown: float  # 最大回撤
    volatility: float  # 波动率
    sharpe_ratio: float  # 夏普比率
    
    # 交易统计
    total_trades: int
    win_trades: int
    lose_trades: int
    win_rate: float  # 胜率
    avg_profit: float  # 平均盈利
    avg_loss: float  # 平均亏损
    profit_factor: float  # 盈亏比
    
    # 持仓统计
    avg_holding_days: float  # 平均持仓天数
    max_position: float  # 最大仓位
    avg_position: float  # 平均仓位
    
    # 详细记录
    trades: List[Trade]
    daily_values: pd.DataFrame


class BuffettBacktester:
    """
    巴菲特策略回测器
    
    回测逻辑:
    1. 获取历史财务数据和行情
    2. 每日计算巴菲特评分和安全边际
    3. 根据交易规则生成买卖信号
    4. 模拟执行交易
    5. 统计绩效指标
    """
    
    # 回测参数
    INITIAL_CAPITAL = 1000000  # 初始资金 100 万
    MAX_POSITION = 0.40  # 单只股票最高 40%
    TRANSACTION_COST = 0.001  # 交易成本 0.1%
    
    # 交易阈值
    BUY_MARGIN = 30.0  # 买入安全边际
    SELL_PREMIUM = 30.0  # 卖出溢价
    
    def __init__(self):
        self.fd = FinancialData(source='akshare')
        self.strategy = BuffettStrategy()
        self.trades: List[Trade] = []
        self.daily_values = []
    
    def get_history_data(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取历史数据
        
        参数:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
        
        返回:
            DataFrame with date, open, high, low, close, volume
        """
        print(f"📊 获取 {code} 历史数据 ({start_date} ~ {end_date})...")
        
        try:
            # 转换代码格式
            if code.startswith('HK.'):
                symbol = code.replace('HK.', '')
            elif code.startswith('CN.'):
                symbol = code.replace('CN.', '')
            elif code.startswith('US.'):
                symbol = code.replace('US.', '')
            else:
                symbol = code
            
            history = self.fd.get_history(symbol, start_date, end_date)
            
            if history is None or history.empty:
                print(f"⚠️ 历史数据为空，生成模拟数据...")
                return self._generate_mock_data(start_date, end_date)
            
            # 数据清洗
            history = history.sort_values('date')
            history = history.dropna()
            
            print(f"✅ 获取 {len(history)} 条数据")
            return history
            
        except Exception as e:
            print(f"⚠️ 获取历史数据失败：{e}")
            print(f"   使用模拟数据继续...")
            return self._generate_mock_data(start_date, end_date)
    
    def _generate_mock_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """生成模拟历史数据（用于演示）"""
        dates = pd.date_range(start=start_date, end=end_date, freq='B')  # 工作日
        
        # 模拟股价走势（随机游走）
        np.random.seed(42)
        n_days = len(dates)
        returns = np.random.randn(n_days) * 0.02  # 日波动 2%
        price_series = 400 * np.cumprod(1 + returns)  # 从 400 开始
        
        df = pd.DataFrame({
            'date': dates,
            'open': price_series * (1 + np.random.randn(n_days) * 0.01),
            'high': price_series * (1 + np.abs(np.random.randn(n_days) * 0.02)),
            'low': price_series * (1 - np.abs(np.random.randn(n_days) * 0.02)),
            'close': price_series,
            'volume': np.random.randint(1000000, 50000000, n_days)
        })
        
        print(f"✅ 生成 {len(df)} 条模拟数据")
        return df
    
    def estimate_historical_financials(self, code: str, date: datetime) -> Dict:
        """
        估算历史财务数据
        
        简化处理：使用当前财务数据作为代理
        实际应用中应该获取历史财报数据
        """
        # 获取当前财务数据
        current_data = self.fd.get_financials(code)
        
        if not current_data:
            return {}
        
        # 简化：假设财务指标在回测期间保持稳定
        # 实际应用中应该按季度更新财务数据
        return current_data
    
    def generate_signal(self, price: float, financials: Dict) -> Tuple[str, float]:
        """
        生成交易信号
        
        参数:
            price: 当前价格
            financials: 财务数据
        
        返回:
            (信号类型，目标仓位)
        """
        if not financials:
            return 'HOLD', 0.0
        
        # 分析股票
        stock = self.strategy.analyze_stock(
            code='TEMP',
            name='TEMP',
            market='HK',
            current_price=price,
            financial_data=financials
        )
        
        if not stock:
            return 'HOLD', 0.0
        
        margin = stock.margin_of_safety
        score = stock.buffett_score
        
        # 交易规则
        if margin >= self.BUY_MARGIN and score >= 70:
            # 买入信号
            target_position = min(self.MAX_POSITION, 0.2 + (margin - self.BUY_MARGIN) / 100)
            return 'BUY', target_position
        
        elif margin <= -self.SELL_PREMIUM:
            # 卖出信号
            return 'SELL', 0.0
        
        else:
            # 持有
            return 'HOLD', 0.0
    
    def run_backtest(self, code: str, start_date: str, end_date: str) -> BacktestResult:
        """
        执行回测
        
        参数:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
        
        返回:
            BacktestResult 回测结果
        """
        print("=" * 60)
        print("📈 巴菲特策略回测系统")
        print("=" * 60)
        print(f"股票代码：{code}")
        print(f"回测期间：{start_date} ~ {end_date}")
        print(f"初始资金：{self.INITIAL_CAPITAL:,.0f}")
        print()
        
        # 获取历史数据
        history = self.get_history_data(code, start_date, end_date)
        if history.empty:
            return None
        
        # 获取股票名称
        financials = self.fd.get_financials(code)
        name = financials.get('name', code) if financials else code
        
        # 初始化
        capital = self.INITIAL_CAPITAL
        shares = 0
        position_value = 0
        peak_value = capital
        
        self.trades = []
        self.daily_values = []
        
        # 估算财务数据
        hist_financials = self.estimate_historical_financials(code, history.iloc[0]['date'])
        
        # 每日回测
        print("🔄 开始回测...")
        
        for idx, row in history.iterrows():
            date = row['date']
            price = row['close']
            
            # 生成信号
            signal, target_position = self.generate_signal(price, hist_financials)
            
            # 当前持仓价值
            current_value = capital + shares * price
            current_position_ratio = (shares * price) / current_value if current_value > 0 else 0
            
            # 执行交易
            if signal == 'BUY' and current_position_ratio < target_position:
                # 买入
                target_shares = int((current_value * target_position) / price / 100) * 100
                buy_shares = target_shares - shares
                
                if buy_shares > 0:
                    cost = buy_shares * price * (1 + self.TRANSACTION_COST)
                    if cost <= capital:
                        shares = buy_shares
                        capital -= cost
                        position_value = shares * price
                        
                        self.trades.append(Trade(
                            date=date,
                            code=code,
                            action='BUY',
                            price=price,
                            shares=buy_shares,
                            value=cost,
                            reason=f"安全边际>{self.BUY_MARGIN}%, 评分>{70}"
                        ))
            
            elif signal == 'SELL' and shares > 0:
                # 卖出
                sell_shares = shares
                proceeds = sell_shares * price * (1 - self.TRANSACTION_COST)
                capital += proceeds
                position_value = 0
                shares = 0
                
                self.trades.append(Trade(
                    date=date,
                    code=code,
                    action='SELL',
                    price=price,
                    shares=sell_shares,
                    value=proceeds,
                    reason=f"溢价>{self.SELL_PREMIUM}%"
                ))
            
            # 记录每日资产
            total_value = capital + shares * price
            peak_value = max(peak_value, total_value)
            
            self.daily_values.append({
                'date': date,
                'capital': capital,
                'shares': shares,
                'price': price,
                'position_value': shares * price,
                'total_value': total_value,
                'peak_value': peak_value,
            })
        
        # 转换为 DataFrame
        daily_df = pd.DataFrame(self.daily_values)
        
        # 计算绩效指标
        result = self.calculate_metrics(code, name, start_date, end_date, daily_df)
        
        # 打印结果
        self.print_result(result)
        
        return result
    
    def calculate_metrics(self, code: str, name: str, start_date: str, end_date: str, 
                         daily_df: pd.DataFrame) -> BacktestResult:
        """计算绩效指标"""
        
        # 基本收益
        initial = self.INITIAL_CAPITAL
        final = daily_df['total_value'].iloc[-1]
        total_return = (final - initial) / initial
        
        # 年化收益
        days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days
        annual_return = (1 + total_return) ** (365 / days) - 1 if days > 0 else 0
        
        # 基准收益（买入持有）
        start_price = daily_df['price'].iloc[0]
        end_price = daily_df['price'].iloc[-1]
        benchmark_return = (end_price - start_price) / start_price
        
        # 超额收益
        alpha = total_return - benchmark_return
        
        # 最大回撤
        daily_df['drawdown'] = (daily_df['peak_value'] - daily_df['total_value']) / daily_df['peak_value']
        max_drawdown = daily_df['drawdown'].max()
        
        # 波动率
        daily_returns = daily_df['total_value'].pct_change().dropna()
        volatility = daily_returns.std() * np.sqrt(252) if len(daily_returns) > 0 else 0
        
        # 夏普比率（假设无风险利率 3%）
        risk_free_rate = 0.03
        sharpe_ratio = (annual_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        # 交易统计
        total_trades = len(self.trades)
        buy_trades = [t for t in self.trades if t.action == 'BUY']
        sell_trades = [t for t in self.trades if t.action == 'SELL']
        
        # 计算胜率
        win_trades = 0
        lose_trades = 0
        total_profit = 0
        total_loss = 0
        
        for i, sell in enumerate(sell_trades):
            # 找到对应的买入
            prev_buy = None
            for buy in reversed(buy_trades):
                if buy.date < sell.date:
                    prev_buy = buy
                    break
            
            if prev_buy:
                profit = (sell.price - prev_buy.price) * sell.shares
                if profit > 0:
                    win_trades += 1
                    total_profit += profit
                else:
                    lose_trades += 1
                    total_loss += abs(profit)
        
        win_rate = win_trades / (win_trades + lose_trades) if (win_trades + lose_trades) > 0 else 0
        avg_profit = total_profit / win_trades if win_trades > 0 else 0
        avg_loss = total_loss / lose_trades if lose_trades > 0 else 0
        profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        # 持仓统计
        avg_position = daily_df['position_value'].mean() / daily_df['total_value'].mean() if daily_df['total_value'].mean() > 0 else 0
        max_position = daily_df['position_value'].max() / daily_df['total_value'].max() if daily_df['total_value'].max() > 0 else 0
        
        return BacktestResult(
            code=code,
            name=name,
            start_date=pd.to_datetime(start_date),
            end_date=pd.to_datetime(end_date),
            initial_capital=initial,
            final_capital=final,
            total_return=total_return,
            annual_return=annual_return,
            benchmark_return=benchmark_return,
            alpha=alpha,
            max_drawdown=max_drawdown,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            total_trades=total_trades,
            win_trades=win_trades,
            lose_trades=lose_trades,
            win_rate=win_rate,
            avg_profit=avg_profit,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            avg_holding_days=0,  # 简化
            max_position=max_position,
            avg_position=avg_position,
            trades=self.trades,
            daily_values=daily_df
        )
    
    def print_result(self, result: BacktestResult):
        """打印回测结果"""
        print()
        print("=" * 60)
        print("📊 回测结果")
        print("=" * 60)
        
        print(f"\n📈 收益指标:")
        print(f"  初始资金：{result.initial_capital:,.0f}")
        print(f"  最终资金：{result.final_capital:,.0f}")
        print(f"  总收益率：{result.total_return*100:+.2f}%")
        print(f"  年化收益率：{result.annual_return*100:.2f}%")
        print(f"  基准收益：{result.benchmark_return*100:+.2f}%")
        print(f"  超额收益：{result.alpha*100:+.2f}%")
        
        print(f"\n⚠️ 风险指标:")
        print(f"  最大回撤：{result.max_drawdown*100:.2f}%")
        print(f"  波动率：{result.volatility*100:.2f}%")
        print(f"  夏普比率：{result.sharpe_ratio:.2f}")
        
        print(f"\n💹 交易统计:")
        print(f"  总交易次数：{result.total_trades}")
        print(f"  盈利次数：{result.win_trades}")
        print(f"  亏损次数：{result.lose_trades}")
        print(f"  胜率：{result.win_rate*100:.1f}%")
        print(f"  平均盈利：{result.avg_profit:,.0f}")
        print(f"  平均亏损：{result.avg_loss:,.0f}")
        print(f"  盈亏比：{result.profit_factor:.2f}")
        
        print(f"\n📦 持仓统计:")
        print(f"  平均仓位：{result.avg_position*100:.1f}%")
        print(f"  最大仓位：{result.max_position*100:.1f}%")
        
        # 交易记录
        if result.trades:
            print(f"\n📋 交易记录:")
            print(f"  {'日期':<12} {'动作':<6} {'价格':>10} {'股数':>10} {'金额':>12} {'原因'}")
            print("  " + "-" * 70)
            for trade in result.trades[:20]:  # 只显示前 20 笔
                action_symbol = '🟢 买入' if trade.action == 'BUY' else '🔴 卖出'
                print(f"  {trade.date.strftime('%Y-%m-%d'):<12} {action_symbol:<8} {trade.price:>10.2f} {trade.shares:>10,.0f} {trade.value:>12,.0f}")
        
        print()
    
    def plot_result(self, result: BacktestResult, save_path: str = None):
        """
        绘制回测结果图
        
        参数:
            result: 回测结果
            save_path: 保存路径（可选）
        """
        fig, axes = plt.subplots(3, 1, figsize=(14, 10))
        
        daily_df = result.daily_values
        
        # 图 1: 资产曲线
        ax1 = axes[0]
        ax1.plot(daily_df['date'], daily_df['total_value'], label='策略价值', linewidth=2)
        
        # 买入持有基准
        initial_shares = self.INITIAL_CAPITAL / daily_df['price'].iloc[0]
        benchmark_value = initial_shares * daily_df['price']
        ax1.plot(daily_df['date'], benchmark_value, label='买入持有', linewidth=2, linestyle='--')
        
        ax1.set_title(f'{result.name} ({result.code}) - 资产曲线对比', fontsize=14)
        ax1.set_ylabel('资产价值 (元)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/10000:.0f}万'))
        
        # 图 2: 回撤曲线
        ax2 = axes[1]
        ax2.fill_between(daily_df['date'], -daily_df['drawdown']*100, 0, alpha=0.5, color='red')
        ax2.set_title('回撤曲线', fontsize=14)
        ax2.set_ylabel('回撤 (%)')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(-max(daily_df['drawdown'])*100*1.2, 0)
        
        # 图 3: 价格与交易信号
        ax3 = axes[2]
        ax3.plot(daily_df['date'], daily_df['price'], label='股价', linewidth=1.5, alpha=0.7)
        
        # 标记买卖点
        buy_trades = [t for t in result.trades if t.action == 'BUY']
        sell_trades = [t for t in result.trades if t.action == 'SELL']
        
        if buy_trades:
            buy_dates = [t.date for t in buy_trades]
            buy_prices = [t.price for t in buy_trades]
            ax3.scatter(buy_dates, buy_prices, color='green', marker='^', s=100, label='买入', zorder=5)
        
        if sell_trades:
            sell_dates = [t.date for t in sell_trades]
            sell_prices = [t.price for t in sell_trades]
            ax3.scatter(sell_dates, sell_prices, color='red', marker='v', s=100, label='卖出', zorder=5)
        
        ax3.set_title('价格与交易信号', fontsize=14)
        ax3.set_xlabel('日期')
        ax3.set_ylabel('价格 (元)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 格式化 x 轴日期
        for ax in axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"📊 图表已保存：{save_path}")
        else:
            plt.show()
    
    def plot_multiple_results(self, results: List[BacktestResult], save_path: str = None):
        """
        对比多个回测结果
        
        参数:
            results: 回测结果列表
            save_path: 保存路径（可选）
        """
        fig, axes = plt.subplots(2, 1, figsize=(14, 8))
        
        # 图 1: 多个策略对比
        ax1 = axes[0]
        for result in results:
            daily_df = result.daily_values
            ax1.plot(daily_df['date'], daily_df['total_value'], label=f'{result.name}', linewidth=2)
        
        ax1.set_title('多策略资产曲线对比', fontsize=14)
        ax1.set_ylabel('资产价值 (元)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/10000:.0f}万'))
        
        # 图 2: 收益对比柱状图
        ax2 = axes[1]
        names = [f'{r.name}\n{r.total_return*100:+.1f}%' for r in results]
        returns = [r.total_return*100 for r in results]
        colors = ['green' if r > 0 else 'red' for r in returns]
        
        bars = ax2.bar(range(len(names)), returns, color=colors)
        ax2.set_xticks(range(len(names)))
        ax2.set_xticklabels(names, rotation=0)
        ax2.set_title('总收益率对比 (%)', fontsize=14)
        ax2.set_ylabel('收益率 (%)')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 在柱子上标注数值
        for bar, ret in zip(bars, returns):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{ret:+.1f}%',
                    ha='center', va='bottom' if height > 0 else 'top')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"📊 对比图表已保存：{save_path}")
        else:
            plt.show()


def demo_backtest():
    """回测演示"""
    backtester = BuffettBacktester()
    
    # 回测腾讯控股
    result = backtester.run_backtest(
        code='HK.00700',
        start_date='2023-01-01',
        end_date='2026-03-21'
    )
    
    if result:
        # 绘制结果
        backtester.plot_result(result, save_path='/home/admin/openclaw/workspace/backtest/result_00700.png')


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='巴菲特策略回测')
    parser.add_argument('--code', type=str, default='HK.00700', help='股票代码')
    parser.add_argument('--start', type=str, default='2023-01-01', help='开始日期')
    parser.add_argument('--end', type=str, default='2026-03-21', help='结束日期')
    parser.add_argument('--demo', action='store_true', help='运行演示')
    
    args = parser.parse_args()
    
    if args.demo:
        demo_backtest()
    else:
        backtester = BuffettBacktester()
        result = backtester.run_backtest(args.code, args.start, args.end)
        
        if result:
            # 保存图表
            save_path = f'/home/admin/openclaw/workspace/backtest/result_{args.code.replace(".", "_")}.png'
            backtester.plot_result(result, save_path=save_path)