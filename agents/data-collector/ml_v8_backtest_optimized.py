#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V8 真实数据版回测 - 保留资金流向因子，调整参数优化版"""

import sys
from pathlib import Path
sys.path.insert(0, '/home/admin/openclaw/workspace')

import pandas as pd
import numpy as np
import lightgbm as lgb
from datetime import datetime
import json

# ========== 调整后的参数 ==========
INITIAL_CAPITAL = 1000000
POSITION_SIZE = 0.15        # 15% → 更集中
HOLDING_PERIOD = 5          # 5 天 → 短线交易
TOP_K = 5                   # 5 只 → 更集中
TRANSACTION_COST = 0.001    # 0.1% → 更保守
# =================================

# V8 因子列表（12 个，保留资金流向）
FACTORS = [
    'north_flow_5d', 'north_flow_20d', 'main_flow_5d', 'main_flow_20d',
    'turnover_ratio', 'volume_ratio', 'price_momentum_10d',
    'rsi_14', 'macd_signal', 'bollinger_position', 'roe', 'pe_ratio'
]

print("=" * 60)
print("🤖 V8 真实数据版回测 - 参数优化版")
print("=" * 60)
print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)
print(f"\n📊 参数调整：")
print(f"  持仓数量：10 → {TOP_K} 只")
print(f"  持有周期：20 → {HOLDING_PERIOD} 天")
print(f"  单只仓位：10% → {POSITION_SIZE*100}%")
print(f"  交易成本：0.05% → {TRANSACTION_COST*100}%")
print(f"\n✅ 保留因子：资金流向 (north_flow, main_flow) + 技术因子")
print("=" * 60)

# 加载 V8 模型
model_dir = Path("/home/admin/openclaw/workspace/agents/data-collector/models")
model_files = list(model_dir.glob("lgbm_v8_real_*.json"))
if not model_files:
    print("❌ 未找到 V8 模型")
    sys.exit(1)

model_file = max(model_files, key=lambda x: x.stat().st_mtime)
model = lgb.Booster(model_file=str(model_file))
print(f"\n📦 加载模型：{model_file.name}")

# 重新生成数据集
import akshare as ak

A50_STOCKS = [
    '000001', '000002', '000063', '000100', '000157', '000333', '000538', '000568', '000596', '000651',
    '000661', '000725', '000776', '000858', '000895', '002001', '002007', '002027', '002049', '002129',
    '002142', '002230', '002236', '002252', '002304', '002352', '002415', '002475', '002594', '002714',
    '300014', '300015', '300059', '300122', '300124', '300142', '300274', '300312', '300347', '300413',
    '300433', '300498', '300601', '300628', '300750', '300759', '300760', '300782', '300896', '600000'
]

def get_north_flow_approx(symbol, df):
    """近似北向资金流向"""
    returns = df['close'].pct_change()
    volume = df['volume']
    flow = returns * volume / volume.mean() * 100
    return flow.rolling(5).mean(), flow.rolling(20).mean()

def get_main_flow_approx(symbol, df):
    """近似主力资金流向"""
    returns = df['close'].pct_change()
    flow = returns * 1000
    return flow.rolling(5).mean(), flow.rolling(20).mean()

print("\n📊 准备回测数据...")
all_data = []
errors = 0

for i, symbol in enumerate(A50_STOCKS, 1):
    try:
        code = f"sh{symbol}" if symbol.startswith('6') else f"sz{symbol}"
        df = ak.stock_zh_a_daily(symbol=code, adjust="qfq")
        if df is not None and len(df) > 700:
            df = df.tail(730).copy()
            df['symbol'] = symbol
            df['date'] = pd.to_datetime(df['date'])
            
            close = df['close']
            volume = df['volume']
            
            # 资金流向
            north_5d, north_20d = get_north_flow_approx(symbol, df)
            main_5d, main_20d = get_main_flow_approx(symbol, df)
            df['north_flow_5d'] = north_5d
            df['north_flow_20d'] = north_20d
            df['main_flow_5d'] = main_5d
            df['main_flow_20d'] = main_20d
            
            # 情绪因子
            df['turnover_ratio'] = volume / volume.rolling(20).mean()
            df['volume_ratio'] = volume / volume.rolling(5).mean()
            df['price_momentum_10d'] = close.pct_change(10)
            
            # 技术因子
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            df['rsi_14'] = 100 - (100 / (1 + gain/loss))
            
            exp1 = close.ewm(span=12, adjust=False).mean()
            exp2 = close.ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            df['macd_signal'] = (macd - signal) / close * 100
            
            ma20 = close.rolling(20).mean()
            std20 = close.rolling(20).std()
            upper = ma20 + 2 * std20
            lower = ma20 - 2 * std20
            df['bollinger_position'] = (close - lower) / (upper - lower + 0.01)
            
            # 质量因子
            df['roe'] = 15.0
            df['pe_ratio'] = 1 / (close.pct_change(252) + 0.01)
            
            df['label'] = df['close'].shift(-HOLDING_PERIOD).pct_change(HOLDING_PERIOD)
            df = df.dropna()
            
            all_data.append(df)
            if i % 10 == 0:
                print(f"  [{i:3d}/50] ✓ {symbol}: {len(df)}条")
    except Exception as e:
        errors += 1

