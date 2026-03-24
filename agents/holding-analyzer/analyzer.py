#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持仓分析 Agent - 锋哥的自主持仓监控助手
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, '/home/admin/openclaw/workspace')

try:
    import akshare as ak
except ImportError:
    print("请安装 akshare: pip install akshare")
    sys.exit(1)

# ============== 配置 ==============

# 基准日期
BENCHMARK_DATE = "2026-03-24"

# 持仓数据（来自富途截图 OCR 识别 - 2026-03-24）
HOLDINGS_US = {
    'GOOGL': {'name': '谷歌-A', 'shares': 583, 'benchmark': 299.86},
    'BRK.B': {'name': '伯克希尔', 'shares': 104, 'benchmark': 480.13},
    'KO': {'name': '可口可乐', 'shares': 1689, 'benchmark': 72.875},
    'ORCL': {'name': '甲骨文', 'shares': 647, 'benchmark': 152.65},
    'MSFT': {'name': '微软', 'shares': 156, 'benchmark': 381.73},
    'AAPL': {'name': '苹果', 'shares': 329, 'benchmark': 250.37},
    'TSLA': {'name': '特斯拉', 'shares': 178, 'benchmark': 391.20},
    'NVDA': {'name': '英伟达', 'shares': 287, 'benchmark': 180.25},
}

HOLDINGS_HK = {
    '00700': {'name': '腾讯控股', 'shares': 2500, 'benchmark': 547.50},
    '00883': {'name': '中海油', 'shares': 11000, 'benchmark': 29.76},
    '09988': {'name': '阿里巴巴', 'shares': 5800, 'benchmark': 132.50},
    '03153': {'name': '南方日经 225', 'shares': 12330, 'benchmark': 107.10},
    '07709': {'name': '南方两倍做多', 'shares': 27500, 'benchmark': 26.40},
    '03355': {'name': '飞速创新', 'shares': 100, 'benchmark': 45.80},
}

# 期权持仓（来自锋哥持仓_2026-03-16.md）
OPTIONS_HOLDINGS = [
    {'symbol': 'GOOGL', 'type': 'CALL', 'expiry': '2026-06-18', 'strike': 320, 'shares': 5, 'cost': 15.50, 'name': '谷歌看涨'},
    {'symbol': 'GOOGL', 'type': 'CALL', 'expiry': '2026-05-15', 'strike': None, 'shares': 5, 'cost': None, 'name': '谷歌看涨 (未知行权价)'},
    {'symbol': 'AAPL', 'type': 'CALL', 'expiry': '2026-05-15', 'strike': 285, 'shares': 4, 'cost': 5.00, 'name': '苹果看涨'},
    {'symbol': 'BRK.B', 'type': 'PUT', 'expiry': '2026-05-15', 'strike': 470, 'shares': -2, 'cost': 8.08, 'name': '伯克希尔看跌 (Short)'},
    {'symbol': 'NVDA', 'type': 'CALL', 'expiry': '2026-05-15', 'strike': 220, 'shares': 5, 'cost': 2.60, 'name': '英伟达看涨'},
    {'symbol': 'NVDA', 'type': 'PUT', 'expiry': '2027-01-15', 'strike': 125, 'shares': 2, 'cost': 7.50, 'name': '英伟达看跌'},
    # 港股期权
    {'symbol': '00883', 'type': 'CALL', 'expiry': '2028-04-29', 'strike': 42, 'shares': 15, 'cost': 19.30, 'name': '中海油认购', 'market': 'HK'},
    {'symbol': '00700', 'type': 'CALL', 'expiry': '2028-05-26', 'strike': 260, 'shares': 10, 'cost': 4.84, 'name': '腾讯认购', 'market': 'HK'},
    {'symbol': '09988', 'type': 'PUT', 'expiry': '2026-03-30', 'strike': 130, 'shares': -20, 'cost': 3.98, 'name': '阿里沽 (Short Put)', 'market': 'HK'},
    {'symbol': '09988', 'type': 'CALL', 'expiry': '2026-05-28', 'strike': 140, 'shares': 10, 'cost': 2.32, 'name': '阿里购', 'market': 'HK'},
]

# 预警阈值
ALERT_THRESHOLD = 3.0  # 3%

# ============== 数据获取 ==============

