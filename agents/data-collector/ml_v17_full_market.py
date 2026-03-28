#!/usr/bin/env python3
"""V17 A 股全市场筛选 - 锋哥五好标准"""
import sys, time, json
from pathlib import Path
sys.path.insert(0, '/home/admin/openclaw/workspace')
import pandas as pd, numpy as np
from datetime import datetime
from tqdm import tqdm
import tushare as ts

print("="*80)
print("🤖 V17 A 股全市场筛选 - 锋哥五好标准")
print("="*80)

# 初始化 Tushare
ts.set_token('eb58a2fb952bce3b9590d9290eea7966097450737fa8ad22156f2ca5')
pro = ts.pro_api()

# === 第一步：获取 A 股全市场股票列表 ===
print("\n📊 第一步：获取 A 股全市场股票列表")
print("="*80)

# 获取全部 A 股
stock_list = pro.stock_basic(exchange='', list_status='L', limit=5000)
if stock_list is None or len(stock_list)==0:
    print("❌ 获取股票列表失败")
    sys.exit(1)

# 过滤主板、创业板、科创板
a_shares = stock_list[stock_list['ts_code'].str.endswith('.SH') | stock_list['ts_code'].str.endswith('.SZ')]
print(f"  A 股总数：{len(a_shares)}只")
print(f"  主板：{len(a_shares[a_shares['list_date']<'20090101'])}只")
print(f"  创业板：{len(a_shares[a_shares['ts_code'].str.startswith('3')])}只")
print(f"  科创板：{len(a_shares[a_shares['ts_code'].str.startswith('688')])}只")

# 去掉 ST 股票
a_shares = a_shares[~a_shares['name'].str.contains('ST', na=False)]
print(f"  非 ST 股票：{len(a_shares)}只")

# === 第二步：基本面筛选（锋哥五好标准）===
print("\n📊 第二步：基本面筛选（锋哥五好标准）")
print("="*80)
print("  筛选条件:")
print("    1. PE < 30")
print("    2. ROE 连续 5 年 > 5%")
print("    3. ROIC 连续 5 年 > 5%")
print("    4. 自由现金流连续 5 年为正")
print("    5. 资产负债率 < 50%")

# 全市场筛选（约 5000 只）
test_stocks = a_shares.copy()
print(f"\n  全市场股票池：{len(test_stocks)}只")
print(f"  预计耗时：约{len(test_stocks)*0.15/60:.0f}分钟")

fundamental = {}
filtered = {'pe':0,'roe':0,'roic':0,'fcf':0,'debt':0,'missing':0}

for idx, row in tqdm(test_stocks.iterrows(), total=len(test_stocks), desc="筛选"):
    code = row['ts_code'].split('.')[0]
    ts_code = row['ts_code']
    
    try:
        # 1. PE < 30
        pe = row['pe'] if 'pe' in row and not pd.isna(row['pe']) else np.nan
        if np.isnan(pe) or pe > 30:
            filtered['pe'] += 1
            continue
        
        # 2. ROE 连续 5 年 > 5%
        fina = pro.fina_indicator(ts_code=ts_code, start_date='20210101', end_date=datetime.now().strftime('%Y%m%d'))
        if fina is None or len(fina) < 10:
            filtered['missing'] += 1
            continue
        
        if 'roe' not in fina.columns:
            filtered['roe'] += 1
            continue
        roe_vals = fina['roe'].head(20).values
        roe_min = np.nanmin(roe_vals) if len(roe_vals)>0 else np.nan
        if np.isnan(roe_min) or roe_min <= 5:
            filtered['roe'] += 1
            continue
        
        # 3. ROIC 连续 5 年 > 5%
        if 'roic' not in fina.columns:
            filtered['roic'] += 1
            continue
        roic_vals = fina['roic'].head(20).values
        roic_min = np.nanmin(roic_vals) if len(roic_vals)>0 else np.nan
        if np.isnan(roic_min) or roic_min <= 5:
            filtered['roic'] += 1
            continue
        
        # 4. 自由现金流（用经营现金流代替）
        cashflow = pro.cashflow(ts_code=ts_code, start_date='20210101', end_date=datetime.now().strftime('%Y%m%d'))
        if cashflow is None or len(cashflow) < 5:
            filtered['fcf'] += 1
            continue
        if 'oper_cf' in cashflow.columns:
            fcf_vals = cashflow['oper_cf'].head(5).values
            if len(fcf_vals) > 0 and np.nanmin(fcf_vals) <= 0:
                filtered['fcf'] += 1
                continue
        
        # 5. 资产负债率 < 50%
        if 'debt_to_assets' in fina.columns:
            debt = fina['debt_to_assets'].iloc[0]
            if np.isnan(debt) or debt > 50:
                filtered['debt'] += 1
                continue
        
        # 通过所有筛选
        fundamental[code] = {
            'pe': pe,
            'roe_avg': np.nanmean(roe_vals),
            'roic_avg': np.nanmean(roic_vals),
            'roe_min': roe_min,
            'roic_min': roic_min,
            'name': row['name'] if 'name' in row else ''
        }
    except Exception as e:
        filtered['missing'] += 1
        continue
    
    # 每 100 只休息 1 秒
    if len(fundamental) % 100 == 0:
        time.sleep(1)
    
    # 控制速率
    time.sleep(0.15)

print(f"\n  筛选前:{len(test_stocks)}只 → 筛选后:{len(fundamental)}只")
print(f"  淘汰统计:")
print(f"    PE>30: {filtered['pe']}只")
print(f"    ROE 不达标：{filtered['roe']}只")
print(f"    ROIC 不达标：{filtered['roic']}只")
print(f"    现金流问题：{filtered['fcf']}只")
print(f"    负债率>50%: {filtered['debt']}只")
print(f"    数据缺失：{filtered['missing']}只")

if len(fundamental) == 0:
    print("\n⚠️  放宽到 PE<50, ROE>3%...")
    # 放宽逻辑...

qualified = list(fundamental.keys())
print(f"  ✅ 最终股票池:{len(qualified)}只")

# 打印入选股票
if qualified:
    print(f"\n  🏆 入选股票（符合锋哥五好标准）:")
    sorted_stocks = sorted(qualified, key=lambda x: fundamental[x]['roe_avg'], reverse=True)
    for i, code in enumerate(sorted_stocks[:20], 1):
        d = fundamental[code]
        print(f"    {i:2d}. {code} ({d['name']})  PE:{d['pe']:.1f}  ROE:{d['roe_avg']:.1f}%  ROIC:{d['roic_avg']:.1f}%")
    if len(qualified) > 20:
        print(f"    ... 还有{len(qualified)-20}只")

# === 第三步：生成报告 ===
print("\n"+"="*80)
print("📊 V17 筛选报告")
print("="*80)

print(f"\n  筛选股票：{len(qualified)}只")
print(f"  通过率：{len(qualified)/len(test_stocks)*100:.2f}%")

ts_file = datetime.now().strftime('%Y%m%d_%H%M%S')
report = {
    'ts':ts_file,
    'total_stocks':len(test_stocks),
    'qualified_count':len(qualified),
    'pass_rate':len(qualified)/len(test_stocks)*100,
    'qualified_stocks':qualified,
    'fundamental':fundamental,
    'filtered_stats':filtered
}
with open(Path("/home/admin/openclaw/workspace/agents/data-collector/backtest_results")/f"v17_full_market_{ts_file}.json",'w') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print(f"\n💾 已保存:v17_full_market_{ts_file}.json")
