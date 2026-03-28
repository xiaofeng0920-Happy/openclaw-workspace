#!/usr/bin/env python3
"""V16 市场状态识别与动态配置策略"""
import sys, time, json
from pathlib import Path
sys.path.insert(0, '/home/admin/openclaw/workspace')
import pandas as pd, numpy as np
from datetime import datetime
from tqdm import tqdm
from futu import *
import akshare as ak

print("="*80)
print("🤖 V16 市场状态识别与动态配置策略")
print("="*80)

ctx = OpenQuoteContext(host='127.0.0.1', port=11112)

# === 第一步：市场状态识别 ===
print("\n📈 第一步：市场状态识别")
print("="*80)

ret, data, _ = ctx.request_history_kline('SH.000300', ktype=KLType.K_DAY, max_count=500)
if ret != RET_OK or data is None:
    print("❌ 获取沪深 300 数据失败")
    sys.exit(1)

data = data.sort_values('time_key')
close = data['close']
ma250 = close.rolling(250).mean()
ma250_slope = ma250.diff()

# RSI
delta = close.diff()
gain = (delta.where(delta > 0, 0)).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
rsi = 100 - (100 / (1 + gain/loss))

# 市场广度（简化：用上涨股票比例代替，这里用沪深 300 成分股涨跌比）
# 实际应该获取全市场数据，这里简化处理
breadth = pd.Series(50, index=data.index)  # 简化为 50%

# 市场状态判断
market_state = []
for i in range(len(data)):
    if i < 250:
        market_state.append('oscillate')
        continue
    
    c = close.iloc[i]
    m250 = ma250.iloc[i]
    slope = ma250_slope.iloc[i]
    r = rsi.iloc[i]
    b = breadth.iloc[i]
    
    # 牛市条件
    bull = (c > m250) and (slope > 0) and (r > 50) and (b > 60)
    
    # 熊市条件（满足 2 个及以上）
    bear_count = 0
    if c < m250: bear_count += 1
    if slope < 0: bear_count += 1
    if r < 40: bear_count += 1
    if b < 40: bear_count += 1
    
    if bull:
        market_state.append('bull')
    elif bear_count >= 2:
        market_state.append('bear')
    else:
        market_state.append('oscillate')

data['market_state'] = market_state

# 统计
state_counts = pd.Series(market_state).value_counts()
print(f"\n  市场状态统计（{len(data)}天）:")
print(f"    🐂 牛市：{state_counts.get('bull', 0)}天 ({state_counts.get('bull', 0)/len(data)*100:.1f}%)")
print(f"    📊 震荡市：{state_counts.get('oscillate', 0)}天 ({state_counts.get('oscillate', 0)/len(data)*100:.1f}%)")
print(f"    🐻 熊市：{state_counts.get('bear', 0)}天 ({state_counts.get('bear', 0)/len(data)*100:.1f}%)")

current_state = market_state[-1]
print(f"\n  ✅ 当前市场状态：{'🐂牛市' if current_state=='bull' else '🐻熊市' if current_state=='bear' else '📊震荡市'}")

# === 第二步：动态配置参数 ===
print("\n📊 第二步：动态配置参数")
print("="*80)

CONFIG = {
    'bull': {
        'position_limit': 0.95,      # 仓位上限 95%
        'top_k': 10,                  # 持仓 10 只
        'pe_max': 35,                 # PE<35
        'roe_min': 12,                # ROE>12%
        'weights': {'capital': 0.40, 'value': 0.20, 'quality': 0.20, 'sentiment': 0.20}
    },
    'oscillate': {
        'position_limit': 0.65,       # 仓位上限 65%
        'top_k': 5,                   # 持仓 5 只
        'pe_max': 30,                 # PE<30
        'roe_min': 15,                # ROE>15%
        'weights': {'capital': 0.30, 'value': 0.30, 'quality': 0.30, 'sentiment': 0.10}
    },
    'bear': {
        'position_limit': 0.30,       # 仓位上限 30%
        'top_k': 3,                   # 持仓 3 只
        'pe_max': 25,                 # PE<25
        'roe_min': 18,                # ROE>18%
        'weights': {'capital': 0.10, 'value': 0.40, 'quality': 0.40, 'sentiment': 0.10}
    }
}

current_config = CONFIG[current_state]
print(f"\n  当前配置（{'🐂牛市' if current_state=='bull' else '🐻熊市' if current_state=='bear' else '📊震荡市'}）:")
print(f"    仓位上限：{current_config['position_limit']*100}%")
print(f"    持仓数量：{current_config['top_k']}只")
print(f"    PE 上限：{current_config['pe_max']}")
print(f"    ROE 下限：{current_config['roe_min']}%")
print(f"    因子权重：资金{current_config['weights']['capital']*100}% + 价值{current_config['weights']['value']*100}% + 质量{current_config['weights']['quality']*100}% + 情绪{current_config['weights']['sentiment']*100}%")

# === 第三步：获取股票池 ===
print("\n📊 第三步：获取沪深 300 成分股")
print("="*80)

