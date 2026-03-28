#!/usr/bin/env python3
"""
Fetch US stock prices for 锋哥's portfolio using East Money API
Benchmark date: 2026-03-16
"""

import requests
import json
from datetime import datetime

# Portfolio data from USER.md
# Note: BRK-B needs special handling as it might be BRKB on East Money
portfolio = {
    'GOOGL': {'shares': 583, 'name': '谷歌', 'secid': '105.GOOGL'},
    'BRKB': {'shares': 207, 'name': '伯克希尔', 'secid': '105.BRKB'},
    'KO': {'shares': 1589, 'name': '可口可乐', 'secid': '105.KO'},
    'ORCL': {'shares': 647, 'name': '甲骨文', 'secid': '105.ORCL'},
    'MSFT': {'shares': 156, 'name': '微软', 'secid': '105.MSFT'},
    'NVDA': {'shares': 287, 'name': '英伟达', 'secid': '105.NVDA'},
    'AAPL': {'shares': 191, 'name': '苹果', 'secid': '105.AAPL'},
    'TSLA': {'shares': 178, 'name': '特斯拉', 'secid': '105.TSLA'},
}

# Benchmark prices from USER.md (2026-03-16)
# These need to be looked up or estimated from the baseline data
# From USER.md, we have the baseline holdings but not exact prices
# We'll need to fetch historical data or use the baseline from the document

# API endpoint for current stock data
CURRENT_API = "https://push2.eastmoney.com/api/qt/stock/get"
# API endpoint for historical K-line data
HISTORY_API = "https://push2his.eastmoney.com/api/qt/stock/kline/get"

def get_current_price(secid):
    """Fetch current stock price from East Money API"""
    params = {
        'secid': secid,
        'fields': 'f43,f57,f58,f60,f169,f170',  # current, symbol, name, prevClose, change, changePct
    }
    try:
        resp = requests.get(CURRENT_API, params=params, timeout=10)
        data = resp.json()
        if data.get('rc') == 0 and data.get('data'):
            d = data['data']
            # Prices are in cents (multiply by 0.001 to get dollars)
            current = d.get('f43', 0) * 0.001
            prev_close = d.get('f60', 0) * 0.001
            change = d.get('f169', 0) * 0.001
            change_pct = d.get('f170', 0) * 0.01  # Already in percentage
            return {
                'current': current,
                'prev_close': prev_close,
                'change': change,
                'change_pct': change_pct,
            }
    except Exception as e:
        print(f"Error fetching {secid}: {e}")
    return None

def get_historical_price(secid, date):
    """Fetch historical stock price for a specific date"""
    # Convert date to format needed (YYYYMMDD)
    date_str = date.replace('-', '')
    params = {
        'secid': secid,
        'klt': 101,  # Daily K-line
        'fqt': 1,  # Adjusted
        'beg': date_str,
        'end': date_str,
        'fields1': 'f1,f2,f3,f4,f5,f6',
        'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
    }
    try:
        resp = requests.get(HISTORY_API, params=params, timeout=10)
        data = resp.json()
        if data.get('data') and data['data'].get('klines'):
            # K-line format: date,open,close,high,low,volume,turnover,...
            kline = data['data']['klines'][0].split(',')
            close_price = float(kline[2])  # Close price
            return close_price
    except Exception as e:
        print(f"Error fetching history for {secid}: {e}")
    return None

print(f"Fetching US stock data for 锋哥's portfolio...\n")
print(f"Benchmark Date: 2026-03-16\n")

results = []

for symbol, data in portfolio.items():
    secid = data['secid']
    print(f"Fetching {symbol} ({data['name']})...")
    
    # Get current price
    current_data = get_current_price(secid)
    if not current_data:
        print(f"  ✗ Failed to fetch current price")
        continue
    
    # Get historical price for benchmark date
    benchmark_price = get_historical_price(secid, '2026-03-16')
    if not benchmark_price:
        print(f"  ✗ Failed to fetch benchmark price")
        continue
    
    shares = data['shares']
    current_price = current_data['current']
    prev_close = current_data['prev_close']
    change = current_data['change']
    change_pct = current_data['change_pct']
    
    # Calculate metrics
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
    
    print(f"  ✓ Current: ${current_price:.2f}, Change: ${change:+.2f} ({change_pct:+.2f}%)")

# Print summary table
print("\n" + "="*130)
print(f"{'股票代码':<10} {'名称':<12} {'持仓':<8} {'最新股价':<12} {'今日涨跌':<18} {'较基准价变化':<20} {'持仓市值':<16} {'持仓盈亏':<18}")
print("="*130)

total_market_value = 0
total_profit_loss = 0

for r in results:
    change_str = f"${r['change']:+.2f} ({r['change_pct']:+.2f}%)"
    benchmark_change_str = f"${r['change_from_benchmark']:+.2f} ({r['change_from_benchmark_pct']:+.2f}%)"
    market_value_str = f"${r['market_value']:,.2f}"
    profit_loss_str = f"${r['profit_loss']:+,.2f} ({r['profit_loss_pct']:+.2f}%)"
    
    # Color coding (using Unicode for visual indication)
    profit_indicator = "✅" if r['profit_loss'] >= 0 else "❌"
    
    print(f"{r['symbol']:<10} {r['name']:<12} {r['shares']:<8} ${r['current_price']:<11.2f} {change_str:<18} {benchmark_change_str:<20} {market_value_str:<16} {profit_loss_str:<18} {profit_indicator}")
    
    total_market_value += r['market_value']
    total_profit_loss += r['profit_loss']

print("="*130)
print(f"{'总计':<38} {'':<8} {'':<12} {'':<18} {'':<20} ${total_market_value:,.2f} ${total_profit_loss:+,.2f}")
print("="*130)

# Output JSON for structured data
print("\n\nJSON Output:")
print(json.dumps(results, indent=2, ensure_ascii=False))

# Calculate total benchmark value for reference
total_benchmark = sum(r['benchmark_price'] * r['shares'] for r in results)
print(f"\nTotal Benchmark Value (2026-03-16): ${total_benchmark:,.2f}")
print(f"Total Return: {((total_market_value - total_benchmark) / total_benchmark * 100):+.2f}%")
