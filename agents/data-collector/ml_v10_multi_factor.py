#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V10 富途 OpenD 多因子回测 - 市场状态判断 + 多因子融合"""

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
HOLDING_PERIOD = 20
TOP_K = 5
TRANSACTION_COST = 0.001
FUTU_HOST = '127.0.0.1'
FUTU_PORT = 11112

# 因子权重（锋哥指定）
FACTOR_WEIGHTS = {'capital': 0.30, 'value': 0.30, 'quality': 0.30, 'sentiment': 0.10}
# ===============================

print("=" * 70)
print("🤖 V10 富途 OpenD 多因子回测")
print("=" * 70)
print(f"因子权重：资金{FACTOR_WEIGHTS['capital']*100}% + 价值{FACTOR_WEIGHTS['value']*100}% + 质量{FACTOR_WEIGHTS['quality']*100}% + 情绪{FACTOR_WEIGHTS['sentiment']*100}%")
print("=" * 70)

from futu import *

quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT)
ret, data = quote_ctx.get_global_state()
if ret != RET_OK:
    print(f"❌ 连接失败"); sys.exit(1)
print("✅ OpenD 连接成功！")

# === 第一步：判断市场状态 ===
print("\n📈 判断市场状态...")
ret, data, _ = quote_ctx.request_history_kline('SH.000300', ktype=KLType.K_DAY, max_count=250)
if ret == RET_OK and data is not None:
    close = data['close'].values
    ma20, ma60, ma250 = close[-1], data['close'].rolling(20).mean().values[-1], data['close'].rolling(60).mean().values[-1]
    change_250 = (close[-1] - close[0]) / close[0] * 100
    
    if ma20 > ma60 and change_250 > 20: market_state = 'bull'
    elif ma20 < ma60 and change_250 < -20: market_state = 'bear'
    else: market_state = 'oscillate'
    
    print(f"  沪深 300: {ma20:.0f}, 250 日涨跌:{change_250:+.1f}% → 市场状态：{market_state}")
    
    # 根据市场调整权重
    if market_state == 'bull': FACTOR_WEIGHTS = {'capital': 0.35, 'value': 0.25, 'quality': 0.20, 'sentiment': 0.20}
    elif market_state == 'bear': FACTOR_WEIGHTS = {'capital': 0.15, 'value': 0.40, 'quality': 0.35, 'sentiment': 0.10}

# === 第二步：获取股票数据 ===
hs300 = ['SH.600000','SH.600036','SH.600519','SH.601318','SH.601398','SZ.000001','SZ.000002','SZ.000333','SZ.000651','SZ.002415','SZ.300059','SZ.300750','SH.600048','SH.600887','SH.601888','SZ.000568','SZ.000858','SZ.002594','SH.600276','SH.600436']
print(f"\n📊 获取{len(hs300)}只股票数据...")

all_data = []
for code in tqdm(hs300, desc="计算因子"):
    try:
        ret, k, _ = quote_ctx.request_history_kline(code, ktype=KLType.K_DAY, max_count=300)
        if ret != RET_OK or k is None or len(k) < 100: continue
        k = k.sort_values('time_key')
        c, v = k['close'], k['volume']
        
        # 资金动能
        mom = c.pct_change(10) * (v / v.rolling(20).mean())
        # 价值
        h52, l52 = c.rolling(250).max(), c.rolling(250).min()
        val = 1 - (c - l52) / (h52 - l52 + 0.01)
        # 质量
        stab = 1 / (c.pct_change().rolling(60).std() + 0.01)
        # 情绪
        delta = c.diff()
        gain, loss = delta.where(delta>0,0).rolling(14).mean(), (-delta.where(delta<0,0)).rolling(14).mean()
        rsi = 100 - (100/(1+gain/loss))
        sent = (50-rsi)/50
        
        # 综合得分
        k['score'] = (mom*FACTOR_WEIGHTS['capital'] + val*FACTOR_WEIGHTS['value'] + stab*FACTOR_WEIGHTS['quality'] + sent*FACTOR_WEIGHTS['sentiment']).fillna(0)
        k['score'] = (k['score'] - k['score'].rolling(60).mean()) / (k['score'].rolling(60).std() + 0.01)
        k['label'] = c.shift(-HOLDING_PERIOD).pct_change(HOLDING_PERIOD)
        k = k.dropna()
        if len(k) > 50: k['code']=code; all_data.append(k)
    except: continue
    time.sleep(0.2)

