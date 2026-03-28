#!/usr/bin/env python3
"""V16 市场状态识别与动态配置策略 - Tushare 版"""
import sys, time, json
from pathlib import Path
sys.path.insert(0, '/home/admin/openclaw/workspace')
import pandas as pd, numpy as np
from datetime import datetime
from tqdm import tqdm
import tushare as ts

print("="*80)
print("🤖 V16 市场状态识别与动态配置策略 - Tushare 版")
print("="*80)

# 初始化 Tushare
ts.set_token('eb58a2fb952bce3b9590d9290eea7966097450737fa8ad22156f2ca5')
pro = ts.pro_api()

# === 第一步：获取沪深 300 数据 ===
print("\n📈 第一步：获取沪深 300 数据")
print("="*80)

# 获取沪深 300 指数日线数据
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

# 简化：用收盘价/MA250 和 RSI 判断
market_state = []
for i in range(len(data)):
    if i < 250:
        market_state.append('oscillate')
        continue
    
    c = close.iloc[i]
    m250 = ma250.iloc[i]
    slope = ma250_slope.iloc[i]
    r = rsi.iloc[i]
    
    # 牛市：收盘>MA250 且 MA250 向上 且 RSI>50
    if (c > m250) and (slope > 0) and (r > 50):
        market_state.append('bull')
    # 熊市：收盘<MA250 且 MA250 向下 且 RSI<40
    elif (c < m250) and (slope < 0) and (r < 40):
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

# === 第三步：动态配置参数 ===
print("\n⚙️ 第三步：动态配置参数")
print("="*80)

CONFIG = {
    'bull': {
        'position_limit': 0.95,
        'top_k': 10,
        'pe_max': 35,
        'roe_min': 12,
        'weights': {'capital': 0.40, 'value': 0.20, 'quality': 0.20, 'sentiment': 0.20}
    },
    'oscillate': {
        'position_limit': 0.65,
        'top_k': 5,
        'pe_max': 30,
        'roe_min': 15,
        'weights': {'capital': 0.30, 'value': 0.30, 'quality': 0.30, 'sentiment': 0.10}
    },
    'bear': {
        'position_limit': 0.30,
        'top_k': 3,
        'pe_max': 25,
        'roe_min': 18,
        'weights': {'capital': 0.10, 'value': 0.40, 'quality': 0.40, 'sentiment': 0.10}
    }
}

current_config = CONFIG[current_state]
print(f"\n  当前配置（{'🐂牛市' if current_state=='bull' else '🐻熊市' if current_state=='bear' else '📊震荡市'}）:")
print(f"    仓位上限：{current_config['position_limit']*100}%")
print(f"    持仓数量：{current_config['top_k']}只")
print(f"    PE 上限：{current_config['pe_max']}")
print(f"    ROE 下限：{current_config['roe_min']}%")

# === 第四步：获取沪深 300 成分股 ===
print("\n📊 第四步：获取沪深 300 成分股")
print("="*80)

weights_data = pro.index_weight(ts_code='000300.SH', start_date=datetime.now().strftime('%Y%m%d'), end_date=datetime.now().strftime('%Y%m%d'))
if weights_data is not None and len(weights_data)>0:
    hs300_codes = weights_data['con_code'].tolist()
    print(f"  获取到{len(hs300_codes)}只成分股")
else:
    # 备用列表
    hs300_codes = ['000001.SZ','000002.SZ','000063.SZ','000100.SZ','000333.SZ','000538.SZ','000568.SZ','000651.SZ','000858.SZ','002415.SZ',
                   '300059.SZ','300750.SZ','600000.SH','600030.SH','600031.SH','600036.SH','600048.SH','600104.SH','600276.SH','600519.SH',
                   '600585.SH','600588.SH','600690.SH','600887.SH','600900.SH','601012.SH','601066.SH','601088.SH','601166.SH','601288.SH',
                   '601318.SH','601328.SH','601398.SH','601601.SH','601628.SH','601633.SH','601668.SH','601688.SH','601857.SH','601888.SH']
    print(f"  使用备用列表:{len(hs300_codes)}只")

# === 第五步：基本面筛选 ===
print("\n📊 第五步：基本面筛选")
print("="*80)
print(f"  条件：PE<{current_config['pe_max']}, ROE>{current_config['roe_min']}%")

