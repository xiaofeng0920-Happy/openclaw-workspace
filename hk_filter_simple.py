#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股全市场筛选 - 锋哥五好标准
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import time
import warnings

warnings.filterwarnings('ignore')

def get_active_hk_stocks():
    """获取活跃港股"""
    print("正在获取港股实时数据...")
    df = ak.stock_hk_spot_em()
    print(f"共获取到 {len(df)} 只港股")
    
    # 筛选成交额 > 1000 万
    df_active = df[df['成交额'] > 10000000].copy()
    print(f"成交额>1000 万的活跃股票：{len(df_active)} 只")
    df_active = df_active.sort_values('成交额', ascending=False)
    return df_active

def get_financials(symbol):
    """获取财务指标"""
    try:
        df = ak.stock_financial_hk_analysis_indicator_em(symbol=symbol)
        if df is None or df.empty:
            return None
        df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'])
        return df
    except Exception as e:
        print(f"  获取财务数据异常：{e}")
        return None

def check_stock(symbol, name, price):
    """检查单只股票"""
    df_fina = get_financials(symbol)
    if df_fina is None:
        return None, "财务数据缺失"
    
    # 获取最新 EPS_TTM
    latest = df_fina.sort_values('REPORT_DATE', ascending=False).iloc[0]
    eps_ttm = latest.get('EPS_TTM')
    
    if pd.isna(eps_ttm) or eps_ttm <= 0:
        return None, f"EPS 无效"
    
    # 计算 PE
    pe = price / eps_ttm
    if pe >= 30:
        return None, f"PE={pe:.1f}"
    
    # 获取过去 5 年数据
    current_year = datetime.now().year
    years_needed = list(range(current_year - 5, current_year))
    
    yearly_data = {}
    for year in years_needed:
        year_df = df_fina[df_fina['REPORT_DATE'].dt.year == year]
        if not year_df.empty:
            latest_year = year_df.sort_values('REPORT_DATE', ascending=False).iloc[0]
            yearly_data[year] = latest_year
    
    if len(yearly_data) < 5:
        return None, f"年份不足{len(yearly_data)}/5"
    
    # 检查 ROE
    roe_ok = True
    roe_values = []
    for year in sorted(yearly_data.keys()):
        roe = yearly_data[year].get('ROE_YEARLY')
        if not pd.isna(roe):
            roe_values.append((year, float(roe)))
            if roe <= 5:
                roe_ok = False
    
    if len(roe_values) < 5 or not roe_ok:
        return None, "ROE 不达标"
    
    # 检查 ROIC
    roic_ok = True
    roic_values = []
    for year in sorted(yearly_data.keys()):
        roic = yearly_data[year].get('ROIC_YEARLY')
        if not pd.isna(roic):
            roic_values.append((year, float(roic)))
            if roic <= 5:
                roic_ok = False
    
    if len(roic_values) < 5 or not roic_ok:
        return None, "ROIC 不达标"
    
    # 检查负债率
    debt_values = []
    for year in sorted(yearly_data.keys()):
        debt = yearly_data[year].get('DEBT_ASSET_RATIO')
        if not pd.isna(debt):
            debt_values.append((year, float(debt)))
    
    if not debt_values or debt_values[-1][1] >= 50:
        return None, "负债率过高"
    
    # 检查现金流
    fcf_ok = True
    for year in sorted(yearly_data.keys()):
        fcf = yearly_data[year].get('PER_NETCASH_OPERATE')
        if not pd.isna(fcf) and fcf <= 0:
            fcf_ok = False
    
    if not fcf_ok:
        return None, "现金流为负"
    
    avg_roe = sum([v[1] for v in roe_values[-5:]]) / 5
    avg_roic = sum([v[1] for v in roic_values[-5:]]) / 5
    avg_debt = sum([v[1] for v in debt_values[-5:]]) / 5
    
    return {
        '代码': symbol,
        '名称': name,
        '股价': round(price, 2),
        'PE': round(pe, 1),
        'ROE_5y': round(avg_roe, 2),
        'ROIC_5y': round(avg_roic, 2),
        '负债率': round(avg_debt, 2)
    }, "OK"

def main():
    print("=" * 70)
    print("港股全市场筛选 - 锋哥五好标准")
    print("=" * 70)
    
    df_active = get_active_hk_stocks()
    if df_active.empty:
        return
    
    passed = []
    failed = {}
    
    test_count = min(50, len(df_active))
    print(f"\n开始筛选前{test_count}只...\n")
    
    for idx in range(test_count):
        row = df_active.iloc[idx]
        symbol = str(row['代码']).zfill(6)
        name = row['名称']
        price = row['最新价']
        
        print(f"[{idx+1}] {symbol} {name}...", end=" ")
        
        try:
            result, status = check_stock(symbol, name, price)
            if result:
                passed.append(result)
                print(f"✅ {status}")
            else:
                print(f"❌ {status}")
                failed[status] = failed.get(status, 0) + 1
        except Exception as e:
            print(f"⚠️ {e}")
            failed['异常'] = failed.get('异常', 0) + 1
        
        if (idx + 1) % 10 == 0:
            time.sleep(2)
    
    print("\n" + "=" * 70)
    print(f"检查：{test_count} | 符合：{len(passed)}")
    
    if passed:
        print("\n✅ 符合的港股：")
        df_result = pd.DataFrame(passed)
        print(df_result.to_string(index=False))
        df_result.to_csv('/home/admin/openclaw/workspace/hk_filtered.csv', index=False)
    else:
        print("\n❌ 无符合股票")
    
    if failed:
        print("\n失败原因：")
        for k, v in sorted(failed.items(), key=lambda x: -x[1])[:5]:
            print(f"  {k}: {v}")
    print("=" * 70)

if __name__ == '__main__':
    main()
