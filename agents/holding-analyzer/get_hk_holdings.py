#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取港股持仓 - 修正版
"""

import futu as ft
import pandas as pd

print("=" * 60)
print("📈 富途 OpenD - 港股实时行情")
print("=" * 60)

HOST = "127.0.0.1"
PORT = 11112

HK_STOCKS = [
    "HK.00700",  # 腾讯控股
    "HK.00883",  # 中海油
    "HK.09988",  # 阿里巴巴
    "HK.03153",  # 南方日经
    "HK.07709",  # 南方两倍
]

print(f"\n连接 {HOST}:{PORT}...")
quote_ctx = ft.OpenQuoteContext(host=HOST, port=PORT)

try:
    # 订阅
    print(f"订阅 {len(HK_STOCKS)} 支港股...")
    ret_sub, _ = quote_ctx.subscribe(HK_STOCKS, [ft.SubType.QUOTE])
    
    if ret_sub == 0:
        # 获取行情
        ret, data = quote_ctx.get_stock_quote(HK_STOCKS)
        
        if ret == 0:
            print("\n✅ 获取成功!")
            print("\n📈 港股实时价格:")
            print(f"{'股票':<15} {'代码':<12} {'现价':<12} {'涨跌':<12} {'涨跌幅':<10}")
            print("-" * 60)
            
            for _, row in data.iterrows():
                code = row['code']
                name = row['name']
                price = row['last_price']
                prev_close = row['prev_close_price']
                
                # 计算涨跌
                change = price - prev_close if pd.notna(prev_close) else 0
                change_pct = (change / prev_close * 100) if pd.notna(prev_close) and prev_close != 0 else 0
                
                change_flag = "📈" if change_pct > 0 else "📉" if change_pct < 0 else "➖"
                print(f"{name:<15} {code:<12} HK${price:<10.2f} {change:+<10.2f} {change_flag} {change_pct:+.2f}%")
        else:
            print(f"❌ 获取失败：{data}")
    else:
        print(f"❌ 订阅失败")

except Exception as e:
    print(f"❌ 错误：{e}")

finally:
    quote_ctx.close()
    print("\n" + "=" * 60)
    print("连接已关闭")
    print("=" * 60)
