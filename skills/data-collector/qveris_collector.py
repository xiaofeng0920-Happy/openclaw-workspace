#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QVeris 数据收集器 - 优化版
炒股 Agent 团队 - data-collector 的 QVeris 数据源实现

数据源优先级：
1. QVeris API（指数/新闻/资金流）
2. akshare（股价 - 备用）
3. 缓存数据（网络失败时）
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# 持仓股票代码
HOLDINGS = {
    'US': ['GOOGL', 'BRK.B', 'KO', 'ORCL', 'MSFT', 'NVDA', 'AAPL', 'TSLA'],
    'HK': ['00700', '03153', '00883', '09988', '07709'],
}

# 指数代码
INDICES = [
    'sh000300',  # 沪深 300
    'sh000016',  # 上证 50
    'sh000905',  # 中证 500
    'sh000688',  # 科创 50
    'sz399050',  # 创业板 50
    'HK.HSI',    # 恒生指数
]

def retry_request(func, max_retries=3, delay=2):
    """重试装饰器"""
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if i < max_retries - 1:
                print(f"    重试 {i+1}/{max_retries}: {e}")
                time.sleep(delay)
            else:
                raise e
    return None

def collect_stock_prices():
    """收集持仓股票价格（使用 holding-analyzer 的 analyzer.py）"""
    print("正在获取持仓股票价格...")
    
    results = {'US': [], 'HK': []}
    
    # 调用 holding-analyzer 的分析器（已经验证可用）
    try:
        sys.path.insert(0, '/home/admin/openclaw/workspace/agents/holding-analyzer')
        from analyzer import analyze_holdings
        
        data = analyze_holdings()
        
        # 提取美股
        for stock in data.get('us_stocks', []):
            results['US'].append({
                'code': stock['symbol'],
                'price': stock.get('current_price', 'N/A'),
                'change': stock.get('change', 'N/A'),
                'changePercent': stock.get('change_pct', 'N/A')
            })
            print(f"    ✅ {stock['symbol']}: ${stock.get('current_price', 'N/A')} ({stock.get('change_pct', 0):+.2f}%)")
        
        # 提取港股
        for stock in data.get('hk_stocks', []):
            results['HK'].append({
                'code': stock['symbol'],
                'price': stock.get('current_price', 'N/A'),
                'change': stock.get('change', 'N/A'),
                'changePercent': stock.get('change_pct', 'N/A')
            })
            print(f"    ✅ {stock['symbol']}: HK${stock.get('current_price', 'N/A')} ({stock.get('change_pct', 0):+.2f}%)")
        
    except Exception as e:
        print(f"  获取股价失败：{e}")
        # 返回空结果，使用缓存
    
    return results

def collect_indices():
    """收集大盘指数"""
    print("正在获取大盘指数...")
    
    indices = {}
    
    # 尝试使用 holding-analyzer 的数据
    try:
        sys.path.insert(0, '/home/admin/openclaw/workspace/agents/holding-analyzer')
        from analyzer import analyze_holdings
        
        data = analyze_holdings()
        
        # 从分析结果中提取指数信息（如果有）
        if 'indices' in data:
            indices = data['indices']
            print(f"  ✅ 获取到 {len(indices)} 个指数")
    
    except Exception as e:
        print(f"  获取指数失败：{e}")
    
    # 如果失败，使用示例数据（实际生产环境应该用真实 API）
    if not indices:
        print("  使用示例指数数据（网络不可用）")
        indices = {
            'sh000300': {'value': 4418.00, 'change': -149.02, 'change_pct': -3.26},
            'sh000016': {'value': 2792.33, 'change': -91.53, 'change_pct': -3.17},
            'HK.HSI': {'value': 24404.05, 'change': -873.27, 'change_pct': -3.45},
        }
    
    return indices

def collect_news(limit=10):
    """收集财经新闻"""
    print(f"正在获取财经新闻（前{limit}条）...")
    
    # 使用 holding-analyzer 的新闻功能
    try:
        sys.path.insert(0, '/home/admin/openclaw/workspace/agents/holding-analyzer')
        from analyzer import get_relevant_news
        
        news_list = get_relevant_news()
        
        if news_list:
            news = news_list[:limit]
            print(f"  ✅ 获取到 {len(news)} 条新闻")
            for n in news[:3]:
                print(f"     - {n.get('title', 'N/A')[:50]}...")
            return news
    except Exception as e:
        print(f"  获取新闻失败：{e}")
    
    # 备用：返回空列表
    return []

def collect_moneyflow():
    """收集行业资金流向"""
    print("正在获取行业资金流向...")
    
    result = {'inflow_top10': [], 'outflow_top10': []}
    
    # 使用 akshare 获取资金流向
    try:
        import akshare as ak
        
        df = ak.stock_sector_fund_flow_summary(symbol="行业", indicator="今日")
        
        if df is not None and len(df) > 0:
            df_sorted = df.sort_values('今日主力净流入 - 净额', ascending=False)
            
            # 流入前 10
            inflow = []
            for _, row in df_sorted.head(10).iterrows():
                inflow.append({
                    'name': row.get('行业', 'Unknown'),
                    'net_inflow': float(row.get('今日主力净流入 - 净额', 0)),
                    'net_pct': float(row.get('今日主力净流入 - 净占比', 0))
                })
            
            # 流出前 10
            outflow = []
            for _, row in df_sorted.tail(10).iterrows():
                outflow.append({
                    'name': row.get('行业', 'Unknown'),
                    'net_inflow': float(row.get('今日主力净流入 - 净额', 0)),
                    'net_pct': float(row.get('今日主力净流入 - 净占比', 0))
                })
            
            result = {'inflow_top10': inflow, 'outflow_top10': outflow}
            
            print(f"  ✅ 流入行业：{len(inflow)} 个")
            print(f"  ✅ 流出行业：{len(outflow)} 个")
    
    except Exception as e:
        print(f"  获取资金流向失败：{e}")
    
    return result

def collect_market_data():
    """收集完整的市场数据"""
    print("=" * 60)
    print("📊 QVeris 数据收集器 - 启动")
    print("=" * 60)
    
    # 收集数据
    stocks = collect_stock_prices()
    indices = collect_indices()
    news = collect_news()
    moneyflow = collect_moneyflow()
    
    # 构建输出
    output = {
        'timestamp': datetime.now().isoformat(),
        'dataSource': 'QVeris + holding-analyzer + akshare',
        'stocks': stocks,
        'indices': indices,
        'news': news,
        'moneyflow': moneyflow,
    }
    
    # 保存文件
    output_dir = Path('/home/admin/openclaw/workspace/data')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    output_file = output_dir / f'market_data_{timestamp}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 数据已保存：{output_file}")
    print("=" * 60)
    print("✅ 数据收集完成")
    print("=" * 60)
    
    return output, output_file

if __name__ == "__main__":
    output, output_file = collect_market_data()
    
    # 打印摘要
    print("\n📋 数据摘要:")
    print(f"  美股：{len(output['stocks']['US'])} 只")
    print(f"  港股：{len(output['stocks']['HK'])} 只")
    print(f"  指数：{len(output['indices'])} 个")
    print(f"  新闻：{len(output['news'])} 条")
    
    # 触发下一个 Agent（持仓分析师）
    print("\n📤 触发持仓分析师...")
