#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
锋哥持仓实时价格监控 - 从富途 OpenD 获取真实持仓

持仓数据：富途 OpenD（美股 + 港股 + 期权）
价格数据：
  - 美股：Finnhub
  - 港股：富途 OpenD

刷新频率：每 5 分钟
"""

import os
import sys
import time
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置 Finnhub API Key
os.environ['FINNHUB_API_KEY'] = 'd6r9v6hr01qgdhqdor50d6r9v6hr01qgdhqdor5g'

from finnhub_data import get_multiple_quotes
import futu as ft

# 导入 futu_data.py 的函数
sys.path.insert(0, str(Path(__file__).parent))
from futu_data import get_us_holdings, get_hk_holdings, close_contexts

# ============== 配置 ==============
REFRESH_INTERVAL = 300  # 5 分钟
LOG_FILE = Path(__file__).parent / "logs" / "price_monitor_realtime.log"
HOLDINGS_FILE = Path(__file__).parent / "reports" / "realtime_holdings.json"

# 确保目录存在
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
HOLDINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

# ============== 日志 ==============
def log(message):
    """打印并记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg + '\n')

# ============== 富途 OpenD 数据获取 ==============
def get_futu_holdings():
    """
    从富途 OpenD 获取真实持仓（使用 futu_data.py 的函数）
    
    返回：
    {
        'us': [{'symbol': 'AAPL', 'shares': 191, 'cost_price': 150.0, ...}],
        'hk': [{'symbol': '00700', 'shares': 2500, 'cost_price': 500.0, ...}],
        'options': []
    }
    """
    holdings = {
        'us': [],
        'hk': [],
        'options': []
    }
    
    try:
        # 获取美股持仓
        log("📈 获取美股持仓...")
        holdings['us'] = get_us_holdings()
        if holdings['us']:
            log(f"   ✅ 美股持仓：{len(holdings['us'])} 只")
        else:
            log(f"   ⚠️  美股无持仓或获取失败")
        
        # 获取港股持仓
        log("📈 获取港股持仓...")
        holdings['hk'] = get_hk_holdings()
        if holdings['hk']:
            log(f"   ✅ 港股持仓：{len(holdings['hk'])} 只")
        else:
            log(f"   ⚠️  港股无持仓或获取失败")
    
    except Exception as e:
        log(f"❌ 获取持仓失败：{e}")
        import traceback
        log(traceback.format_exc())
    
    finally:
        close_contexts()
    
    return holdings

def get_futu_quotes(symbols, market='HK'):
    """从富途获取实时价格"""
    HOST = "127.0.0.1"
    PORT = 11112
    
    quote_ctx = ft.OpenQuoteContext(host=HOST, port=PORT)
    
    try:
        # 订阅
        ret_sub, _ = quote_ctx.subscribe(symbols, [ft.SubType.QUOTE])
        
        if ret_sub == 0:
            ret, data = quote_ctx.get_stock_quote(symbols)
            
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
                        'name': row['name'],
                        'price': price,
                        'change': change,
                        'change_pct': change_pct,
                    }
                return results
    finally:
        quote_ctx.close()
    
    return {}

