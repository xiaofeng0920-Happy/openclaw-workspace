#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V8 真实资金流向数据回测 - 沪深 300 短线版（5 天持有期）"""

import sys
from pathlib import Path
sys.path.insert(0, '/home/admin/openclaw/workspace')

import pandas as pd
import numpy as np
from datetime import datetime
import json
import time
from tqdm import tqdm

# ========== 回测参数 ==========
INITIAL_CAPITAL = 1000000
POSITION_SIZE = 0.15        # 15% 单只仓位
HOLDING_PERIOD = 5          # 5 天短线
TOP_K = 5                   # 5 只
TRANSACTION_COST = 0.001    # 0.1%

# 流动性过滤：日均成交额 > 1 亿
MIN_TURNOVER = 100000000    # 1 亿元
# ===============================

print("=" * 70)
print("🤖 V8 真实资金流向数据回测 - 沪深 300 短线版")
print("=" * 70)
print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)
print(f"\n📊 策略参数：")
print(f"  股票池：沪深 300（大盘股）")
print(f"  初始资金：{INITIAL_CAPITAL:,} 元")
print(f"  持仓数量：{TOP_K} 只")
print(f"  持有周期：{HOLDING_PERIOD} 天（短线）")
print(f"  单只仓位：{POSITION_SIZE*100}%")
print(f"  交易成本：{TRANSACTION_COST*100}%")
print(f"  流动性过滤：日均成交额 > {MIN_TURNOVER/1e8:.0f}亿")
print(f"\n🎯 核心因子：")
print(f"    - 主力净流入 5 日均值")
print(f"    - 超大单净流入 5 日均值")
print(f"    - 大单净流入 5 日均值")
print("=" * 70)

import akshare as ak

def get_hs300_stocks():
    """获取沪深 300 成分股"""
    try:
        df = ak.index_stock_cons(symbol="000300")
        stocks = df['品种代码'].tolist() if '品种代码' in df.columns else df['股票代码'].tolist()
        print(f"✅ 沪深 300 成分股：{len(stocks)} 只")
        return stocks
    except Exception as e:
        print(f"❌ 获取沪深 300 失败：{e}")
        return []

def get_stock_fund_flow(symbol, market):
    """获取个股历史资金流向数据"""
    try:
        df = ak.stock_individual_fund_flow(stock=symbol, market=market)
        if df is not None and len(df) > 80:
            df['日期'] = pd.to_datetime(df['日期'])
            df = df.sort_values('日期')
            return df
    except Exception as e:
        pass
    return None

def get_price_data(symbol, market):
    """获取个股历史行情数据"""
    try:
        code = f"{market}{symbol}"
        df = ak.stock_zh_a_daily(symbol=code, adjust="qfq")
        if df is not None and len(df) > 80:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            return df
    except Exception as e:
        pass
    return None

# 获取股票池
print("\n📊 获取沪深 300 成分股...")
hs300 = get_hs300_stocks()
print(f"📦 待测试：{len(hs300)} 只")

print("\n📊 获取真实资金流向数据（带流动性过滤）...")
print(f"  预计耗时：约{len(hs300) * 1.5:.0f}秒")

all_data = []
filtered_out = 0

