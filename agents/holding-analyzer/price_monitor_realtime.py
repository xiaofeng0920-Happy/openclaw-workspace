#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
锋哥持仓实时价格监控 - 每 5 分钟刷新

美股：Finnhub
港股：富途 OpenD (端口 11112)

运行时间：交易时段（港股 9:30-16:00，美股 21:30-4:00）
刷新频率：每 5 分钟
"""

import os
import sys
import time
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置 Finnhub API Key
os.environ['FINNHUB_API_KEY'] = 'd6r9v6hr01qgdhqdor50d6r9v6hr01qgdhqdor5g'

from finnhub_data import get_multiple_quotes
import futu as ft

# ============== 配置 ==============
US_STOCKS = ["GOOGL", "BRK.B", "KO", "ORCL", "MSFT", "NVDA", "AAPL", "TSLA"]
HK_STOCKS = ["HK.00700", "HK.00883", "HK.09988", "HK.03153", "HK.07709"]

HK_NAMES = {
    "HK.00700": "腾讯控股",
    "HK.00883": "中国海洋石油",
    "HK.09988": "阿里巴巴-W",
    "HK.03153": "南方日经 225",
    "HK.07709": "南方两倍做多"
}

REFRESH_INTERVAL = 300  # 5 分钟 = 300 秒
LOG_FILE = Path(__file__).parent / "logs" / "price_monitor.log"

# 确保日志目录存在
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# ============== 日志 ==============
def log(message):
    """打印并记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg + '\n')

# ============== 数据获取 ==============
def get_us_prices():
    """获取美股价格"""
    return get_multiple_quotes(US_STOCKS)

def get_hk_prices():
    """获取港股价格"""
    quote_ctx = ft.OpenQuoteContext(host="127.0.0.1", port=11112)
    try:
        ret_sub, _ = quote_ctx.subscribe(HK_STOCKS, [ft.SubType.QUOTE])
        if ret_sub == 0:
            ret, data = quote_ctx.get_stock_quote(HK_STOCKS)
            if ret == 0:
                results = {}
                for _, row in data.iterrows():
                    code = row['code']
                    price = row['last_price']
                    prev_close = row['prev_close_price']
                    
                    change = price - prev_close if pd.notna(prev_close) else 0
                    change_pct = (change / prev_close * 100) if pd.notna(prev_close) and prev_close != 0 else 0
                    
                    results[code] = {
                        'symbol': code,
                        'name': HK_NAMES.get(code, row['name']),
                        'price': price,
                        'change': change,
                        'change_pct': change_pct,
                    }
                return results
    finally:
        quote_ctx.close()
    return {}

# ============== 显示 ==============
def print_header():
    """打印表头"""
    print("\n" + "=" * 100)
    print(f"📊 锋哥持仓实时价格监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("   美股：Finnhub | 港股：富途 OpenD (11112) | 刷新：每 5 分钟")
    print("=" * 100)

def print_us_table(quotes):
    """打印美股表格"""
    print("\n🇺🇸 美股持仓")
    print("-" * 100)
    print(f"{'股票':<15} {'代码':<10} {'现价':<14} {'涨跌':<14} {'涨跌幅':<12} {'状态':<10}")
    print("-" * 100)
    
    for symbol in US_STOCKS:
        if symbol in quotes:
            q = quotes[symbol]
            change_flag = "📈" if q['change_pct'] > 0 else "📉" if q['change_pct'] < 0 else "➖"
            status = "🔴" if abs(q['change_pct']) > 3 else "🟡" if abs(q['change_pct']) > 1 else "🟢"
            print(f"{symbol:<15} {symbol:<10} ${q['price']:<13.2f} {q['change']:+<13.2f} {change_flag} {q['change_pct']:+.2f}%    {status}")

def print_hk_table(quotes):
    """打印港股表格"""
    print("\n🇭🇰 港股持仓")
    print("-" * 100)
    print(f"{'股票':<15} {'代码':<12} {'现价':<14} {'涨跌':<14} {'涨跌幅':<12} {'状态':<10}")
    print("-" * 100)
    
    for code in HK_STOCKS:
        if code in quotes:
            q = quotes[code]
            change_flag = "📈" if q['change_pct'] > 0 else "📉" if q['change_pct'] < 0 else "➖"
            status = "🔴" if abs(q['change_pct']) > 3 else "🟡" if abs(q['change_pct']) > 1 else "🟢"
            print(f"{q['name']:<15} {code:<12} HK${q['price']:<12.2f} {q['change']:+<13.2f} {change_flag} {q['change_pct']:+.2f}%    {status}")

# ============== 主循环 ==============
def main():
    """主函数"""
    log("🚀 启动实时价格监控")
    log(f"📁 日志文件：{LOG_FILE}")
    log(f"⏱️  刷新间隔：{REFRESH_INTERVAL}秒")
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            log(f"\n{'='*50}")
            log(f"📊 第 {iteration} 次更新")
            print_header()
            
            # 获取美股数据
            log("📈 获取美股数据...")
            us_quotes = get_us_prices()
            print_us_table(us_quotes)
            
            # 获取港股数据
            log("📈 获取港股数据...")
            hk_quotes = get_hk_prices()
            print_hk_table(hk_quotes)
            
            # 检查显著变化
            log("\n⚠️  显著变化 (>3%):")
            significant_changes = []
            
            for symbol, q in us_quotes.items():
                if abs(q['change_pct']) > 3:
                    significant_changes.append(f"{symbol}: {q['change_pct']:+.2f}%")
            
            for code, q in hk_quotes.items():
                if abs(q['change_pct']) > 3:
                    significant_changes.append(f"{q['name']}: {q['change_pct']:+.2f}%")
            
            if significant_changes:
                for change in significant_changes:
                    log(f"   🔴 {change}")
            else:
                log("   🟢 无显著变化")
            
            # 等待下次刷新
            next_update = datetime.now() + timedelta(seconds=REFRESH_INTERVAL)
            log(f"\n⏱️  下次更新：{next_update.strftime('%H:%M:%S')}")
            log(f"💤 等待 {REFRESH_INTERVAL} 秒...")
            
            time.sleep(REFRESH_INTERVAL)
    
    except KeyboardInterrupt:
        log("\n\n🛑 用户中断，退出监控")
    except Exception as e:
        log(f"\n\n❌ 错误：{e}")
        import traceback
        log(traceback.format_exc())
    
    log("👋 监控结束")

if __name__ == "__main__":
    main()
