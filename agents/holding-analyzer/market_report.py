#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股市场日报 - 使用 akshare 获取数据
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/admin/openclaw/workspace')

try:
    import akshare as ak
    import pandas as pd
except ImportError:
    print("请安装 akshare 和 pandas: pip install akshare pandas")
    sys.exit(1)

def get_index_data():
    """获取主要指数数据"""
    print("正在获取指数数据...")
    
    # 指数代码（akshare 格式）
    indices = {
        '沪深 300': '000300',
        '上证 50': '000016',
        '中证 500': '000905',
        '科创 50': '000688',
        '中证红利': 'H30269',
        '上证红利': 'H50040',
        '恒生指数': 'HSI',
        '创业板 50': '399050',
    }
    
    results = []
    for name, code in indices.items():
        try:
            if name == '恒生指数':
                # 港股指数
                df = ak.stock_hk_index_daily(symbol=code)
            elif code.startswith('399'):
                # 深证指数
                df = ak.stock_sz_index_daily(symbol=code)
            else:
                # 上证指数
                df = ak.stock_sh_index_daily(symbol=code)
            
            if df is not None and len(df) > 0:
                latest = df.iloc[-1]
                prev = df.iloc[-2] if len(df) > 1 else latest
                
                close = float(latest['close'])
                change = close - float(prev['close'])
                change_pct = (change / float(prev['close'])) * 100
                
                results.append({
                    'name': name,
                    'code': code,
                    'close': close,
                    'change': change,
                    'change_pct': change_pct,
                })
        except Exception as e:
            print(f"  获取 {name} 失败：{e}")
    
    return results

def get_sector_moneyflow():
    """获取行业资金流向"""
    print("正在获取行业资金流向...")
    
    try:
        # 获取行业资金流向
        df = ak.stock_sector_fund_flow_summary(symbol="行业", indicator="今日")
        if df is not None and len(df) > 0:
            # 按净流入排序
            df_sorted = df.sort_values('今日主力净流入-净额', ascending=False)
            
            inflow_top10 = df_sorted.head(10)[['行业', '今日主力净流入 - 净额', '今日主力净流入 - 净占比']].to_dict('records')
            outflow_top10 = df_sorted.tail(10)[['行业', '今日主力净流入 - 净额', '今日主力净流入 - 净占比']].to_dict('records')
            
            return inflow_top10, outflow_top10
    except Exception as e:
        print(f"  获取行业资金流向失败：{e}")
    
    return [], []

def get_new_high_stocks():
    """获取创新高股票"""
    print("正在获取创新高股票...")
    
    try:
        # 获取创历史新高股票
        df = ak.stock_cxg_em(symbol="创历史新高股票")
        if df is not None and len(df) > 0:
            return df.head(10)[['股票代码', '股票名称', '最新价', '涨跌幅']].to_dict('records')
    except Exception as e:
        print(f"  获取创新高股票失败：{e}")
    
    return []

def get_financial_news():
    """获取财经新闻"""
    print("正在获取财经新闻...")
    
    try:
        # 获取财经新闻
        df = ak.stock_news_em(symbol="全部")
        if df is not None and len(df) > 0:
            return df.head(10)[['新闻标题', '文章来源', '发布时间', '新闻链接']].to_dict('records')
    except Exception as e:
        print(f"  获取财经新闻失败：{e}")
    
    return []