# ============== 显示 ==============
def print_holdings_header():
    """打印表头"""
    print("\n" + "=" * 120)
    print(f"📊 锋哥持仓实时监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("   持仓：富途 OpenD | 美股价格：Finnhub | 港股价格：富途 OpenD | 刷新：每 5 分钟")
    print("=" * 120)

def print_us_holdings(holdings, quotes):
    """打印美股持仓"""
    if not holdings:
        print("\n🇺🇸 美股持仓：无持仓")
        return
    
    print("\n🇺🇸 美股持仓")
    print("-" * 120)
    print(f"{'股票':<12} {'数量':<10} {'成本':<12} {'现价':<12} {'市值':<14} {'盈亏':<14} {'盈亏率':<10} {'状态':<8}")
    print("-" * 120)
    
    total_market_value = 0
    total_pl = 0
    
    for h in holdings:
        symbol = h['symbol']
        shares = h['shares']
        cost = h['cost_price']
        
        # 使用实时价格
        if symbol in quotes:
            current_price = quotes[symbol]['price']
        else:
            current_price = h['current_price']
        
        market_value = shares * current_price
        pl = (current_price - cost) * shares
        pl_pct = ((current_price - cost) / cost * 100) if cost > 0 else 0
        
        total_market_value += market_value
        total_pl += pl
        
        change_flag = "📈" if pl_pct > 0 else "📉" if pl_pct < 0 else "➖"
        status = "🔴" if abs(pl_pct) > 10 else "🟡" if abs(pl_pct) > 5 else "🟢"
        
        print(f"{symbol:<12} {shares:<10.0f} ${cost:<11.2f} ${current_price:<11.2f} ${market_value:<13.2f} {pl:+<13.2f} {change_flag} {pl_pct:+.2f}%    {status}")
    
    print("-" * 120)
    print(f"{'美股合计':<12} {'':<10} {'':<12} {'':<12} ${total_market_value:<13.2f} {total_pl:+<13.2f}")

def print_hk_holdings(holdings, quotes):
    """打印港股持仓"""
    if not holdings:
        print("\n🇭🇰 港股持仓：无持仓")
        return
    
    print("\n🇭🇰 港股持仓")
    print("-" * 120)
    print(f"{'股票':<15} {'数量':<10} {'成本':<12} {'现价':<12} {'市值':<14} {'盈亏':<14} {'盈亏率':<10} {'状态':<8}")
    print("-" * 120)
    
    total_market_value = 0
    total_pl = 0
    
    for h in holdings:
        symbol = h['symbol']
        name = h.get('name', symbol)
        shares = h['shares']
        cost = h['cost_price']
        
        # 使用实时价格
        if symbol in quotes:
            current_price = quotes[symbol]['price']
        else:
            current_price = h['current_price']
        
        market_value = shares * current_price
        pl = (current_price - cost) * shares
        pl_pct = ((current_price - cost) / cost * 100) if cost > 0 else 0
        
        total_market_value += market_value
        total_pl += pl
        
        change_flag = "📈" if pl_pct > 0 else "📉" if pl_pct < 0 else "➖"
        status = "🔴" if abs(pl_pct) > 10 else "🟡" if abs(pl_pct) > 5 else "🟢"
        
        print(f"{name:<15} {shares:<10.0f} ${cost:<11.2f} ${current_price:<11.2f} ${market_value:<13.2f} {pl:+<13.2f} {change_flag} {pl_pct:+.2f}%    {status}")
    
    print("-" * 120)
    print(f"{'港股合计':<15} {'':<10} {'':<12} {'':<12} ${total_market_value:<13.2f} {total_pl:+<13.2f}")

def print_options_holdings(holdings):
    """打印期权持仓"""
    if not holdings:
        print("\n📜 期权持仓：无持仓")
        return
    
    print("\n📜 期权持仓")
    print("-" * 120)
    print(f"{'名称':<30} {'数量':<10} {'成本':<12} {'现价':<12} {'市值':<14} {'盈亏':<14} {'状态':<8}")
    print("-" * 120)
    
    for h in holdings:
        name = h.get('name', h['symbol'])
        shares = h['shares']
        cost = h['cost_price']
        current = h['current_price']
        market_value = h['market_value']
        pl = h['pl']
        pl_pct = h['pl_pct']
        
        change_flag = "📈" if pl_pct > 0 else "📉" if pl_pct < 0 else "➖"
        status = "🔴" if abs(pl_pct) > 50 else "🟡" if abs(pl_pct) > 20 else "🟢"
        
        print(f"{name:<30} {shares:<10.0f} ${cost:<11.2f} ${current:<11.2f} ${market_value:<13.2f} {pl:+<13.2f} {change_flag} {pl_pct:+.2f}%    {status}")

# ============== 主循环 ==============
def main():
    """主函数"""
    log("🚀 启动实时持仓监控（富途 OpenD 真实持仓）")
    log(f"📁 日志文件：{LOG_FILE}")
    log(f"💾 持仓缓存：{HOLDINGS_FILE}")
    log(f"⏱️  刷新间隔：{REFRESH_INTERVAL}秒")
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            log(f"\n{'='*60}")
            log(f"📊 第 {iteration} 次更新")
            print_holdings_header()
            
            # 1. 从富途获取真实持仓
            log("📥 从富途 OpenD 获取持仓...")
            holdings = get_futu_holdings()
            
            # 保存持仓快照
            with open(HOLDINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(holdings, f, indent=2, ensure_ascii=False, default=str)
            
            # 2. 获取实时价格
            log("📈 获取实时价格...")
            
            # 美股价格（Finnhub）
            us_symbols = [h['symbol'] for h in holdings['us']]
            us_quotes = get_multiple_quotes(us_symbols) if us_symbols else {}
            
            # 港股价格（富途）
            hk_symbols = [h['symbol'] for h in holdings['hk']]
            hk_quotes = get_futu_quotes(hk_symbols) if hk_symbols else {}
            
            # 3. 显示持仓
            print_us_holdings(holdings['us'], us_quotes)
            print_hk_holdings(holdings['hk'], hk_quotes)
            print_options_holdings(holdings['options'])
            
            # 4. 检查显著变化
            log("\n⚠️  股价警报 (>3%):")
            
            # 股票名称映射
            US_NAMES = {
                'GOOGL': '谷歌', 'BRK.B': '伯克希尔', 'KO': '可口可乐',
                'ORCL': '甲骨文', 'MSFT': '微软', 'NVDA': '英伟达',
                'AAPL': '苹果', 'TSLA': '特斯拉'
            }
            
            significant_changes = []
            
            # 美股警报
            for symbol, q in us_quotes.items():
                if abs(q['change_pct']) > 3:
                    name = US_NAMES.get(symbol, symbol)
                    severity = "🔴" if abs(q['change_pct']) > 5 else "🟡"
                    significant_changes.append({
                        'severity': severity,
                        'name': name,
                        'symbol': symbol,
                        'change_pct': q['change_pct'],
                        'market': 'US'
                    })
            
            # 港股警报
            for symbol, q in hk_quotes.items():
                if abs(q['change_pct']) > 3:
                    name = q.get('name', symbol)
                    severity = "🔴" if abs(q['change_pct']) > 5 else "🟡"
                    significant_changes.append({
                        'severity': severity,
                        'name': name,
                        'symbol': symbol,
                        'change_pct': q['change_pct'],
                        'market': 'HK'
                    })
            
            if significant_changes:
                # 按变化幅度排序
                significant_changes.sort(key=lambda x: abs(x['change_pct']), reverse=True)
                
                for alert in significant_changes:
                    market_flag = "🇺🇸" if alert['market'] == 'US' else "🇭🇰"
                    direction = "📈" if alert['change_pct'] > 0 else "📉"
                    log(f"   {alert['severity']} {market_flag} {alert['name']} ({alert['symbol']}): {direction} {alert['change_pct']:+.2f}%")
            else:
                log("   🟢 无显著变化")
            
            # 5. 等待下次刷新
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
