#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final earnings data query for portfolio stocks
"""
import akshare as ak
import pandas as pd
import warnings
import time
import json
warnings.filterwarnings('ignore')

# US Stocks to query
us_stocks = {
    'GOOGL': '谷歌',
    'BRK.B': '伯克希尔',
    'KO': '可口可乐',
    'ORCL': '甲骨文',
    'MSFT': '微软',
    'NVDA': '英伟达',
    'AAPL': '苹果',
    'TSLA': '特斯拉'
}

# HK Stocks to query  
hk_stocks = {
    '00883': '中国海洋石油',
    '09988': '阿里巴巴-W'
}

def query_us_stock_earnings(symbol):
    """Query US stock quarterly earnings data from analysis indicators"""
    try:
        df = ak.stock_financial_us_analysis_indicator_em(symbol=symbol, indicator="单季报")
        if df is None or len(df) == 0:
            return None
            
        latest = df.iloc[0]
        
        # Get previous quarter for YoY comparison
        reports = sorted(df['REPORT'].unique(), reverse=True)
        prev_report = reports[1] if len(reports) > 1 else None
        
        result = {
            'report_date': str(latest.get('REPORT_DATE', 'N/A')),
            'report_period': latest.get('REPORT', 'N/A'),
            'revenue': latest.get('OPERATE_INCOME', 'N/A'),
            'revenue_yoy': latest.get('OPERATE_INCOME_YOY', 'N/A'),
            'net_profit': latest.get('PARENT_HOLDER_NETPROFIT', 'N/A'),
            'net_profit_yoy': latest.get('PARENT_HOLDER_NETPROFIT_YOY', 'N/A'),
            'eps': latest.get('BASIC_EPS', latest.get('DILUTED_EPS', 'N/A')),
            'eps_yoy': latest.get('BASIC_EPS_YOY', 'N/A'),
            'roe': latest.get('ROE_AVG', 'N/A'),
            'roa': latest.get('ROA', 'N/A'),
            'gross_margin': latest.get('GROSS_PROFIT_RATIO', 'N/A'),
            'net_margin': latest.get('NET_PROFIT_RATIO', 'N/A'),
        }
        
        return result
    except Exception as e:
        print(f"Error querying {symbol}: {e}")
    return None

def query_hk_stock_earnings(symbol):
    """Query HK stock earnings data"""
    try:
        hk_symbol = f"HK{symbol}"
        # Try stock_hk_financial_indicator_em
        df = ak.stock_hk_financial_indicator_em(symbol=hk_symbol)
        if df is None or len(df) == 0:
            return None
            
        latest = df.iloc[0]
        
        result = {
            'report_date': str(latest.get('REPORT_DATE', latest.get('报告期', 'N/A'))),
        }
        
        # Map fields
        field_map = {
            'revenue': ['营业总收入', '营业收入', 'REVENUE'],
            'revenue_yoy': ['营业总收入同比增长率', '营业收入同比增长率'],
            'net_profit': ['净利润', '归属母公司股东净利润'],
            'net_profit_yoy': ['净利润同比增长率'],
            'eps': ['每股收益', 'EPS'],
            'roe': ['净资产收益率 ROE'],
        }
        
        for key, names in field_map.items():
            for name in names:
                for col in latest.index:
                    if name in str(col):
                        result[key] = latest[col]
                        break
                        
        return result
    except Exception as e:
        print(f"Error querying HK {symbol}: {e}")
    return None

def format_number(val):
    """Format large numbers to billions/millions"""
    if val is None or val == 'N/A' or pd.isna(val):
        return 'N/A'
    try:
        num = float(val)
        if abs(num) >= 1e9:
            return f"{num/1e9:.2f}B"
        elif abs(num) >= 1e6:
            return f"{num/1e6:.2f}M"
        else:
            return f"{num:.2f}"
    except:
        return str(val)

def format_pct(val):
    """Format percentage"""
    if val is None or val == 'N/A' or pd.isna(val):
        return 'N/A'
    try:
        return f"{float(val):.2f}%"
    except:
        return str(val)

print("=" * 80)
print("查询美股财报数据...")
print("=" * 80)

us_results = {}
for symbol, name in us_stocks.items():
    print(f"\n查询 {symbol} ({name})...")
    time.sleep(1)
    earnings = query_us_stock_earnings(symbol)
    
    if earnings:
        result = {'name': name, 'market': '美股'}
        result.update(earnings)
        us_results[symbol] = result
        print(f"  ✓ 获取成功 - {earnings.get('report_period', 'N/A')}")
    else:
        print(f"  ✗ 获取失败")

print("\n" + "=" * 80)
print("查询港股财报数据...")
print("=" * 80)

hk_results = {}
for symbol, name in hk_stocks.items():
    print(f"\n查询 {symbol} ({name})...")
    time.sleep(2)
    financial = query_hk_stock_earnings(symbol)
    
    if financial:
        result = {'name': name, 'market': '港股'}
        result.update(financial)
        hk_results[symbol] = result
        print(f"  ✓ 获取成功 - {financial.get('report_date', 'N/A')}")
    else:
        print(f"  ✗ 获取失败")

# Print formatted results
print("\n" + "=" * 80)
print("财报数据汇总表")
print("=" * 80)

print("\n【美股】")
print("-" * 80)
for symbol, data in us_results.items():
    print(f"\n{symbol} ({data.get('name', 'N/A')}):")
    print(f"  财报季度：{data.get('report_period', data.get('report_date', 'N/A'))}")
    print(f"  营收：{format_number(data.get('revenue'))} (同比：{format_pct(data.get('revenue_yoy'))})")
    print(f"  净利润：{format_number(data.get('net_profit'))} (同比：{format_pct(data.get('net_profit_yoy'))})")
    print(f"  EPS: {format_number(data.get('eps'))} (同比：{format_pct(data.get('eps_yoy'))})")
    print(f"  ROE: {format_pct(data.get('roe'))}")
    print(f"  毛利率：{format_pct(data.get('gross_margin'))}")
    print(f"  净利率：{format_pct(data.get('net_margin'))}")

print("\n【港股】")
print("-" * 80)
for symbol, data in hk_results.items():
    print(f"\n{symbol} ({data.get('name', 'N/A')}):")
    print(f"  财报季度：{data.get('report_date', 'N/A')}")
    print(f"  营收：{format_number(data.get('revenue'))} (同比：{format_pct(data.get('revenue_yoy'))})")
    print(f"  净利润：{format_number(data.get('net_profit'))} (同比：{format_pct(data.get('net_profit_yoy'))})")
    print(f"  EPS: {format_number(data.get('eps'))}")
    print(f"  ROE: {format_pct(data.get('roe'))}")

# Create markdown table
print("\n" + "=" * 80)
print("Markdown 表格格式")
print("=" * 80)

print("\n### 美股财报数据")
print("\n| 代码 | 名称 | 财报季度 | 营收 | 营收同比 | 净利润 | 净利润同比 | EPS | ROE | 毛利率 |")
print("|------|------|----------|------|----------|--------|------------|-----|-----|--------|")
for symbol, data in us_results.items():
    print(f"| {symbol} | {data.get('name', '')} | {data.get('report_period', '')} | {format_number(data.get('revenue'))} | {format_pct(data.get('revenue_yoy'))} | {format_number(data.get('net_profit'))} | {format_pct(data.get('net_profit_yoy'))} | {format_number(data.get('eps'))} | {format_pct(data.get('roe'))} | {format_pct(data.get('gross_margin'))} |")

print("\n### 港股财报数据")
print("\n| 代码 | 名称 | 财报季度 | 营收 | 营收同比 | 净利润 | 净利润同比 | EPS | ROE |")
print("|------|------|----------|------|----------|--------|------------|-----|-----|")
for symbol, data in hk_results.items():
    print(f"| {symbol} | {data.get('name', '')} | {data.get('report_date', '')} | {format_number(data.get('revenue'))} | {format_pct(data.get('revenue_yoy'))} | {format_number(data.get('net_profit'))} | {format_pct(data.get('net_profit_yoy'))} | {format_number(data.get('eps'))} | {format_pct(data.get('roe'))} |")

# Save to file
all_results = {'us': us_results, 'hk': hk_results}
with open('/home/admin/openclaw/workspace/memory/财报数据查询结果_2026-03-19.json', 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)

print(f"\n结果已保存到：/home/admin/openclaw/workspace/memory/财报数据查询结果_2026-03-19.json")