if not all_data:
    print("❌ 未获取到数据")
    sys.exit(1)

dataset = pd.concat(all_data, ignore_index=True)
print(f"\n  总计：{len(dataset)}条记录")
print(f"  错误：{errors}只")

dates = sorted(dataset['date'].unique())
print(f"  日期范围：{dates[0]} 至 {dates[-1]}")

# 执行回测
print(f"\n📈 执行回测...")
print(f"  初始资金：{INITIAL_CAPITAL:,} 元")
print(f"  持仓数量：{TOP_K} 只")
print(f"  持有周期：{HOLDING_PERIOD} 天")
print(f"  交易成本：{TRANSACTION_COST*100}%")

capital = INITIAL_CAPITAL
positions = {}
trades = []
portfolio_values = []

for date in dates[:-HOLDING_PERIOD]:
    day_data = dataset[dataset['date'] == date]
    
    # 卖出到期持仓
    for symbol in list(positions.keys()):
        pos = positions[symbol]
        days_held = (pd.to_datetime(date) - pd.to_datetime(pos['entry_date'])).days
        if days_held >= HOLDING_PERIOD:
            stock_data = day_data[day_data['symbol'] == symbol]
            if len(stock_data) > 0:
                exit_price = stock_data['close'].values[0]
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
    
    # 买入新持仓
    if len(positions) < TOP_K:
        X = day_data[FACTORS]
        predictions = model.predict(X)
        
        available = TOP_K - len(positions)
        top_indices = np.argsort(predictions)[-available:]
        
        for idx in top_indices:
            row = day_data.iloc[idx]
            symbol = row['symbol']
            price = row['close']
            
            position_value = capital * POSITION_SIZE
            shares = int(position_value / price / 100) * 100
            
            if shares > 0:
                cost = price * shares * TRANSACTION_COST
                if capital >= price * shares + cost:
                    capital -= price * shares + cost
                    positions[symbol] = {'entry_price': price, 'entry_date': date, 'shares': shares}
    
    # 计算组合价值
    portfolio_value = capital
    for symbol, pos in positions.items():
        stock_data = day_data[day_data['symbol'] == symbol]
        if len(stock_data) > 0:
            current_price = stock_data['close'].values[0]
            portfolio_value += pos['shares'] * current_price
    portfolio_values.append({'date': date, 'value': portfolio_value})

# 清仓
last_date = dates[-1]
last_data = dataset[dataset['date'] == last_date]
for symbol, pos in positions.items():
    stock_data = last_data[last_data['symbol'] == symbol]
    if len(stock_data) > 0:
        exit_price = stock_data['close'].values[0]
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
print("\n" + "=" * 60)
print("📊 回测结果:")
print("=" * 60)
print(f"  初始资金：{INITIAL_CAPITAL:,} 元")
print(f"  最终价值：{final_value:,.0f} 元")
print(f"  总收益：{total_return:+.2f}%")
print(f"  年化收益：{annual_return:+.2f}%")
print(f"  最大回撤：{max_drawdown:.2f}%")
print(f"  夏普比率：{sharpe:.2f}")
print(f"  交易次数：{len(trades)}")
print(f"  胜率：{win_rate:.1f}%")
print("=" * 60)

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
        'transaction_cost': TRANSACTION_COST
    },
    'factors': FACTORS,
    'trades': trades[:20]  # 只保存前 20 笔交易详情
}

output_dir = Path("/home/admin/openclaw/workspace/agents/data-collector/backtest_results")
output_dir.mkdir(exist_ok=True)
output_file = output_dir / f"backtest_result_v8_optimized_{timestamp}.json"

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"\n💾 结果已保存：{output_file.name}")
print("=" * 60)
