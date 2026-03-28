#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股全市场筛选 - 锋哥五好标准（最终版）
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import time
import warnings

warnings.filterwarnings('ignore')

def get_hk_stocks():
    """获取港股列表"""
    print("正在获取港股数据...")
    df = ak.stock_hk_spot_em()
    print(f"共 {len(df)} 只港股")
    
    # 过滤 ETF/基金（名称包含"基金"、"ETF"、"指数"等）
    exclude_keywords = ['基金', 'ETF', '指数', '两倍', '做空', '做多', 'XL', 'FI', 'SO']
    mask = ~df['名称'].str.contains('|'.join(exclude_keywords), regex=False)
    df_stocks = df[mask].copy()
    print(f"过滤 ETF 后：{len(df_stocks)} 只股票")
    
    # 按成交额排序
    df_stocks = df_stocks.sort_values('成交额', ascending=False)
    return df_stocks

def get_financials(symbol):
    """获取财务指标（带重试）"""
    for retry in range(3):
        try:
            df = ak.stock_financial_hk_analysis_indicator_em(symbol=symbol)
            if df is not None and not df.empty:
                df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'])
                return df
        except:
            pass
        time.sleep(2)
    return None

def check_stock(symbol, name, price):
    """检查股票"""
    df = get_financials(symbol)
    if df is None:
        return None, "无财务数据"
    
    # 获取最新 EPS
    latest = df.sort_values('REPORT_DATE', ascending=False).iloc[0]
    eps = latest.get('EPS_TTM')
    if pd.isna(eps) or eps <= 0:
        return None, "EPS 无效"
    
    # 计算 PE
    pe = price / eps
    if pe >= 30:
        return None, f"PE={pe:.0f}"
    
    # 获取 5 年数据
    current_year = datetime.now().year
    years_data = {}
    for year in range(current_year - 5, current_year):
        ydf = df[df['REPORT_DATE'].dt.year == year]
        if not ydf.empty:
            years_data[year] = ydf.sort_values('REPORT_DATE', ascending=False).iloc[0]
    
    if len(years_data) < 5:
        return None, f"数据{len(years_data)}/5 年"
    
    # 检查 ROE
    roe_vals = []
    for y in sorted(years_data.keys()):
        roe = years_data[y].get('ROE_YEARLY')
        if not pd.isna(roe):
            roe_vals.append(roe)
            if roe <= 5:
                return None, "ROE<5%"
    if len(roe_vals) < 5:
        return None, "ROE 数据不足"
    
    # 检查 ROIC
    roic_vals = []
    for y in sorted(years_data.keys()):
        roic = years_data[y].get('ROIC_YEARLY')
        if not pd.isna(roic):
            roic_vals.append(roic)
            if roic <= 5:
                return None, "ROIC<5%"
    if len(roic_vals) < 5:
        return None, "ROIC 数据不足"
    
    # 检查负债率
    debt = years_data[sorted(years_data.keys())[-1]].get('DEBT_ASSET_RATIO')
    if pd.isna(debt) or debt >= 50:
        return None, f"负债率={debt:.0f}%"
    
    # 检查现金流
    for y in sorted(years_data.keys()):
        fcf = years_data[y].get('PER_NETCASH_OPERATE')
        if not pd.isna(fcf) and fcf <= 0:
            return None, "现金流负"
    
    return {
        '代码': symbol,
        '名称': name,
        '股价': round(price, 1),
        'PE': round(pe, 1),
        'ROE_5y': round(sum(roe_vals)/len(roe_vals), 1),
        'ROIC_5y': round(sum(roic_vals)/len(roic_vals), 1),
        '负债率': round(debt, 1)
    }, "OK"

def main():
    print("=" * 70)
    print("港股筛选 - 锋哥五好标准")
    print("=" * 70)
    print("条件：PE<30, ROE>5%(5 年), ROIC>5%(5 年), 现金流正，负债率<50%")
    print("=" * 70)
    
    df = get_hk_stocks()
    passed = []
    failed = {}
    
    # 检查前 100 只活跃股票
    n = min(100, len(df))
    print(f"\n筛选前{n}只活跃股票...\n")
    
    for i in range(n):
        row = df.iloc[i]
        sym = str(row['代码']).zfill(6)
        name = row['名称']
        price = row['最新价']
        
        print(f"[{i+1}/{n}] {sym} {name}...", end=" ")
        
        try:
            result, status = check_stock(sym, name, price)
            if result:
                passed.append(result)
                print(f"✅")
            else:
                print(f"❌ {status}")
                failed[status] = failed.get(status, 0) + 1
        except Exception as e:
            print(f"⚠️ {e}")
            failed['异常'] = failed.get('异常', 0) + 1
        
        # 每 5 只暂停
        if (i + 1) % 5 == 0:
            time.sleep(3)
            print(f"  (进度{i+1}/{n})")
    
    print("\n" + "=" * 70)
    print(f"检查{n}只 | 符合{len(passed)}只 | 通过率{len(passed)/n*100:.1f}%")
    
    if passed:
        print("\n✅ 符合的港股：")
        df_r = pd.DataFrame(passed)
        print(df_r.to_string(index=False))
        df_r.to_csv('/home/admin/openclaw/workspace/hk_filtered_final.csv', index=False)
        print("\n已保存到 hk_filtered_final.csv")
    else:
        print("\n❌ 无符合股票")
    
    if failed:
        print("\n失败原因 TOP5：")
        for k, v in sorted(failed.items(), key=lambda x: -x[1])[:5]:
            print(f"  {k}: {v}")
    print("=" * 70)

if __name__ == '__main__':
    main()
