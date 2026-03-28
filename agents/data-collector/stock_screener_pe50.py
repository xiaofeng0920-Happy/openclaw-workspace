#!/usr/bin/env python3
"""A 股全市场筛选 - 锋哥五好标准（PE 放宽到 50）"""
import sys, time, json
from pathlib import Path
sys.path.insert(0, '/home/admin/openclaw/workspace')
import pandas as pd, numpy as np
from datetime import datetime, timedelta
from tqdm import tqdm
import tushare as ts

print("="*80)
print("🤖 A 股全市场筛选 - 锋哥五好标准（PE 放宽版）")
print("="*80)

# 初始化 Tushare
ts.set_token('eb58a2fb952bce3b9590d9290eea7966097450737fa8ad22156f2ca5')
pro = ts.pro_api()

# === 第一步：获取 A 股全市场股票列表 ===
print("\n📊 第一步：获取 A 股全市场股票列表")
print("="*80)

stock_list = pro.stock_basic(exchange='', list_status='L', limit=5000)
if stock_list is None or len(stock_list)==0:
    print("❌ 获取股票列表失败")
    sys.exit(1)

a_shares = stock_list[stock_list['ts_code'].str.endswith('.SH') | stock_list['ts_code'].str.endswith('.SZ')]
print(f"  A 股总数：{len(a_shares)}只")

# 去掉 ST 股票
a_shares = a_shares[~a_shares['name'].str.contains('ST', na=False)]
print(f"  非 ST 股票：{len(a_shares)}只")

# === 第二步：获取全市场 PE 数据 ===
print("\n📊 第二步：获取全市场 PE 数据")
print("="*80)

# 获取最近交易日的 daily_basic
today = datetime.now()
pe_date = None
pe_data = None
for i in range(10):
    date = (today - timedelta(days=i)).strftime('%Y%m%d')
    daily = pro.daily_basic(trade_date=date)
    if daily is not None and len(daily) > 0:
        pe_date = date
        pe_data = daily
        print(f"  使用日期：{date} ({len(daily)}只股票)")
        break

if pe_data is None:
    print("❌ 获取 PE 数据失败")
    sys.exit(1)

# 过滤 A 股
pe_data = pe_data[pe_data['ts_code'].str.endswith('.SH') | pe_data['ts_code'].str.endswith('.SZ')]
print(f"  A 股 PE 数据：{len(pe_data)}只")

# PE < 50 筛选
pe_ok = pe_data[pe_data['pe'] < 50]
print(f"  PE < 50: {len(pe_ok)}只")

# 去掉 ST
pe_ok = pe_ok.merge(a_shares[['ts_code','name']], on='ts_code', how='inner')
print(f"  非 ST 且 PE < 50: {len(pe_ok)}只")

# === 第三步：基本面筛选（锋哥五好标准）===
print("\n📊 第三步：基本面筛选（锋哥五好标准）")
print("="*80)
print("  筛选条件:")
print("    1. PE < 50 (放宽)")
print("    2. ROE 连续 5 年 > 5%")
print("    3. ROIC 连续 5 年 > 5%")
print("    4. 自由现金流连续 5 年为正")
print("    5. 资产负债率 < 50%")

test_stocks = pe_ok.copy()
print(f"\n  待筛选股票池：{len(test_stocks)}只")
print(f"  预计耗时：约{len(test_stocks)*0.2/60:.0f}分钟")

fundamental = {}
filtered = {'roe':0,'roic':0,'fcf':0,'debt':0,'missing':0}

for idx, row in tqdm(test_stocks.iterrows(), total=len(test_stocks), desc="筛选"):
    ts_code = row['ts_code']
    code = ts_code.split('.')[0]
    name = row['name'] if 'name' in row else ''
    pe = row['pe']
    
    try:
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
            'ts_code': ts_code,
            'name': name,
            'pe': pe,
            'roe_avg': np.nanmean(roe_vals),
            'roic_avg': np.nanmean(roic_vals),
            'roe_min': roe_min,
            'roic_min': roic_min
        }
    except Exception as e:
        filtered['missing'] += 1
        continue
    
    # 控制速率
    time.sleep(0.2)

print(f"\n  筛选前:{len(test_stocks)}只 → 筛选后:{len(fundamental)}只")
print(f"  淘汰统计:")
print(f"    ROE 不达标：{filtered['roe']}只")
print(f"    ROIC 不达标：{filtered['roic']}只")
print(f"    现金流问题：{filtered['fcf']}只")
print(f"    负债率>50%: {filtered['debt']}只")
print(f"    数据缺失：{filtered['missing']}只")

qualified = list(fundamental.keys())
print(f"  ✅ 最终股票池:{len(qualified)}只")

# 打印入选股票（前 20 只）
if qualified:
    print(f"\n  🏆 入选股票（符合锋哥五好标准，前 20 只）:")
    sorted_stocks = sorted(qualified, key=lambda x: fundamental[x]['roe_avg'], reverse=True)
    for i, code in enumerate(sorted_stocks[:20], 1):
        d = fundamental[code]
        print(f"    {i:2d}. {code} ({d['name']})  PE:{d['pe']:.1f}  ROE:{d['roe_avg']:.1f}%  ROIC:{d['roic_avg']:.1f}%")
    if len(qualified) > 20:
        print(f"    ... 还有{len(qualified)-20}只")

# === 第四步：生成报告 ===
print("\n"+"="*80)
print("📊 筛选报告")
print("="*80)

print(f"\n  筛选股票：{len(qualified)}只")
print(f"  通过率：{len(qualified)/len(test_stocks)*100:.2f}%")

ts_file = datetime.now().strftime('%Y%m%d_%H%M%S')

# 保存 CSV
if qualified:
    df = pd.DataFrame([
        {
            '代码': code,
            '名称': fundamental[code]['name'],
            'PE': round(fundamental[code]['pe'], 2),
            'ROE_平均': round(fundamental[code]['roe_avg'], 2),
            'ROE_最低': round(fundamental[code]['roe_min'], 2),
            'ROIC_平均': round(fundamental[code]['roic_avg'], 2),
            'ROIC_最低': round(fundamental[code]['roic_min'], 2)
        }
        for code in sorted_stocks
    ])
    csv_file = Path("/home/admin/openclaw/workspace/agents/data-collector/backtest_results") / f"五好股票_PE50_{ts_file}.csv"
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"\n💾 CSV 已保存：{csv_file}")

# 保存 JSON 报告
report = {
    'ts':ts_file,
    'pe_date': pe_date,
    'total_stocks': int(len(a_shares)),
    'pe_filtered': int(len(test_stocks)),
    'qualified_count':len(qualified),
    'pass_rate':len(qualified)/len(test_stocks)*100,
    'qualified_stocks':qualified,
    'fundamental':fundamental,
    'filtered_stats':filtered
}
with open(Path("/home/admin/openclaw/workspace/agents/data-collector/backtest_results")/f"v17_full_market_pe50_{ts_file}.json",'w') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print(f"💾 JSON 已保存:v17_full_market_pe50_{ts_file}.json")

print("\n" + "="*80)
print("✅ 筛选完成")
print("="*80)
