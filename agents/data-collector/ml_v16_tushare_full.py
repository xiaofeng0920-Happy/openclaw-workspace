#!/usr/bin/env python3
"""V16 市场状态识别与动态配置策略 - Tushare 完整版"""
import sys, time, json
from pathlib import Path
sys.path.insert(0, '/home/admin/openclaw/workspace')
import pandas as pd, numpy as np
from datetime import datetime
from tqdm import tqdm
import tushare as ts

print("="*80)
print("🤖 V16 市场状态识别与动态配置策略 - Tushare 完整版")
print("="*80)

# 初始化 Tushare
ts.set_token('eb58a2fb952bce3b9590d9290eea7966097450737fa8ad22156f2ca5')
pro = ts.pro_api()

# === 第一步：获取沪深 300 数据 ===
print("\n📈 第一步：获取沪深 300 指数数据")
print("="*80)

data = pro.index_daily(ts_code='000300.SH', start_date='20200101', end_date=datetime.now().strftime('%Y%m%d'))
if data is None or len(data)==0:
    print("❌ 获取沪深 300 数据失败")
    sys.exit(1)

data = data.sort_values('trade_date')
data['trade_date'] = pd.to_datetime(data['trade_date'])
data = data.set_index('trade_date')

close = data['close']
ma250 = close.rolling(250).mean()
ma250_slope = ma250.diff()

# RSI
delta = close.diff()
gain = (delta.where(delta > 0, 0)).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
rsi = 100 - (100 / (1 + gain/loss))

print(f"  数据范围：{data.index[0]} 至 {data.index[-1]}")
print(f"  数据条数：{len(data)}天")
print(f"  当前点位：{close.iloc[-1]:.2f}")
print(f"  MA250: {ma250.iloc[-1]:.2f}")
print(f"  RSI(14): {rsi.iloc[-1]:.2f}")

# === 第二步：市场状态识别 ===
print("\n📊 第二步：市场状态识别")
print("="*80)

market_state = []
for i in range(len(data)):
    if i < 250:
        market_state.append('oscillate')
        continue
    
    c = close.iloc[i]
    m250 = ma250.iloc[i]
    slope = ma250_slope.iloc[i]
    r = rsi.iloc[i]
    
    if (c > m250) and (slope > 0) and (r > 50):
        market_state.append('bull')
    elif (c < m250) and (slope < 0) and (r < 40):
        market_state.append('bear')
    else:
        market_state.append('oscillate')

data['market_state'] = market_state

state_counts = pd.Series(market_state).value_counts()
print(f"\n  市场状态统计（{len(data)}天）:")
print(f"    🐂 牛市：{state_counts.get('bull', 0)}天 ({state_counts.get('bull', 0)/len(data)*100:.1f}%)")
print(f"    📊 震荡市：{state_counts.get('oscillate', 0)}天 ({state_counts.get('oscillate', 0)/len(data)*100:.1f}%)")
print(f"    🐻 熊市：{state_counts.get('bear', 0)}天 ({state_counts.get('bear', 0)/len(data)*100:.1f}%)")

current_state = market_state[-1]
print(f"\n  ✅ 当前市场状态：{'🐂牛市' if current_state=='bull' else '🐻熊市' if current_state=='bear' else '📊震荡市'}")

# === 第三步：动态配置参数 ===
print("\n⚙️ 第三步：动态配置参数")
print("="*80)

CONFIG = {
    'bull': {'position_limit':0.95,'top_k':10,'pe_max':35,'roe_min':12,'weights':{'capital':0.40,'value':0.20,'quality':0.20,'sentiment':0.20}},
    'oscillate': {'position_limit':0.65,'top_k':5,'pe_max':30,'roe_min':15,'weights':{'capital':0.30,'value':0.30,'quality':0.30,'sentiment':0.10}},
    'bear': {'position_limit':0.30,'top_k':3,'pe_max':25,'roe_min':18,'weights':{'capital':0.10,'value':0.40,'quality':0.40,'sentiment':0.10}}
}

current_config = CONFIG[current_state]
print(f"\n  当前配置:")
print(f"    仓位上限：{current_config['position_limit']*100}%")
print(f"    持仓数量：{current_config['top_k']}只")

# === 第四步：获取沪深 300 成分股 ===
print("\n📊 第四步：获取沪深 300 成分股")
print("="*80)

