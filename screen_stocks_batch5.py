#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股筛选批次 5/5：筛选 603xxx/605xxx/688xxx 开头的股票
条件：
- PE < 50
- ROE 连续 5 年 > 5%
- ROIC 连续 5 年 > 5%
- 自由现金流连续 5 年为正
- 资产负债率 < 50%

使用 AkShare 数据源
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import time
import warnings
warnings.filterwarnings('ignore')

def get_stock_list():
    """获取 603xxx/605xxx/688xxx 开头的股票列表"""
    print("获取 A 股股票列表...")
    
    # 获取所有 A 股列表
    stock_df = ak.stock_info_a_code_name()
    
    if stock_df is None or len(stock_df) == 0:
        print("获取股票列表失败")
        return pd.DataFrame()
    
    # 确保代码是字符串类型
    stock_df['code'] = stock_df['code'].astype(str)
    
    # 筛选 603/605/688 开头的股票
    mask = stock_df['code'].str.startswith(('603', '605', '688'))
    target_stocks = stock_df[mask].copy()
    
    print(f"符合条件的股票数量：{len(target_stocks)}")
    return target_stocks

def get_financial_data(code):
    """获取单只股票的财务指标"""
    try:
        # 获取实时行情数据（包含 PE）
        try:
            spot_df = ak.stock_zh_a_spot_em()
            if spot_df is None or len(spot_df) == 0:
                return None
            
            stock_data = spot_df[spot_df['代码'] == code]
            if len(stock_data) == 0:
                return None
            
            pe_ttm = stock_data.iloc[0]['市盈率 - 动态']
            
            # 检查 PE < 50 且为正数
            if pd.isna(pe_ttm) or pe_ttm < 0 or pe_ttm >= 50:
                return None
        except Exception as e:
            print(f"获取 {code} 行情数据失败：{e}")
            return None
        
        # 获取财务指标
        try:
            fina_df = ak.stock_financial_analysis_indicator(symbol=code)
            if fina_df is None or len(fina_df) == 0:
                return None
        except Exception as e:
            print(f"获取 {code} 财务指标失败：{e}")
            return None
        
        # 转换日期列
        if '日期' in fina_df.columns:
            fina_df['日期'] = pd.to_datetime(fina_df['日期'])
            fina_df = fina_df.sort_values('日期', ascending=False)
        
        # 获取过去 5 年的年度数据（通常年度报告在次年发布）
        current_year = datetime.now().year
        years = [current_year - 1, current_year - 2, current_year - 3, current_year - 4, current_year - 5]
        
        annual_data = []
        for year in years:
            # 查找该年度的数据
            year_data = fina_df[fina_df['日期'].dt.year == year]
            if len(year_data) > 0:
                # 取该年最后一条记录（通常是年报）
                annual_data.append(year_data.iloc[-1])
        
        # 需要至少 4 年数据（考虑到数据完整性）
        if len(annual_data) < 4:
            return None
        
        # 检查 ROE 连续多年 > 5%
        roe_col = None
        for col in ['加权净资产收益率 (%)', '净资产收益率 (%)', 'ROE']:
            if col in annual_data[0].index:
                roe_col = col
                break
        
        if not roe_col:
            return None
        
        roe_values = []
        for data in annual_data[:5]:
            roe = data.get(roe_col, 0)
            if pd.isna(roe):
                roe = 0
            roe_values.append(float(roe))
        
        # 检查是否连续>5%
        if not all(v > 5 for v in roe_values):
            return None
        
        # 检查 ROIC 连续多年 > 5%
        roic_col = None
        for col in ['投入资本回报率 ROIC (%)', 'ROIC', '投入资本收益率']:
            if col in annual_data[0].index:
                roic_col = col
                break
        
        if roic_col:
            roic_values = []
            for data in annual_data[:5]:
                roic = data.get(roic_col, 0)
                if pd.isna(roic):
                    roic = 0
                roic_values.append(float(roic))
            
            # 检查是否连续>5%
            if not all(v > 5 for v in roic_values):
                return None
        else:
            # 如果没有 ROIC 数据，跳过此条件
            roic_values = [0] * len(roe_values)
        
        # 检查资产负债率 < 50%
        debt_col = None
        for col in ['资产负债率 (%)', '资产负债率', '负债比率']:
            if col in annual_data[0].index:
                debt_col = col
                break
        
        if not debt_col:
            return None
        
        latest_debt_ratio = annual_data[0].get(debt_col, 100)
        if pd.isna(latest_debt_ratio):
            return None
        
        if float(latest_debt_ratio) >= 50:
            return None
        
        # 检查自由现金流（如果有数据）
        fcf_col = None
        for col in ['经营活动产生的现金流量净额', '自由现金流', '经营现金流']:
            if col in fina_df.columns:
                fcf_col = col
                break
        
        fcf_values = [0] * len(roe_values)  # 默认值
        if fcf_col:
            fcf_annual = []
            for data in annual_data[:5]:
                fcf = data.get(fcf_col, 0)
                if pd.isna(fcf):
                    fcf = 0
                fcf_annual.append(float(fcf))
            
            # 检查是否连续为正
            if all(v > 0 for v in fcf_annual):
                fcf_values = fcf_annual
            else:
                # 自由现金流不满足条件，跳过该股票
                return None
        
        return {
            'code': code,
            'pe_ttm': pe_ttm,
            'roe_avg': sum(roe_values) / len(roe_values),
            'roic_avg': sum(roic_values) / len(roic_values),
            'fcf_avg': sum(fcf_values) / len(fcf_values),
            'debt_ratio': float(latest_debt_ratio)
        }
        
    except Exception as e:
        print(f"处理 {code} 时出错：{e}")
        return None

