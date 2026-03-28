#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股筛选批次 4/5：筛选 601xxx 开头的股票
条件：PE<50，ROE 连续 5 年>5%，ROIC 连续 5 年>5%，自由现金流连续 5 年为正，资产负债率<50%
"""

import tushare as ts
import pandas as pd
from datetime import datetime
import os
from pathlib import Path

# 设置 Tushare Token（优先从已有配置读取）
TOKEN_FILE = Path('/home/admin/openclaw/workspace/agents/data-collector/.tushare_token')
TS_TOKEN = os.environ.get('TUSHARE_TOKEN', '')

if not TS_TOKEN and TOKEN_FILE.exists():
    TS_TOKEN = TOKEN_FILE.read_text().strip()

if not TS_TOKEN:
    print("❌ 错误：未找到 Tushare Token")
    print("请按以下方式之一配置：")
    print("  1. 设置环境变量：export TUSHARE_TOKEN='your_token'")
    print(f"  2. 保存 token 到文件：{TOKEN_FILE}")
    print("\n获取 Token: 注册 https://tushare.pro 后在个人中心获取")
    exit(1)

ts.set_token(TS_TOKEN)
pro = ts.pro_api()
print(f"✅ Tushare 初始化成功")

def get_601_stocks():
    """获取所有 601 开头的股票"""
    # 获取股票列表
    stock_list = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,market,list_date')
    # 筛选 601 开头的股票
    stocks_601 = stock_list[stock_list['symbol'].str.startswith('601')]
    print(f"找到 601 开头的股票数量：{len(stocks_601)}")
    return stocks_601['ts_code'].tolist()

def get_latest_pe(ts_codes):
    """获取最新 PE 数据"""
    # 获取每日指标
    df = pro.daily_basic(ts_code=','.join(ts_codes), fields='ts_code,pe,pe_ttm,pb')
    # 取最新数据（按日期排序取最后一条）
    latest_pe = df.sort_values('trade_date').groupby('ts_code').last().reset_index()
    return latest_pe[['ts_code', 'pe_ttm']]

def check_roe_5years(ts_code, years=5):
    """检查 ROE 连续 5 年是否>5%"""
    try:
        # 获取财务指标
        df = pro.fina_indicator(ts_code=ts_code)
        if len(df) == 0:
            return False
        
        # 按报告期排序
        df = df.sort_values('end_date', ascending=False)
        
        # 取最近 5 年的年报数据（ann_date 包含年份信息）
        df['year'] = pd.to_datetime(df['end_date']).dt.year
        annual_df = df[df['report_type'].str.contains('年报', na=False)]
        
        if len(annual_df) < years:
            return False
        
        # 取最近 5 年
        recent_5y = annual_df.head(years)
        
        # 检查 ROE 是否都>5%
        roe_values = recent_5y['roe'].dropna()
        if len(roe_values) < years:
            return False
        
        return all(roe > 5 for roe in roe_values)
    except Exception as e:
        print(f"ROE 检查失败 {ts_code}: {e}")
        return False

def check_roic_5years(ts_code, years=5):
    """检查 ROIC 连续 5 年是否>5%"""
    try:
        df = pro.fina_indicator(ts_code=ts_code)
        if len(df) == 0:
            return False
        
        df = df.sort_values('end_date', ascending=False)
        df['year'] = pd.to_datetime(df['end_date']).dt.year
        annual_df = df[df['report_type'].str.contains('年报', na=False)]
        
        if len(annual_df) < years:
            return False
        
        recent_5y = annual_df.head(years)
        
        # 检查 ROIC 是否都>5%
        roic_values = recent_5y['roic'].dropna()
        if len(roic_values) < years:
            return False
        
        return all(roic > 5 for roic in roic_values)
    except Exception as e:
        print(f"ROIC 检查失败 {ts_code}: {e}")
        return False

def check_fcf_5years(ts_code, years=5):
    """检查自由现金流连续 5 年是否为正"""
    try:
        df = pro.fina_indicator(ts_code=ts_code)
        if len(df) == 0:
            return False
        
        df = df.sort_values('end_date', ascending=False)
        df['year'] = pd.to_datetime(df['end_date']).dt.year
        annual_df = df[df['report_type'].str.contains('年报', na=False)]
        
        if len(annual_df) < years:
            return False
        
        recent_5y = annual_df.head(years)
        
        # 检查自由现金流是否都为正
        fcf_values = recent_5y['free_cash_flow'].dropna()
        if len(fcf_values) < years:
            return False
        
        return all(fcf > 0 for fcf in fcf_values)
    except Exception as e:
        print(f"自由现金流检查失败 {ts_code}: {e}")
        return False

def check_debt_ratio(ts_code):
    """检查资产负债率是否<50%"""
    try:
        df = pro.fina_indicator(ts_code=ts_code)
        if len(df) == 0:
            return False
        
        # 取最新数据
        df = df.sort_values('end_date', ascending=False)
        latest = df.iloc[0]
        
        debt_ratio = latest['debt_to_assets']
        return debt_ratio < 50 if pd.notna(debt_ratio) else False
    except Exception as e:
        print(f"资产负债率检查失败 {ts_code}: {e}")
        return False

def main():
    print("=" * 60)
    print("A 股筛选批次 4/5：601xxx 股票筛选")
    print("条件：PE<50, ROE 连续 5 年>5%, ROIC 连续 5 年>5%, 自由现金流连续 5 年为正，资产负债率<50%")
    print("=" * 60)
    
    # 1. 获取 601 开头的股票
    ts_codes = get_601_stocks()
    
    # 2. 获取最新 PE 数据
    print("\n获取 PE 数据...")
    pe_data = get_latest_pe(ts_codes)
    
    # 筛选 PE<50 的股票
    pe_filtered = pe_data[pe_data['pe_ttm'] < 50]
    pe_filtered = pe_filtered[pe_filtered['pe_ttm'] > 0]  # 排除负值
    print(f"PE<50 的股票数量：{len(pe_filtered)}")
    
    qualified_stocks = []
    
    # 3. 对 PE 合格的股票进行详细筛选
    print("\n开始详细财务指标筛选...")
    for idx, row in pe_filtered.iterrows():
        ts_code = row['ts_code']
        pe = row['pe_ttm']
        
        # 获取股票基本信息
        stock_info = pro.stock_basic(ts_code=ts_code, fields='ts_code,name')
        stock_name = stock_info['name'].iloc[0] if len(stock_info) > 0 else 'Unknown'
        
        print(f"\n检查 {ts_code} ({stock_name}) PE={pe:.2f}...")
        
        # 检查各项指标
        roe_ok = check_roe_5years(ts_code)
        print(f"  ROE 5 年>5%: {roe_ok}")
        
        if not roe_ok:
            continue
            
        roic_ok = check_roic_5years(ts_code)
        print(f"  ROIC 5 年>5%: {roic_ok}")
        
        if not roic_ok:
            continue
            
        fcf_ok = check_fcf_5years(ts_code)
        print(f"  自由现金流 5 年>0: {fcf_ok}")
        
        if not fcf_ok:
            continue
            
        debt_ok = check_debt_ratio(ts_code)
        print(f"  资产负债率<50%: {debt_ok}")
        
        if debt_ok:
            qualified_stocks.append({
                '代码': ts_code,
                '名称': stock_name,
                'PE': pe
            })
            print(f"  ✅ 符合条件!")
    
    # 4. 输出结果
    print("\n" + "=" * 60)
    print(f"筛选完成！符合条件的股票数量：{len(qualified_stocks)}")
    print("=" * 60)
    
    if qualified_stocks:
        df_result = pd.DataFrame(qualified_stocks)
        print("\n符合条件的股票列表：")
        print(df_result.to_string(index=False))
        
        # 保存结果
        output_file = f"/home/admin/openclaw/workspace/601_stocks_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df_result.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n结果已保存至：{output_file}")
    else:
        print("\n未找到符合所有条件的股票。")

if __name__ == "__main__":
    main()
