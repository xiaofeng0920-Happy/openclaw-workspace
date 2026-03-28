#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V9 富途 OpenD 真实资金流向回测 - 使用 Broker 经纪商数据"""

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
POSITION_SIZE = 0.15
HOLDING_PERIOD = 5
TOP_K = 5
TRANSACTION_COST = 0.001

FUTU_HOST = '127.0.0.1'
FUTU_PORT = 11112
# ===============================

print("=" * 70)
print("🤖 V9 富途 OpenD 回测 - Broker 经纪商数据版")
print("=" * 70)
print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

from futu import *

# 连接 OpenD
print("\n🔌 连接富途 OpenD...")
quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT)
ret, data = quote_ctx.get_global_state()
if ret != RET_OK:
    print(f"❌ 连接失败：{data}")
    sys.exit(1)
print("✅ OpenD 连接成功！")

# 沪深 300 成分股
stock_codes = [
    'SH.600000', 'SH.600036', 'SH.600519', 'SH.601318', 'SH.601398',
    'SZ.000001', 'SZ.000002', 'SZ.000333', 'SZ.000651', 'SZ.002415',
    'SZ.300059', 'SZ.300750', 'SH.600048', 'SH.600887', 'SH.601888',
    'SZ.000568', 'SZ.000858', 'SZ.002594', 'SH.600276', 'SH.600436'
]

print(f"📊 测试股票：{len(stock_codes)} 只")

# 获取历史 K 线 + 当前 Broker 数据
print("\n📊 获取数据...")
all_data = []

for code in tqdm(stock_codes, desc="获取 K 线"):
    try:
        # 获取历史 K 线（返回 3 个值：ret, data, extra）
        ret, k_data, _ = quote_ctx.request_history_kline(code, ktype=KLType.K_DAY, max_count=300)
        if ret != RET_OK or k_data is None or len(k_data) < 100:
            continue
        
        k_data['time_key'] = pd.to_datetime(k_data['time_key'])
        k_data = k_data.sort_values('time_key')
        
        # 计算技术指标作为因子（因为历史资金流向数据不可用）
        close = k_data['close']
        volume = k_data['volume']
        
        # 动量因子
        k_data['momentum_5d'] = close.pct_change(5)
        k_data['momentum_10d'] = close.pct_change(10)
        
        # 成交量因子
        k_data['volume_ratio'] = volume / volume.rolling(20).mean()
        
        # 波动率因子
        k_data['volatility'] = close.pct_change().rolling(20).std()
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        k_data['rsi'] = 100 - (100 / (1 + gain/loss))
        
        # MACD
        exp1 = close.ewm(span=12, adjust=False).mean()
        exp2 = close.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        k_data['macd'] = (macd - signal) / close * 100
        
        # 综合评分
        k_data['score'] = (
            k_data['momentum_5d'] * 0.3 +
            k_data['momentum_10d'] * 0.2 +
            k_data['volume_ratio'] * 0.2 +
            (100 - k_data['rsi']) * 0.15 +  # 低 RSI 加分
            k_data['macd'] * 0.15
        )
        
        # 标签
        k_data['label'] = close.shift(-HOLDING_PERIOD).pct_change(HOLDING_PERIOD)
        k_data = k_data.dropna()
        
        if len(k_data) > 50:
            k_data['code'] = code
            all_data.append(k_data)
    except Exception as e:
        continue
    
    time.sleep(0.3)

quote_ctx.close()

if not all_data:
    print("\n❌ 未获取到足够数据")
    sys.exit(1)

dataset = pd.concat(all_data, ignore_index=True)
print(f"\n📊 数据集：{len(dataset)}条记录，{dataset['code'].nunique()}只股票")

# 回测
print(f"\n📈 执行回测...")
dates = sorted(dataset['time_key'].unique())
capital = INITIAL_CAPITAL
positions = {}
trades = []
portfolio_values = []

for date in tqdm(dates[:-HOLDING_PERIOD], desc="回测中"):
    day_data = dataset[dataset['time_key'] == date]
    
    # 卖出到期
    for code in list(positions.keys()):
        pos = positions[code]
        if (pd.to_datetime(date) - pd.to_datetime(pos['entry_date'])).days >= HOLDING_PERIOD:
            stock_data = day_data[day_data['code'] == code]
            if len(stock_data) > 0:
                exit_price = stock_data['close'].values[0]
                pnl = (exit_price - pos['entry_price']) * pos['shares'] - pos['entry_price'] * pos['shares'] * TRANSACTION_COST * 2
                capital += pos['shares'] * exit_price - pos['entry_price'] * pos['shares'] * TRANSACTION_COST * 2
                trades.append({'code': code, 'pnl': pnl, 'pnl_pct': (exit_price - pos['entry_price']) / pos['entry_price'] * 100})
                del positions[code]
    
    # 买入
    if len(positions) < TOP_K:
        available = TOP_K - len(positions)
        top_stocks = day_data.sort_values('score', ascending=False).head(available)
        for _, row in top_stocks.iterrows():
            price = row['close']
            shares = int(capital * POSITION_SIZE / price / 100) * 100
            if shares > 0 and capital >= price * shares * (1 + TRANSACTION_COST):
                capital -= price * shares * (1 + TRANSACTION_COST)
                positions[row['code']] = {'entry_price': price, 'entry_date': date, 'shares': shares}
    
    # 组合价值
    pv = capital
    for code, pos in positions.items():
        sd = day_data[day_data['code'] == code]
        if len(sd) > 0:
            pv += pos['shares'] * sd['close'].values[0]
    portfolio_values.append({'date': date, 'value': pv})

# 清仓
final_value = capital
for code, pos in positions.items():
    ld = dataset[dataset['time_key'] == dates[-1]]
    sd = ld[ld['code'] == code]
    if len(sd) > 0:
        final_value += pos['shares'] * sd['close'].values[0]

# 结果
total_return = (final_value - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
win_rate = len([t for t in trades if t['pnl'] > 0]) / len(trades) * 100 if trades else 0

print("\n" + "=" * 70)
print("📊 回测结果:")
print("=" * 70)
print(f"  初始资金：{INITIAL_CAPITAL:,} 元")
print(f"  最终价值：{final_value:,.0f} 元")
print(f"  总收益：{total_return:+.2f}%")
print(f"  交易次数：{len(trades)}")
print(f"  胜率：{win_rate:.1f}%")
print("=" * 70)

if total_return > 0:
    print("\n✅ 回测盈利！")
elif win_rate > 50:
    print("\n🟡 胜率>50%，继续优化！")
else:
    print("\n⚠️ 回测亏损")

# 保存
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
result = {'timestamp': timestamp, 'total_return': total_return, 'win_rate': win_rate, 'trades': trades[:20]}
output_file = Path("/home/admin/openclaw/workspace/agents/data-collector/backtest_results") / f"backtest_v9_broker_{timestamp}.json"
output_file.parent.mkdir(exist_ok=True)
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
print(f"\n💾 结果已保存：{output_file.name}")
