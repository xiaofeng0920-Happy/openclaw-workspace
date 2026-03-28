#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V9 富途 OpenD 真实资金流向回测 - A 股沪深 300"""

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

# 富途 OpenD 配置
FUTU_HOST = '127.0.0.1'
FUTU_PORT = 11112           # 锋哥配置的端口
# ===============================

print("=" * 70)
print("🤖 V9 富途 OpenD 真实资金流向回测 - A 股沪深 300")
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
print(f"\n🔌 富途 OpenD 配置：")
print(f"  主机：{FUTU_HOST}")
print(f"  端口：{FUTU_PORT}")
print(f"\n🎯 核心因子：")
print(f"    - 主力净流入 5 日均值")
print(f"    - 超大单净流入 5 日均值")
print(f"    - 大单净流入 5 日均值")
print("=" * 70)

from futu import *

# 初始化 OpenD 连接
print("\n🔌 连接富途 OpenD...")
try:
    quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT)
    ret, data = quote_ctx.get_global_state()
    if ret != RET_OK:
        print(f"❌ OpenD 连接失败：{data}")
        print("\n请确保：")
        print("  1. OpenD 服务已启动")
        print("  2. 已在 OpenD GUI 界面完成登录")
        print("  3. 端口号配置正确（当前：11112）")
        sys.exit(1)
    
    print("✅ OpenD 连接成功！")
    print(f"  服务器版本：{data['server_ver']}")
    print(f"  行情登录：{'是' if data['qot_logined'] else '否'}")
    print(f"  交易登录：{'是' if data['trd_logined'] else '否'}")
except Exception as e:
    print(f"❌ 连接异常：{e}")
    sys.exit(1)

# 获取沪深 300 成分股（使用备用列表，避免 API 兼容性问题）
print("\n📊 加载沪深 300 成分股...")
hs300_codes = [
    'SH.600000', 'SH.600009', 'SH.600016', 'SH.600028', 'SH.600030',
    'SH.600036', 'SH.600048', 'SH.600050', 'SH.600104', 'SH.600276',
    'SH.600309', 'SH.600346', 'SH.600436', 'SH.600519', 'SH.600585',
    'SH.600588', 'SH.600690', 'SH.600745', 'SH.600809', 'SH.600887',
    'SH.600893', 'SH.600900', 'SH.600905', 'SH.600919', 'SH.600938',
    'SH.601012', 'SH.601066', 'SH.601088', 'SH.601166', 'SH.601211',
    'SH.601225', 'SH.601288', 'SH.601318', 'SH.601328', 'SH.601390',
    'SH.601398', 'SH.601601', 'SH.601628', 'SH.601633', 'SH.601668',
    'SH.601688', 'SH.601728', 'SH.601766', 'SH.601800', 'SH.601816',
    'SH.601857', 'SH.601888', 'SH.601898', 'SH.601899', 'SH.601919',
    'SZ.000001', 'SZ.000002', 'SZ.000063', 'SZ.000100', 'SZ.000157',
    'SZ.000333', 'SZ.000538', 'SZ.000568', 'SZ.000596', 'SZ.000651',
    'SZ.000661', 'SZ.000725', 'SZ.000776', 'SZ.000858', 'SZ.000895',
    'SZ.002001', 'SZ.002007', 'SZ.002027', 'SZ.002049', 'SZ.002129',
    'SZ.002142', 'SZ.002230', 'SZ.002236', 'SZ.002252', 'SZ.002304',
    'SZ.002352', 'SZ.002415', 'SZ.002475', 'SZ.002594', 'SZ.002714',
    'SZ.300014', 'SZ.300015', 'SZ.300059', 'SZ.300122', 'SZ.300124',
    'SZ.300142', 'SZ.300274', 'SZ.300312', 'SZ.300347', 'SZ.300413',
    'SZ.300433', 'SZ.300498', 'SZ.300601', 'SZ.300628', 'SZ.300750',
    'SZ.300759', 'SZ.300760', 'SZ.300782', 'SZ.300896'
]
print(f"✅ 沪深 300 成分股：{len(hs300_codes)} 只")

