#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股创业板 (300xxx) 股票筛选
条件：
- PE < 50
- ROE 连续 5 年 > 5%
- ROIC 连续 5 年 > 5%
- 自由现金流连续 5 年为正
- 资产负债率 < 50%
"""

import tushare as ts
import pandas as pd
from datetime import datetime
import time

# 设置 Tushare Token
ts.set_token('eb58a2fb952bce3b9590d9290eea7966097450737fa8ad22156f2ca5')
pro = ts.pro_api()

def get_chi_next_stocks():
    """获取所有创业板股票 (300xxx)"""
    print("正在获取创业板股票列表...")
    stocks = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    chi_next_stocks = stocks[stocks['symbol'].str.startswith('300')]
    print(f"创业板股票数量：{len(chi_next_stocks)}")
    return chi_next_stocks

def get_annual_financial_data(ts_code, years=5):
    """获取连续多年的年度财务数据"""
    current_year = datetime.now().year
    
    all_data = []
    for year_offset in range(years):
        year = current_year - 1 - year_offset
        
        try:
            # 获取财务指标
            df = pro.fina_indicator(ts_code=ts_code, start_date=f'{year}0101', end_date=f'{year}1231')
            if df.empty:
                continue
            
            # 取年报数据（报告期包含 12-31）
            df['ann_date'] = pd.to_datetime(df['ann_date'])
            annual_df = df[df['ann_date'].dt.strftime('%m%d') == '1231']
            
            if annual_df.empty:
                # 如果没有年报，取最新一期
                annual_df = df.sort_values('ann_date', ascending=False).iloc[[0]]
            
            for _, row in annual_df.iterrows():
                all_data.append({
                    'year': year,
                    'roe': row.get('roe', None),
                    'roic': row.get('roic', None),
                    'debt_to_asset': row.get('debt_to_asset', None),
                    'fcf': row.get('fcf', None)
                })
        except Exception as e:
            print(f"  获取 {ts_code} {year} 年数据失败：{e}")
            continue
        
        time.sleep(0.1)  # 避免请求过快
    
    return all_data

def get_current_pe(ts_code):
    """获取当前 PE(TTM)"""
    try:
        today = datetime.now().strftime('%Y%m%d')
        df = pro.daily_basic(ts_code=ts_code, trade_date=today)
        
        if df.empty:
            # 获取最近的数据
            df = pro.daily_basic(ts_code=ts_code)
            if df.empty:
                return None
            df = df.sort_values('trade_date', ascending=False).iloc[[0]]
        
        pe_ttm = df.iloc[0].get('pe_ttm', None)
        return pe_ttm
    except Exception as e:
        print(f"  获取 {ts_code} PE 失败：{e}")
        return None

def screen_stock(row):
    """筛选单只股票"""
    ts_code = row['ts_code']
    name = row['name']
    
    # 获取当前 PE
    pe = get_current_pe(ts_code)
    if pe is None or pe <= 0 or pe >= 50:
        return None
    
    # 获取连续 5 年财务数据
    fin_data = get_annual_financial_data(ts_code, years=5)
    
    if len(fin_data) < 5:
        return None
    
    # 检查所有年份是否都满足条件
    roe_pass = all(d['roe'] is not None and d['roe'] > 5 for d in fin_data)
    roic_pass = all(d['roic'] is not None and d['roic'] > 5 for d in fin_data)
    debt_pass = all(d['debt_to_asset'] is not None and d['debt_to_asset'] < 50 for d in fin_data)
    fcf_pass = all(d['fcf'] is not None and d['fcf'] > 0 for d in fin_data)
    
    if roe_pass and roic_pass and debt_pass and fcf_pass:
        # 计算平均值
        avg_roe = sum(d['roe'] for d in fin_data) / len(fin_data)
        avg_roic = sum(d['roic'] for d in fin_data) / len(fin_data)
        avg_debt = sum(d['debt_to_asset'] for d in fin_data) / len(fin_data)
        latest_fcf = fin_data[0]['fcf']
        
        return {
            'ts_code': ts_code,
            'name': name,
            'pe_ttm': round(pe, 2),
            'roe_5y_avg': round(avg_roe, 2),
            'roic_5y_avg': round(avg_roic, 2),
            'debt_ratio_avg': round(avg_debt, 2),
            'fcf_latest': round(latest_fcf / 100000000, 2)  # 转换为亿元
        }
    
    return None

def main():
    print("=" * 80)
    print("A 股创业板 (300xxx) 股票筛选")
    print("条件：PE<50, ROE 连续 5 年>5%, ROIC 连续 5 年>5%, 自由现金流连续 5 年>0, 资产负债率<50%")
    print("=" * 80)
    
    # 获取创业板股票列表
    chi_next_stocks = get_chi_next_stocks()
    
    # 筛选股票
    passed_stocks = []
    total = len(chi_next_stocks)
    
    print(f"\n开始筛选 {total} 只股票...\n")
    
    for i, (_, row) in enumerate(chi_next_stocks.iterrows()):
        if i % 50 == 0 and i > 0:
            print(f"进度：{i}/{total} ({i/total*100:.1f}%), 已通过：{len(passed_stocks)}")
        
        result = screen_stock(row)
        if result:
            passed_stocks.append(result)
            print(f"  ✓ {result['ts_code']} {result['name']} PE:{result['pe_ttm']} ROE:{result['roe_5y_avg']}%")
        
        time.sleep(0.2)  # 控制请求频率
    
    # 输出结果
    print("\n" + "=" * 80)
    print(f"筛选完成！共 {len(passed_stocks)}/{total} 只股票符合条件")
    print("=" * 80)
    
    if passed_stocks:
        df = pd.DataFrame(passed_stocks)
        print("\n符合条件的股票列表：")
        print(df.to_string(index=False))
        
        # 保存结果
        output_file = f"/home/admin/openclaw/workspace/chi_next_screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n结果已保存到：{output_file}")
        
        # 也保存为 Excel
        xlsx_file = f"/home/admin/openclaw/workspace/chi_next_screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(xlsx_file, index=False, engine='openpyxl')
        print(f"Excel 版本：{xlsx_file}")
    else:
        print("\n没有股票符合所有条件")

if __name__ == "__main__":
    main()
