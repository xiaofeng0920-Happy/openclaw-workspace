#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V11 多因子动态权重回测 - 富途 K 线 + AkShare 基本面"""

import sys
from pathlib import Path
sys.path.insert(0, '/home/admin/openclaw/workspace')

import pandas as pd
import numpy as np
from datetime import datetime
import json
import time
from tqdm import tqdm

INITIAL_CAPITAL = 1000000
POSITION_SIZE = 0.15
HOLDING_PERIOD = 20
TOP_K = 5
TRANSACTION_COST = 0.001
FUTU_HOST = '127.0.0.1'
FUTU_PORT = 11112

print("=" * 80)
print("🤖 V11 多因子动态权重回测 - 富途 K 线 + AkShare 基本面")
print("=" * 80)

from futu import *
import akshare as ak

# === 第一步：判断市场状态 ===
print("\n📈 第一步：判断 A 股市场状态")
print("=" * 80)

quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT)
ret, data, _ = quote_ctx.request_history_kline('SH.000300', ktype=KLType.K_DAY, max_count=250)

if ret == RET_OK and data is not None:
    close = data['close'].values
    ma20 = data['close'].rolling(20).mean().values[-1]
    ma60 = data['close'].rolling(60).mean().values[-1]
    ma250 = data['close'].rolling(250).mean().values[-1]
    current = close[-1]
    change_250 = (close[-1] - close[0]) / close[0] * 100
    
    bull = (current>ma20) + (current>ma60) + (current>ma250) + (2 if ma20>ma60>ma250 else 0)
    bear = (current<ma20) + (current<ma60) + (current<ma250) + (2 if ma20<ma60<ma250 else 0)
    
    if bull >= 4 and change_250 > 20: market_state = 'bull'
    elif bear >= 4 and change_250 < -20: market_state = 'bear'
    else: market_state = 'oscillate'
    
    print(f"  沪深 300: {current:.0f} | 250 日:{change_250:+.1f}% | 多:{bull} 空:{bear}")
    print(f"  ✅ 市场状态：{'🐂牛市' if market_state=='bull' else '🐻熊市' if market_state=='bear' else '📊震荡市'}")

# === 第二步：动态权重 ===
print("\n📊 第二步：动态调整因子权重")
print("=" * 80)

if market_state == 'bull':
    WEIGHTS = {'capital': 0.40, 'sentiment': 0.20, 'value': 0.20, 'quality': 0.20}
    print("  🐂 牛市进攻型：资金 40% + 情绪 20% + 价值 20% + 质量 20%")
elif market_state == 'bear':
    WEIGHTS = {'value': 0.40, 'quality': 0.40, 'capital': 0.10, 'sentiment': 0.10}
    print("  🐻 熊市防御型：价值 40% + 质量 40% + 资金 10% + 情绪 10%")
else:
    WEIGHTS = {'capital': 0.30, 'value': 0.30, 'quality': 0.30, 'sentiment': 0.10}
    print("  📊 震荡市均衡型：资金 30% + 价值 30% + 质量 30% + 情绪 10%")

# === 第三步：获取基本面数据 ===
print("\n📊 第三步：获取基本面数据 (AkShare)")
print("=" * 80)

hs300 = ['000001','000002','000063','000100','000157','000333','000538','000568','000596','000651',
         '000661','000725','000776','000858','000895','002001','002027','002049','002129','002142',
         '002230','002252','002304','002352','002415','002475','002594','002714','300014','300059']

fundamental = {}
print(f"  获取{len(hs300)}只股票基本面数据...")
for code in tqdm(hs300, desc="基本面"):
    try:
        ret = ak.stock_financial_analysis_indicator(symbol=code)
        if ret is not None and len(ret) > 0:
            latest = ret.iloc[0]
            fundamental[code] = {
                'roe': float(latest.get('净资产收益率 - 加权%', np.nan)) if '净资产收益率 - 加权%' in latest.index else np.nan,
                'gross': float(latest.get('销售毛利率%', np.nan)) if '销售毛利率%' in latest.index else np.nan,
                'pe': float(latest.get('市盈率 - 动态%', np.nan)) if '市盈率 - 动态%' in latest.index else np.nan
            }
    except: continue
    time.sleep(0.1)
print(f"  ✅ 获取到{len(fundamental)}只股票基本面数据")

# === 第四步：计算多因子得分 ===
print("\n📊 第四步：计算多因子得分")
print("=" * 80)