fundamental = {}
for code in tqdm(hs300_codes[:50], desc="筛选"):  # 先测试 50 只
    try:
        # 获取财务指标
        fin_data = pro.fina_indicator(ts_code=code, start_date='20230101', end_date=datetime.now().strftime('%Y%m%d'))
        if fin_data is None or len(fin_data)==0: continue
        
        latest = fin_data.iloc[0]
        roe = latest.get('roe', np.nan)
        
        # 获取 PE
        basic_data = pro.stock_basic(ts_code=code)
        if basic_data is None or len(basic_data)==0: continue
        pe = basic_data['pe'].iloc[0] if 'pe' in basic_data.columns else np.nan
        
        if np.isnan(pe) or pe > current_config['pe_max']: continue
        if np.isnan(roe) or roe < current_config['roe_min']: continue
        
        fundamental[code] = {'pe':pe,'roe':roe}
    except: continue
    time.sleep(0.2)

if len(fundamental) < 5:
    print(f"\n⚠️  筛选后仅{len(fundamental)}只，放宽条件...")
    for code in hs300_codes[:50]:
        try:
            fin_data = pro.fina_indicator(ts_code=code, start_date='20230101', end_date=datetime.now().strftime('%Y%m%d'))
            if fin_data is None or len(fin_data)==0: continue
            roe = fin_data['roe'].iloc[0] if 'roe' in fin_data.columns else 10
            fundamental[code] = {'pe':20,'roe':roe}
        except: continue
        time.sleep(0.2)

qualified = list(fundamental.keys())
print(f"  ✅ 筛选后:{len(qualified)}只")

# === 第六步：回测 ===
print("\n📈 第六步：回测（动态配置）")
print("="*80)

def backtest_dynamic():
    """简化回测：按市场状态计算收益"""
    results = {'bull':[],'oscillate':[],'bear':[]}
    
    # 获取成分股日线数据
    for code in qualified[:10]:  # 测试前 10 只
        try:
            stock_data = pro.daily(ts_code=code, start_date='20230101', end_date=datetime.now().strftime('%Y%m%d'))
            if stock_data is None or len(stock_data)<100: continue
            
            stock_data = stock_data.sort_values('trade_date')
            stock_data['trade_date'] = pd.to_datetime(stock_data['trade_date'])
            stock_data = stock_data.set_index('trade_date')
            
            # 对齐日期计算收益
            for i in range(250, len(data)-10):
                state = market_state[i]
                if state == 'oscillate': continue
                
                date = data.index[i]
                if date not in stock_data.index: continue
                
                # 计算 10 日后收益
                if i+10 >= len(stock_data): continue
                ret = stock_data['close'].iloc[i+10] / stock_data['close'].iloc[i] - 1
                results[state].append(ret)
        except: continue
    
    return results

results = backtest_dynamic()
print("\n  各市场状态平均收益（10 日持有期）:")
for state, rets in results.items():
    if rets:
        avg = np.mean(rets) * (365/10)  # 年化
        emoji = '🐂' if state=='bull' else '🐻' if state=='bear' else '📊'
        print(f"    {emoji} {state}: {avg*100:+.2f}% ({len(rets)}个样本)")

# === 第七步：生成报告 ===
print("\n"+"="*80)
print("📊 V16 策略报告")
print("="*80)

report = {
    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'market_state': current_state,
    'current_config': current_config,
    'pool_size': len(qualified),
    'state_distribution': state_counts.to_dict()
}

print(f"\n  报告时间：{report['timestamp']}")
print(f"  当前市场：{'🐂牛市' if current_state=='bull' else '🐻熊市' if current_state=='bear' else '📊震荡市'}")
print(f"  股票池：{len(qualified)}只")
print(f"  配置：仓位{current_config['position_limit']*100}% / 持仓{current_config['top_k']}只 / PE<{current_config['pe_max']} / ROE>{current_config['roe_min']}%")

# 保存
ts_file = datetime.now().strftime('%Y%m%d_%H%M%S')
with open(Path("/home/admin/openclaw/workspace/agents/data-collector/backtest_results")/f"v16_tushare_{ts_file}.json",'w') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print(f"\n💾 已保存:v16_tushare_{ts_file}.json")
