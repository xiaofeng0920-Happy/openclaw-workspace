#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
锋哥持仓实时监控 - 混合数据源 v2

数据源：
- 持仓数据：富途 OpenD + OCR 识别结果
- 美股价格：Finnhub
- 港股价格：富途 OpenD

刷新频率：每 5 分钟
"""

import os
import sys
import time
import json
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
REFRESH_INTERVAL = 300  # 5 分钟
LOG_FILE = Path(__file__).parent / "logs" / "price_monitor_v2.log"
HOLDINGS_FILE = Path(__file__).parent / "reports" / "realtime_holdings_v2.json"

# OCR 识别的持仓数据
OCR_HOLDINGS_FILE = Path(__file__).parent.parent / "holdings_parsed.json"

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

# ============== 持仓加载 ==============
def load_holdings():
    """加载持仓数据（OCR + 配置）"""
    holdings = {
        'us': [],
        'hk': [],
        'options': []
    }
    
    # 1. 加载 OCR 识别的持仓
    if OCR_HOLDINGS_FILE.exists():
        log("📥 加载 OCR 持仓数据...")
        with open(OCR_HOLDINGS_FILE, 'r', encoding='utf-8') as f:
            ocr_data = json.load(f)
        
        # 股票持仓
        for h in ocr_data.get('holdings', []):
            symbol = h.get('股票代码', '')
            if symbol in ['GOOGL', 'NVDA', 'AAPL', 'MSFT', 'TSLA', 'BRK.B', 'KO', 'ORCL']:
                holdings['us'].append({
                    'symbol': symbol,
                    'name': h.get('股票名称', symbol),
                    'shares': h.get('持仓数量', 0),
                    'cost_price': h.get('成本价', 0),
                })
        
        # 期权持仓
        for opt in ocr_data.get('options_details', []):
            holdings['options'].append({
                'symbol': opt.get('标的', '') + opt.get('类型', ''),
                'name': f"{opt.get('标的')} {opt.get('类型')} {opt.get('到期日')} {opt.get('行权价')}",
                'shares': opt.get('数量', 0),
                'cost': opt.get('成本', 0),
                'market_value': opt.get('市值', 0),
            })
        
        log(f"   ✅ OCR 持仓：{len(holdings['us'])} 只股票 + {len(holdings['options'])} 个期权")
    
    # 2. 加载配置的持仓（MEMORY.md）
    # TODO: 解析 memory/锋哥持仓_2026-03-16.md
    
    return holdings

# ============== 价格获取 ==============
def get_us_prices(symbols):
    """获取美股价格（Finnhub）"""
    if not symbols:
        return {}
    return get_multiple_quotes(symbols)

def get_hk_prices(symbols):
    """获取港股价格（富途 OpenD）"""
    if not symbols:
        return {}
    
    HOST = "127.0.0.1"
    PORT = 11112
    
    quote_ctx = ft.OpenQuoteContext(host=HOST, port=PORT)
    try:
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
    print("\n" + "=" * 100)
    print(f"📊 锋哥持仓实时监控 v2 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("   持仓：OCR+ 配置 | 美股：Finnhub | 港股：富途 OpenD | 刷新：每 5 分钟")
    print("=" * 100)

def print_us_holdings(holdings, quotes):
    """打印美股持仓"""
    if not holdings:
        print("\n🇺🇸 美股持仓：无持仓")
        return
    
    print("\n🇺🇸 美股持仓")
    print("-" * 100)
    print(f"{'股票':<12} {'数量':<10} {'成本':<12} {'现价':<12} {'市值':<14} {'盈亏':<14} {'状态':<8}")
    print("-" * 100)
    
    total_market_value = 0
    total_pl = 0
    
    for h in holdings:
        symbol = h['symbol']
        shares = h.get('shares', 0) or 0
        cost = h.get('cost_price', 0) or 0
        
        # 使用实时价格
        if symbol in quotes:
            current_price = quotes[symbol]['price']
        else:
            current_price = 0
        
        market_value = shares * current_price
        pl = (current_price - cost) * shares if cost > 0 else 0
        pl_pct = ((current_price - cost) / cost * 100) if cost > 0 else 0
        
        total_market_value += market_value
        total_pl += pl
        
        change_flag = "📈" if pl_pct > 0 else "📉" if pl_pct < 0 else "➖"
        status = "🔴" if abs(pl_pct) > 10 else "🟡" if abs(pl_pct) > 5 else "🟢"
        
        if shares > 0:
            print(f"{symbol:<12} {shares:<10.0f} ${cost:<11.2f} ${current_price:<11.2f} ${market_value:<13.2f} {pl:+<13.2f} {change_flag} {pl_pct:+.2f}%    {status}")
    
    print("-" * 100)
    print(f"{'美股合计':<12} {'':<10} {'':<12} {'':<12} ${total_market_value:<13.2f} {total_pl:+<13.2f}")

def print_options_holdings(holdings):
    """打印期权持仓"""
    if not holdings:
        print("\n📜 期权持仓：无持仓")
        return
    
    print("\n📜 期权持仓")
    print("-" * 100)
    print(f"{'名称':<40} {'数量':<10} {'成本':<12} {'市值':<14} {'状态':<8}")
    print("-" * 100)
    
    total_value = 0
    
    for h in holdings:
        name = h.get('name', h['symbol'])
        shares = h.get('shares', 0)
        cost = h.get('cost', 0)
        market_value = h.get('market_value', 0)
        
        total_value += market_value
        
        status = "🔴" if market_value < 0 else "🟢"
        
        if shares != 0:
            print(f"{name:<40} {shares:<10.0f} ${cost:<11.2f} ${market_value:<13.2f} {status}")
    
    print("-" * 100)
    print(f"{'期权合计':<40} {'':<10} {'':<12} ${total_value:<13.2f}")

# ============== 主循环 ==============
def main():
    """主函数"""
    log("🚀 启动实时持仓监控 v2（OCR+ 富途）")
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
            
            # 1. 加载持仓
            log("📥 加载持仓数据...")
            holdings = load_holdings()
            
            # 2. 获取实时价格
            log("📈 获取实时价格...")
            
            # 美股价格（Finnhub）
            us_symbols = [h['symbol'] for h in holdings['us']]
            us_quotes = get_us_prices(us_symbols) if us_symbols else {}
            
            # 3. 显示持仓
            print_us_holdings(holdings['us'], us_quotes)
            print_options_holdings(holdings['options'])
            
            # 4. 检查显著变化
            log("\n⚠️  股价警报 (>3%):")
            significant_changes = []
            
            for symbol, q in us_quotes.items():
                if abs(q['change_pct']) > 3:
                    severity = "🔴" if abs(q['change_pct']) > 5 else "🟡"
                    direction = "📈" if q['change_pct'] > 0 else "📉"
                    significant_changes.append(f"{severity} 🇺🇸 {symbol}: {direction} {q['change_pct']:+.2f}%")
            
            if significant_changes:
                for change in significant_changes:
                    log(f"   {change}")
            else:
                log("   🟢 无显著变化")
            
            # 5. 保存持仓快照
            snapshot = {
                'timestamp': datetime.now().isoformat(),
                'holdings': holdings,
                'quotes': us_quotes,
            }
            with open(HOLDINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(snapshot, f, indent=2, ensure_ascii=False, default=str)
            
            # 6. 等待下次刷新
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
