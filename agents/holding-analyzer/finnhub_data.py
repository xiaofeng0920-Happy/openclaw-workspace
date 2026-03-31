#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finnhub 数据源集成模块

Finnhub 提供全球股票、外汇、加密货币实时行情数据。
免费套餐：60 次/分钟，支持美股实时行情。

API 文档：https://finnhub.io/docs/api

安全等级：✅ 已扫描，低风险
集成日期：2026-03-31
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# ============== 配置 ==============

# API Key（从环境变量或配置文件读取）
FINNHUB_API_KEY = os.environ.get('FINNHUB_API_KEY', '')

# 配置文件路径
CONFIG_FILE = Path.home() / '.futu' / 'finnhub_config.json'

# 如果配置文件存在，从文件读取
if CONFIG_FILE.exists():
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            FINNHUB_API_KEY = config.get('api_key', FINNHUB_API_KEY)
    except:
        pass

# API 端点
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

# ============== 数据获取 ==============

def get_quote(symbol: str) -> Optional[Dict]:
    """
    获取实时股价
    
    Args:
        symbol: 股票代码（美股直接写代码，港股需要.SS 或.SZ 后缀）
    
    Returns:
        {
            'c': 当前价,
            'h': 最高价,
            'l': 最低价,
            'o': 开盘价,
            'pc': 昨收价,
            't': 时间戳
        }
    """
    if not FINNHUB_API_KEY:
        print("❌ Finnhub API Key 未配置")
        return None
    
    try:
        url = f"{FINNHUB_BASE_URL}/quote"
        params = {
            'symbol': symbol,
            'token': FINNHUB_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # 检查是否成功
        if data.get('c') is None:
            print(f"⚠️  无法获取 {symbol} 数据")
            return None
        
        return {
            'symbol': symbol,
            'price': data.get('c'),
            'high': data.get('h'),
            'low': data.get('l'),
            'open': data.get('o'),
            'prev_close': data.get('pc'),
            'change': data.get('c') - data.get('pc') if data.get('c') and data.get('pc') else 0,
            'change_pct': ((data.get('c') - data.get('pc')) / data.get('pc') * 100) if data.get('pc') else 0,
            'timestamp': data.get('t'),
        }
    
    except Exception as e:
        print(f"❌ 获取 {symbol} 失败：{e}")
        return None


def get_stock_symbols(exchange: str = "US") -> List[Dict]:
    """
    获取交易所股票列表
    
    Args:
        exchange: 交易所代码 (US, HK, SH, SZ)
    
    Returns:
        股票列表
    """
    if not FINNHUB_API_KEY:
        return []
    
    try:
        url = f"{FINNHUB_BASE_URL}/stock/symbol"
        params = {
            'exchange': exchange,
            'token': FINNHUB_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        return response.json()
    
    except Exception as e:
        print(f"❌ 获取股票列表失败：{e}")
        return []


def get_company_profile(symbol: str) -> Optional[Dict]:
    """
    获取公司简介
    
    Args:
        symbol: 股票代码
    
    Returns:
        公司简介信息
    """
    if not FINNHUB_API_KEY:
        return None
    
    try:
        url = f"{FINNHUB_BASE_URL}/stock/profile2"
        params = {
            'symbol': symbol,
            'token': FINNHUB_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if not data:
            return None
        
        return {
            'symbol': symbol,
            'name': data.get('name'),
            'sector': data.get('finnhubIndustry'),
            'description': data.get('description'),
            'website': data.get('website'),
            'market_cap': data.get('marketCapitalization'),
        }
    
    except Exception as e:
        print(f"❌ 获取公司简介失败：{e}")
        return None


def get_earnings(symbol: str) -> List[Dict]:
    """
    获取财报数据
    
    Args:
        symbol: 股票代码
    
    Returns:
        财报数据列表
    """
    if not FINNHUB_API_KEY:
        return []
    
    try:
        url = f"{FINNHUB_BASE_URL}/stock/earnings"
        params = {
            'symbol': symbol,
            'token': FINNHUB_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        return response.json()
    
    except Exception as e:
        print(f"❌ 获取财报失败：{e}")
        return []


def get_technical_indicator(symbol: str, indicator: str = "sma", 
                           resolution: str = "D", count: int = 30) -> Optional[Dict]:
    """
    获取技术指标
    
    Args:
        symbol: 股票代码
        indicator: 指标类型 (sma, ema, rsi, macd, etc.)
        resolution: 时间周期 (D=日，W=周，M=月)
        count: 数据点数
    
    Returns:
        技术指标数据
    """
    if not FINNHUB_API_KEY:
        return None
    
    try:
        url = f"{FINNHUB_BASE_URL}/indicator"
        params = {
            'symbol': symbol,
            'indicator': indicator,
            'resolution': resolution,
            'count': count,
            'token': FINNHUB_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        return response.json()
    
    except Exception as e:
        print(f"❌ 获取技术指标失败：{e}")
        return None


def get_market_news(category: str = "general", limit: int = 10) -> List[Dict]:
    """
    获取市场新闻
    
    Args:
        category: 新闻类别 (general, forex, crypto)
        limit: 返回数量
    
    Returns:
        新闻列表
    """
    if not FINNHUB_API_KEY:
        return []
    
    try:
        from datetime import timedelta
        
        # 获取今天和昨天的日期
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        url = f"{FINNHUB_BASE_URL}/news"
        params = {
            'category': category,
            'from': yesterday,
            'to': today,
            'token': FINNHUB_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        return data[:limit] if data else []
    
    except Exception as e:
        print(f"❌ 获取新闻失败：{e}")
        return []


# ============== 批量获取 ==============

def get_multiple_quotes(symbols: List[str]) -> Dict[str, Dict]:
    """
    批量获取多支股票价格
    
    Args:
        symbols: 股票代码列表
    
    Returns:
        {symbol: quote_data} 字典
    """
    results = {}
    
    print(f"📈 正在获取 {len(symbols)} 支股票行情...")
    
    for i, symbol in enumerate(symbols, 1):
        print(f"   [{i}/{len(symbols)}] {symbol}", end='\r')
        quote = get_quote(symbol)
        if quote:
            results[symbol] = quote
    
    print(f"✅ 完成 {len(results)}/{len(symbols)}")
    return results


# ============== 配置管理 ==============

def save_config(api_key: str):
    """保存 API Key 到配置文件"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    config = {
        'api_key': api_key,
        'updated': datetime.now().isoformat()
    }
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ 配置已保存：{CONFIG_FILE}")


def check_api_status() -> Dict:
    """检查 API 状态"""
    if not FINNHUB_API_KEY:
        return {
            'status': 'error',
            'message': 'API Key 未配置'
        }
    
    # 测试 API
    test_symbol = "AAPL"
    quote = get_quote(test_symbol)
    
    if quote:
        return {
            'status': 'ok',
            'message': 'API 正常',
            'test_symbol': test_symbol,
            'test_price': quote['price']
        }
    else:
        return {
            'status': 'error',
            'message': 'API 调用失败'
        }


# ============== 命令行 ==============

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("📊 Finnhub 数据源测试")
    print("=" * 60)
    
    # 检查 API 状态
    print("\n1️⃣  检查 API 状态...")
    status = check_api_status()
    print(f"   状态：{status['status']}")
    print(f"   消息：{status['message']}")
    
    if status['status'] == 'ok':
        print(f"   测试：{status['test_symbol']} = ${status['test_price']}")
    else:
        print("\n   💡 配置 API Key:")
        print("      1. 注册 Finnhub: https://finnhub.io/register")
        print("      2. 获取 API Key: https://finnhub.io/dashboard")
        print("      3. 设置环境变量：export FINNHUB_API_KEY=your_key")
        print("      或创建配置文件：~/.futu/finnhub_config.json")
        sys.exit(1)
    
    # 测试获取股价
    print("\n2️⃣  测试获取股价...")
    test_symbols = ["AAPL", "GOOGL", "TSLA", "NVDA", "MSFT"]
    
    for symbol in test_symbols:
        quote = get_quote(symbol)
        if quote:
            change_flag = "📈" if quote['change_pct'] > 0 else "📉" if quote['change_pct'] < 0 else "➖"
            print(f"   {change_flag} {symbol}: ${quote['price']:.2f} ({quote['change_pct']:+.2f}%)")
    
    # 测试获取公司简介
    print("\n3️⃣  测试获取公司简介...")
    profile = get_company_profile("AAPL")
    if profile:
        print(f"   公司：{profile['name']}")
        print(f"   行业：{profile['sector']}")
        print(f"   市值：${profile['market_cap']:,}" if profile['market_cap'] else "   市值：N/A")
    
    # 测试批量获取
    print("\n4️⃣  测试批量获取...")
    quotes = get_multiple_quotes(["AAPL", "GOOGL", "MSFT"])
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