for i, symbol in enumerate(tqdm(hs300, desc="获取数据"), 1):
    market = 'sh' if symbol.startswith('6') else 'sz'
    
    # 获取资金流向数据
    fund_df = get_stock_fund_flow(symbol, market)
    if fund_df is None:
        continue
    
    # 获取行情数据
    price_df = get_price_data(symbol, market)
    if price_df is None:
        continue
    
    # 流动性过滤：计算日均成交额
    price_df['turnover'] = price_df['close'] * price_df['volume']
    avg_turnover = price_df['turnover'].mean()
    
    if avg_turnover < MIN_TURNOVER:
        filtered_out += 1
        continue
    
    # 合并资金流向和行情数据（按日期）
    merged = pd.merge(price_df, fund_df, left_on='date', right_on='日期', how='inner')
    
    if len(merged) < 60:
        continue
    
    # 计算资金流向因子
    merged['main_flow_5d'] = merged['主力净流入-净占比'].rolling(5).mean()
    merged['main_flow_20d'] = merged['主力净流入-净占比'].rolling(20).mean()
    merged['big_order_5d'] = merged['大单净流入-净占比'].rolling(5).mean()
    merged['super_order_5d'] = merged['超大单净流入-净占比'].rolling(5).mean()
    
    # 综合因子：主力 + 超大单加权（超大单权重更高）
    merged['flow_score'] = (
        merged['main_flow_5d'] * 0.3 + 
        merged['super_order_5d'] * 0.5 + 
        merged['big_order_5d'] * 0.2
    )
    
    # 计算标签：未来 5 天收益
    merged['label'] = merged['收盘价'].shift(-HOLDING_PERIOD).pct_change(HOLDING_PERIOD)
    merged = merged.dropna()
    
    if len(merged) > 40:
        merged['symbol'] = symbol
        merged['avg_turnover'] = avg_turnover
        all_data.append(merged)
    
    # 避免请求过快
    if i % 100 == 0:
        time.sleep(1)

if not all_data:
    print("\n❌ 未获取到足够数据")
    sys.exit(1)

dataset = pd.concat(all_data, ignore_index=True)
print(f"\n📊 数据集统计：")
print(f"  总记录数：{len(dataset)}")
print(f"  股票数量：{dataset['symbol'].nunique()} 只")
print(f"  流动性过滤：{filtered_out} 只（成交额<{MIN_TURNOVER/1e8:.1f}亿）")
print(f"  日期范围：{dataset['date'].min()} 至 {dataset['date'].max()}")

# 执行回测
print(f"\n📈 执行回测...")
print(f"  初始资金：{INITIAL_CAPITAL:,} 元")
print(f"  持仓数量：{TOP_K} 只")
print(f"  持有周期：{HOLDING_PERIOD} 天")

dates = sorted(dataset['date'].unique())
capital = INITIAL_CAPITAL
positions = {}
trades = []
portfolio_values = []

for date in tqdm(dates[:-HOLDING_PERIOD], desc="回测中"):
    day_data = dataset[dataset['date'] == date]
    
    # 卖出到期持仓
    for symbol in list(positions.keys()):
        pos = positions[symbol]
        days_held = (pd.to_datetime(date) - pd.to_datetime(pos['entry_date'])).days
        if days_held >= HOLDING_PERIOD:
            stock_data = day_data[day_data['symbol'] == symbol]
            if len(stock_data) > 0:
                exit_price = stock_data['收盘价'].values[0]
                pnl = (exit_price - pos['entry_price']) * pos['shares']
                cost = pos['entry_price'] * pos['shares'] * TRANSACTION_COST * 2
                pnl -= cost
                capital += pos['shares'] * exit_price - cost
                trades.append({
                    'symbol': symbol, 
                    'pnl': pnl, 
                    'pnl_pct': (exit_price - pos['entry_price']) / pos['entry_price'] * 100,
                    'entry_date': str(pos['entry_date']),
                    'exit_date': str(date)
                })
                del positions[symbol]
    
    # 买入新持仓（按 flow_score 综合因子排序）
    if len(positions) < TOP_K:
        available = TOP_K - len(positions)
        day_data_sorted = day_data.sort_values('flow_score', ascending=False)
        top_stocks = day_data_sorted.head(available)
        
        for idx, row in top_stocks.iterrows():
            symbol = row['symbol']
            price = row['收盘价']
            
            position_value = capital * POSITION_SIZE
            shares = int(position_value / price / 100) * 100
            
            if shares > 0:
                cost = price * shares * TRANSACTION_COST
                if capital >= price * shares + cost:
                    capital -= price * shares + cost
                    positions[symbol] = {
                        'entry_price': price, 
                        'entry_date': date, 
                        'shares': shares
                    }
    
    # 计算组合价值
    portfolio_value = capital
    for symbol, pos in positions.items():
        stock_data = day_data[day_data['symbol'] == symbol]
        if len(stock_data) > 0:
            current_price = stock_data['收盘价'].values[0]
            portfolio_value += pos['shares'] * current_price
    portfolio_values.append({'date': date, 'value': portfolio_value})

