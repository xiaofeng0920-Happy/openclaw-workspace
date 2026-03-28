#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股创业板 (300xxx) 股票筛选 - 优化版
条件：
- PE < 50
- ROE 连续 5 年 > 5%
- ROIC 连续 5 年 > 5%
- 自由现金流连续 5 年为正
- 资产负债率 < 50%

优化策略：批量获取数据，减少 API 调用次数
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

def get_chi_next_stocks():
    """获取所有创业板股票 (300xxx)"""
    print("正在获取创业板股票列表...")
    stocks = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    chi_next_stocks = stocks[stocks['symbol'].str.startswith('300')]
    print(f"创业板股票数量：{len(chi_next_stocks)}")
    return chi_next_stocks

def get_all_financial_data_batch(ts_codes, years=5):
    """批量获取多年财务数据"""
    current_year = datetime.now().year
    
    all_data = {}
    
    for year_offset in range(years):
        year = current_year - 1 - year_offset
        start_date = f'{year}0101'
        end_date = f'{year}1231'
        
        try:
            print(f"  获取 {year} 年财务数据...")
            # 批量获取所有股票的财务指标
            df = pro.fina_indicator(ts_code=','.join(ts_codes), start_date=start_date, end_date=end_date)
            
            if not df.empty:
                # 取年报数据
                df['ann_date'] = pd.to_datetime(df['ann_date'])
                annual_df = df[df['ann_date'].dt.strftime('%m%d') == '1231']
                
                if annual_df.empty:
                    # 如果没有年报，取最新一期
                    annual_df = df.sort_values('ann_date', ascending=False).drop_duplicates('ts_code', keep='first')
                
                for _, row in annual_df.iterrows():
                    ts_code = row['ts_code']
                    if ts_code not in all_data:
                        all_data[ts_code] = []
                    
                    all_data[ts_code].append({
                        'year': year,
                        'roe': row.get('roe', None),
                        'roic': row.get('roic', None),
                        'debt_to_asset': row.get('debt_to_asset', None),
                        'fcf': row.get('fcf', None)
                    })
            
            time.sleep(0.5)  # 控制频率
            
        except Exception as e:
            print(f"  获取 {year} 年数据失败：{e}")
            time.sleep(2)
    
    return all_data

def get_all_pe_batch(ts_codes):
    """批量获取当前 PE"""
    try:
        today = datetime.now().strftime('%Y%m%d')
        df = pro.daily_basic(ts_code=','.join(ts_codes), trade_date=today)
        
        if df.empty:
            # 获取最近的数据
            df = pro.daily_basic(ts_code=','.join(ts_codes))
            if df.empty:
                return {}
            df = df.sort_values('trade_date', ascending=False).drop_duplicates('ts_code', keep='first')
        
        pe_dict = {}
        for _, row in df.iterrows():
            pe_dict[row['ts_code']] = row.get('pe_ttm', None)
        
        return pe_dict
    except Exception as e:
        print(f"获取 PE 数据失败：{e}")
        return {}

def screen_stock(ts_code, fin_data, pe_dict):
    """筛选单只股票"""
    # 检查 PE
    pe = pe_dict.get(ts_code)
    if pe is None or pe <= 0 or pe >= 50:
        return None
    
    # 检查是否有 5 年数据
    if ts_code not in fin_data or len(fin_data[ts_code]) < 5:
        return None
    
    stock_data = fin_data[ts_code]
    
    # 检查所有年份是否都满足条件
    roe_pass = all(d['roe'] is not None and d['roe'] > 5 for d in stock_data)
    roic_pass = all(d['roic'] is not None and d['roic'] > 5 for d in stock_data)
    debt_pass = all(d['debt_to_asset'] is not None and d['debt_to_asset'] < 50 for d in stock_data)
    fcf_pass = all(d['fcf'] is not None and d['fcf'] > 0 for d in stock_data)
    
    if roe_pass and roic_pass and debt_pass and fcf_pass:
        # 计算平均值
        avg_roe = sum(d['roe'] for d in stock_data) / len(stock_data)
        avg_roic = sum(d['roic'] for d in stock_data) / len(stock_data)
        avg_debt = sum(d['debt_to_asset'] for d in stock_data) / len(stock_data)
        latest_fcf = stock_data[0]['fcf']
        
        return {
            'ts_code': ts_code,
            'pe_ttm': round(pe, 2),
            'roe_5y_avg': round(avg_roe, 2),
            'roic_5y_avg': round(avg_roic, 2),
            'debt_ratio_avg': round(avg_debt, 2),
            'fcf_latest': round(latest_fcf / 100000000, 2)  # 转换为亿元
        }
    
    return None