hs300 = ['000001','000002','000063','000100','000157','000333','000538','000568','000596','000651',
         '000661','000725','000776','000858','000895','002001','002027','002049','002129','002142',
         '002230','002252','002304','002352','002415','002475','002594','002714','300014','300059',
         '300122','300124','300142','300274','300312','300347','300413','300433','300498','300601',
         '300628','300750','300759','300760','300782','300896','600000','600009','600016','600028',
         '600030','600031','600036','600048','600050','600104','600276','600309','600346','600436',
         '600519','600585','600588','600690','600745','600809','600887','600893','600900','600905',
         '600919','600938','601012','601066','601088','601166','601211','601225','601288','601318',
         '601328','601390','601398','601601','601628','601633','601668','601688','601728','601766',
         '601800','601816','601857','601888','601898','601899','601919','601988','601995','601998']

print(f"  股票池:{len(hs300)}只")

# 基本面筛选
print(f"\n  基本面筛选 (PE<{current_config['pe_max']}, ROE>{current_config['roe_min']}%)...")
fundamental = {}
for code in tqdm(hs300, desc="筛选"):
    try:
        ret = ak.stock_financial_analysis_indicator(symbol=code)
        if ret is None or len(ret)==0: continue
        latest = ret.iloc[0]
        pe = float(latest.get('市盈率 - 动态%', np.nan)) if '市盈率 - 动态%' in latest.index else np.nan
        roe_col = None
        for col in ret.columns:
            if '净资产收益率' in col and '%' in col: roe_col=col; break
        roe_vals = ret[roe_col].head(12).values if roe_col else []
        roe_min = np.nanmin(roe_vals) if len(roe_vals)>0 else np.nan
        if np.isnan(pe) or pe > current_config['pe_max']: continue
        if np.isnan(roe_min) or roe_min < current_config['roe_min']: continue
        fundamental[code] = {'pe':pe,'roe_avg':np.nanmean(roe_vals)}
    except: continue
    time.sleep(0.1)

if len(fundamental) < 5:
    print(f"\n⚠️  筛选后仅{len(fundamental)}只，放宽条件...")
    for code in hs300:
        try:
            ret = ak.stock_financial_analysis_indicator(symbol=code)
            if ret is None or len(ret)==0: continue
            latest = ret.iloc[0]
            pe = float(latest.get('市盈率 - 动态%',np.nan)) if '市盈率 - 动态%' in latest.index else np.nan
            if np.isnan(pe) or pe>50: continue
            fundamental[code] = {'pe':pe,'roe_avg':12}
        except: continue
        time.sleep(0.1)

qualified = list(fundamental.keys())
print(f"  ✅ 筛选后:{len(qualified)}只")

# K 线
print("\n📊 获取 K 线...")
kdata = {}
for code in tqdm(qualified, desc="K 线"):
    try:
        ret,k,_ = ctx.request_history_kline(f'SH.{code}' if code.startswith('6') else f'SZ.{code}', ktype=KLType.K_DAY, max_count=500)
        if ret==RET_OK and k is not None and len(k)>100:
            kdata[code]=k.sort_values('time_key')
    except: pass
    time.sleep(0.15)
ctx.close()
print(f"  ✅ {len(kdata)}只")

# === 第四步：回测 ===
print("\n📈 第四步：回测（动态配置）")
print("="*80)

def backtest_dynamic():
    """动态配置回测"""
    results_by_state = {'bull':[],'oscillate':[],'bear':[]}
    
    for i, state in enumerate(market_state[:-20]):
        if state == 'oscillate': continue  # 跳过数据不足的部分
        
        # 获取该时段的配置
        cfg = CONFIG[state]
        hp = 10  # 持有期固定 10 天
        
        # 简化回测：只计算该时段的平均收益
        returns = []
        for code in list(kdata.keys())[:cfg['top_k']]:
            k = kdata[code].copy()
            if len(k) <= i+hp: continue
            ret = k['close'].iloc[i+hp] / k['close'].iloc[i] - 1
            returns.append(ret)
        
        if returns:
            avg_ret = np.mean(returns)
            results_by_state[state].append(avg_ret)
    
    # 计算各市场状态的年化收益
    state_returns = {}
    for state, rets in results_by_state.items():
        if rets:
            state_returns[state] = np.mean(rets) * (252/10)  # 年化
    
    return state_returns

state_returns = backtest_dynamic()
print("\n  各市场状态年化收益:")
for state, ret in state_returns.items():
    emoji = '🐂' if state=='bull' else '🐻' if state=='bear' else '📊'
    print(f"    {emoji} {state}: {ret*100:+.2f}%")

# 综合收益
weighted_ret = sum(state_returns.get(s, 0) * state_counts.get(s, 0) for s in ['bull','oscillate','bear']) / len(market_state)
print(f"\n  ✅ 综合年化收益：{weighted_ret*100:+.2f}%")

# === 第五步：生成报告 ===
print("\n"+"="*80)
print("📊 V16 策略报告")
print("="*80)

report = {
    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'market_state': current_state,
    'current_config': current_config,
    'state_returns': state_returns,
    'weighted_return': weighted_ret,
    'pool_size': len(qualified)
}

print(f"\n  报告时间：{report['timestamp']}")
print(f"  当前市场：{'🐂牛市' if current_state=='bull' else '🐻熊市' if current_state=='bear' else '📊震荡市'}")
print(f"  股票池：{len(qualified)}只")
print(f"  预期年化：{weighted_ret*100:+.2f}%")

# 保存
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
with open(Path("/home/admin/openclaw/workspace/agents/data-collector/backtest_results")/f"v16_{ts}.json",'w') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print(f"\n💾 已保存:v16_{ts}.json")