quote_ctx.close()
if not all_data: print("❌ 无数据"); sys.exit(1)

ds = pd.concat(all_data, ignore_index=True)
print(f"✅ 数据集:{len(ds)}条，{ds['code'].nunique()}只股票")

# === 第三步：回测 ===
print("\n📈 执行回测...")
dates = sorted(ds['time_key'].unique())
cap, pos, trades, pv = INITIAL_CAPITAL, {}, [], []

for date in tqdm(dates[:-HOLDING_PERIOD], desc="回测"):
    dd = ds[ds['time_key']==date]
    # 卖出
    for code in list(pos.keys()):
        p = pos[code]
        if (pd.to_datetime(date)-pd.to_datetime(p['entry_date'])).days >= HOLDING_PERIOD:
            sd = dd[dd['code']==code]
            if len(sd)>0:
                ep = sd['close'].values[0]
                pnl = (ep-p['entry_price'])*p['shares'] - p['entry_price']*p['shares']*TRANSACTION_COST*2
                cap += p['shares']*ep - p['entry_price']*p['shares']*TRANSACTION_COST*2
                trades.append({'code':code,'pnl':pnl,'pnl_pct':(ep-p['entry_price'])/p['entry_price']*100})
                del pos[code]
    # 买入
    if len(pos) < TOP_K:
        top = dd.sort_values('score', ascending=False).head(TOP_K-len(pos))
        for _,r in top.iterrows():
            sh = int(cap*POSITION_SIZE/r['close']/100)*100
            if sh>0 and cap>=r['close']*sh*(1+TRANSACTION_COST):
                cap -= r['close']*sh*(1+TRANSACTION_COST)
                pos[r['code']] = {'entry_price':r['close'],'entry_date':date,'shares':sh}
    # 组合价值
    pvv = cap
    for code,p in pos.items():
        sd = dd[dd['code']==code]
        if len(sd)>0: pvv += p['shares']*sd['close'].values[0]
    pv.append({'date':date,'value':pvv})

# 清仓
fv = cap
for code,p in pos.items():
    sd = ds[ds['time_key']==dates[-1]]
    sd = sd[sd['code']==code]
    if len(sd)>0: fv += p['shares']*sd['close'].values[0]

tr = (fv-INITIAL_CAPITAL)/INITIAL_CAPITAL*100
wr = len([t for t in trades if t['pnl']>0])/len(trades)*100 if trades else 0

print("\n"+"="*70)
print("📊 回测结果:")
print("="*70)
print(f"  初始资金:{INITIAL_CAPITAL:,}元  最终价值:{fv:,.0f}元")
print(f"  总收益:{tr:+.2f}%  胜率:{wr:.1f}%  交易:{len(trades)}笔")
print("="*70)
print("✅ 盈利!" if tr>0 else "🟡 胜率>50%" if wr>50 else "⚠️ 亏损")

ts = datetime.now().strftime('%Y%m%d_%H%M%S')
res = {'timestamp':ts,'market_state':market_state,'total_return':tr,'win_rate':wr,'trades':trades[:20]}
of = Path("/home/admin/openclaw/workspace/agents/data-collector/backtest_results")/f"backtest_v10_{ts}.json"
of.parent.mkdir(exist_ok=True)
with open(of,'w',encoding='utf-8') as f: json.dump(res,f,indent=2,ensure_ascii=False)
print(f"\n💾 已保存:{of.name}")