def get_us_stock_price(symbol):
    """获取美股价格"""
    try:
        df = ak.stock_us_daily(symbol=symbol)
        if df is not None and len(df) > 0:
            return float(df.iloc[-1]['close'])
    except Exception as e:
        print(f"获取美股 {symbol} 失败：{e}")
    return None

def get_hk_stock_price(symbol):
    """获取港股价格"""
    try:
        df = ak.stock_hk_daily(symbol=symbol, adjust="qfq")
        if df is not None and len(df) > 0:
            return float(df.iloc[-1]['close'])
    except Exception as e:
        print(f"获取港股 {symbol} 失败：{e}")
    return None

def get_stock_news(symbol, market="US"):
    """获取股票相关新闻（使用新浪财经/东方财富）"""
    news_list = []
    try:
        if market == "US":
            # 使用 akshare 获取美股财经新闻
            df = ak.stock_news_em(symbol=symbol)
            if df is not None and len(df) > 0:
                for _, row in df.head(5).iterrows():
                    news_list.append({
                        'title': row.get('新闻标题', 'N/A'),
                        'source': row.get('文章来源', 'N/A'),
                        'date': row.get('发布时间', 'N/A'),
                        'url': row.get('新闻链接', 'N/A')
                    })
        elif market == "HK":
            # 港股新闻（使用 akshare 的个股新闻）
            df = ak.stock_news_em(symbol=symbol)
            if df is not None and len(df) > 0:
                for _, row in df.head(5).iterrows():
                    news_list.append({
                        'title': row.get('新闻标题', 'N/A'),
                        'source': row.get('文章来源', 'N/A'),
                        'date': row.get('发布时间', 'N/A'),
                        'url': row.get('新闻链接', 'N/A')
                    })
    except Exception as e:
        print(f"获取 {symbol} 新闻失败：{e}")
    return news_list

# ============== 分析逻辑 ==============

def analyze_holdings():
    """分析持仓变化"""
    results = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'us_stocks': [],
        'hk_stocks': [],
        'significant_changes': [],
        'options_status': []
    }
    
    # 分析美股
    print("正在获取美股数据...")
    for symbol, data in HOLDINGS_US.items():
        current_price = get_us_stock_price(symbol)
        if current_price:
            change_pct = ((current_price - data['benchmark']) / data['benchmark']) * 100
            change_value = (current_price - data['benchmark']) * data['shares']
            market_value = current_price * data['shares']
            
            stock_info = {
                'symbol': symbol,
                'name': data['name'],
                'benchmark': data['benchmark'],
                'current': current_price,
                'change_pct': change_pct,
                'change_value': change_value,
                'market_value': market_value,
                'shares': data['shares']
            }
            results['us_stocks'].append(stock_info)
            
            if abs(change_pct) >= ALERT_THRESHOLD:
                results['significant_changes'].append(stock_info)
    
    # 分析港股
    print("正在获取港股数据...")
    for symbol, data in HOLDINGS_HK.items():
        current_price = get_hk_stock_price(symbol)
        if current_price:
            change_pct = ((current_price - data['benchmark']) / data['benchmark']) * 100
            change_value = (current_price - data['benchmark']) * data['shares']
            market_value = current_price * data['shares']
            
            stock_info = {
                'symbol': symbol,
                'name': data['name'],
                'benchmark': data['benchmark'],
                'current': current_price,
                'change_pct': change_pct,
                'change_value': change_value,
                'market_value': market_value,
                'shares': data['shares'],
                'market': 'HK'
            }
            results['hk_stocks'].append(stock_info)
            
            if abs(change_pct) >= ALERT_THRESHOLD:
                results['significant_changes'].append(stock_info)
    
    return results

def get_options_status():
    """获取期权持仓状态（简化版，基于正股价格估算）"""
    options_status = []
    
    for opt in OPTIONS_HOLDINGS:
        symbol = opt['symbol']
        market = opt.get('market', 'US')
        
        # 获取正股价格
        if market == 'HK':
            current_price = get_hk_stock_price(symbol)
        else:
            current_price = get_us_stock_price(symbol)
        
        if current_price and opt['cost']:
            # 简化估算：假设期权价格变化与正股变化成正比（实际更复杂）
            # 这里只展示基本信息，实际期权定价需要 Black-Scholes 模型
            opt_info = {
                'name': opt['name'],
                'symbol': symbol,
                'type': opt['type'],
                'expiry': opt['expiry'],
                'strike': opt['strike'],
                'shares': opt['shares'],
                'cost': opt['cost'],
                'stock_price': current_price,
                'intrinsic_value': max(0, (current_price - opt['strike']) * opt['shares']) if opt['type'] == 'CALL' else max(0, (opt['strike'] - current_price) * opt['shares']),
                'status': 'active'
            }
            options_status.append(opt_info)
    
    return options_status

