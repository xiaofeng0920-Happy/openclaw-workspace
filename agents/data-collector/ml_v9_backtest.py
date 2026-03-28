#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V9 简化版回测 - 只用 6 个技术因子"""

import sys
from pathlib import Path
sys.path.insert(0, '/home/admin/openclaw/workspace')

import pandas as pd
import numpy as np
import lightgbm as lgb

# 回测配置
INITIAL_CAPITAL = 1000000
POSITION_SIZE = 0.1
HOLDING_PERIOD = 20
TOP_K = 10
TRANSACTION_COST = 0.0005

# 因子列表
FACTORS = ['price_momentum_10d', 'price_momentum_20d', 'rsi_14', 'macd_signal', 'bollinger_position', 'volume_ratio']

# 加载模型
model_dir = Path("/home/admin/openclaw/workspace/agents/data-collector/models")
model_files = list(model_dir.glob("lgbm_v9_simple_*.json"))
model = lgb.Booster(model_file=str(model_files[0]))
print(f"✅ 加载模型：{model_files[0].name}")

# 加载数据（从 V9 训练数据）
import akshare as ak

A50_STOCKS = ['000001', '000002', '000063', '000100', '000157', '000333', '000538', '000568', '000596', '000651',
    '000661', '000725', '000776', '000858', '000895', '002001', '002007', '002027', '002049', '002129',
    '002142', '002230', '002236', '002252', '002304', '002352', '002415', '002475', '002594', '002714',
    '300014', '300015', '300059', '300122', '300124', '300142', '300274', '300312', '300347', '300413',
    '300433', '300498', '300601', '300628', '300750', '300759', '300760', '300782', '300896', '600000']

print("\n📊 准备回测数据...")
all_data = []

for i, symbol in enumerate(A50_STOCKS, 1):
    code = f"sh{symbol}" if symbol.startswith('6') else f"sz{symbol}"
    df = ak.stock_zh_a_daily(symbol=code, adjust="qfq")
    if df is not None and len(df) > 700:
        df = df.tail(730).copy()
        df['symbol'] = symbol
        
        # 计算因子
        close = df['close']
        volume = df['volume']
        
        df['price_momentum_10d'] = close.pct_change(10)
        df['price_momentum_20d'] = close.pct_change(20)
        
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
        
        df['volume_ratio'] = volume / volume.rolling(5).mean()
        df['label'] = df['close'].shift(-20).pct_change(20)
        
        df = df.dropna()
        all_data.append(df)
        if i % 10 == 0:
            print(f"  [{i:3d}/50] ✓ {symbol}: {len(df)}条")

dataset = pd.concat(all_data, ignore_index=True)
print(f"\n  总计：{len(dataset)}条记录")

# 回测
print("\n📈 执行回测...")
print(f"  初始资金：{INITIAL_CAPITAL:,} 元")
print(f"  持仓数量：{TOP_K} 只")
print(f"  持有周期：{HOLDING_PERIOD} 天")

dates = sorted(dataset['date'].unique())
capital = INITIAL_CAPITAL
positions = {}
trades = []

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
                trades.append({'symbol': symbol, 'pnl': pnl, 'pnl_pct': (exit_price - pos['entry_price']) / pos['entry_price'] * 100})
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
annual_return = ((final_value / INITIAL_CAPITAL) ** (365 / days) - 1) * 100

winning = [t for t in trades if t['pnl'] > 0]
win_rate = len(winning) / len(trades) * 100 if trades else 0

print("\n📊 回测结果:")
print(f"  初始资金：{INITIAL_CAPITAL:,} 元")
print(f"  最终价值：{final_value:,.0f} 元")
print(f"  总收益：{total_return:+.2f}%")
print(f"  年化收益：{annual_return:+.2f}%")
print(f"  交易次数：{len(trades)}")
print(f"  胜率：{win_rate:.1f}%")

if annual_return > 0:
    print("\n✅ 回测盈利！")
else:
    print("\n⚠️ 回测亏损，继续优化...")