ret, state = quote_ctx.get_global_state()
if ret != RET_OK: print("❌ OpenD 连接失败"); sys.exit(1)
print("✅ OpenD 连接成功！")

all_data = []
for code in tqdm(hs300, desc="计算因子"):
    try:
        ret, k, _ = quote_ctx.request_history_kline(f'SH.{code}' if code.startswith('6') else f'SZ.{code}', ktype=KLType.K_DAY, max_count=300)
        if ret != RET_OK or k is None or len(k) < 100: continue
        k = k.sort_values('time_key')
        c, v = k['close'], k['volume']
        
        # 资金动能
        mom = c.pct_change(10) * (v / v.rolling(20).mean())
        obv = (np.sign(c.diff()) * v).rolling(20).sum().pct_change(10)
        capital = (mom * 0.6 + obv * 0.4).fillna(0)
        
        # 价值（用 AkShare 真实 PE）
        if code in fundamental and not np.isnan(fundamental[code].get('pe', np.nan)) and fundamental[code]['pe'] > 0:
            value = pd.Series(1 / (fundamental[code]['pe'] + 0.01), index=k.index)
        else:
            h52, l52 = c.rolling(250).max(), c.rolling(250).min()
            value = (1 - (c - l52) / (h52 - l52 + 0.01)).fillna(0)
        
        # 质量（用 AkShare 真实 ROE）
        if code in fundamental and not np.isnan(fundamental[code].get('roe', np.nan)):
            roe_score = pd.Series(fundamental[code]['roe'] / 100, index=k.index)
        else:
            roe_score = (1 / (c.pct_change().rolling(60).std() + 0.01)).pct_change().fillna(0)
        gross_score = pd.Series(fundamental.get(code, {}).get('gross', 10) / 100, index=k.index) if code in fundamental else pd.Series(0.5, index=k.index)
        quality = (roe_score * 0.6 + gross_score * 0.4).fillna(0)
        
        # 情绪
        delta = c.diff()
        gain, loss = delta.where(delta>0,0).rolling(14).mean(), (-delta.where(delta<0,0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + gain / loss))
        sent = ((50 - rsi) / 50).fillna(0)
        
        # 综合得分
        k['score'] = (capital * WEIGHTS['capital'] + value * WEIGHTS['value'] + quality * WEIGHTS['quality'] + sent * WEIGHTS['sentiment'])
        k['score'] = (k['score'] - k['score'].rolling(60).mean()) / (k['score'].rolling(60).std() + 0.01)
        k['label'] = c.shift(-HOLDING_PERIOD).pct_change(HOLDING_PERIOD)
        k = k.dropna()
        if len(k) > 50: k['code'] = code; all_data.append(k)
    except: continue
    time.sleep(0.2)

quote_ctx.close()
if not all_data: print("❌ 无数据"); sys.exit(1)

ds = pd.concat(all_data, ignore_index=True)
print(f"✅ 数据集:{len(ds)}条，{ds['code'].nunique()}只股票")

# === 第五步：回测 ===
print("\n📈 第五步：执行回测")
print("=" * 80)

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

print("\n"+"="*80)
print("📊 回测结果:")
print("="*80)
print(f"  初始资金:{INITIAL_CAPITAL:,}元  最终价值:{fv:,.0f}元")
print(f"  总收益:{tr:+.2f}%  胜率:{wr:.1f}%  交易:{len(trades)}笔")
print(f"  市场状态:{'🐂牛市' if market_state=='bull' else '🐻熊市' if market_state=='bear' else '📊震荡市'}")
print(f"  因子权重:资金{WEIGHTS['capital']*100}% 价值{WEIGHTS['value']*100}% 质量{WEIGHTS['quality']*100}% 情绪{WEIGHTS['sentiment']*100}%")
print("="*80)
print("✅ 盈利!" if tr>0 else "🟡 胜率>50%" if wr>50 else "⚠️ 亏损")

ts = datetime.now().strftime('%Y%m%d_%H%M%S')
res = {'timestamp':ts,'market_state':market_state,'weights':WEIGHTS,'total_return':tr,'win_rate':wr,'trades':trades[:20]}
of = Path("/home/admin/openclaw/workspace/agents/data-collector/backtest_results")/f"backtest_v11_{ts}.json"
of.parent.mkdir(exist_ok=True)
with open(of,'w',encoding='utf-8') as f: json.dump(res,f,indent=2,ensure_ascii=False)
print(f"\n💾 已保存:{of.name}")