def get_relevant_news():
    """获取持仓股票的相关新闻"""
    all_news = []
    
    # 获取重点股票新闻
    focus_stocks_us = ['NVDA', 'TSLA', 'MSFT', 'GOOGL', 'AAPL']
    focus_stocks_hk = ['00700', '09988', '00883']
    
    for symbol in focus_stocks_us:
        news = get_stock_news(symbol, "US")
        for n in news:
            n['symbol'] = symbol
            all_news.append(n)
    
    for symbol in focus_stocks_hk:
        news = get_stock_news(symbol, "HK")
        for n in news:
            n['symbol'] = symbol
            all_news.append(n)
    
    return all_news[:10]  # 返回最新 10 条

# ============== 报告生成 ==============

def generate_report(results, options_status, news):
    """生成 Markdown 报告"""
    lines = []
    lines.append("# 📊 持仓监控报告")
    lines.append(f"**生成时间：** {results['timestamp']}")
    lines.append(f"**基准日期：** {BENCHMARK_DATE}")
    lines.append("")
    
    # 显著变化
    if results['significant_changes']:
        lines.append("## ⚠️ 显著变化 (>{threshold}%)".format(threshold=ALERT_THRESHOLD))
        lines.append("")
        lines.append("| 股票 | 代码 | 基准价 | 现价 | 变化 | 市值影响 |")
        lines.append("|------|------|--------|------|------|---------|")
        
        for stock in sorted(results['significant_changes'], key=lambda x: abs(x['change_pct']), reverse=True):
            flag = "📈" if stock['change_pct'] > 0 else "📉"
            currency = "HK$" if stock.get('market') == 'HK' else "$"
            lines.append(f"| {stock['name']} | {stock['symbol']} | {currency}{stock['benchmark']:.2f} | {currency}{stock['current']:.2f} | {stock['change_pct']:+.2f}% | {currency}{stock['change_value']:,.0f} |")
        
        lines.append("")
    
    # 期权状态
    lines.append("## 📋 期权持仓状态")
    lines.append("")
    lines.append("| 名称 | 类型 | 到期日 | 行权价 | 正股价 | 状态 |")
    lines.append("|------|------|--------|--------|--------|------|")
    
    for opt in options_status:
        if opt['stock_price']:
            currency = "HK$" if opt.get('market') == 'HK' else "$"
            moneyness = "实值" if (opt['type'] == 'CALL' and opt['stock_price'] > opt['strike']) or (opt['type'] == 'PUT' and opt['stock_price'] < opt['strike']) else "虚值"
            lines.append(f"| {opt['name']} | {opt['type']} | {opt['expiry']} | {currency}{opt['strike']} | {currency}{opt['stock_price']:.2f} | {moneyness} |")
    
    lines.append("")
    
    # 新闻
    if news:
        lines.append("## 📰 相关新闻")
        lines.append("")
        for n in news[:5]:
            lines.append(f"- **{n['symbol']}**: {n['title']} ({n['source']}, {n['date']})")
        lines.append("")
    
    return "\n".join(lines)

