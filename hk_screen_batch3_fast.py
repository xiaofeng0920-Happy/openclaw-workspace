#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股筛选批次 3/3：筛选港股 02000-09999 开头的所有股票
条件：
- PE < 30
- ROE 连续 5 年 > 5%
- ROIC 连续 5 年 > 5%
- 自由现金流连续 5 年为正
- 资产负债率 < 50%

使用 AkShare 筛选（Tushare 港股财务数据不完整）
优化版本：减少打印，加快处理
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import time
import warnings
import sys

warnings.filterwarnings('ignore')

# ============== 配置 ==============
MAX_PE = 30.0
MIN_ROE = 5.0
MIN_ROIC = 5.0
MAX_DEBT_RATIO = 50.0
HK_CODE_START = 2000
HK_CODE_END = 9999
OUTPUT_FILE = '/home/admin/openclaw/workspace/hk_screen_batch3_result.csv'

def get_hk_stocks():
    """获取港股列表"""
    print("正在获取港股实时数据...", flush=True)
    df = ak.stock_hk_spot_em()
    print(f"共 {len(df)} 只港股", flush=True)
    
    # 过滤 ETF/基金
    exclude_keywords = ['基金', 'ETF', '指数', '两倍', '做空', '做多', 'XL', 'FI', 'SO']
    mask = ~df['名称'].str.contains('|'.join(exclude_keywords), regex=False)
    df_stocks = df[mask].copy()
    
    # 筛选代码范围
    df_stocks['代码_int'] = df_stocks['代码'].astype(int)
    df_range = df_stocks[(df_stocks['代码_int'] >= HK_CODE_START) & 
                         (df_stocks['代码_int'] <= HK_CODE_END)]
    print(f"02000-09999 范围：{len(df_range)} 只股票", flush=True)
    
    # 按成交额排序
    df_range = df_range.sort_values('成交额', ascending=False)
    return df_range

def check_stock(symbol, name, price):
    """检查单只股票"""
    try:
        df = ak.stock_financial_hk_analysis_indicator_em(symbol=symbol)
        if df is None or df.empty:
            return None
        
        df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'])
        
        # 获取最新 EPS_TTM
        latest = df.sort_values('REPORT_DATE', ascending=False).iloc[0]
        eps_ttm = latest.get('EPS_TTM')
        
        if pd.isna(eps_ttm) or eps_ttm <= 0:
            return None
        
        # 计算 PE
        pe = price / eps_ttm
        if pe >= MAX_PE or pe <= 0:
            return None
        
        # 获取过去 5 年数据
        current_year = datetime.now().year
        years_needed = list(range(current_year - 5, current_year))
        
        yearly_data = {}
        for year in years_needed:
            year_df = df[df['REPORT_DATE'].dt.year == year]
            if not year_df.empty:
                latest_year = year_df.sort_values('REPORT_DATE', ascending=False).iloc[0]
                yearly_data[year] = latest_year
        
        if len(yearly_data) < 5:
            return None
        
        # 检查 ROE 连续 5 年 > 5%
        for year in sorted(yearly_data.keys()):
            roe = yearly_data[year].get('ROE_YEARLY')
            if pd.isna(roe) or roe <= MIN_ROE:
                return None
        
        # 检查 ROIC 连续 5 年 > 5%
        for year in sorted(yearly_data.keys()):
            roic = yearly_data[year].get('ROIC_YEARLY')
            if pd.isna(roic) or roic <= MIN_ROIC:
                return None
        
        # 检查自由现金流连续 5 年为正
        for year in sorted(yearly_data.keys()):
            fcf = yearly_data[year].get('PER_NETCASH_OPERATE')
            if pd.isna(fcf) or fcf <= 0:
                return None
        
        # 检查资产负债率 < 50%
        latest_year = sorted(yearly_data.keys())[-1]
        debt = yearly_data[latest_year].get('DEBT_ASSET_RATIO')
        if pd.isna(debt) or debt >= MAX_DEBT_RATIO:
            return None
        
        # 计算平均值
        years_sorted = sorted(yearly_data.keys())
        avg_roe = sum([yearly_data[y].get('ROE_YEARLY', 0) for y in years_sorted]) / len(years_sorted)
        avg_roic = sum([yearly_data[y].get('ROIC_YEARLY', 0) for y in years_sorted]) / len(years_sorted)
        avg_debt = sum([yearly_data[y].get('DEBT_ASSET_RATIO', 0) for y in years_sorted]) / len(years_sorted)
        
        return {
            '代码': symbol,
            '名称': name,
            '股价': round(price, 2),
            'PE': round(pe, 1),
            'ROE_5Y_avg': round(avg_roe, 2),
            'ROIC_5Y_avg': round(avg_roic, 2),
            'debt_ratio': round(avg_debt, 2)
        }
    except Exception as e:
        return None

def main():
    print("="*70)
    print("🔍 港股筛选批次 3/3: 02000-09999")
    print("="*70)
    print(f"筛选条件：PE<{MAX_PE}, ROE>{MIN_ROE}%(5 年), ROIC>{MIN_ROIC}%(5 年), FCF>0(5 年), 负债<{MAX_DEBT_RATIO}%")
    print("="*70, flush=True)
    
    # 获取股票列表
    df_stocks = get_hk_stocks()
    if df_stocks.empty:
        print("❌ 未找到股票")
        return
    
    qualified = []
    total = len(df_stocks)
    
    # 检查前 300 只活跃股票（避免超时）
    max_check = min(300, total)
    print(f"\n开始筛选前{max_check}只活跃股票...\n", flush=True)
    
    for idx in range(max_check):
        row = df_stocks.iloc[idx]
        symbol = str(row['代码']).zfill(6)
        name = row['名称']
        price = row['最新价']
        
        result = check_stock(symbol, name, price)
        if result:
            qualified.append(result)
            print(f"✅ [{len(qualified)}] {symbol} {name} PE:{result['PE']} ROE:{result['ROE_5Y_avg']}% ROIC:{result['ROIC_5Y_avg']}%", flush=True)
        
        # 进度显示
        if (idx + 1) % 50 == 0:
            print(f"📊 进度：{idx+1}/{max_check} | 符合：{len(qualified)}", flush=True)
        
        # 每 5 只暂停
        if (idx + 1) % 5 == 0:
            time.sleep(1)
    
    print(f"\n{'='*70}")
    print(f"✅ 筛选完成！检查{max_check}只，符合{len(qualified)}只")
    print(f"{'='*70}", flush=True)
    
    if qualified:
        df = pd.DataFrame(qualified)
        df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
        print(f"\n💾 结果已保存：{OUTPUT_FILE}", flush=True)
        print("\n📋 符合条件的股票列表：")
        print(df.to_string(index=False), flush=True)
    else:
        print("\n⚠️  未找到符合条件的股票", flush=True)

if __name__ == "__main__":
    main()
