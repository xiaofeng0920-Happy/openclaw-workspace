#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股筛选批次 4/5：筛选 601xxx 开头的股票
条件：PE<50，ROE 连续 5 年>5%，ROIC 连续 5 年>5%，自由现金流连续 5 年为正，资产负债率<50%
使用 AkShare（无需 Token）
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import time
import warnings

warnings.filterwarnings('ignore')

def get_601_stocks():
    """获取所有 601 开头的股票"""
    print("获取 A 股股票列表...")
    
    # 获取 A 股列表
    stock_info = ak.stock_info_a_code_name()
    
    # 筛选 601 开头的股票
    stocks_601 = stock_info[stock_info['code'].str.startswith('601')]
    print(f"找到 601 开头的股票数量：{len(stocks_601)}")
    return stocks_601

def get_all_stock_pe():
    """获取所有股票的 PE 数据"""
    print("获取全市场 PE 数据（可能需要 1-2 分钟）...")
    
    # 获取全市场实时行情
    df = ak.stock_zh_a_spot_em()
    
    # 提取需要的列（注意列名是"市盈率 - 动态"连字符无空格）
    pe_df = df[['代码', '名称', '市盈率-动态']].copy()
    pe_df.columns = ['code', 'name', 'pe']
    
    # 转换 PE 为数值
    pe_df['pe'] = pd.to_numeric(pe_df['pe'], errors='coerce')
    
    print(f"获取到 {len(pe_df)} 只股票的 PE 数据")
    return pe_df

def get_financial_data(stock_code):
    """获取股票财务数据"""
    try:
        # 获取财务指标
        df = ak.stock_financial_analysis_indicator(symbol=stock_code)
        
        if len(df) == 0:
            return None
        
        # 按日期排序
        df['日期'] = pd.to_datetime(df['日期'])
        df = df.sort_values('日期', ascending=False)
        
        return df
    except Exception as e:
        print(f"  获取财务数据失败：{e}")
        return None

def check_roe_5years(df):
    """检查 ROE 连续 5 年是否>5%"""
    try:
        if df is None or len(df) == 0:
            return False, []
        
        # 提取年度数据（取每年最后一个报告期）
        df['年份'] = df['日期'].dt.year
        annual = df.groupby('年份').last().reset_index()
        annual = annual.sort_values('年份', ascending=False)
        
        # 取最近 5 年
        if len(annual) < 5:
            return False, []
        
        recent_5y = annual.head(5)
        
        # 检查是否有 ROE 列
        roe_col = None
        for col in recent_5y.columns:
            if '净资产收益率' in col and '%' in col:
                roe_col = col
                break
        
        if roe_col is None:
            return False, []
        
        roe_values = recent_5y[roe_col].tolist()
        valid_roe = [v for v in roe_values if pd.notna(v)]
        
        if len(valid_roe) < 5:
            return False, roe_values
        
        all_above_5 = all(v > 5 for v in valid_roe)
        return all_above_5, roe_values
    except Exception as e:
        return False, []

def check_roic_5years(df):
    """检查 ROIC 连续 5 年是否>5%"""
    try:
        if df is None or len(df) == 0:
            return False, []
        
        df['年份'] = df['日期'].dt.year
        annual = df.groupby('年份').last().reset_index()
        annual = annual.sort_values('年份', ascending=False)
        
        if len(annual) < 5:
            return False, []
        
        recent_5y = annual.head(5)
        
        # 检查是否有 ROIC 列（总资产净利率）
        roic_col = None
        for col in recent_5y.columns:
            if '总资产净利率' in col and '%' in col:
                roic_col = col
                break
        
        if roic_col is None:
            return False, []
        
        roic_values = recent_5y[roic_col].tolist()
        valid_roic = [v for v in roic_values if pd.notna(v)]
        
        if len(valid_roic) < 5:
            return False, roic_values
        
        all_above_5 = all(v > 5 for v in valid_roic)
        return all_above_5, roic_values
    except Exception as e:
        return False, []

