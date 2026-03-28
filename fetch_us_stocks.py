#!/usr/bin/env python3
"""
Fetch US stock prices for 锋哥's portfolio
Benchmark date: 2026-03-16
"""

import yfinance as yf
import time
import random
from datetime import datetime

# Portfolio data from USER.md
portfolio = {
    'GOOGL': {'shares': 583, 'name': '谷歌'},
    'BRK-B': {'shares': 207, 'name': '伯克希尔'},
    'KO': {'shares': 1589, 'name': '可口可乐'},
    'ORCL': {'shares': 647, 'name': '甲骨文'},
    'MSFT': {'shares': 156, 'name': '微软'},
    'NVDA': {'shares': 287, 'name': '英伟达'},
    'AAPL': {'shares': 191, 'name': '苹果'},
    'TSLA': {'shares': 178, 'name': '特斯拉'},
}

# Benchmark date
benchmark_date = '2026-03-16'

print(f"Fetching US stock data...\n")
print(f"Benchmark Date: {benchmark_date}\n")

results = []

for i, (symbol, data) in enumerate(portfolio.items()):
    try:
        # Add delay between requests to avoid rate limiting
        if i > 0:
            delay = random.uniform(2, 4)
            time.sleep(delay)
        
        stock = yf.Ticker(symbol)
        
        # Get current price info
        info = stock.info
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        
        # Get today's change
        prev_close = info.get('previousClose', 0)
        change = current_price - prev_close if prev_close else 0
        change_pct = (change / prev_close * 100) if prev_close else 0
        
        # Get benchmark price (2026-03-16)
        time.sleep(1)  # Additional delay before history request
        hist = stock.history(start='2026-03-16', end='2026-03-17')
        benchmark_price = hist['Close'].iloc[0] if not hist.empty else 0
        
        # Calculate metrics
        shares = data['shares']
        market_value = current_price * shares
        benchmark_value = benchmark_price * shares
        profit_loss = market_value - benchmark_value
        profit_loss_pct = (profit_loss / benchmark_value * 100) if benchmark_value else 0
        change_from_benchmark = current_price - benchmark_price
        change_from_benchmark_pct = (change_from_benchmark / benchmark_price * 100) if benchmark_price else 0
        
        results.append({
            'symbol': symbol,
            'name': data['name'],
            'shares': shares,
            'current_price': current_price,
            'change': change,
            'change_pct': change_pct,
            'benchmark_price': benchmark_price,
            'change_from_benchmark': change_from_benchmark,
            'change_from_benchmark_pct': change_from_benchmark_pct,
            'market_value': market_value,
            'profit_loss': profit_loss,
            'profit_loss_pct': profit_loss_pct,
        })
        
        print(f"✓ {symbol} ({data['name']}): ${current_price:.2f}")
        
    except Exception as e:
        print(f"✗ {symbol}: Error - {e}")
        results.append({
            'symbol': symbol,
            'name': data['name'],
            'shares': data['shares'],
            'current_price': 0,
            'error': str(e),
        })
        # Longer delay on error
        time.sleep(5)

# Print summary table
print("\n" + "="*120)
print(f"{'股票代码':<10} {'名称':<12} {'持仓':<8} {'最新股价':<12} {'今日涨跌':<15} {'较基准价变化':<18} {'持仓市值':<15} {'持仓盈亏':<15}")
print("="*120)

total_market_value = 0
total_profit_loss = 0

for r in results:
    if 'error' in r:
        print(f"{r['symbol']:<10} {r['name']:<12} {r['shares']:<8} {'N/A':<12} {'N/A':<15} {'N/A':<18} {'N/A':<15} {'N/A':<15}")
    else:
        change_str = f"${r['change']:+.2f} ({r['change_pct']:+.2f}%)".replace('+', '')
        benchmark_change_str = f"${r['change_from_benchmark']:+.2f} ({r['change_from_benchmark_pct']:+.2f}%)".replace('+', '')
        market_value_str = f"${r['market_value']:,.2f}"
        profit_loss_str = f"${r['profit_loss']:+,.2f} ({r['profit_loss_pct']:+.2f}%)".replace('+', '')
        
        print(f"{r['symbol']:<10} {r['name']:<12} {r['shares']:<8} ${r['current_price']:<11.2f} {change_str:<15} {benchmark_change_str:<18} {market_value_str:<15} {profit_loss_str:<15}")
        
        total_market_value += r['market_value']
        total_profit_loss += r['profit_loss']

print("="*120)
print(f"{'总计':<38} {'':<8} {'':<12} {'':<15} {'':<18} ${total_market_value:,.2f} ${total_profit_loss:+,.2f}")
print("="*120)

# Output JSON for structured data
import json
print("\n\nJSON Output:")
print(json.dumps(results, indent=2, ensure_ascii=False))
