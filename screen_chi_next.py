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

# 设置 Tushare Token
ts.set_token('eb58a2fb952bce3b9590d9290eea7966097450737fa8ad22156f2ca5')
pro = ts.pro_api()

def get_chi_next_stocks():
    """获取所有创业板股票 (300xxx)"""
    print("正在获取创业板股票列表...")
    stocks = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    chi_next_stocks = stocks[stocks['symbol'].str.startswith('300')]
    print(f"创业板股票数量：{len(chi_next_stocks)}")
    return chi_next_stocks['ts_code'].tolist()

def get_financial_indicator(ts_code, year):
    """获取指定年份的财务指标"""
    try:
        # 获取 ROE
        roe_df = pro.fina_indicator(ts_code=ts_code, start_date=f'{year}0101', end_date=f'{year}1231')
        if roe_df.empty:
            return None
        
        # 取最新报告期
        roe_df = roe_df.sort_values('end_date', ascending=False).iloc[0]
        
        # 获取 ROIC
        roic = roe_df.get('roic', None)
        
        # 获取 ROE (加权)
        roe = roe_df.get('roe_wa', None)
        
        # 获取资产负债率
        debt_ratio = roe_df.get('debt_to_assets', None)
        
        return {
            'year': year,
            'roe': roe,
            'roic': roic,
            'debt_ratio': debt_ratio
        }
    except Exception as e:
        print(f"获取 {ts_code} {year} 年数据失败：{e}")
        return None

def get_cash_flow(ts_code, year):
    """获取指定年份的现金流量"""
    try:
        cash_df = pro.cashflow(ts_code=ts_code, start_date=f'{year}0101', end_date=f'{year}1231')
        if cash_df.empty:
            return None
        
        # 取最新报告期
        cash_df = cash_df.sort_values('end_date', ascending=False).iloc[0]
        
        # 自由现金流 = 经营活动产生的现金流量净额 - 资本支出
        operating_cash = cash_df.get('oper_cf', None)
        capex = cash_df.get('capex', None)
        
        if operating_cash is not None and capex is not None:
            free_cash_flow = operating_cash - capex
        else:
            free_cash_flow = operating_cash
        
        return {
            'year': year,
            'free_cash_flow': free_cash_flow
        }
    except Exception as e:
        print(f"获取 {ts_code} {year} 年现金流失败：{e}")
        return None

def get_pe_ratio(ts_code):
    """获取当前 PE 比率"""
    try:
        daily_basic = pro.daily_basic(ts_code=ts_code, trade_date=datetime.now().strftime('%Y%m%d'))
        if daily_basic.empty:
            # 如果今天的数据没有，尝试获取最近的数据
            daily_basic = pro.daily_basic(ts_code=ts_code)
            if daily_basic.empty:
                return None
            daily_basic = daily_basic.sort_values('trade_date', ascending=False).iloc[0]
        else:
            daily_basic = daily_basic.iloc[0]
        
        pe = daily_basic.get('pe_ttm', None)
        return pe
    except Exception as e:
        print(f"获取 {ts_code} PE 失败：{e}")
        return None

def screen_stock(ts_code, years=5):
    """筛选单只股票"""
    current_year = datetime.now().year
    
    # 获取 PE
    pe = get_pe_ratio(ts_code)
    if pe is None or pe <= 0 or pe >= 50:
        return None
    
    # 检查连续 5 年的 ROE, ROIC, 资产负债率
    roe_pass = True
    roic_pass = True
    debt_pass = True
    cash_pass = True
    
    for year_offset in range(years):
        year = current_year - 1 - year_offset
        
        # 获取财务指标
        fin_data = get_financial_indicator(ts_code, year)
        if fin_data is None:
            return None
        
        # 检查 ROE
        if fin_data['roe'] is None or fin_data['roe'] <= 5:
            roe_pass = False
            break
        
        # 检查 ROIC
        if fin_data['roic'] is None or fin_data['roic'] <= 5:
            roic_pass = False
            break
        
        # 检查资产负债率
        if fin_data['debt_ratio'] is None or fin_data['debt_ratio'] >= 50:
            debt_pass = False
            break
        
        # 获取现金流
        cash_data = get_cash_flow(ts_code, year)
        if cash_data is None or cash_data['free_cash_flow'] is None or cash_data['free_cash_flow'] <= 0:
            cash_pass = False
            break
    
    if roe_pass and roic_pass and debt_pass and cash_pass:
        return {
            'ts_code': ts_code,
            'pe': pe,
            'roe_5y_avg': 'N/A',  # 需要计算
            'roic_5y_avg': 'N/A',
            'debt_ratio': fin_data['debt_ratio'],
            'free_cash_flow': cash_data['free_cash_flow']
        }
    
    return None

def main():
    print("=" * 60)
    print("A 股创业板股票筛选")
    print("条件：PE<50, ROE 连续 5 年>5%, ROIC 连续 5 年>5%, 自由现金流连续 5 年>0, 资产负债率<50%")
    print("=" * 60)
    
    # 获取创业板股票列表
    stock_list = get_chi_next_stocks()
    
    # 筛选股票
    passed_stocks = []
    total = len(stock_list)
    
    for i, ts_code in enumerate(stock_list):
        if i % 50 == 0:
            print(f"进度：{i}/{total} ({i/total*100:.1f}%)")
        
        result = screen_stock(ts_code)
        if result:
            passed_stocks.append(result)
            print(f"✓ 通过：{ts_code}")
    
    # 输出结果
    print("\n" + "=" * 60)
    print(f"筛选结果：{len(passed_stocks)}/{total} 只股票符合条件")
    print("=" * 60)
    
    if passed_stocks:
        df = pd.DataFrame(passed_stocks)
        print(df.to_string(index=False))
        
        # 保存结果
        output_file = f"chi_next_screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n结果已保存到：{output_file}")
    else:
        print("没有股票符合所有条件")

if __name__ == "__main__":
    main()