def generate_report_futu(results, options_status, news):
    """生成 Markdown 报告（富途实盘数据版本）"""
    lines = []
    lines.append("# 📊 持仓监控报告 (富途实盘)")
    lines.append(f"**生成时间：** {results['timestamp']}")
    lines.append(f"**数据源：** 富途 OpenD")
    lines.append("")
    
    # 显著变化
    if results['significant_changes']:
        lines.append("## ⚠️ 显著变化 (>{threshold}%)".format(threshold=ALERT_THRESHOLD))
        lines.append("")
        lines.append("| 股票 | 代码 | 持仓 | 盈亏% | 盈亏金额 |")
        lines.append("|------|------|------|------|---------|")
        
        for stock in sorted(results['significant_changes'], key=lambda x: abs(x.get('pl_pct', x.get('change_pct', 0))), reverse=True):
            flag = "📈" if stock.get('pl_pct', stock.get('change_pct', 0)) > 0 else "📉"
            currency = "HK$" if stock.get('market') == 'HK' else "$"
            pct = stock.get('pl_pct', stock.get('change_pct', 0))
            pl = stock.get('pl', stock.get('change_value', 0))
            shares = stock.get('shares', 0)
            lines.append(f"| {flag} {stock.get('name', stock['symbol'])} | {stock['symbol']} | {shares:.0f} | {pct:+.2f}% | {currency}{pl:,.0f} |")
        
        lines.append("")
    
    # 全部持仓
    lines.append("## 📋 全部持仓")
    lines.append("")
    
    if results.get('us_stocks'):
        lines.append("### 美股")
        lines.append("| 股票 | 代码 | 持仓 | 盈亏% | 盈亏金额 |")
        lines.append("|------|------|------|------|---------|")
        for stock in results['us_stocks']:
            flag = "📈" if stock.get('pl_pct', 0) > 0 else "📉" if stock.get('pl_pct', 0) < 0 else ""
            pct = stock.get('pl_pct', 0)
            pl = stock.get('pl', 0)
            shares = stock.get('shares', 0)
            lines.append(f"| {flag} {stock.get('name', stock['symbol'])} | {stock['symbol']} | {shares:.0f} | {pct:+.2f}% | ${pl:,.0f} |")
        lines.append("")
    
    if results.get('hk_stocks'):
        lines.append("### 港股")
        lines.append("| 股票 | 代码 | 持仓 | 盈亏% | 盈亏金额 |")
        lines.append("|------|------|------|------|---------|")
        for stock in results['hk_stocks']:
            flag = "📈" if stock.get('pl_pct', 0) > 0 else "📉" if stock.get('pl_pct', 0) < 0 else ""
            pct = stock.get('pl_pct', 0)
            pl = stock.get('pl', 0)
            shares = stock.get('shares', 0)
            lines.append(f"| {flag} {stock.get('name', stock['symbol'])} | {stock['symbol']} | {shares:.0f} | {pct:+.2f}% | HK${pl:,.0f} |")
        lines.append("")
    
    # 期权状态
    if options_status:
        lines.append("## 📋 期权持仓")
        lines.append("")
        lines.append("| 名称 | 代码 | 持仓 | 成本 | 市值 | 盈亏 |")
        lines.append("|------|------|------|------|------|------|")
        
        for opt in options_status:
            currency = "HK$" if opt.get('market') == 'HK' else "$"
            pl = opt.get('pl', 0)
            pl_flag = "📈" if pl > 0 else "📉" if pl < 0 else ""
            lines.append(f"| {opt['name']} | {opt.get('symbol', opt.get('code', '-'))} | {opt['shares']:.0f} | {currency}{opt.get('cost', 0):.2f} | {currency}{opt.get('market_value', 0):.0f} | {pl_flag}{currency}{pl:,.0f} |")
        
        lines.append("")
    
    # 新闻
    if news:
        lines.append("## 📰 相关新闻")
        lines.append("")
        for n in news[:5]:
            lines.append(f"- **{n['symbol']}**: {n['title']} ({n['source']}, {n['date']})")
        lines.append("")
    
    return "\n".join(lines)


# ============== QVeris 市场日报 ==============

