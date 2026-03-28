#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股创业板 (300xxx) 股票筛选 - AkShare 版本
条件：
- PE < 50
- ROE 连续 5 年 > 5%
- ROIC 连续 5 年 > 5%
- 自由现金流连续 5 年为正
- 资产负债率 < 50%

使用 AkShare（免费无限制）
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import time
import warnings

warnings.filterwarnings('ignore')

def get_chi_next_stocks():
    """获取所有创业板股票"""
    print("正在获取创业板股票列表...")
    df = ak.stock_info_a_code_name()
    chi_next_stocks = df[df['code'].str.startswith('300')]
    print(f"创业板股票数量：{len(chi_next_stocks)}")
    return chi_next_stocks

def get_stock_pe(ts_code):
    """获取股票 PE(TTM)"""
    try:
        # 获取实时行情
        df = ak.stock_zh_a_spot_em()
        if not df.empty:
            stock = df[df['代码'] == ts_code]
            if not stock.empty:
                pe = stock.iloc[0].get('市盈率 - 动态', None)
                return pe
    except:
        pass
    return None

def get_financial_data(ts_code, years=5):
    """获取财务数据"""
    try:
        # 获取 ROE 数据
        df = ak.stock_financial_analysis_indicator(symbol=ts_code, start_year=str(datetime.now().year - years))
        
        if df.empty:
            return []
        
        # 提取年度数据
        data = []
        current_year = datetime.now().year
        
        for year_offset in range(years):
            year = current_year - 1 - year_offset
            year_str = f"{year}年"
            
            year_data = df[df['报告期'].str.contains(year_str, na=False)]
            
            if not year_data.empty:
                # 取最新一期
                row = year_data.iloc[-1]
                data.append({
                    'year': year,
                    'roe': float(row.get('加权净资产收益率 (%)', 0) or 0),
                    'roic': float(row.get('总资产净利润率 (%)', 0) or 0),
                    'debt_ratio': float(row.get('资产负债率 (%)', 0) or 0),
                })
        
        return data
    
    except Exception as e:
        print(f"  获取 {ts_code} 财务数据失败：{e}")
        return []

def get_cash_flow_data(ts_code, years=5):
    """获取现金流数据"""
    try:
        df = ak.stock_cash_flow_by_yearly_em(symbol=ts_code)
        
        if df.empty:
            return []
        
        data = []
        current_year = datetime.now().year
        
        for year_offset in range(years):
            year = current_year - 1 - year_offset
            
            year_data = df[df['报告期'] == str(year)]
            if not year_data.empty:
                row = year_data.iloc[0]
                fcf = float(row.get('自由现金流', 0) or 0)
                data.append({'year': year, 'fcf': fcf})
        
        return data
    
    except:
        return []

def screen_stock(ts_code, name):
    """筛选单只股票"""
    try:
        # 获取 PE
        df = ak.stock_zh_a_spot_em()
        stock = df[df['代码'] == ts_code]
        if stock.empty:
            return None
        
        pe = float(stock.iloc[0].get('市盈率 - 动态', 999) or 999)
        if pe <= 0 or pe >= 50:
            return None
        
        # 获取财务数据
        fin_data = get_financial_data(ts_code, years=5)
        if len(fin_data) < 5:
            return None
        
        # 获取现金流
        cash_data = get_cash_flow_data(ts_code, years=5)
        if len(cash_data) < 5:
            return None
        
        # 检查条件
        roe_pass = all(d['roe'] > 5 for d in fin_data)
        roic_pass = all(d['roic'] > 5 for d in fin_data)
        debt_pass = all(d['debt_ratio'] < 50 for d in fin_data)
        fcf_pass = all(d['fcf'] > 0 for d in cash_data)
        
        if roe_pass and roic_pass and debt_pass and fcf_pass:
            avg_roe = sum(d['roe'] for d in fin_data) / len(fin_data)
            avg_roic = sum(d['roic'] for d in fin_data) / len(fin_data)
            avg_debt = sum(d['debt_ratio'] for d in fin_data) / len(fin_data)
            
            return {
                'ts_code': ts_code,
                'name': name,
                'pe_ttm': round(pe, 2),
                'roe_5y_avg': round(avg_roe, 2),
                'roic_5y_avg': round(avg_roic, 2),
                'debt_ratio_avg': round(avg_debt, 2),
            }
        
        return None
    
    except Exception as e:
        return None

def main():
    print("=" * 80)
    print("A 股创业板 (300xxx) 股票筛选 - AkShare 版本")
    print("条件：PE<50, ROE 连续 5 年>5%, ROIC 连续 5 年>5%, 自由现金流连续 5 年>0, 资产负债率<50%")
    print("=" * 80)
    
    # 获取股票列表
    stocks = get_chi_next_stocks()
    
    # 获取实时行情（一次性获取所有股票）
    print("\n正在获取实时行情数据...")
    df_spot = ak.stock_zh_a_spot_em()
    print(f"获取到 {len(df_spot)} 只股票行情")
    
    # 筛选创业板且 PE<50 的股票
    chi_next_spot = df_spot[df_spot['代码'].str.startswith('300')]
    chi_next_spot = chi_next_spot[chi_next_spot['市盈率 - 动态'].notna()]
    chi_next_spot = chi_next_spot[(chi_next_spot['市盈率 - 动态'] > 0) & (chi_next_spot['市盈率 - 动态'] < 50)]
    
    print(f"创业板中 PE<50 的股票数量：{len(chi_next_spot)}")
    
    if len(chi_next_spot) == 0:
        print("没有 PE<50 的创业板股票")
        return
    
    # 逐一筛选
    print("\n开始详细筛选...")
    passed_stocks = []
    total = len(chi_next_spot)
    
    for i, (_, row) in enumerate(chi_next_spot.iterrows()):
        ts_code = row['代码']
        name = row['名称']
        
        if i % 10 == 0:
            print(f"进度：{i}/{total} ({i/total*100:.1f}%), 已通过：{len(passed_stocks)}")
        
        result = screen_stock(ts_code, name)
        if result:
            passed_stocks.append(result)
            print(f"  ✓ {ts_code} {name} PE:{result['pe_ttm']} ROE:{result['roe_5y_avg']}%")
        
        time.sleep(1)  # 控制频率
    
    # 输出结果
    print("\n" + "=" * 80)
    print(f"筛选完成！共 {len(passed_stocks)}/{total} 只股票符合条件")
    print("=" * 80)
    
    if passed_stocks:
        df = pd.DataFrame(passed_stocks)
        df = df.sort_values('roe_5y_avg', ascending=False)
        
        print("\n符合条件的股票列表：")
        print(df.to_string(index=False))
        
        # 保存结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"/home/admin/openclaw/workspace/chi_next_screen_akshare_{timestamp}.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n结果已保存到：{output_file}")
    else:
        print("\n没有股票符合所有条件")

if __name__ == "__main__":
    main()
