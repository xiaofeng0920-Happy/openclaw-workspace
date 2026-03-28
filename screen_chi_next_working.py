#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股创业板 (300xxx) 股票筛选 - 工作版本
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
import warnings

warnings.filterwarnings('ignore')

# 设置 Tushare Token
ts.set_token('eb58a2fb952bce3b9590d9290eea7966097450737fa8ad22156f2ca5')
pro = ts.pro_api()

# 最新交易日
LATEST_TRADE_DATE = '20260327'

def get_chi_next_stocks():
    """获取所有创业板股票 (300xxx)"""
    print("正在获取创业板股票列表...")
    stocks = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    chi_next_stocks = stocks[stocks['symbol'].str.startswith('300')]
    print(f"创业板股票数量：{len(chi_next_stocks)}")
    return chi_next_stocks

def get_pe_for_all_stocks(ts_codes, trade_date):
    """获取所有股票的 PE 数据"""
    print(f"正在获取 {trade_date} 的 PE 数据...")
    
    pe_dict = {}
    total = len(ts_codes)
    
    for i, ts_code in enumerate(ts_codes):
        try:
            df = pro.daily_basic(ts_code=ts_code, trade_date=trade_date)
            if not df.empty:
                pe_dict[ts_code] = df.iloc[0].get('pe_ttm', None)
            
            if (i + 1) % 100 == 0:
                print(f"  进度：{i+1}/{total} ({(i+1)/total*100:.1f}%)")
            
            time.sleep(0.05)  # 控制频率
            
        except Exception as e:
            time.sleep(1)
    
    return pe_dict

def get_financial_data_for_stock(ts_code, years=5):
    """获取单只股票的多年财务数据"""
    current_year = datetime.now().year
    all_data = []
    
    for year_offset in range(years):
        year = current_year - 1 - year_offset
        start_date = f'{year}0101'
        end_date = f'{year}1231'
        
        try:
            df = pro.fina_indicator(ts_code=ts_code, start_date=start_date, end_date=end_date)
            
            if df.empty:
                continue
            
            # 取年报数据
            df['ann_date'] = pd.to_datetime(df['ann_date'])
            annual_df = df[df['ann_date'].dt.strftime('%m%d') == '1231']
            
            if annual_df.empty:
                annual_df = df.sort_values('ann_date', ascending=False).iloc[[0]]
            
            for _, row in annual_df.iterrows():
                all_data.append({
                    'year': year,
                    'roe': row.get('roe', None),
                    'roic': row.get('roic', None),
                    'debt_to_asset': row.get('debt_to_asset', None),
                    'fcf': row.get('fcf', None)
                })
            
            time.sleep(0.1)
            
        except Exception as e:
            time.sleep(1)
    
    return all_data

def screen_stock(ts_code, name, pe, fin_data):
    """筛选单只股票"""
    # 检查 PE
    if pe is None or pe <= 0 or pe >= 50:
        return None
    
    # 检查是否有 5 年数据
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
            'fcf_latest': round(latest_fcf / 100000000, 2)
        }
    
    return None

def main():
    print("=" * 80)
    print("A 股创业板 (300xxx) 股票筛选")
    print("条件：PE<50, ROE 连续 5 年>5%, ROIC 连续 5 年>5%, 自由现金流连续 5 年>0, 资产负债率<50%")
    print("=" * 80)
    
    # 获取创业板股票列表
    chi_next_stocks = get_chi_next_stocks()
    ts_codes = chi_next_stocks['ts_code'].tolist()
    stock_names = chi_next_stocks.set_index('ts_code')['name'].to_dict()
    
    print(f"最新交易日：{LATEST_TRADE_DATE}")
    
    # 获取 PE 数据
    pe_dict = get_pe_for_all_stocks(ts_codes, LATEST_TRADE_DATE)
    valid_pe_count = len([v for v in pe_dict.values() if v is not None and v > 0])
    print(f"获取到 {valid_pe_count} 只股票的有效 PE 数据")
    
    # 先筛选 PE<50 的股票
    filtered_codes = [code for code in ts_codes if pe_dict.get(code) is not None and 0 < pe_dict[code] < 50]
    print(f"PE<50 的股票数量：{len(filtered_codes)}")
    
    if not filtered_codes:
        print("没有 PE<50 的股票")
        return
    
    # 筛选股票
    print(f"\n开始筛选 {len(filtered_codes)} 只股票...")
    passed_stocks = []
    total = len(filtered_codes)
    
    for i, ts_code in enumerate(filtered_codes):
        if i % 20 == 0:
            print(f"进度：{i}/{total} ({i/total*100:.1f}%), 已通过：{len(passed_stocks)}")
        
        name = stock_names.get(ts_code, '')
        pe = pe_dict[ts_code]
        fin_data = get_financial_data_for_stock(ts_code, years=5)
        
        result = screen_stock(ts_code, name, pe, fin_data)
        if result:
            passed_stocks.append(result)
            print(f"  ✓ {ts_code} {name} PE:{result['pe_ttm']} ROE:{result['roe_5y_avg']}% ROIC:{result['roic_5y_avg']}%")
        
        time.sleep(0.3)  # 控制频率
    
    # 输出结果
    print("\n" + "=" * 80)
    print(f"筛选完成！共 {len(passed_stocks)}/{len(filtered_codes)} 只股票符合条件")
    print("=" * 80)
    
    if passed_stocks:
        df = pd.DataFrame(passed_stocks)
        df = df.sort_values('roe_5y_avg', ascending=False)
        
        print("\n符合条件的股票列表：")
        print(df.to_string(index=False))
        
        # 保存结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"/home/admin/openclaw/workspace/chi_next_screen_{timestamp}.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n结果已保存到：{output_file}")
        
        xlsx_file = f"/home/admin/openclaw/workspace/chi_next_screen_{timestamp}.xlsx"
        df.to_excel(xlsx_file, index=False, engine='openpyxl')
        print(f"Excel 版本：{xlsx_file}")
    else:
        print("\n没有股票符合所有条件")

if __name__ == "__main__":
    main()