def generate_market_report(market_data):
    """生成 QVeris 市场日报"""
    from datetime import datetime
    
    lines = []
    lines.append("# 📊 A 股市场日报")
    lines.append(f"**日期：** {datetime.now().strftime('%Y-%m-%d')}")
    lines.append(f"**生成时间：** {market_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}")
    lines.append(f"**数据源：** QVeris API")
    lines.append("")
    
    # 一、指数表现
    indices = market_data.get('indices', [])
    if indices:
        lines.append("## 一、主要指数表现")
        lines.append("")
        lines.append("| 指数 | 代码 | 收盘价 | 涨跌 | 涨跌幅 |")
        lines.append("|------|------|--------|------|--------|")
        
        for idx in indices:
            flag = "📈" if idx['change_pct'] > 0 else "📉" if idx['change_pct'] < 0 else "➖"
            lines.append(f"| {flag} {idx.get('name', idx['code'])} | {idx['code']} | {idx['price']:.2f} | {idx['change']:+.2f} | {idx['change_pct']:+.2f}% |")
        
        lines.append("")
    
    # 二、资金流向
    inflow = market_data.get('inflow_top10', [])
    outflow = market_data.get('outflow_top10', [])
    
    if inflow or outflow:
        lines.append("## 二、行业资金流向")
        lines.append("")
        
        if inflow:
            lines.append("### 资金流入前 10 行业")
            lines.append("| 排名 | 行业 | 净流入 |")
            lines.append("|------|------|--------|")
            for i, sector in enumerate(inflow, 1):
                lines.append(f"| {i} | {sector.get('name', sector.get('code', '-'))} | {sector.get('net_inflow', 0):.2f} |")
            lines.append("")
        
        if outflow:
            lines.append("### 资金流出前 10 行业")
            lines.append("| 排名 | 行业 | 净流入 |")
            lines.append("|------|------|--------|")
            for i, sector in enumerate(outflow, 1):
                lines.append(f"| {i} | {sector.get('name', sector.get('code', '-'))} | {sector.get('net_inflow', 0):.2f} |")
            lines.append("")
    
    # 三、创新高股票
    new_highs = market_data.get('new_highs', [])
    if new_highs:
        lines.append("## 三、创新高股票")
        lines.append("")
        lines.append("| 排名 | 代码 | 名称 | 最新价 | 涨跌幅 |")
        lines.append("|------|------|------|--------|--------|")
        for i, stock in enumerate(new_highs, 1):
            lines.append(f"| {i} | {stock.get('code', '-')} | {stock.get('name', '-')} | {stock.get('price', 0):.2f} | {stock.get('change_pct', 0):+.2f}% |")
        lines.append("")
    
    # 四、财经新闻
    news = market_data.get('news', [])
    if news:
        lines.append("## 四、重要财经新闻")
        lines.append("")
        for i, n in enumerate(news[:10], 1):
            lines.append(f"{i}. **{n.get('title', '-')}** - {n.get('source', '-')}")
        lines.append("")
    
    # 五、市场展望
    lines.append("## 五、市场展望与风险提示")
    lines.append("")
    
    # 根据指数表现生成展望
    up_count = sum(1 for idx in indices if idx['change_pct'] > 0) if indices else 0
    down_count = len(indices) - up_count if indices else 0
    
    lines.append("### 市场展望")
    lines.append("")
    if up_count > down_count:
        lines.append("✅ 今日市场整体表现积极，多数指数上涨。")
    elif up_count == down_count:
        lines.append("⚖️ 今日市场震荡整理，指数涨跌互现。")
    else:
        lines.append("⚠️ 今日市场承压，多数指数下跌，需谨慎操作。")
    
    lines.append("")
    lines.append("### 风险提示")
    lines.append("")
    lines.append("1. **市场波动风险** - 关注指数关键支撑/阻力位")
    lines.append("2. **资金流向变化** - 持续跟踪主力资金动向")
    lines.append("3. **外部因素** - 关注宏观经济数据及政策变化")
    lines.append("4. **个股分化** - 创新高股票需警惕回调风险")
    lines.append("")
    lines.append("---")
    lines.append(f"*数据来源：QVeris API | 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    
    return "\n".join(lines)


# ============== 主函数 ==============

def main():
    print("=" * 50)
    print("持仓分析 Agent - 启动")
    print("=" * 50)
    
    # 分析持仓
    results = analyze_holdings()
    
    # 获取期权状态
    print("正在分析期权持仓...")
    options_status = get_options_status()
    
    # 获取新闻
    print("正在获取相关新闻...")
    news = get_relevant_news()
    
    # 生成报告
    report = generate_report(results, options_status, news)
    
    # 输出结果
    print("\n" + "=" * 50)
    print("报告生成完成")
    print("=" * 50)
    print(report)
    
    # 保存报告
    output_path = Path("/home/admin/openclaw/workspace/agents/holding-analyzer/reports")
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = output_path / f"report_{timestamp}.md"
    report_file.write_text(report, encoding='utf-8')
    
    print(f"\n报告已保存至：{report_file}")
    
    # 返回 JSON 结果（用于飞书推送）
    output_json = {
        'report': report,
        'significant_count': len(results['significant_changes']),
        'timestamp': results['timestamp']
    }
    
    json_file = output_path / f"result_{timestamp}.json"
    json_file.write_text(json.dumps(output_json, ensure_ascii=False, indent=2), encoding='utf-8')
    
    return output_json

if __name__ == "__main__":
    main()