def check_fcf_5years(df):
    """检查自由现金流连续 5 年是否为正"""
    try:
        if df is None or len(df) == 0:
            return False, []
        
        df['年份'] = df['日期'].dt.year
        annual = df.groupby('年份').last().reset_index()
        annual = annual.sort_values('年份', ascending=False)
        
        if len(annual) < 5:
            return False, []
        
        recent_5y = annual.head(5)
        
        # 检查是否有经营活动现金流相关列
        fcf_col = None
        for col in recent_5y.columns:
            if '经营活动' in col and ('现金流' in col or '现金流量' in col):
                fcf_col = col
                break
        
        if fcf_col is None:
            return False, []
        
        fcf_values = recent_5y[fcf_col].tolist()
        valid_fcf = [v for v in fcf_values if pd.notna(v)]
        
        if len(valid_fcf) < 5:
            return False, fcf_values
        
        all_positive = all(v > 0 for v in valid_fcf)
        return all_positive, fcf_values
    except Exception as e:
        return False, []

def check_debt_ratio(df):
    """检查资产负债率是否<50%"""
    try:
        if df is None or len(df) == 0:
            return False
        
        # 取最新数据
        latest = df.iloc[0]
        
        # 检查是否有资产负债率列
        debt_col = None
        for col in latest.index:
            if '资产负债率' in col and '%' in col:
                debt_col = col
                break
        
        if debt_col is None:
            return False
        
        debt_ratio = latest[debt_col]
        return pd.notna(debt_ratio) and debt_ratio < 50
    except Exception as e:
        return False

def main():
    print("=" * 60)
    print("A 股筛选批次 4/5:601xxx 股票筛选")
    print("条件：PE<50, ROE 连续 5 年>5%, ROIC 连续 5 年>5%, 自由现金流连续 5 年为正，资产负债率<50%")
    print("=" * 60)
    
    # 1. 获取 601 开头的股票
    stocks_601 = get_601_stocks()
    
    # 2. 获取全市场 PE 数据
    pe_data = get_all_stock_pe()
    
    # 合并 PE 数据
    stocks_601 = stocks_601.merge(pe_data, on=['code', 'name'], how='left')
    
    # 筛选 PE<50 且>0 的股票
    stocks_601 = stocks_601[(stocks_601['pe'] > 0) & (stocks_601['pe'] < 50)]
    print(f"PE<50 的股票数量：{len(stocks_601)}")
    
    qualified_stocks = []
    total = len(stocks_601)
    
    # 3. 对 PE 合格的股票进行详细筛选
    print("\n开始详细财务指标筛选...")
    for idx, row in stocks_601.iterrows():
        code = row['code']
        name = row['name']
        pe = row['pe']
        
        print(f"\n[{idx+1}/{total}] 检查 {code} ({name}) PE={pe:.2f}...")
        
        # 获取财务数据
        financial_df = get_financial_data(code)
        if financial_df is None:
            print(f"  无法获取财务数据")
            continue
        
        # 检查 ROE
        roe_ok, roe_values = check_roe_5years(financial_df)
        print(f"  ROE 5 年>5%: {roe_ok}")
        if not roe_ok:
            continue
        
        # 检查 ROIC
        roic_ok, roic_values = check_roic_5years(financial_df)
        print(f"  ROIC 5 年>5%: {roic_ok}")
        if not roic_ok:
            continue
        
        # 检查自由现金流
        fcf_ok, fcf_values = check_fcf_5years(financial_df)
        print(f"  自由现金流 5 年>0: {fcf_ok}")
        if not fcf_ok:
            continue
        
        # 检查资产负债率
        debt_ok = check_debt_ratio(financial_df)
        print(f"  资产负债率<50%: {debt_ok}")
        if not debt_ok:
            continue
        
        # 所有条件符合
        qualified_stocks.append({
            '代码': code,
            '名称': name,
            'PE': pe
        })
        print(f"  ✅ 符合条件!")
        
        # 避免请求过快
        time.sleep(0.5)
    
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