try:
    weights = pro.index_weight(ts_code='000300.SH', start_date=datetime.now().strftime('%Y%m%d'), end_date=datetime.now().strftime('%Y%m%d'))
    if weights is not None and len(weights)>0:
        hs300_codes = weights['con_code'].tolist()
        # 转换代码格式（去掉后缀）
        hs300_codes = [c.split('.')[0] for c in hs300_codes]
        print(f"  获取到{len(hs300_codes)}只成分股")
    else:
        raise Exception("API 返回空")
except Exception as e:
    print(f"  ⚠️  {e}，使用备用列表...")
    hs300_codes = ['000001','000002','000063','000100','000333','000538','000568','000651','000858','002415',
                   '300059','300750','600000','600030','600031','600036','600048','600104','600276','600519',
                   '600585','600588','600690','600887','600900','601012','601066','601088','601166','601288',
                   '601318','601328','601398','601601','601628','601633','601668','601688','601857','601888',
                   '600036','600016','600009','600893','600919','600938','601012','601390','601919','601988']
    print(f"  备用列表:{len(hs300_codes)}只")

# === 第五步：基本面筛选（锋哥条件）===
print("\n📊 第五步：基本面筛选（锋哥五好标准）")
print("="*80)
print("  筛选条件:")
print("    1. PE < 30")
print("    2. ROE 连续 5 年 > 5%")
print("    3. ROIC 连续 5 年 > 5%")
print("    4. 自由现金流连续 5 年为正")
print("    5. 资产负债率 < 50%")

fundamental = {}
filtered = {'pe':0,'roe':0,'roic':0,'fcf':0,'debt':0,'missing':0}

for code in tqdm(hs300_codes, desc="筛选"):
    try:
        # 添加后缀
        ts_code = f"{code}.SH" if code.startswith('6') else f"{code}.SZ"
        
        # 获取 PE
        basic = pro.stock_basic(ts_code=ts_code)
        if basic is None or len(basic)==0:
            filtered['missing'] += 1
            continue
        pe = basic['pe'].iloc[0] if 'pe' in basic.columns else np.nan
        if np.isnan(pe) or pe > 30:
            filtered['pe'] += 1
            continue
        
        # 获取财务指标（最近 5 年）
        fin_data = pro.fina_indicator(ts_code=ts_code, start_date='20210101', end_date=datetime.now().strftime('%Y%m%d'))
        if fin_data is None or len(fin_data) < 10:  # 至少 10 个季度
            filtered['missing'] += 1
            continue
        
        # ROE（净资产收益率）
        roe_col = 'roe' if 'roe' in fin_data.columns else None
        if not roe_col:
            filtered['roe'] += 1
            continue
        roe_vals = fin_data['roe'].head(20).values  # 最近 20 个季度
        roe_min = np.nanmin(roe_vals) if len(roe_vals)>0 else np.nan
        if np.isnan(roe_min) or roe_min <= 5:
            filtered['roe'] += 1
            continue
        
        # ROIC（投入资本回报率）
        roic_col = 'roic' if 'roic' in fin_data.columns else None
        if not roic_col:
            filtered['roic'] += 1
            continue
        roic_vals = fin_data['roic'].head(20).values
        roic_min = np.nanmin(roic_vals) if len(roic_vals)>0 else np.nan
        if np.isnan(roic_min) or roic_min <= 5:
            filtered['roic'] += 1
            continue
        
        # 自由现金流（经营现金流 - 资本支出）
        cash_flow = pro.cashflow(ts_code=ts_code, start_date='20210101', end_date=datetime.now().strftime('%Y%m%d'))
        if cash_flow is None or len(cash_flow) < 5:
            filtered['fcf'] += 1
            continue
        
        # 简化：用经营现金流代替自由现金流
        fcf_col = 'oper_cf' if 'oper_cf' in cash_flow.columns else None
        if fcf_col:
            fcf_vals = cash_flow[fcf_col].head(5).values  # 最近 5 年
            if len(fcf_vals) > 0 and np.nanmin(fcf_vals) <= 0:
                filtered['fcf'] += 1
                continue
        
        # 资产负债率
        debt_col = 'debt_to_assets' if 'debt_to_assets' in fin_data.columns else None
        if debt_col:
            debt = fin_data[debt_col].iloc[0] if len(fin_data)>0 else np.nan
            if np.isnan(debt) or debt > 50:
                filtered['debt'] += 1
                continue
        
        # 通过所有筛选
        fundamental[code] = {
            'pe': pe,
            'roe_avg': np.nanmean(roe_vals),
            'roic_avg': np.nanmean(roic_vals),
            'roe_min': roe_min,
            'roic_min': roic_min
        }
    except Exception as e:
        filtered['missing'] += 1
        continue
    time.sleep(0.2)