def main():
    print("=" * 80)
    print("A 股创业板 (300xxx) 股票筛选 - 批量优化版")
    print("条件：PE<50, ROE 连续 5 年>5%, ROIC 连续 5 年>5%, 自由现金流连续 5 年>0, 资产负债率<50%")
    print("=" * 80)
    
    # 获取创业板股票列表
    chi_next_stocks = get_chi_next_stocks()
    ts_codes = chi_next_stocks['ts_code'].tolist()
    
    # 批量获取 PE 数据
    print("\n正在批量获取 PE 数据...")
    pe_dict = get_all_pe_batch(ts_codes)
    print(f"获取到 {len(pe_dict)} 只股票的 PE 数据")
    
    # 先筛选 PE<50 的股票，减少后续 API 调用
    filtered_codes = [code for code in ts_codes if pe_dict.get(code) is not None and 0 < pe_dict[code] < 50]
    print(f"PE<50 的股票数量：{len(filtered_codes)}")
    
    if not filtered_codes:
        print("没有 PE<50 的股票")
        return
    
    # 分批获取财务数据（每批 200 只股票）
    print("\n正在批量获取财务数据...")
    all_fin_data = {}
    batch_size = 200
    
    for i in range(0, len(filtered_codes), batch_size):
        batch = filtered_codes[i:i+batch_size]
        print(f"\n批次 {i//batch_size + 1}/{(len(filtered_codes)+batch_size-1)//batch_size}")
        batch_data = get_all_financial_data_batch(batch, years=5)
        all_fin_data.update(batch_data)
    
    # 筛选股票
    print("\n正在筛选符合条件的股票...")
    passed_stocks = []
    
    # 获取股票名称
    stock_names = chi_next_stocks.set_index('ts_code')['name'].to_dict()
    
    for ts_code in filtered_codes:
        result = screen_stock(ts_code, all_fin_data, pe_dict)
        if result:
            result['name'] = stock_names.get(ts_code, '')
            passed_stocks.append(result)
            print(f"  ✓ {ts_code} {result['name']} PE:{result['pe_ttm']} ROE:{result['roe_5y_avg']}% ROIC:{result['roic_5y_avg']}%")
    
    # 输出结果
    print("\n" + "=" * 80)
    print(f"筛选完成！共 {len(passed_stocks)}/{len(filtered_codes)} 只股票符合条件")
    print("=" * 80)
    
    if passed_stocks:
        df = pd.DataFrame(passed_stocks)
        # 按 ROE 排序
        df = df.sort_values('roe_5y_avg', ascending=False)
        
        print("\n符合条件的股票列表：")
        print(df.to_string(index=False))
        
        # 保存结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"/home/admin/openclaw/workspace/chi_next_screen_{timestamp}.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n结果已保存到：{output_file}")
        
        # 也保存为 Excel
        xlsx_file = f"/home/admin/openclaw/workspace/chi_next_screen_{timestamp}.xlsx"
        df.to_excel(xlsx_file, index=False, engine='openpyxl')
        print(f"Excel 版本：{xlsx_file}")
    else:
        print("\n没有股票符合所有条件")

if __name__ == "__main__":
    main()
