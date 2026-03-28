#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股筛选批次 2/3：筛选港股 00800-01999 开头的所有股票
条件：
- PE < 30
- ROE 连续 5 年 > 5%
- ROIC 连续 5 年 > 5%
- 经营现金流连续 5 年为正
- 资产负债率 < 50%

使用 AkShare 筛选
"""

import sys
import time
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

try:
    import akshare as ak
except ImportError:
    print("❌ 请安装 akshare: pip install akshare")
    sys.exit(1)

# ============== 配置 ==============

# 输出路径
OUTPUT_DIR = Path('/home/admin/openclaw/workspace/agents/data-collector/tushare_data')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 筛选条件
MAX_PE = 30.0
MIN_ROE = 5.0
MIN_ROIC = 5.0
MIN_FCF_YEARS = 5
MAX_DEBT_RATIO = 50.0

# 港股代码范围
HK_CODE_START = 800
HK_CODE_END = 1999

# ============== 工具函数 ==============

def get_hk_stocks():
    """获取港股列表"""
    try:
        df = ak.stock_hk_spot_em()
        # 提取股票代码数字部分
        df['code_int'] = df['代码'].astype(int)
        # 筛选 00800-01999 范围
        df_range = df[(df['code_int'] >= HK_CODE_START) & 
                      (df['code_int'] <= HK_CODE_END)]
        return df_range
    except Exception as e:
        print(f"❌ 获取港股列表失败：{e}")
        return None

def get_financial_data(symbol):
    """获取港股财务分析指标"""
    try:
        symbol_clean = str(int(symbol))
        df = ak.stock_financial_hk_analysis_indicator_em(symbol=symbol_clean)
        
        if df is None or len(df) == 0:
            return None
        
        df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'])
        df = df.sort_values('REPORT_DATE', ascending=False)
        
        return df
    except Exception as e:
        return None

def get_pe(symbol):
    """获取 PE"""
    try:
        symbol_clean = str(int(symbol))
        df = ak.stock_hk_financial_indicator_em(symbol=symbol_clean)
        
        if df is not None and len(df) > 0:
            if '市盈率' in df.columns:
                pe = df.iloc[0]['市盈率']
                if pd.notna(pe) and pe > 0:
                    return pe
    except Exception as e:
        pass
    
    return None

def check_roe_continuous(df, min_roe=5.0, years=5):
    """检查 ROE 连续 N 年 > min_roe"""
    if df is None or len(df) == 0:
        return False, []
    
    df = df.copy()
    df['year'] = df['REPORT_DATE'].dt.year
    yearly = df.groupby('year').first().reset_index()
    yearly = yearly.sort_values('year', ascending=False)
    recent = yearly.head(years)
    
    if len(recent) < years:
        return False, []
    
    if 'ROE_YEARLY' not in recent.columns:
        return False, []
    
    roe_values = recent['ROE_YEARLY'].tolist()
    
    for roe in roe_values:
        if pd.isna(roe) or roe <= min_roe:
            return False, roe_values
    
    return True, roe_values

def check_roic_continuous(df, min_roic=5.0, years=5):
    """检查 ROIC 连续 N 年 > min_roic"""
    if df is None or len(df) == 0:
        return False, []
    
    df = df.copy()
    df['year'] = df['REPORT_DATE'].dt.year
    yearly = df.groupby('year').first().reset_index()
    yearly = yearly.sort_values('year', ascending=False)
    recent = yearly.head(years)
    
    if len(recent) < years:
        return False, []
    
    if 'ROIC_YEARLY' not in recent.columns:
        return False, []
    
    roic_values = recent['ROIC_YEARLY'].tolist()
    
    for roic in roic_values:
        if pd.isna(roic) or roic <= min_roic:
            return False, roic_values
    
    return True, roic_values

def check_debt_ratio(df, max_ratio=50.0):
    """检查资产负债率 < max_ratio"""
    if df is None or len(df) == 0:
        return False, None
    
    latest = df.iloc[0]
    
    if 'DEBT_ASSET_RATIO' not in latest.index:
        return False, None
    
    debt_ratio = latest['DEBT_ASSET_RATIO']
    
    if pd.isna(debt_ratio):
        return False, None
    
    return debt_ratio < max_ratio, debt_ratio

def check_fcf_continuous(df, years=5):
    """检查经营现金流连续 5 年为正"""
    if df is None or len(df) == 0:
        return False, []
    
    df = df.copy()
    df['year'] = df['REPORT_DATE'].dt.year
    yearly = df.groupby('year').first().reset_index()
    yearly = yearly.sort_values('year', ascending=False)
    recent = yearly.head(years)
    
    if len(recent) < years:
        return False, []
    
    if 'PER_NETCASH_OPERATE' not in recent.columns:
        return False, []
    
    fcf_values = recent['PER_NETCASH_OPERATE'].tolist()
    
    for fcf in fcf_values:
        if pd.isna(fcf) or fcf <= 0:
            return False, fcf_values
    
    return True, fcf_values

def screen_hk_stocks():
    """筛选港股 00800-01999"""
    print("="*60)
    print("🔍 港股筛选批次 2/3:00800-01999")
    print("="*60)
    print(f"筛选条件：")
    print(f"  - PE < {MAX_PE}")
    print(f"  - ROE 连续 5 年 > {MIN_ROE}%")
    print(f"  - ROIC 连续 5 年 > {MIN_ROIC}%")
    print(f"  - 经营现金流连续 5 年 > 0")
    print(f"  - 资产负债率 < {MAX_DEBT_RATIO}%")
    print("="*60)
    
    # 获取港股列表
    print("\n📥 获取港股列表...")
    df_hk = get_hk_stocks()
    
    if df_hk is None:
        print("❌ 获取港股列表失败")
        return []
    
    print(f"   00800-01999 范围：{len(df_hk)} 只股票")
    
    qualified = []
    total_checked = 0
    skipped_no_data = 0
    skipped_pe = 0
    skipped_pe_neg = 0
    skipped_roe = 0
    skipped_roic = 0
    skipped_debt = 0
    skipped_fcf = 0
    
    # 遍历股票
    for idx, row in df_hk.iterrows():
        symbol = row['代码']
        name = row['名称']
        
        total_checked += 1
        
        if total_checked % 50 == 0:
            print(f"\n📊 已检查 {total_checked}/{len(df_hk)} 只股票，"
                  f"符合{len(qualified)}只，"
                  f"PE{skipped_pe}(负{skipped_pe_neg})/ROE{skipped_roe}/ROIC{skipped_roic}/负债{skipped_debt}/现金流{skipped_fcf}/无数据{skipped_no_data}...")
        
        # 获取 PE
        pe = get_pe(symbol)
        if pe is None:
            skipped_pe += 1
            continue
        if pe <= 0:
            skipped_pe_neg += 1
            continue
        if pe >= MAX_PE:
            skipped_pe += 1
            continue
        
        # 获取财务数据
        df_fina = get_financial_data(symbol)
        
        if df_fina is None or len(df_fina) == 0:
            skipped_no_data += 1
            continue
        
        # 检查 ROE 连续 5 年 > 5%
        roe_ok, roe_values = check_roe_continuous(df_fina, MIN_ROE, 5)
        if not roe_ok:
            skipped_roe += 1
            continue
        
        # 检查 ROIC 连续 5 年 > 5%
        roic_ok, roic_values = check_roic_continuous(df_fina, MIN_ROIC, 5)
        if not roic_ok:
            skipped_roic += 1
            continue
        
        # 检查资产负债率 < 50%
        debt_ok, debt_ratio = check_debt_ratio(df_fina, MAX_DEBT_RATIO)
        if not debt_ok:
            skipped_debt += 1
            continue
        
        # 检查经营现金流连续 5 年为正
        fcf_ok, fcf_values = check_fcf_continuous(df_fina, 5)
        if not fcf_ok:
            skipped_fcf += 1
            continue
        
        # 所有条件符合
        qualified.append({
            '代码': symbol,
            '名称': name,
            'PE': round(pe, 2),
            'ROE_5Y_avg': round(sum(roe_values)/len(roe_values), 2),
            'ROIC_5Y_avg': round(sum(roic_values)/len(roic_values), 2),
            '现金流_5Y': '连续为正',
            '负债率': round(debt_ratio, 2)
        })
        
        print(f"✅ [{len(qualified)}] {symbol} {name} - PE:{pe:.1f} ROE:{roe_values[0]:.1f}% ROIC:{roic_values[0]:.1f}% 负债:{debt_ratio:.1f}%")
        
        # 避免请求过快
        time.sleep(0.2)
    
    print(f"\n{'='*60}")
    print(f"✅ 筛选完成！")
    print(f"   检查股票数：{total_checked}")
    print(f"   符合条件：{len(qualified)} 只")
    print(f"   筛选掉：PE{skipped_pe}(负{skipped_pe_neg})/ROE{skipped_roe}/ROIC{skipped_roic}/负债{skipped_debt}/现金流{skipped_fcf}/无数据{skipped_no_data}")
    print(f"{'='*60}")
    
    return qualified

def main():
    """主函数"""
    # 运行筛选
    qualified = screen_hk_stocks()
    
    # 保存结果
    if qualified:
        df = pd.DataFrame(qualified)
        csv_file = OUTPUT_DIR / f'hk_screen_batch2_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 结果已保存：{csv_file}")
        
        # 打印结果
        print("\n📋 符合条件的股票列表：")
        print(df.to_string(index=False))
    else:
        print("\n⚠️  未找到符合条件的股票")

if __name__ == "__main__":
    main()
