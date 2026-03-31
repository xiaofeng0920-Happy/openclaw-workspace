#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Public-apis.org 数据源集成模块
从全球免费 API 集合获取补充数据

安全等级：✅ 已扫描，低风险
集成日期：2026-03-29
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

# ============== 配置 ==============

# Public-apis 分类（与量化相关）
QUANT_RELATED_CATEGORIES = [
    "finance",
    "economics",
    "cryptocurrency",
    "stock",
    "currency",
    "weather",  # 商品期货相关
]

# 推荐使用的免费 API（已验证）
RECOMMENDED_APIS = {
    "finance": [
        {
            "name": "Alpha Vantage",
            "url": "https://www.alphavantage.co/query",
            "description": "股票/外汇/加密货币数据",
            "auth": "API Key (免费)",
            "rate_limit": "5 次/分钟 (免费)",
            "use_case": "美股实时股价、历史数据"
        },
        {
            "name": "Financial Modeling Prep",
            "url": "https://financialmodelingprep.com/api/v3",
            "description": "财务数据、财报",
            "auth": "API Key (免费 250 次/天)",
            "rate_limit": "250 次/天",
            "use_case": "公司财报、财务指标"
        },
        {
            "name": "Yahoo Finance API",
            "url": "https://query1.finance.yahoo.com/v8/finance/chart",
            "description": "股票行情数据",
            "auth": "无需认证",
            "rate_limit": "未公开",
            "use_case": "股价、K 线数据"
        }
    ],
    "economics": [
        {
            "name": "FRED API",
            "url": "https://api.stlouisfed.org/fred",
            "description": "美国经济数据",
            "auth": "API Key (免费)",
            "rate_limit": "120 次/分钟",
            "use_case": "GDP、CPI、利率等宏观数据"
        }
    ],
    "cryptocurrency": [
        {
            "name": "CoinGecko",
            "url": "https://api.coingecko.com/api/v3",
            "description": "加密货币数据",
            "auth": "无需认证 (免费)",
            "rate_limit": "10-50 次/分钟",
            "use_case": "比特币、以太坊价格"
        }
    ]
}

# ============== 数据获取 ==============

def fetch_public_apis_list(category: str = "finance") -> List[Dict]:
    """
    从 public-apis.org 获取指定类别的 API 列表
    
    Args:
        category: API 类别 (finance, economics, etc.)
    
    Returns:
        API 列表
    """
    try:
        # public-apis 的 GitHub 原始数据
        url = "https://raw.githubusercontent.com/public-apis/public-apis/master/data/data.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        apis = data.get("entries", [])
        
        # 过滤指定类别
        filtered = [api for api in apis if api.get("Category", "").lower() == category.lower()]
        
        return filtered[:20]  # 限制返回数量
    except Exception as e:
        print(f"⚠️ 获取 public-apis 失败：{e}")
        return []

def get_alpha_vantage_quote(symbol: str, api_key: str) -> Optional[Dict]:
    """
    使用 Alpha Vantage 获取股票报价
    
    Args:
        symbol: 股票代码 (如 AAPL)
        api_key: Alpha Vantage API Key
    
    Returns:
        报价数据字典
    """
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        quote = data.get("Global Quote", {})
        
        if quote:
            return {
                "symbol": quote.get("01. symbol"),
                "price": float(quote.get("05. price", 0)),
                "change": float(quote.get("09. change", 0)),
                "change_percent": quote.get("10. change percent"),
                "volume": int(quote.get("06. volume", 0)),
                "timestamp": quote.get("07. latest trading day")
            }
        return None
    except Exception as e:
        print(f"⚠️ Alpha Vantage 获取失败 ({symbol}): {e}")
        return None

def get_yahoo_finance_quote(symbol: str) -> Optional[Dict]:
    """
    使用 Yahoo Finance 获取股票报价（无需 API Key）
    
    Args:
        symbol: 股票代码 (如 AAPL)
    
    Returns:
        报价数据字典
    """
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {
            "interval": "1d",
            "range": "1d"
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        result = data.get("chart", {}).get("result", [])
        
        if result and len(result) > 0:
            meta = result[0].get("meta", {})
            quote = {
                "symbol": meta.get("symbol"),
                "price": meta.get("regularMarketPrice"),
                "change": meta.get("regularMarketChange"),
                "change_percent": meta.get("regularMarketChangePercent"),
                "volume": meta.get("regularMarketVolume"),
                "timestamp": datetime.fromtimestamp(meta.get("regularMarketTime", 0)).strftime("%Y-%m-%d")
            }
            return quote
        return None
    except Exception as e:
        print(f"⚠️ Yahoo Finance 获取失败 ({symbol}): {e}")
        return None

def get_coingecko_price(coin_id: str = "bitcoin") -> Optional[Dict]:
    """
    使用 CoinGecko 获取加密货币价格（无需 API Key）
    
    Args:
        coin_id: 加密货币 ID (bitcoin, ethereum, etc.)
    
    Returns:
        价格数据字典
    """
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_24hr_vol": "true"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if coin_id in data:
            coin_data = data[coin_id]
            return {
                "name": coin_id,
                "price_usd": coin_data.get("usd"),
                "change_24h": coin_data.get("usd_24h_change"),
                "volume_24h": coin_data.get("usd_24h_vol")
            }
        return None
    except Exception as e:
        print(f"⚠️ CoinGecko 获取失败 ({coin_id}): {e}")
        return None

# ============== 集成测试 ==============

def test_all_apis():
    """测试所有集成的 API"""
    print("=" * 60)
    print("🔌 Public-apis 集成测试")
    print("=" * 60)
    
    # 测试 Yahoo Finance（无需 API Key）
    print("\n1️⃣ 测试 Yahoo Finance...")
    quote = get_yahoo_finance_quote("AAPL")
    if quote:
        print(f"   ✅ AAPL: ${quote['price']:.2f} ({quote['change_percent']:+.2f}%)")
    else:
        print("   ❌ 失败")
    
    # 测试 CoinGecko
    print("\n2️⃣ 测试 CoinGecko...")
    crypto = get_coingecko_price("bitcoin")
    if crypto:
        print(f"   ✅ BTC: ${crypto['price_usd']:.2f} ({crypto['change_24h']:+.2f}%)")
    else:
        print("   ❌ 失败")
    
    # 测试 public-apis 列表
    print("\n3️⃣ 测试 public-apis 列表...")
    apis = fetch_public_apis_list("finance")
    if apis:
        print(f"   ✅ 找到 {len(apis)} 个金融类 API")
        for api in apis[:3]:
            print(f"      - {api.get('API', 'Unknown')}: {api.get('Description', '')[:50]}")
    else:
        print("   ❌ 失败")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)

# ============== 主程序 ==============

if __name__ == "__main__":
    test_all_apis()
