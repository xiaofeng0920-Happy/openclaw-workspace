#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QVeris 数据获取模块
支持：指数行情、个股价格、资金流向、财经新闻等
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

# QVeris 配置
QVERIS_CONFIG = {
    'api_key': os.environ.get('QVERIS_API_KEY', 'sk-85Z4EEYSR-0A4ifflY7zcHCPOCt_b8ARlMWCQleVvMQ'),
    'cli_path': Path.home() / '.openclaw' / 'skills' / 'qveris-official' / 'scripts' / 'qveris_tool.mjs',
}

def run_qveris_command(args, timeout=60):
    """运行 QVeris CLI 命令"""
    cmd = ['node', str(QVERIS_CONFIG['cli_path'])] + args
    env = os.environ.copy()
    env['QVERIS_API_KEY'] = QVERIS_CONFIG['api_key']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
        output = result.stdout.strip() if result.stdout else ''
        
        # QVeris CLI 输出包含人类可读文本 + JSON
        # 尝试从输出中提取 JSON
        if output.startswith('{') or output.startswith('['):
            return json.loads(output)
        else:
            # 返回原始输出，由调用者解析
            return {'raw': output, 'stderr': result.stderr}
    except json.JSONDecodeError as e:
        print(f"QVeris JSON 解析失败：{e}")
        return {'raw': result.stdout, 'stderr': result.stderr, 'error': str(e)}
    except Exception as e:
        print(f"QVeris 命令异常：{e}")
        return None

def discover_tools(query, limit=5):
    """发现工具"""
    result = run_qveris_command(['discover', query, '--limit', str(limit)])
    if result and 'data' in result:
        return result['data']
    return []

def call_tool(tool_id, discovery_id, params=None):
    """调用工具"""
    if params is None:
        params = {}
    
    args = [
        'call', tool_id,
        '--discovery-id', discovery_id,
        '--params', json.dumps(params)
    ]
    
    result = run_qveris_command(args, timeout=90)
    if result and 'data' in result:
        return result['data']
    return None

# ============== 指数数据 ==============

def get_index_quotes(codes):
    """
    获取指数实时行情
    codes: 指数代码列表，如 ['000300.SH', '000016.SH', 'HSI.HK']
    """
    # 发现工具
    discovery = discover_tools("中国指数行情 沪深 300 恒生指数")
    if not discovery:
        print("未发现指数行情工具")
        return None
    
    # 使用同花顺实时行情工具
    tool_id = 'ths_ifind.real_time_quotation.v1'
    discovery_id = None
    for tool in discovery:
        if 'ths_ifind.real_time_quotation' in tool.get('id', ''):
            tool_id = tool['id']
            discovery_id = tool.get('discovery_id')
            break
    
    if not discovery_id:
        # 使用新的发现
        result = run_qveris_command(['discover', 'iFinD real-time quotation', '--limit', '3'])
        if result and 'data' in result:
            for tool in result['data']:
                if 'ths_ifind.real_time_quotation' in tool.get('id', ''):
                    tool_id = tool['id']
                    discovery_id = tool.get('discovery_id')
                    break
    
    if not discovery_id:
        print("未找到合适的指数行情工具")
        return None
    
    # 调用工具
    codes_str = ','.join(codes)
    data = call_tool(tool_id, discovery_id, {'codes': codes_str})
    
    if data:
        # 解析返回数据
        results = []
        for item in data:
            if isinstance(item, list) and len(item) > 0:
                quote = item[0]
                results.append({
                    'code': quote.get('thscode', ''),
                    'name': quote.get('name', ''),
                    'price': quote.get('latest', 0),
                    'change': quote.get('change', 0),
                    'change_pct': quote.get('changeRatio', 0),
                    'volume': quote.get('volume', 0),
                    'amount': quote.get('amount', 0),
                    'high': quote.get('high', 0),
                    'low': quote.get('low', 0),
                    'open': quote.get('open', 0),
                    'pre_close': quote.get('preClose', 0),
                })
        return results
    
    return None

# ============== 个股数据 ==============

def get_stock_quotes(codes):
    """
    获取个股实时行情
    codes: 股票代码列表，如 ['600519.SH', '00700.HK', 'AAPL.US']
    """
    return get_index_quotes(codes)  # 同花顺工具支持股票和指数