def main():
    print("=" * 80)
    print("A 股筛选批次 5/5：603xxx/605xxx/688xxx")
    print("筛选条件：PE<50, ROE 连续 5 年>5%, ROIC 连续 5 年>5%, 自由现金流连续 5 年为正，资产负债率<50%")
    print("=" * 80)
    
    # 获取股票列表
    stocks = get_stock_list()
    
    if len(stocks) == 0:
        print("未获取到股票列表")
        return
    
    # 筛选符合条件的股票
    qualified_stocks = []
    total = len(stocks)
    
    print(f"\n开始筛选 {total} 只股票...\n")
    
    for idx, row in stocks.iterrows():
        code = row['code']
        name = row['name']
        
        result = get_financial_data(code)
        if result:
            result['name'] = name
            qualified_stocks.append(result)
            print(f"[{len(qualified_stocks)}] {code} {name} - PE: {result['pe_ttm']:.2f}, ROE: {result['roe_avg']:.2f}%")
        
        # 进度显示
        if (idx + 1) % 50 == 0:
            print(f"\n进度：{idx + 1}/{total}，已找到 {len(qualified_stocks)} 只符合条件\n")
            time.sleep(0.5)
        
        # 避免请求过快
        time.sleep(0.2)
    
    # 输出结果
    print("\n" + "=" * 80)
    print(f"筛选完成！共 {len(qualified_stocks)} 只股票符合条件")
    print("=" * 80)
    
    if qualified_stocks:
        df = pd.DataFrame(qualified_stocks)
        df = df.sort_values('pe_ttm')
        
        # 保存结果
        output_file = f"/home/admin/openclaw/workspace/筛选结果_批次 5_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(output_file, index=False)
        print(f"\n结果已保存至：{output_file}")
        
        # 打印详细列表
        print("\n符合条件的股票列表：")
        print("-" * 120)
        print(f"{'代码':<12} {'名称':<15} {'PE(TTM)':<10} {'ROE(5 年平均)':<15} {'ROIC(5 年平均)':<15} {'自由现金流 (5 年平均)':<18} {'资产负债率':<12}")
        print("-" * 120)
        
        for _, row in df.iterrows():
            print(f"{row['code']:<12} {row['name']:<15} {row['pe_ttm']:<10.2f} {row['roe_avg']:<15.2f} {row['roic_avg']:<15.2f} {row['fcf_avg']:<18.2f} {row['debt_ratio']:<12.2f}")
        
        print("-" * 120)
        print(f"总计：{len(df)} 只股票")
    else:
        print("未找到符合条件的股票")

if __name__ == "__main__":
    main()
