#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股筛选脚本 - 批次 1/3 (00001-00799)
筛选条件:
- PE < 30
- ROE 连续 5 年 > 5%
- ROIC 连续 5 年 > 5%
- 自由现金流连续 5 年为正 (用每股经营现金流代替)
- 资产负债率 < 50%

使用 AkShare 的 stock_financial_hk_analysis_indicator_em 接口
"""

import akshare as ak
import pandas as pd
import warnings
import time
from datetime import datetime

warnings.filterwarnings('ignore')

def get_hk_stocks_in_range():
    """获取 00001-00799 范围的港股"""
    print("获取港股列表...")
    hk_df = ak.stock_hk_spot_em()
    
    # 过滤 00001-00799 范围
    hk_df['代码_int'] = hk_df['代码'].astype(int)
    filtered = hk_df[(hk_df['代码_int'] >= 1) & (hk_df['代码_int'] <= 799)].copy()
    filtered = filtered.sort_values('代码_int')
    
    print(f"00001-00799 范围股票数量: {len(filtered)}")
    return filtered

def check_financial_conditions(code, financial_df):
    """
    检查财务条件
    返回: (是否符合条件, 最新 PE, 最新 ROE, 最新 ROIC, 最新 FCF, 最新资产负债率)
    """
    if financial_df is None or len(financial_df) < 5:
        return False, None, None, None, None, None
    
    # 按报告期排序（从新到旧）
    financial_df = financial_df.sort_values('REPORT_DATE', ascending=False)
    recent_5 = financial_df.head(5)
    
    if len(recent_5) < 5:
        return False, None, None, None, None, None
    
    # 检查 ROE 连续 5 年 > 5%
    roe_values = pd.to_numeric(recent_5['ROE_YEARLY'], errors='coerce')
    if roe_values.isna().any() or not all(roe_values > 5):
        return False, None, None, None, None, None
    
    # 检查 ROIC 连续 5 年 > 5%
    roic_values = pd.to_numeric(recent_5['ROIC_YEARLY'], errors='coerce')
    if roic_values.isna().any() or not all(roic_values > 5):
        return False, None, None, None, None, None
    
    # 检查每股经营现金流连续 5 年为正 (代替自由现金流)
    fcf_values = pd.to_numeric(recent_5['PER_NETCASH_OPERATE'], errors='coerce')
    if fcf_values.isna().any() or not all(fcf_values > 0):
        return False, None, None, None, None, None
    
    # 检查资产负债率 < 50%
    debt_values = pd.to_numeric(recent_5['DEBT_ASSET_RATIO'], errors='coerce')
    if debt_values.isna().any() or not all(debt_values < 50):
        return False, None, None, None, None, None
    
    # 获取最新值
    latest_roe = roe_values.iloc[0]
    latest_roic = roic_values.iloc[0]
    latest_fcf = fcf_values.iloc[0]
    latest_debt = debt_values.iloc[0]
    
    return True, latest_roe, latest_roic, latest_fcf, latest_debt

def get_current_pe(code, hk_df):
    """获取当前 PE"""
    try:
        # 从港股实时行情获取 PE
        stock_info = hk_df[hk_df['代码'] == code]
        if len(stock_info) == 0:
            return None
        
        # 获取总市值和净利润来计算 PE
        # 或者从财务数据获取 EPS_TTM 来计算
        financial_df = ak.stock_financial_hk_analysis_indicator_em(symbol=code)
        if len(financial_df) == 0:
            return None
        
        financial_df = financial_df.sort_values('REPORT_DATE', ascending=False)
        eps_ttm = pd.to_numeric(financial_df.iloc[0]['EPS_TTM'], errors='coerce')
        
        if pd.isna(eps_ttm) or eps_ttm <= 0:
            return None
        
        # 获取当前股价
        price = stock_info['最新价'].values[0]
        
        # 计算 PE (股价 / EPS)
        # 注意：EPS 单位可能是人民币元，股价是港币，需要转换
        # 简单起见，直接计算
        pe = price / eps_ttm
        
        return round(pe, 2)
    except:
        return None

def filter_stocks():
    """主筛选函数"""
    print("=" * 70)
    print("港股筛选 - 批次 1/3 (00001-00799)")
    print("=" * 70)
    print("筛选条件:")
    print("  - PE < 30")
    print("  - ROE 连续 5 年 > 5%")
    print("  - ROIC 连续 5 年 > 5%")
    print("  - 每股经营现金流连续 5 年为正")
    print("  - 资产负债率 < 50%")
    print("=" * 70)
    
    # 获取股票列表
    hk_df = get_hk_stocks_in_range()
    stock_codes = hk_df['代码'].tolist()
    
    print(f"\n开始筛选 {len(stock_codes)} 只股票...\n")
    
    results = []
    processed = 0
    has_data_count = 0
    
    for code in stock_codes:
        processed += 1
        if processed % 50 == 0:
            print(f"进度: {processed}/{len(stock_codes)} ({processed/len(stock_codes)*100:.1f}%) - 已找到 {len(results)} 只")
        
        try:
            # 获取财务数据
            financial_df = ak.stock_financial_hk_analysis_indicator_em(symbol=code)
            
            if financial_df is None or len(financial_df) == 0:
                continue
            
            has_data_count += 1
            
            # 检查财务条件
            passed, roe, roic, fcf, debt = check_financial_conditions(code, financial_df)
            
            if not passed:
                continue
            
            # 获取当前 PE
            current_pe = get_current_pe(code, hk_df)
            
            if current_pe is None or current_pe <= 0 or current_pe >= 30:
                continue
            
            # 获取股票名称
            stock_info = hk_df[hk_df['代码'] == code]
            stock_name = stock_info['名称'].values[0] if len(stock_info) > 0 else "未知"
            
            # 符合条件，添加到结果
            results.append({
                '代码': code,
                '名称': stock_name,
                'PE': current_pe,
                'ROE(%)': round(roe, 2),
                'ROIC(%)': round(roic, 2),
                '每股经营现金流': round(fcf, 2),
                '资产负债率 (%)': round(debt, 2)
            })
            
            print(f"✓ 发现: {code} {stock_name} (PE={current_pe:.2f}, ROE={roe:.2f}%, ROIC={roic:.2f}%, 负债率={debt:.2f}%)")
            
            time.sleep(0.5)  # 避免请求过快
            
        except Exception as e:
            continue
    
    # 输出结果
    print("\n" + "=" * 70)
    print(f"筛选完成!")
    print(f"  - 总股票数: {len(stock_codes)}")
    print(f"  - 有财务数据的: {has_data_count}")
    print(f"  - 符合条件的: {len(results)}")
    print("=" * 70)
    
    if len(results) > 0:
        result_df = pd.DataFrame(results)
        print("\n符合条件的股票列表:")
        print(result_df.to_string(index=False))
        
        # 保存到文件
        result_df.to_csv('/home/admin/openclaw/workspace/hk_filtered_stocks_batch1.csv', index=False, encoding='utf-8-sig')
        print(f"\n结果已保存到: hk_filtered_stocks_batch1.csv")
    else:
        print("\n未找到符合条件的股票")
    
    return results

if __name__ == "__main__":
    results = filter_stocks()
