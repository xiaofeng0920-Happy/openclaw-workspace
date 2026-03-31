#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 Finnhub 获取锋哥持仓实时数据
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from finnhub_data import get_quote, get_multiple_quotes

# 锋哥持仓股票（来自 MEMORY.md）
US_STOCKS = ["GOOGL", "BRK.B", "KO", "ORCL", "MSFT", "NVDA", "AAPL", "TSLA"]
HK_STOCKS = ["00700.HK", "00883.HK", "09988.HK", "03153.HK", "07709.HK"]

print("=" * 80)
print("📊 锋哥持仓实时监控 - Finnhub 数据源")
print("=" * 80)
print()

# 获取美股持仓
print("🇺🇸 美股持仓:")
print("-" * 80)
us_quotes = get_multiple_quotes(US_STOCKS)

print("\n📈 美股实时价格:")
print(f"{'股票':<10} {'代码':<10} {'现价':<12} {'涨跌':<12} {'涨跌幅':<10}")
print("-" * 80)

for symbol in US_STOCKS:
    if symbol in us_quotes:
        q = us_quotes[symbol]
        change_flag = "📈" if q['change_pct'] > 0 else "📉" if q['change_pct'] < 0 else "➖"
        print(f"{symbol:<10} {symbol:<10} ${q['price']:<11.2f} {q['change']:+<11.2f} {change_flag} {q['change_pct']:+.2f}%")

print()
print("-" * 80)

# 获取港股持仓（Finnhub 港股需要.HK 后缀）
print("\n🇭🇰 港股持仓:")
print("-" * 80)
hk_quotes = get_multiple_quotes(HK_STOCKS)

print("\n📈 港股实时价格:")
print(f"{'股票':<15} {'代码':<12} {'现价':<12} {'涨跌':<12} {'涨跌幅':<10}")
print("-" * 80)

hk_names = {
    "00700.HK": "腾讯控股",
    "00883.HK": "中海油",
    "09988.HK": "阿里巴巴",
    "03153.HK": "南方日经",
    "07709.HK": "南方两倍"
}

for symbol in HK_STOCKS:
    if symbol in hk_quotes:
        q = hk_quotes[symbol]
        name = hk_names.get(symbol, symbol)
        change_flag = "📈" if q['change_pct'] > 0 else "📉" if q['change_pct'] < 0 else "➖"
        print(f"{name:<15} {symbol:<12} HK${q['price']:<10.2f} {q['change']:+<10.2f} {change_flag} {q['change_pct']:+.2f}%")

print()
print("=" * 80)
print("✅ 数据获取完成")
print("=" * 80)
