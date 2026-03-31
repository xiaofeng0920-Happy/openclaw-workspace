#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
锋哥持仓实时监控 - 混合数据源

美股：Finnhub
港股：富途 OpenD
"""

import os
import sys
import pandas as pd
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置 Finnhub API Key
os.environ['FINNHUB_API_KEY'] = 'd6r9v6hr01qgdhqdor50d6r9v6hr01qgdhqdor5g'

from finnhub_data import get_multiple_quotes
import futu as ft

print("=" * 80)
print("📊 锋哥持仓实时监控 - 混合数据源")
print("   美股：Finnub | 港股：富途 OpenD")
print("=" * 80)
print()

# ============== 美股持仓 ==============
US_STOCKS = ["GOOGL", "BRK.B", "KO", "ORCL", "MSFT", "NVDA", "AAPL", "TSLA"]

print("🇺🇸 美股持仓 (Finnhub)")
print("-" * 80)
us_quotes = get_multiple_quotes(US_STOCKS)

print(f"\n{'股票':<15} {'代码':<10} {'现价':<12} {'涨跌':<12} {'涨跌幅':<10}")
print("-" * 80)

for symbol in US_STOCKS:
    if symbol in us_quotes:
        q = us_quotes[symbol]
        change_flag = "📈" if q['change_pct'] > 0 else "📉" if q['change_pct'] < 0 else "➖"
        print(f"{symbol:<15} {symbol:<10} ${q['price']:<11.2f} {q['change']:+<11.2f} {change_flag} {q['change_pct']:+.2f}%")

print()

# ============== 港股持仓 ==============
HK_STOCKS = ["HK.00700", "HK.00883", "HK.09988", "HK.03153", "HK.07709"]
HK_NAMES = {
    "HK.00700": "腾讯控股",
    "HK.00883": "中国海洋石油",
    "HK.09988": "阿里巴巴-W",
    "HK.03153": "南方日经 225",
    "HK.07709": "南方两倍做多"
}

print("🇭🇰 港股持仓 (富途 OpenD)")
print("-" * 80)

quote_ctx = ft.OpenQuoteContext(host="127.0.0.1", port=11112)

try:
    # 订阅
    ret_sub, _ = quote_ctx.subscribe(HK_STOCKS, [ft.SubType.QUOTE])
    
    if ret_sub == 0:
        # 获取行情
        ret, data = quote_ctx.get_stock_quote(HK_STOCKS)
        
        if ret == 0:
            print(f"\n{'股票':<15} {'代码':<12} {'现价':<12} {'涨跌':<12} {'涨跌幅':<10}")
            print("-" * 80)
            
            for _, row in data.iterrows():
                code = row['code']
                name = HK_NAMES.get(code, row['name'])
                price = row['last_price']
                prev_close = row['prev_close_price']
                
                change = price - prev_close if pd.notna(prev_close) else 0
                change_pct = (change / prev_close * 100) if pd.notna(prev_close) and prev_close != 0 else 0
                
                change_flag = "📈" if change_pct > 0 else "📉" if change_pct < 0 else "➖"
                print(f"{name:<15} {code:<12} HK${price:<10.2f} {change:+<10.2f} {change_flag} {change_pct:+.2f}%")
finally:
    quote_ctx.close()

print()
print("=" * 80)
print("✅ 数据获取完成")
print("=" * 80)