def generate_report(indices, inflow, outflow, new_highs, news):
    """生成 Markdown 报告"""
    lines = []
    lines.append("# 📊 A 股市场日报")
    lines.append(f"**日期：** {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")
    
    # 一、指数表现
    lines.append("## 一、主要指数表现")
    lines.append("")
    lines.append("| 指数 | 代码 | 收盘价 | 涨跌 | 涨跌幅 |")
    lines.append("|------|------|--------|------|--------|")
    
    for idx in indices:
        flag = "📈" if idx['change_pct'] > 0 else "📉" if idx['change_pct'] < 0 else "➖"
        lines.append(f"| {flag} {idx['name']} | {idx['code']} | {idx['close']:.2f} | {idx['change']:+.2f} | {idx['change_pct']:+.2f}% |")
    
    lines.append("")
    
    # 二、资金流向
    lines.append("## 二、行业资金流向")
    lines.append("")
    
    if inflow:
        lines.append("### 资金流入前 10 行业")
        lines.append("| 排名 | 行业 | 净流入 (亿) | 净占比 |")
        lines.append("|------|------|------------|--------|")
        for i, row in enumerate(inflow, 1):
            net = row.get('今日主力净流入 - 净额', 0)
            net_pct = row.get('今日主力净流入 - 净占比', 0)
            lines.append(f"| {i} | {row.get('行业', '-')} | {net:.2f} | {net_pct:.2f}% |")
        lines.append("")
    
    if outflow:
        lines.append("### 资金流出前 10 行业")
        lines.append("| 排名 | 行业 | 净流入 (亿) | 净占比 |")
        lines.append("|------|------|------------|--------|")
        for i, row in enumerate(outflow, 1):
            net = row.get('今日主力净流入 - 净额', 0)
            net_pct = row.get('今日主力净流入 - 净占比', 0)
            lines.append(f"| {i} | {row.get('行业', '-')} | {net:.2f} | {net_pct:.2f}% |")
        lines.append("")
    
    # 三、创新高股票
    lines.append("## 三、创新高股票（前 10）")
    lines.append("")
    lines.append("| 排名 | 代码 | 名称 | 最新价 | 涨跌幅 |")
    lines.append("|------|------|------|--------|--------|")
    
    for i, stock in enumerate(new_highs, 1):
        code = stock.get('股票代码', '-')
        name = stock.get('股票名称', '-')
        price = stock.get('最新价', 0)
        pct = stock.get('涨跌幅', 0)
        lines.append(f"| {i} | {code} | {name} | {price:.2f} | {pct:+.2f}% |")
    
    lines.append("")
    
    # 四、财经新闻
    lines.append("## 四、重要财经新闻（前 10）")
    lines.append("")
    
    for i, n in enumerate(news, 1):
        title = n.get('新闻标题', '-')
        source = n.get('文章来源', '-')
        time = n.get('发布时间', '-')
        lines.append(f"{i}. **{title}** - {source} ({time})")
    
    lines.append("")
    
    # 五、市场展望与风险提示
    lines.append("## 五、市场展望与风险提示")
    lines.append("")
    lines.append("### 市场展望")
    lines.append("")
    
    # 根据指数表现生成展望
    up_count = sum(1 for idx in indices if idx['change_pct'] > 0)
    down_count = len(indices) - up_count
    
    if up_count > down_count:
        lines.append("✅ 今日市场整体表现积极，多数指数上涨，资金流入明显。")
    elif up_count == down_count:
        lines.append("⚖️ 今日市场震荡整理，指数涨跌互现，观望情绪较浓。")
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
    lines.append("*数据来源：akshare | 生成时间：" + datetime.now().strftime('%Y-%m-%d %H:%M') + "*")
    
    return "\n".join(lines)

def main():
    print("=" * 60)
    print("📊 A 股市场日报 - 生成中")
    print("=" * 60)
    
    # 获取数据
    indices = get_index_data()
    inflow, outflow = get_sector_moneyflow()
    new_highs = get_new_high_stocks()
    news = get_financial_news()
    
    # 生成报告
    report = generate_report(indices, inflow, outflow, new_highs, news)
    
    # 保存报告
    output_path = Path(__file__).parent / "reports"
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d')
    report_file = output_path / f"market_report_{timestamp}.md"
    report_file.write_text(report, encoding='utf-8')
    
    print(f"\n💾 报告已保存：{report_file}")
    print("\n" + "=" * 60)
    print(report)
    
    return report

if __name__ == "__main__":
    main()