if not hs300_codes:
    print("⚠️  无法获取沪深 300 成分股，使用备用列表...")
    # 沪深 300 主要成分股（简化版）
    hs300_codes = [
        'SH.600000', 'SH.600009', 'SH.600016', 'SH.600028', 'SH.600030',
        'SH.600036', 'SH.600048', 'SH.600050', 'SH.600104', 'SH.600276',
        'SH.600309', 'SH.600346', 'SH.600436', 'SH.600519', 'SH.600585',
        'SH.600588', 'SH.600690', 'SH.600745', 'SH.600809', 'SH.600887',
        'SH.600893', 'SH.600900', 'SH.600905', 'SH.600919', 'SH.600938',
        'SH.601012', 'SH.601066', 'SH.601088', 'SH.601166', 'SH.601211',
        'SH.601225', 'SH.601288', 'SH.601318', 'SH.601328', 'SH.601390',
        'SH.601398', 'SH.601601', 'SH.601628', 'SH.601633', 'SH.601668',
        'SH.601688', 'SH.601728', 'SH.601766', 'SH.601800', 'SH.601816',
        'SH.601857', 'SH.601888', 'SH.601898', 'SH.601899', 'SH.601919',
        'SZ.000001', 'SZ.000002', 'SZ.000063', 'SZ.000100', 'SZ.000157',
        'SZ.000333', 'SZ.000538', 'SZ.000568', 'SZ.000596', 'SZ.000651',
        'SZ.000661', 'SZ.000725', 'SZ.000776', 'SZ.000858', 'SZ.000895',
        'SZ.002001', 'SZ.002007', 'SZ.002027', 'SZ.002049', 'SZ.002129',
        'SZ.002142', 'SZ.002230', 'SZ.002236', 'SZ.002252', 'SZ.002304',
        'SZ.002352', 'SZ.002415', 'SZ.002475', 'SZ.002594', 'SZ.002714',
        'SZ.300014', 'SZ.300015', 'SZ.300059', 'SZ.300122', 'SZ.300124',
        'SZ.300142', 'SZ.300274', 'SZ.300312', 'SZ.300347', 'SZ.300413',
        'SZ.300433', 'SZ.300498', 'SZ.300601', 'SZ.300628', 'SZ.300750',
        'SZ.300759', 'SZ.300760', 'SZ.300782', 'SZ.300896'
    ]
    print(f"  备用列表：{len(hs300_codes)} 只")

# 限制测试数量
TEST_LIMIT = 20
test_codes = hs300_codes[:TEST_LIMIT]
print(f"🧪 本次测试：{len(test_codes)} 只")

print("\n📊 获取富途真实资金流向数据...")
print("  预计耗时：约", len(test_codes) * 2, "秒")

all_data = []

for i, code in enumerate(tqdm(test_codes, desc="获取数据"), 1):
    try:
        # 获取资金流向数据
        ret, fund_df = quote_ctx.get_fund_flow(code)
        if ret != RET_OK or fund_df is None or len(fund_df) < 50:
            continue
        
        # 获取 K 线数据
        ret, k_data = quote_ctx.get_history_kline(code, ktype=KLType.K_DAY, autype=AdjustType.QFQ, max_count=300)
        if ret != RET_OK or k_data is None or len(k_data) < 50:
            continue
        
        # 数据处理
        fund_df['time_key'] = pd.to_datetime(fund_df['time_key'])
        fund_df = fund_df.sort_values('time_key')
        k_data['time_key'] = pd.to_datetime(k_data['time_key'])
        k_data = k_data.sort_values('time_key')
        
        # 合并
        merged = pd.merge(k_data, fund_df, on='time_key', how='inner')
        if len(merged) < 40:
            continue
        
        # 计算因子
        merged['main_flow_5d'] = merged['main_net_inflow'].rolling(5).mean()
        merged['super_order_5d'] = merged['super_net_inflow'].rolling(5).mean()
        merged['big_order_5d'] = merged['big_net_inflow'].rolling(5).mean()
        merged['flow_score'] = merged['main_flow_5d'] * 0.4 + merged['super_order_5d'] * 0.4 + merged['big_order_5d'] * 0.2
        
        # 标签
        merged['label'] = merged['close'].shift(-HOLDING_PERIOD).pct_change(HOLDING_PERIOD)
        merged = merged.dropna()
        
        if len(merged) > 30:
            merged['code'] = code
            all_data.append(merged)
    except Exception as e:
        continue
    
    time.sleep(0.5)

quote_ctx.close()

if not all_data:
    print("\n❌ 未获取到足够数据")
    sys.exit(1)

dataset = pd.concat(all_data, ignore_index=True)
print(f"\n📊 数据集：{len(dataset)}条记录，{dataset['code'].nunique()}只股票")

# 执行回测
print(f"\n📈 执行回测...")
dates = sorted(dataset['time_key'].unique())
capital = INITIAL_CAPITAL
positions = {}
trades = []

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
        top_stocks = day_data.sort_values('flow_score', ascending=False).head(available)
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

# 清仓计算
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
output_file = Path("/home/admin/openclaw/workspace/agents/data-collector/backtest_results") / f"backtest_v9_futu_{timestamp}.json"
output_file.parent.mkdir(exist_ok=True)
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
print(f"\n💾 结果已保存：{output_file.name}")