def get_stock_news(symbol, limit=10):
    """
    获取股票相关新闻
    symbol: 股票代码或名称
    """
    discovery = discover_tools("财经新闻 股市新闻")
    if not discovery:
        return []
    
    tool_id = 'finnhub.news.execute.v1'
    discovery_id = None
    for tool in discovery:
        if 'finnhub.news' in tool.get('id', ''):
            tool_id = tool['id']
            discovery_id = tool.get('discovery_id')
            break
    
    if not discovery_id:
        return []
    
    data = call_tool(tool_id, discovery_id, {'category': 'general'})
    if data and isinstance(data, list):
        news = []
        for item in data[:limit]:
            news.append({
                'title': item.get('headline', ''),
                'source': item.get('source', ''),
                'time': item.get('datetime', 0),
                'url': item.get('url', ''),
                'summary': item.get('summary', ''),
            })
        return news
    
    return []

# ============== 资金流向 ==============

def get_sector_moneyflow(date=None):
    """
    获取行业资金流向
    date: 日期，格式 YYYY-MM-DD，默认今天
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    discovery = discover_tools("A 股资金流向 行业板块")
    if not discovery:
        return [], []
    
    # 尝试使用同花顺资金流向工具
    tool_id = 'ths_ifind.money_flow.v1'
    discovery_id = None
    for tool in discovery:
        if 'ths_ifind.money_flow' in tool.get('id', ''):
            tool_id = tool['id']
            discovery_id = tool.get('discovery_id')
            break
    
    if not discovery_id:
        return [], []
    
    # 使用行业代码列表
    sector_codes = [f'THS_{i:03d}' for i in range(1, 31)]
    codes_str = ','.join(sector_codes)
    
    data = call_tool(tool_id, discovery_id, {
        'scope': 'sector',
        'codes': codes_str,
        'startdate': date
    })
    
    if data:
        # 解析数据
        sectors = []
        for item in data:
            if isinstance(item, list) and len(item) > 0:
                sector = item[0]
                if sector.get('sector_name'):  # 有行业名称
                    sectors.append({
                        'code': sector.get('code', ''),
                        'name': sector.get('sector_name', ''),
                        'net_inflow': sector.get('main_net_inflow', 0),
                        'change_pct': sector.get('change_pct', 0),
                    })
        
        # 排序
        sectors_sorted = sorted(sectors, key=lambda x: x['net_inflow'] or 0, reverse=True)
        inflow_top10 = sectors_sorted[:10]
        outflow_top10 = sectors_sorted[-10:][::-1]
        
        return inflow_top10, outflow_top10
    
    return [], []

# ============== 创新高股票 ==============

def get_new_high_stocks(limit=10):
    """
    获取创新高股票
    """
    discovery = discover_tools("股票创新高 新高股票")
    if not discovery:
        return []
    
    # 目前 QVeris 没有直接的创新高工具，返回空列表
    # 后续可以扩展
    return []

# ============== 市场数据综合 ==============

def get_market_daily_report():
    """
    获取市场日报数据
    返回：指数、资金流向、新闻等综合数据
    """
    print("正在获取指数数据...")
    indices = get_index_quotes([
        '000300.SH',  # 沪深 300
        '000016.SH',  # 上证 50
        '000905.SH',  # 中证 500
        '000688.SH',  # 科创 50
        'H30269.CSI', # 中证红利
        'H50040.CSI', # 上证红利
        'HSI.HK',     # 恒生指数
        '399050.SZ',  # 创业板 50
    ])
    
    print("正在获取资金流向...")
    inflow, outflow = get_sector_moneyflow()
    
    print("正在获取财经新闻...")
    news = get_stock_news('general', limit=10)
    
    print("正在获取创新高股票...")
    new_highs = get_new_high_stocks()
    
    return {
        'indices': indices or [],
        'inflow_top10': inflow,
        'outflow_top10': outflow,
        'news': news,
        'new_highs': new_highs,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }

if __name__ == "__main__":
    # 测试
    print("=" * 60)
    print("QVeris 数据模块测试")
    print("=" * 60)
    
    # 测试指数行情
    print("\n1. 测试指数行情...")
    indices = get_index_quotes(['000300.SH', 'HSI.HK'])
    if indices:
        for idx in indices:
            print(f"   {idx['code']}: {idx['price']:.2f} ({idx['change_pct']:+.2f}%)")
    else:
        print("   获取失败")
    
    # 测试资金流向
    print("\n2. 测试资金流向...")
    inflow, outflow = get_sector_moneyflow()
    print(f"   流入行业：{len(inflow)} 个")
    print(f"   流出行业：{len(outflow)} 个")
    
    # 测试新闻
    print("\n3. 测试财经新闻...")
    news = get_stock_news('general', limit=5)
    for n in news[:3]:
        print(f"   - {n['title'][:50]}...")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
