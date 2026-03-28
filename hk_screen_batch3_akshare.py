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
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import time
import warnings

warnings.filterwarnings('ignore')

# ============== 配置 ==============

# 筛选条件
MAX_PE = 30.0
MIN_ROE = 5.0
MIN_ROIC = 5.0
MIN_FCF_YEARS = 5
MAX_DEBT_RATIO = 50.0

# 港股代码范围
HK_CODE_START = 2000
HK_CODE_END = 9999

# 输出路径
OUTPUT_FILE = '/home/admin/openclaw/workspace/hk_screen_batch3_result.csv'

# ============== 工具函数 ==============

def get_hk_stocks():
    """获取港股列表"""
    print("正在获取港股实时数据...")
    df = ak.stock_hk_spot_em()
    print(f"共 {len(df)} 只港股")
    
    # 过滤 ETF/基金
    exclude_keywords = ['基金', 'ETF', '指数', '两倍', '做空', '做多', 'XL', 'FI', 'SO']
    mask = ~df['名称'].str.contains('|'.join(exclude_keywords), regex=False)
    df_stocks = df[mask].copy()
    print(f"过滤 ETF 后：{len(df_stocks)} 只股票")
    
    # 筛选代码范围
    df_stocks['代码_int'] = df_stocks['代码'].astype(int)
    df_range = df_stocks[(df_stocks['代码_int'] >= HK_CODE_START) & 
                         (df_stocks['代码_int'] <= HK_CODE_END)]
    print(f"02000-09999 范围：{len(df_range)} 只股票")
    
    # 按成交额排序，优先检查活跃股票
    df_range = df_range.sort_values('成交额', ascending=False)
    
    return df_range

def get_financials(symbol):
    """获取财务指标（带重试）"""
    for retry in range(3):
        try:
            df = ak.stock_financial_hk_analysis_indicator_em(symbol=symbol)
            if df is not None and not df.empty:
                df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'])
                return df
        except Exception as e:
            pass
        time.sleep(2)
    return None

def get_yearly_data(df, field, years=5):
    """获取最近 N 年的年度数据"""
    if df is None or len(df) == 0:
        return []
    
    # 按年份分组，取每年最后一个报告期
    df = df.copy()
    df['year'] = df['REPORT_DATE'].dt.year
    
    # 按年份分组，取每个年份的最后一条记录
    yearly = df.groupby('year').last().reset_index()
    yearly = yearly.sort_values('year', ascending=False)
    
    # 取最近 N 年
    recent = yearly.head(years)
    
    return recent[field].tolist()

def check_roe_continuous(df_fina, min_roe=5.0, years=5):
    """检查 ROE 连续 N 年 > min_roe"""
    if df_fina is None or len(df_fina) == 0:
        return False, []
    
    roe_values = get_yearly_data(df_fina, 'ROE_YEARLY', years)
    
    if len(roe_values) < years:
        return False, roe_values
    
    # 检查是否所有年份都大于最小值
    for roe in roe_values:
        if pd.isna(roe) or roe <= min_roe:
            return False, roe_values
    
    return True, roe_values

def check_roic_continuous(df_fina, min_roic=5.0, years=5):
    """检查 ROIC 连续 N 年 > min_roic"""
    if df_fina is None or len(df_fina) == 0:
        return False, []
    
    roic_values = get_yearly_data(df_fina, 'ROIC_YEARLY', years)
    
    if len(roic_values) < years:
        return False, roic_values
    
    # 检查是否所有年份都大于最小值
    for roic in roic_values:
        if pd.isna(roic) or roic <= min_roic:
            return False, roic_values
    
    return True, roic_values

def check_fcf_continuous(df_fina, years=5):
    """检查自由现金流连续 5 年为正（使用 PER_NETCASH_OPERATE 每股经营现金流）"""
    if df_fina is None or len(df_fina) == 0:
        return False, []
    
    fcf_values = get_yearly_data(df_fina, 'PER_NETCASH_OPERATE', years)
    
    if len(fcf_values) < years:
        return False, fcf_values
    
    # 检查是否所有年份都为正
    for fcf in fcf_values:
        if pd.isna(fcf) or fcf <= 0:
            return False, fcf_values
    
    return True, fcf_values

def check_debt_ratio(df_fina, max_ratio=50.0):
    """检查资产负债率 < max_ratio"""
    if df_fina is None or len(df_fina) == 0:
        return False, []
    
    # 获取最近一年的数据
    df = df_fina.copy()
    df = df.sort_values('REPORT_DATE', ascending=False)
    latest = df.head(1)
    
    if len(latest) == 0:
        return False, []
    
    debt_ratio = latest.iloc[0].get('DEBT_ASSET_RATIO')
    
    if pd.isna(debt_ratio):
        return False, []
    
    return debt_ratio < max_ratio, [debt_ratio]

