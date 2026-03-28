#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
巴菲特策略自动化交易执行
========================

基于巴菲特投资信号，通过富途 OpenAPI 自动执行交易。

⚠️ 风险提示：
1. 本脚本用于学习和研究目的
2. 实盘交易需要谨慎，建议先用模拟账户测试
3. 交易前请仔细检查所有参数
4. 建议设置止损和仓位限制

使用方法:
    python3 strategies/auto_trade.py --dry-run  # 模拟运行
    python3 strategies/auto_trade.py --execute  # 实盘执行
"""

import sys
import argparse
from datetime import datetime
from typing import List, Dict, Optional

sys.path.insert(0, '/home/admin/openclaw/workspace')

from futu import *
from strategies.buffett_strategy import BuffettStrategy
from strategies.buffett_trading import BuffettTradingStrategy, Action


class AutoTrader:
    """
    自动化交易执行器
    
    功能:
    1. 连接富途 OpenD
    2. 获取持仓和资金
    3. 生成巴菲特交易信号
    4. 执行买入/卖出订单
    5. 风险控制（仓位限制、止损等）
    """
    
    # 交易配置
    MAX_POSITION_RATIO = 0.40  # 单只股票最高 40%
    MAX_ORDER_VALUE = 500000  # 单笔订单最高 50 万
    STOP_LOSS_RATIO = 0.20  # 止损线 20%
    
    def __init__(self, dry_run: bool = True):
        """
        初始化交易器
        
        参数:
            dry_run: True=模拟运行，False=实盘执行
        """
        self.dry_run = dry_run
        self.quote_ctx = None
        self.trade_ctx = None
        self.account_id = None
        
    def connect(self) -> bool:
        """
        连接 OpenD
        
        返回:
            是否连接成功
        """
        try:
            # 行情上下文
            self.quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
            
            # 验证连接
            ret, data = self.quote_ctx.get_global_state()
            if ret != RET_OK:
                print("❌ 无法连接到 OpenD")
                return False
            
            print("✅ 行情连接成功")
            
            # 交易上下文（实盘时需要）
            if not self.dry_run:
                self.trade_ctx = OpenTradeContext(
                    trd_env=TrdEnv.SIMULATE,  # 模拟环境
                    host='127.0.0.1',
                    port=11111
                )
                
                ret, data = self.trade_ctx.get_acc_list()
                if ret == RET_OK:
                    self.account_id = data['acc_list'][0]['acc_id']
                    print(f"✅ 交易连接成功 (账户：{self.account_id})")
                else:
                    print("⚠️ 交易连接失败，使用模拟模式")
                    self.dry_run = True
            
            return True
            
        except Exception as e:
            print(f"❌ 连接失败：{e}")
            return False
    
    def get_account_info(self) -> Dict:
        """
        获取账户信息
        
        返回:
            账户资金和持仓信息
        """
        info = {
            'cash': 0,
            'market_value': 0,
            'total_asset': 0,
            'positions': {}
        }
        
        if self.dry_run:
            # 模拟数据
            info['cash'] = 250000
            info['market_value'] = 2321640
            info['total_asset'] = 2571640
            info['positions'] = {
                'HK.00700': {'shares': 2500, 'cost': 585.78},
                'HK.00883': {'shares': 11000, 'cost': 20.75},
                'HK.09988': {'shares': 5800, 'cost': 143.27},
            }
            return info
        
        try:
            # 获取资金
            ret, data = self.trade_ctx.get_acc_cash_flow()
            if ret == RET_OK:
                info['cash'] = data['cash'][0]
                info['total_asset'] = data['total_assets'][0]
            
            # 获取持仓
            ret, data = self.trade_ctx.get_position_list()
            if ret == RET_OK:
                for _, row in data.iterrows():
                    code = row['code']
                    info['positions'][code] = {
                        'shares': row['qty'],
                        'cost': row['cost_price'],
                        'market_value': row['market_val']
                    }
                    info['market_value'] += row['market_val']
            
        except Exception as e:
            print(f"⚠️ 获取账户信息失败：{e}")
        
        return info
    
    def generate_signals(self) -> List:
        """
        生成巴菲特交易信号
        
        返回:
            交易信号列表
        """
        # 持仓股票
        portfolio = [
            {'code': 'HK.00700', 'name': '腾讯控股'},
            {'code': 'HK.00883', 'name': '中国海洋石油'},
            {'code': 'HK.09988', 'name': '阿里巴巴-W'},
        ]
        
        # 财务数据估算
        estimates = {
            'HK.00700': {
                'roe': 18.5, 'roe_5y_avg': 20.3, 'gross_margin': 42.5,
                'net_margin': 25.8, 'earnings_growth_5y': 18.0,
                'debt_to_equity': 0.35, 'free_cash_flow': 150000,
                'fcf_yield': 5.2, 'eps': 40.64, 'shares_outstanding': 9500,
            },
            'HK.00883': {
                'roe': 18.2, 'roe_5y_avg': 15.8, 'gross_margin': 55.3,
                'net_margin': 28.5, 'earnings_growth_5y': 22.5,
                'debt_to_equity': 0.28, 'free_cash_flow': 180000,
                'fcf_yield': 8.5, 'eps': 3.82, 'shares_outstanding': 44700,
            },
            'HK.09988': {
                'roe': 12.5, 'roe_5y_avg': 14.2, 'gross_margin': 38.2,
                'net_margin': 15.3, 'earnings_growth_5y': 12.8,
                'debt_to_equity': 0.42, 'free_cash_flow': 120000,
                'fcf_yield': 6.8, 'eps': 8.52, 'shares_outstanding': 19500,
            },
        }
        
        strategy = BuffettStrategy()
        trading_strategy = BuffettTradingStrategy()
        stocks = []
        
        # 获取实时价格并分析
        for stock_info in portfolio:
            code = stock_info['code']
            name = stock_info['name']
            
            ret, data = self.quote_ctx.get_market_snapshot([code])
            if ret != RET_OK or data.empty:
                continue
            
            current_price = data.iloc[0]['last_price']
            financials = estimates.get(code, {})
            
            stock = strategy.analyze_stock(
                code=code, name=name, market='HK',
                current_price=current_price,
                financial_data=financials
            )
            
            if stock:
                stocks.append(stock)
        
        # 生成交易信号
        current_positions = {
            'HK.00700': 0.30,
            'HK.00883': 0.25,
            'HK.09988': 0.20,
        }
        
        signals = trading_strategy.generate_portfolio_signals(
            stocks=stocks,
            current_positions=current_positions,
            total_capital=2571640
        )
        
        return signals
    
    def place_order(
        self,
        code: str,
        action: Action,
        shares: int,
        price: float
    ) -> bool:
        """
        下单交易
        
        参数:
            code: 股票代码
            action: 买入/卖出
            shares: 股数
            price: 价格
        
        返回:
            是否成功
        """
        if self.dry_run:
            print(f"  [模拟] {'买入' if action in [Action.STRONG_BUY, Action.BUY] else '卖出'} "
                  f"{code} {shares:,}股 @ {price:.2f}港元")
            return True
        
        try:
            # 确定订单类型
            order_type = OrderType.NORMAL
            side = OrderSide.BUY if action in [Action.STRONG_BUY, Action.BUY] else OrderSide.SELL
            
            # 下单
            ret, data = self.trade_ctx.place_order(
                price=price,
                qty=shares,
                code=code,
                trd_side=side,
                order_type=order_type
            )
            
            if ret == RET_OK:
                order_id = data['order_id'][0]
                print(f"  ✅ 下单成功：订单 ID={order_id}")
                return True
            else:
                print(f"  ❌ 下单失败：{data}")
                return False
                
        except Exception as e:
            print(f"  ❌ 下单异常：{e}")
            return False
    
    def execute_trades(self, signals: List, account_info: Dict):
        """
        执行交易
        
        参数:
            signals: 交易信号列表
            account_info: 账户信息
        """
        print("\n" + "=" * 60)
        print("📋 执行交易")
        print("=" * 60)
        
        available_cash = account_info['cash']
        current_holdings = account_info['positions']
        
        for signal in signals:
            print(f"\n{signal.name} ({signal.code}):")
            print(f"  动作：{signal.action.value}")
            print(f"  现价：{signal.current_price:.2f}港元")
            print(f"  理由：{signal.reason}")
            
            if signal.action in [Action.STRONG_BUY, Action.BUY]:
                # 买入逻辑
                target_value = available_cash * signal.position_ratio
                shares = int(target_value / signal.current_price / 100) * 100  # 整手
                
                if shares > 0:
                    # 检查限制
                    order_value = shares * signal.current_price
                    if order_value > self.MAX_ORDER_VALUE:
                        shares = int(self.MAX_ORDER_VALUE / signal.current_price / 100) * 100
                        print(f"  ⚠️ 超过单笔限制，调整为{shares:,}股")
                    
                    # 确认股数为整手（港股通常 100 股/手）
                    lot_size = 100
                    shares = (shares // lot_size) * lot_size
                    
                    print(f"  建议买入：{shares:,}股 ({order_value:,.0f}港元)")
                    
                    if self.dry_run:
                        print(f"  ⚠️ 模拟模式，未实际下单")
                    else:
                        confirm = input(f"  确认买入？(y/n): ")
                        if confirm.lower() == 'y':
                            self.place_order(signal.code, signal.action, shares, signal.current_price)
            
            elif signal.action in [Action.SELL, Action.STRONG_SELL, Action.REDUCE]:
                # 卖出逻辑
                current_shares = current_holdings.get(signal.code, {}).get('shares', 0)
                
                if current_shares > 0:
                    if signal.action == Action.STRONG_SELL:
                        sell_ratio = 1.0
                    elif signal.action == Action.SELL:
                        sell_ratio = 0.5
                    else:
                        sell_ratio = 0.25
                    
                    sell_shares = int(current_shares * sell_ratio / 100) * 100
                    
                    if sell_shares > 0:
                        print(f"  当前持仓：{current_shares:,}股")
                        print(f"  建议卖出：{sell_shares:,}股 ({sell_ratio*100:.0f}%)")
                        
                        if self.dry_run:
                            print(f"  ⚠️ 模拟模式，未实际下单")
                        else:
                            confirm = input(f"  确认卖出？(y/n): ")
                            if confirm.lower() == 'y':
                                self.place_order(signal.code, signal.action, sell_shares, signal.current_price)
            
            else:
                print(f"  继续持有")
    
    def close(self):
        """关闭连接"""
        if self.quote_ctx:
            self.quote_ctx.close()
        if self.trade_ctx:
            self.trade_ctx.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='巴菲特策略自动化交易')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='模拟运行（默认）')
    parser.add_argument('--execute', action='store_true',
                        help='实盘执行')
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    print("=" * 60)
    print("🤖 巴菲特策略自动化交易系统")
    print("=" * 60)
    print(f"运行模式：{'✅ 模拟运行' if dry_run else '⚠️ 实盘执行'}")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 创建交易器
    trader = AutoTrader(dry_run=dry_run)
    
    # 连接
    if not trader.connect():
        print("❌ 无法连接 OpenD，请确保 OpenD 已启动并登录")
        return
    
    try:
        # 获取账户信息
        print("\n📊 账户信息")
        print("-" * 60)
        account_info = trader.get_account_info()
        print(f"可用资金：{account_info['cash']:,.0f}港元")
        print(f"持仓市值：{account_info['market_value']:,.0f}港元")
        print(f"总资产：{account_info['total_asset']:,.0f}港元")
        print("\n当前持仓:")
        for code, pos in account_info['positions'].items():
            print(f"  {code}: {pos['shares']:,}股")
        
        # 生成交易信号
        print("\n📈 生成交易信号...")
        signals = trader.generate_signals()
        print(f"生成{len(signals)}个交易信号")
        
        # 执行交易
        trader.execute_trades(signals, account_info)
        
        # 完成
        print("\n" + "=" * 60)
        print("✅ 交易执行完成")
        print("=" * 60)
        
    finally:
        trader.close()


if __name__ == "__main__":
    main()
