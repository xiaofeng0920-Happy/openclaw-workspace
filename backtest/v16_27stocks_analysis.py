#!/usr/bin/env python3
"""V16 回测深度分析 - 按市场状态分解收益"""

import sys
sys.path.insert(0, '/home/admin/openclaw/workspace')

import pandas as pd
import numpy as np
from datetime import datetime
import akshare as ak

print("="*80)
print("📊 V16 回测深度分析 - 按市场状态分解")
print("="*80)

# 读取回测数据
df = pd.read_csv('/home/admin/openclaw/workspace/backtest/v16_27stocks_daily_values.csv')
df['date'] = pd.to_datetime(df['date'])
df = df.set_index('date')

# 获取沪深 300 数据
hs300 = ak.stock_zh_index_daily(symbol="sh000300")
hs300['date'] = pd.to_datetime(hs300['date'])
hs300 = hs300[(hs300['date']>='2020-01-01') & (hs300['date']<='2026-12-31')].sort_values('date')

# 重新计算市场状态
close = hs300['close']
ma250 = close.rolling(250).mean()
slope = ma250.diff()
delta = close.diff()
gain = delta.where(delta>0, 0).rolling(14).mean()
loss = (-delta.where(delta<0, 0)).rolling(14).mean()
rsi = 100 - (100/(1+gain/loss))

states = []
for i in range(len(hs300)):
    if i < 250:
        states.append('oscillate')
        continue
    c, m, s, r = close.iloc[i], ma250.iloc[i], slope.iloc[i], rsi.iloc[i]
    if (c>m) and (s>0) and (r>50):
        states.append('bull')
    elif (c<m) + (s<0) + (r<40) >= 2:
        states.append('bear')
    else:
        states.append('oscillate')

hs300['state'] = states
hs300 = hs300.set_index('date')

# 合并数据
df['hs300_close'] = hs300['close']
df['state'] = hs300['state']

# 初始资金
initial = 1000000

print("\n📈 各市场状态详细分析")
print("="*80)

results = []
for state in ['bull', 'oscillate', 'bear']:
    state_data = df[df['state']==state].copy()
    if len(state_data) < 10:
        continue
    
    # 计算该状态下的收益
    start_val = state_data['value'].iloc[0]
    end_val = state_data['value'].iloc[-1]
    period_ret = (end_val - start_val) / start_val
    
    # 计算年化
    days = len(state_data)
    ann_ret = (1 + period_ret) ** (252/days) - 1 if days > 0 else 0
    
    # 计算该状态下最大回撤
    rolling_max = state_data['value'].cummax()
    drawdown = (state_data['value'] - rolling_max) / rolling_max
    max_dd = drawdown.min()
    
    # 计算波动率
    daily_rets = state_data['value'].pct_change().dropna()
    vol = daily_rets.std() * np.sqrt(252) if len(daily_rets) > 10 else 0
    
    # 计算夏普
    rf = 0.03
    sharpe = (ann_ret - rf) / vol if vol > 0 else 0
    
    # 沪深 300 同期表现
    hs300_state = hs300[hs300['state']==state]
    if len(hs300_state) > 1:
        bm_ret = (hs300_state['close'].iloc[-1] / hs300_state['close'].iloc[0] - 1)
        bm_ann = (1 + bm_ret) ** (252/len(hs300_state)) - 1
    else:
        bm_ret = 0
        bm_ann = 0
    
    alpha = ann_ret - bm_ann
    
    emoji = '🐂' if state=='bull' else '🐻' if state=='bear' else '📊'
    state_name = '牛市' if state=='bull' else '熊市' if state=='bear' else '震荡市'
    
    print(f"\n{emoji} {state_name} ({days}天, {days/252:.1f}年)")
    print(f"  策略收益：{period_ret*100:+.1f}% (年化{ann_ret*100:+.1f}%)")
    print(f"  沪深 300: {bm_ret*100:+.1f}% (年化{bm_ann*100:+.1f}%)")
    print(f"  超额收益：{alpha*100:+.1f}%")
    print(f"  最大回撤：{max_dd*100:.1f}%")
    print(f"  波动率：{vol*100:.1f}%")
    print(f"  夏普比率：{sharpe:.2f}")
    
    results.append({
        'state': state_name,
        'days': days,
        'period_ret': period_ret,
        'ann_ret': ann_ret,
        'benchmark_ret': bm_ret,
        'alpha': alpha,
        'max_dd': max_dd,
        'volatility': vol,
        'sharpe': sharpe
    })

# 按年度分析
print("\n\n📅 分年度表现")
print("="*80)

df['year'] = df.index.year
for year in sorted(df['year'].unique()):
    year_data = df[df['year']==year]
    if len(year_data) < 50:
        continue
    
    start_val = year_data['value'].iloc[0]
    end_val = year_data['value'].iloc[-1]
    ret = (end_val - start_val) / start_val
    
    # 沪深 300 同年表现
    year_hs300 = hs300[hs300.index.year==year]
    if len(year_hs300) > 1:
        bm_ret = (year_hs300['close'].iloc[-1] / year_hs300['close'].iloc[0] - 1)
    else:
        bm_ret = 0
    
    # 该年市场状态分布
    state_dist = year_data['state'].value_counts()
    
    print(f"\n{year}年:")
    print(f"  策略收益：{ret*100:+.1f}% | 沪深 300: {bm_ret*100:+.1f}% | 超额：{(ret-bm_ret)*100:+.1f}%")
    print(f"  市场状态：牛市{state_dist.get('bull',0)}天 | 震荡{state_dist.get('oscillate',0)}天 | 熊市{state_dist.get('bear',0)}天")

# 滚动收益分析
print("\n\n📊 滚动 12 个月收益")
print("="*80)

df['ret_12m'] = df['value'].pct_change(252)
df['bm_12m'] = df['hs300_close'].pct_change(252)

# 最近 12 个月
recent = df.dropna(subset=['ret_12m']).iloc[-1]
print(f"\n最近 12 个月:")
print(f"  策略收益：{recent['ret_12m']*100:+.1f}%")
print(f"  沪深 300: {recent['bm_12m']*100:+.1f}%")
print(f"  超额收益：{(recent['ret_12m']-recent['bm_12m'])*100:+.1f}%")

# 最佳/最差时期
best_idx = df['ret_12m'].idxmax()
worst_idx = df['ret_12m'].idxmin()

print(f"\n最佳 12 个月：{best_idx.strftime('%Y-%m-%d')} ({df.loc[best_idx, 'ret_12m']*100:+.1f}%)")
print(f"最差 12 个月：{worst_idx.strftime('%Y-%m-%d')} ({df.loc[worst_idx, 'ret_12m']*100:+.1f}%)")

# 生成对比表格
print("\n\n📋 完整对比表")
print("="*80)

summary_df = pd.DataFrame(results)
summary_df = summary_df.set_index('state')
print("\n" + summary_df.to_string(float_format=lambda x: f'{x*100:.1f}%' if 'ret' in str(x) or 'dd' in str(x) or 'vol' in str(x) else f'{x:.2f}' if 'sharpe' in str(x) else f'{x:.0f}'))

# 保存详细分析
output = {
    'summary': summary_df.to_dict(),
    'annual': {},
    'recent_12m': {
        'strategy': recent['ret_12m'],
        'benchmark': recent['bm_12m'],
        'alpha': recent['ret_12m'] - recent['bm_12m']
    }
}

import json
with open('/home/admin/openclaw/workspace/backtest/v16_27stocks_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, default=str)

print("\n\n✅ 详细分析已保存至：v16_27stocks_analysis.json")
print("="*80)
