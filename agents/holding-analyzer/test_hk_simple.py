#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速获取港股持仓 - 简化版
"""

import futu as ft
import time

print("=" * 60)
print("🔌 富途 OpenD 快速测试")
print("=" * 60)

# 配置
HOST = "127.0.0.1"
PORT = 11112  # OpenD 实际端口

print(f"\n连接 {HOST}:{PORT}...")

# 创建报价上下文
quote_ctx = ft.OpenQuoteContext(host=HOST, port=PORT)

# 测试订阅
symbols = ["HK.00700", "HK.00883"]
print(f"订阅股票：{symbols}")

try:
    # 订阅
    ret_sub, err_sub = quote_ctx.subscribe(symbols, [ft.SubType.QUOTE])
    print(f"订阅结果：{ret_sub}")
    
    if ret_sub:
        # 获取行情
        ret, data = quote_ctx.get_stock_quote(symbols)
        
        if ret == 0:
            print("\n✅ 获取成功!")
            print("\n📈 港股实时价格:")
            print(f"{'股票':<15} {'代码':<12} {'现价':<12} {'涨跌':<12} {'涨跌幅':<10}")
            print("-" * 60)
            
            for _, row in data.iterrows():
                code = row['code']
                name = row['name']
                price = row['last_price']
                change = row['change']
                change_pct = row['change_percent']
                
                change_flag = "📈" if change_pct > 0 else "📉" if change_pct < 0 else "➖"
                print(f"{name:<15} {code:<12} HK${price:<10.2f} {change:+<10.2f} {change_flag} {change_pct:+.2f}%")
        else:
            print(f"❌ 获取失败：{data}")
    else:
        print(f"❌ 订阅失败：{err_sub}")

except Exception as e:
    print(f"❌ 错误：{e}")

finally:
    quote_ctx.close()
    print("\n" + "=" * 60)
    print("连接已关闭")
    print("=" * 60)