print(f"\n  筛选前:{len(hs300_codes)}只 → 筛选后:{len(fundamental)}只")
print(f"  淘汰统计:")
print(f"    PE>30: {filtered['pe']}只")
print(f"    ROE 不达标：{filtered['roe']}只")
print(f"    ROIC 不达标：{filtered['roic']}只")
print(f"    现金流问题：{filtered['fcf']}只")
print(f"    负债率>50%: {filtered['debt']}只")
print(f"    数据缺失：{filtered['missing']}只")

if len(fundamental) == 0:
    print("\n⚠️  筛选后无股票，放宽到 PE<40...")
    for code in hs300_codes:
        try:
            ts_code = f"{code}.SH" if code.startswith('6') else f"{code}.SZ"
            basic = pro.stock_basic(ts_code=ts_code)
            if basic is None or len(basic)==0: continue
            pe = basic['pe'].iloc[0] if 'pe' in basic.columns else np.nan
            if np.isnan(pe) or pe > 40: continue
            fundamental[code] = {'pe':pe,'roe_avg':10}
        except: continue
        time.sleep(0.2)
    print(f"  放宽后:{len(fundamental)}只")

qualified = list(fundamental.keys())
print(f"  ✅ 最终股票池:{len(qualified)}只")

# 打印入选股票
if qualified:
    print(f"\n  🏆 入选股票（符合锋哥五好标准）:")
    for i, code in enumerate(qualified[:20], 1):
        data = fundamental[code]
        print(f"    {i:2d}. {code}  PE:{data['pe']:.1f}  ROE:{data['roe_avg']:.1f}%  ROIC:{data.get('roic_avg',0):.1f}%")
    if len(qualified) > 20:
        print(f"    ... 还有{len(qualified)-20}只")

# === 第六步：回测 ===
print("\n📈 第六步：回测（10 日持有期）")
print("="*80)

results = {'bull':[],'oscillate':[],'bear':[]}
for code in qualified[:10]:
    try:
        ts_code = f"{code}.SH" if code.startswith('6') else f"{code}.SZ"
        stock_data = pro.daily(ts_code=ts_code, start_date='20200101', end_date=datetime.now().strftime('%Y%m%d'))
        if stock_data is None or len(stock_data)<300: continue
        stock_data = stock_data.sort_values('trade_date')
        stock_data['trade_date'] = pd.to_datetime(stock_data['trade_date'])
        stock_data = stock_data.set_index('trade_date')
        
        for i in range(250, len(data)-10):
            state = market_state[i]
            date = data.index[i]
            if date not in stock_data.index: continue
            if i+10 >= len(stock_data): continue
            ret = stock_data['close'].iloc[i+10] / stock_data['close'].iloc[i] - 1
            results[state].append(ret)
    except: continue

print("\n  各市场状态平均收益:")
for state, rets in results.items():
    if rets:
        avg = np.mean(rets) * (365/10)
        emoji = '🐂' if state=='bull' else '🐻' if state=='bear' else '📊'
        print(f"    {emoji} {state}: {avg*100:+.2f}% ({len(rets)}个样本)")

# === 第七步：生成报告 ===
print("\n"+"="*80)
print("📊 V16 策略报告")
print("="*80)

print(f"\n  当前市场：{'🐂牛市' if current_state=='bull' else '🐻熊市' if current_state=='bear' else '📊震荡市'}")
print(f"  股票池：{len(qualified)}只")
print(f"  配置：仓位{current_config['position_limit']*100}% / 持仓{current_config['top_k']}只")

ts_file = datetime.now().strftime('%Y%m%d_%H%M%S')
report = {'ts':ts_file,'market':current_state,'config':current_config,'pool_size':len(qualified),'qualified':qualified}
with open(Path("/home/admin/openclaw/workspace/agents/data-collector/backtest_results")/f"v16_tushare_full_{ts_file}.json",'w') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print(f"\n💾 已保存:v16_tushare_full_{ts_file}.json")