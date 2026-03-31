#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tushare 数据获取示例
"""

import tushare as ts
import os

# 配置 Token
TOKEN = os.environ.get('TUSHARE_TOKEN', '1dbdfba7c672d47f22db86f586d5aff9730124b321c2ebdda91890d3')
ts.set_token(TOKEN)
pro = ts.pro_api()

print('='*60)
print('Tushare 数据测试')
print('='*60)

# 测试 1：获取港股行情
print('\n1. 获取腾讯控股 (00700.HK) 行情')
try:
    data = pro.hk_daily(ts_code='00700.HK')
    if len(data) > 0:
        latest = data.iloc[0]
        print(f"   日期：{latest['trade_date']}")
        print(f"   收盘：{latest['close']}")
        print(f"   涨跌：{latest['pct_chg']}%")
    else:
        print("   无数据")
except Exception as e:
    print(f"   错误：{e}")

# 测试 2：获取 A 股行情
print('\n2. 获取贵州茅台 (600519.SH) 行情')
try:
    data = pro.daily(ts_code='600519.SH')
    if len(data) > 0:
        latest = data.iloc[0]
        print(f"   日期：{latest['trade_date']}")
        print(f"   收盘：{latest['close']}")
        print(f"   涨跌：{latest['pct_chg']}%")
    else:
        print("   无数据")
except Exception as e:
    print(f"   错误：{e}")

# 测试 3：获取指数行情
print('\n3. 获取上证指数 (000001.SH) 行情')
try:
    data = pro.index_daily(ts_code='000001.SH')
    if len(data) > 0:
        latest = data.iloc[0]
        print(f"   日期：{latest['trade_date']}")
        print(f"   收盘：{latest['close']}")
        print(f"   涨跌：{latest['pct_chg']}%")
    else:
        print("   无数据")
except Exception as e:
    print(f"   错误：{e}")

print('\n' + '='*60)
print('测试完成')
print('='*60)
