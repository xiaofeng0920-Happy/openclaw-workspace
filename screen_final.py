#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股创业板 (300xxx) 股票筛选
条件：PE<50, ROE 连续 5 年>5%, ROIC 连续 5 年>5%, 自由现金流连续 5 年>0, 资产负债率<50%
"""

import tushare as ts
import pandas as pd
from datetime import datetime
import time

ts.set_token('eb58a2fb952bce3b9590d9290eea7966097450737fa8ad22156f2ca5')
pro = ts.pro_api()

print("="*80)
print("A 股创业板 (300xxx) 股票筛选")
print("条件：PE<50, ROE 连续 5 年>5%, ROIC 连续 5 年>5%, 自由现金流连续 5 年>0, 资产负债率<50%")
print("="*80)

# 1. 获取创业板股票
print("\n1. 获取创业板股票列表...")
stocks = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name')
chi_next = stocks[stocks['symbol'].str.startswith('300')]
print(f"   创业板股票：{len(chi_next)} 只")

# 2. 获取 PE 数据
print("\n2. 获取 PE 数据...")
pe_results = []
total = len(chi_next)

for i, (_, row) in enumerate(chi_next.iterrows()):
    ts_code = row['ts_code']
    try:
        df = pro.daily_basic(ts_code=ts_code, trade_date='20260327')
        if not df.empty:
            pe = df.iloc[0]['pe_ttm']
            pe_results.append({'ts_code': ts_code, 'name': row['name'], 'pe_ttm': pe})
    except:
        pass
    
    if (i + 1) % 100 == 0:
        print(f"   进度：{i+1}/{total}")
    time.sleep(0.05)

# 筛选 PE<50
pe_filtered = [r for r in pe_results if r['pe_ttm'] is not None and 0 < r['pe_ttm'] < 50]
print(f"\n   PE<50 的股票：{len(pe_filtered)}/{len(pe_results)} 只")

if not pe_filtered:
    print("没有 PE<50 的股票")
    exit(0)

# 3. 获取财务数据并筛选
print("\n3. 获取财务数据并筛选...")
passed_stocks = []
total_filter = len(pe_filtered)

for i, stock in enumerate(pe_filtered):
    ts_code = stock['ts_code']
    
    try:
        # 获取财务指标
        fin_data = []
        current_year = datetime.now().year
        
        for year_offset in range(5):
            year = current_year - 1 - year_offset
            df = pro.fina_indicator(ts_code=ts_code, start_date=f'{year}0101', end_date=f'{year}1231')
            
            if not df.empty:
                df['ann_date'] = pd.to_datetime(df['ann_date'])
                annual = df[df['ann_date'].dt.strftime('%m%d') == '1231']
                if annual.empty:
                    annual = df.sort_values('ann_date', ascending=False).iloc[[0]]
                
                row = annual.iloc[0]
                fin_data.append({
                    'year': year,
                    'roe': row.get('roe', None),
                    'roic': row.get('roic', None),
                    'debt_ratio': row.get('debt_to_asset', None),
                    'fcf': row.get('fcf', None)
                })
            time.sleep(0.1)
        
        if len(fin_data) < 5:
            continue
        
        # 检查条件
        roe_pass = all(d['roe'] is not None and d['roe'] > 5 for d in fin_data)
        roic_pass = all(d['roic'] is not None and d['roic'] > 5 for d in fin_data)
        debt_pass = all(d['debt_ratio'] is not None and d['debt_ratio'] < 50 for d in fin_data)
        fcf_pass = all(d['fcf'] is not None and d['fcf'] > 0 for d in fin_data)
        
        if roe_pass and roic_pass and debt_pass and fcf_pass:
            avg_roe = sum(d['roe'] for d in fin_data) / len(fin_data)
            avg_roic = sum(d['roic'] for d in fin_data) / len(fin_data)
            avg_debt = sum(d['debt_ratio'] for d in fin_data) / len(fin_data)
            
            result = {
                'ts_code': ts_code,
                'name': stock['name'],
                'pe_ttm': round(stock['pe_ttm'], 2),
                'roe_5y_avg': round(avg_roe, 2),
                'roic_5y_avg': round(avg_roic, 2),
                'debt_ratio_avg': round(avg_debt, 2)
            }
            passed_stocks.append(result)
            print(f"   ✓ {ts_code} {stock['name']} PE:{result['pe_ttm']} ROE:{result['roe_5y_avg']}% ROIC:{result['roic_5y_avg']}%")
        
        time.sleep(0.2)
    
    except Exception as e:
        pass
    
    if (i + 1) % 20 == 0:
        print(f"   进度：{i+1}/{total_filter}, 已通过：{len(passed_stocks)}")

# 4. 输出结果
print("\n" + "="*80)
print(f"筛选完成！共 {len(passed_stocks)}/{len(pe_filtered)} 只股票符合条件")
print("="*80)

if passed_stocks:
    df = pd.DataFrame(passed_stocks)
    df = df.sort_values('roe_5y_avg', ascending=False)
    
    print("\n符合条件的股票列表：")
    print(df.to_string(index=False))
    
    # 保存
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = f'/home/admin/openclaw/workspace/chi_next_screen_{timestamp}.csv'
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"\n结果已保存到：{csv_file}")
    
    xlsx_file = f'/home/admin/openclaw/workspace/chi_next_screen_{timestamp}.xlsx'
    df.to_excel(xlsx_file, index=False, engine='openpyxl')
    print(f"Excel: {xlsx_file}")
else:
    print("\n没有股票符合所有条件")