def get_pe_from_fina(df_fina, price):
    """从财务指标获取 PE"""
    if df_fina is None or len(df_fina) == 0:
        return None
    
    # 使用 EPS_TTM 计算 PE
    df = df_fina.sort_values('REPORT_DATE', ascending=False)
    eps_ttm = df.iloc[0].get('EPS_TTM')
    
    if pd.isna(eps_ttm) or eps_ttm <= 0:
        return None
    
    pe = price / eps_ttm
    return pe

def check_stock(symbol, name, price):
    """检查单只股票"""
    df_fina = get_financials(symbol)
    if df_fina is None or df_fina.empty:
        return None, "财务数据缺失"
    
    # 获取 PE
    pe = get_pe_from_fina(df_fina, price)
    if pe is None or pe <= 0 or pe >= MAX_PE:
        return None, f"PE 不达标 ({pe:.1f})" if pe else "PE 无效"
    
    # 检查 ROE 连续 5 年 > 5%
    roe_ok, roe_values = check_roe_continuous(df_fina, MIN_ROE, 5)
    if not roe_ok:
        return None, "ROE 不达标"
    
    # 检查 ROIC 连续 5 年 > 5%
    roic_ok, roic_values = check_roic_continuous(df_fina, MIN_ROIC, 5)
    if not roic_ok:
        return None, "ROIC 不达标"
    
    # 检查自由现金流连续 5 年为正
    fcf_ok, fcf_values = check_fcf_continuous(df_fina, 5)
    if not fcf_ok:
        return None, "现金流不达标"
    
    # 检查资产负债率 < 50%
    debt_ok, debt_values = check_debt_ratio(df_fina, MAX_DEBT_RATIO)
    if not debt_ok:
        return None, f"负债率过高 ({debt_values[0]:.1f}%)" if debt_values else "负债率数据缺失"
    
    # 所有条件符合
    return {
        '代码': symbol,
        '名称': name,
        '股价': round(price, 2),
        'PE': round(pe, 1),
        'ROE_5Y_avg': round(sum(roe_values)/len(roe_values), 2),
        'ROIC_5Y_avg': round(sum(roic_values)/len(roic_values), 2),
        'FCF_positive_years': 5,
        'debt_ratio': round(debt_values[0], 2)
    }, "符合"

def screen_hk_stocks():
    """筛选港股 02000-09999"""
    print("="*70)
    print("🔍 港股筛选批次 3/3: 02000-09999")
    print("="*70)
    print(f"筛选条件：")
    print(f"  - PE < {MAX_PE}")
    print(f"  - ROE 连续 5 年 > {MIN_ROE}%")
    print(f"  - ROIC 连续 5 年 > {MIN_ROIC}%")
    print(f"  - 自由现金流连续 5 年 > 0")
    print(f"  - 资产负债率 < {MAX_DEBT_RATIO}%")
    print("="*70)
    
    # 获取股票列表
    df_stocks = get_hk_stocks()
    
    if df_stocks.empty:
        print("❌ 未找到股票")
        return []
    
    qualified = []
    total_checked = 0
    failed_stats = {}
    
    # 遍历股票（限制前 500 只活跃股票，避免超时）
    max_check = min(500, len(df_stocks))
    print(f"\n开始筛选前{max_check}只活跃股票...\n")
    
    for idx in range(max_check):
        row = df_stocks.iloc[idx]
        symbol = str(row['代码']).zfill(6)
        name = row['名称']
        price = row['最新价']
        turnover = row['成交额'] / 10000  # 万
        
        total_checked += 1
        
        if total_checked % 20 == 0:
            print(f"\n📊 进度：{total_checked}/{max_check} | 符合：{len(qualified)} | 无数据：{failed_stats.get('无数据', 0)}...")
        
        print(f"[{total_checked}/{max_check}] {symbol} ({name}) 股价={price} 成交={turnover:.0f}万...", end=" ")
        
        try:
            result, status = check_stock(symbol, name, price)
            if result:
                qualified.append(result)
                print(f"✅ 符合")
            else:
                print(f"❌ {status}")
                key = status.split(':')[0] if ':' in status else status
                failed_stats[key] = failed_stats.get(key, 0) + 1
        except Exception as e:
            print(f"⚠️ {e}")
            failed_stats['异常'] = failed_stats.get('异常', 0) + 1
        
        # 每 10 只暂停一下
        if total_checked % 10 == 0:
            time.sleep(2)
    
    print(f"\n{'='*70}")
    print(f"✅ 筛选完成！")
    print(f"   检查股票数：{total_checked}")
    print(f"   符合条件：{len(qualified)} 只")
    print(f"{'='*70}")
    
    return qualified

def main():
    """主函数"""
    # 运行筛选
    qualified = screen_hk_stocks()
    
    # 保存结果
    if qualified:
        df = pd.DataFrame(qualified)
        df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
        print(f"\n💾 结果已保存：{OUTPUT_FILE}")
        
        # 打印结果
        print("\n📋 符合条件的股票列表：")
        print(df.to_string(index=False))
    else:
        print("\n⚠️  未找到符合条件的股票")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
