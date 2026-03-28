#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股筛选脚本 - 批次 1/3 (00001-00799)
筛选条件:
- PE < 30
- ROE 连续 5 年 > 5%
- ROIC 连续 5 年 > 5%
- 自由现金流连续 5 年为正
- 资产负债率 < 50%
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
    return filtered['代码'].tolist()

def get_financial_indicator(symbol):
    """获取单只股票的财务指标"""
    try:
        # 获取港股财务指标
        df = ak.stock_hk_financial_indicator_em(symbol=symbol)
        return df
    except Exception as e:
        return None

def get_hk_stock_fund_flow(symbol):
    """获取港股资金流向（包含 PE 等指标）"""
    try:
        df = ak.stock_hk_fund_flow_em(symbol=symbol)
        return df
    except:
        return None

def get_hk_stock_pe_pb(symbol):
    """获取港股 PE/PB 数据"""
    try:
        # 获取港股估值数据
        df = ak.stock_hk_valuation_em(symbol=symbol)
        return df
    except:
        return None

def get_stock_basic_info(symbol):
    """获取股票基本信息"""
    try:
        df = ak.stock_profile_cninfo(symbol=symbol)
        return df
    except:
        return None

def filter_stocks():
    """主筛选函数"""
    print("=" * 60)
    print("港股筛选 - 批次 1/3 (00001-00799)")
    print("筛选条件:")
    print("  - PE < 30")
    print("  - ROE 连续 5 年 > 5%")
    print("  - ROIC 连续 5 年 > 5%")
    print("  - 自由现金流连续 5 年为正")
    print("  - 资产负债率 < 50%")
    print("=" * 60)
    
    # 获取股票列表
    stock_codes = get_hk_stocks_in_range()
    print(f"\n开始筛选 {len(stock_codes)} 只股票...\n")
    
    results = []
    processed = 0
    
    for code in stock_codes:
        processed += 1
        if processed % 50 == 0:
            print(f"进度: {processed}/{len(stock_codes)} ({processed/len(stock_codes)*100:.1f}%)")
        
        try:
            # 获取财务指标
            financial_df = get_financial_indicator(code)
            
            if financial_df is None or len(financial_df) == 0:
                continue
            
            # 获取估值数据 (PE)
            valuation_df = get_hk_stock_pe_pb(code)
            
            # 检查最新 PE
            current_pe = None
            if valuation_df is not None and len(valuation_df) > 0:
                if '市盈率' in valuation_df.columns:
                    current_pe = valuation_df.iloc[-1]['市盈率']
                elif 'PE(TTM)' in valuation_df.columns:
                    current_pe = valuation_df.iloc[-1]['PE(TTM)']
            
            # 如果没有 PE 数据，跳过
            if current_pe is None or pd.isna(current_pe) or current_pe <= 0:
                continue
            
            # 检查 PE < 30
            if current_pe >= 30:
                continue
            
            # 检查财务指标 (ROE, ROIC, 自由现金流，资产负债率)
            # 需要检查最近 5 年的数据
            if len(financial_df) < 5:
                continue
            
            # 按报告期排序
            financial_df = financial_df.sort_values('报告期', ascending=False)
            recent_5 = financial_df.head(5)
            
            if len(recent_5) < 5:
                continue
            
            # 检查 ROE 连续 5 年 > 5%
            roe_col = None
            for col in ['净资产收益率 (%)', 'ROE', '净资产收益率']:
                if col in recent_5.columns:
                    roe_col = col
                    break
            
            if roe_col is None:
                continue
            
            roe_values = pd.to_numeric(recent_5[roe_col], errors='coerce')
            if not all(roe_values > 5):
                continue
            
            # 检查 ROIC 连续 5 年 > 5%
            roic_col = None
            for col in ['投入资本回报率 (%)', 'ROIC', '投入资本回报率']:
                if col in recent_5.columns:
                    roic_col = col
                    break
            
            if roic_col is None:
                continue
            
            roic_values = pd.to_numeric(recent_5[roic_col], errors='coerce')
            if not all(roic_values > 5):
                continue
            
            # 检查自由现金流连续 5 年为正
            fcf_col = None
            for col in ['自由现金流', '自由现金流 (元)', '经营活动产生的现金流量净额']:
                if col in recent_5.columns:
                    fcf_col = col
                    break
            
            if fcf_col is None:
                continue
            
            fcf_values = pd.to_numeric(recent_5[fcf_col], errors='coerce')
            if not all(fcf_values > 0):
                continue
            
            # 检查资产负债率 < 50%
            debt_col = None
            for col in ['资产负债率 (%)', '资产负债率']:
                if col in recent_5.columns:
                    debt_col = col
                    break
            
            if debt_col is None:
                continue
            
            debt_values = pd.to_numeric(recent_5[debt_col], errors='coerce')
            if not all(debt_values < 50):
                continue
            
            # 获取股票名称
            stock_name = hk_df[hk_df['代码'] == code]['名称'].values
            stock_name = stock_name[0] if len(stock_name) > 0 else "未知"
            
            # 符合条件，添加到结果
            results.append({
                '代码': code,
                '名称': stock_name,
                'PE': round(current_pe, 2),
                '最新 ROE(%)': round(roe_values.iloc[0], 2),
                '最新 ROIC(%)': round(roic_values.iloc[0], 2),
                '最新自由现金流': round(fcf_values.iloc[0], 2),
                '最新资产负债率 (%)': round(debt_values.iloc[0], 2)
            })
            
            print(f"✓ 发现符合条件股票: {code} {stock_name} (PE={current_pe:.2f})")
            
            time.sleep(0.3)  # 避免请求过快
            
        except Exception as e:
            continue
    
    # 输出结果
    print("\n" + "=" * 60)
    print(f"筛选完成! 共找到 {len(results)} 只符合条件的股票")
    print("=" * 60)
    
    if len(results) > 0:
        result_df = pd.DataFrame(results)
        print("\n符合条件的股票列表:")
        print(result_df.to_string(index=False))
        
        # 保存到文件
        result_df.to_csv('/home/admin/openclaw/workspace/hk_filtered_stocks_batch1.csv', index=False, encoding='utf-8-sig')
        print(f"\n结果已保存到: hk_filtered_stocks_batch1.csv")
    
    return results

if __name__ == "__main__":
    # 先获取港股列表
    hk_df = ak.stock_hk_spot_em()
    
    results = filter_stocks()