# 清仓
last_date = dates[-1]
last_data = dataset[dataset['date'] == last_date]
for symbol, pos in positions.items():
    stock_data = last_data[last_data['symbol'] == symbol]
    if len(stock_data) > 0:
        exit_price = stock_data['收盘价'].values[0]
        capital += pos['shares'] * exit_price

# 计算结果
final_value = capital
total_return = (final_value - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
days = (pd.to_datetime(dates[-1]) - pd.to_datetime(dates[0])).days
annual_return = ((final_value / INITIAL_CAPITAL) ** (365 / days) - 1) * 100 if days > 0 else 0

winning = [t for t in trades if t['pnl'] > 0]
win_rate = len(winning) / len(trades) * 100 if trades else 0

portfolio_df = pd.DataFrame(portfolio_values)
portfolio_df['peak'] = portfolio_df['value'].cummax()
portfolio_df['drawdown'] = (portfolio_df['value'] - portfolio_df['peak']) / portfolio_df['peak'] * 100
max_drawdown = portfolio_df['drawdown'].min()

portfolio_df['daily_return'] = portfolio_df['value'].pct_change()
sharpe = (portfolio_df['daily_return'].mean() / portfolio_df['daily_return'].std() * np.sqrt(252)) if len(portfolio_df) > 2 else 0

# 打印结果
print("\n" + "=" * 70)
print("📊 回测结果:")
print("=" * 70)
print(f"  初始资金：{INITIAL_CAPITAL:,} 元")
print(f"  最终价值：{final_value:,.0f} 元")
print(f"  总收益：{total_return:+.2f}%")
print(f"  年化收益：{annual_return:+.2f}%")
print(f"  最大回撤：{max_drawdown:.2f}%")
print(f"  夏普比率：{sharpe:.2f}")
print(f"  交易次数：{len(trades)}")
print(f"  胜率：{win_rate:.1f}%")
print("=" * 70)

if total_return > 0:
    print("\n✅ 回测盈利！策略有效！")
elif win_rate > 50:
    print("\n🟡 胜率>50%，继续优化有望盈利！")
else:
    print("\n⚠️ 回测亏损，需要重新考虑策略...")

# 保存结果
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
result = {
    'timestamp': timestamp,
    'initial_capital': INITIAL_CAPITAL,
    'final_value': final_value,
    'total_return': total_return,
    'annual_return': annual_return,
    'max_drawdown': max_drawdown,
    'sharpe': sharpe,
    'trade_count': len(trades),
    'win_rate': win_rate,
    'parameters': {
        'position_size': POSITION_SIZE,
        'holding_period': HOLDING_PERIOD,
        'top_k': TOP_K,
        'transaction_cost': TRANSACTION_COST,
        'stock_pool': '沪深 300',
        'min_turnover': MIN_TURNOVER,
        'data_source': 'akshare 真实资金流向',
        'factors': ['main_flow_5d', 'super_order_5d', 'big_order_5d'],
        'factor_weights': {'main': 0.3, 'super': 0.5, 'big': 0.2}
    },
    'trades': trades[:30]
}

output_dir = Path("/home/admin/openclaw/workspace/agents/data-collector/backtest_results")
output_dir.mkdir(exist_ok=True)
output_file = output_dir / f"backtest_result_v8_hs300_short_{timestamp}.json"

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"\n💾 结果已保存：{output_file.name}")
print("=" * 70)
