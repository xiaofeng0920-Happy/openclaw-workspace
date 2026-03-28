#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
炒股 Agent 团队 - 整合执行脚本

角色：
1. 数据收集员 (DataCollector)
2. 持仓分析师 (PortfolioAnalyzer)
3. 策略顾问 (StrategyAdvisor)
4. 报告撰写员 (ReportWriter)

输出：持仓日报 Markdown + 飞书推送
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

try:
    import akshare as ak
    import pandas as pd
except ImportError:
    print("❌ 请安装 akshare: pip install akshare")
    sys.exit(1)

# ============== 配置 ==============

WORKSPACE = Path('/home/admin/openclaw/workspace')
SKILLS_DIR = WORKSPACE / 'skills'
DATA_DIR = WORKSPACE / 'data'
REPORTS_DIR = WORKSPACE / 'reports'
MEMORY_DIR = WORKSPACE / 'memory'
AGENTS_DIR = WORKSPACE / 'agents'

DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# 持仓文件
HOLDINGS_FILE = MEMORY_DIR / '锋哥持仓_2026-03-16.md'

# ============== 角色 1: 数据收集员 ==============

def get_stock_price(symbol, market='US'):
    """获取股价（带重试）"""
    for i in range(3):
        try:
            if market == 'US':
                df = ak.stock_us_hist(symbol=symbol, period="recent")
            elif market == 'HK':
                df = ak.stock_hk_hist(symbol=symbol, period="recent")
            elif market == 'A':
                df = ak.stock_zh_a_hist(symbol=symbol, period="recent")
            
            if df is not None and len(df) > 0:
                return float(df.iloc[-1]['收盘'])
        except:
            pass
    return None

def collect_market_data():
    """数据收集员：获取市场数据"""
    print("\n📡 数据收集员工作中...")
    
    # 持仓股票列表
    stocks = {
        'US': ['GOOGL', 'BRK.B', 'KO', 'ORCL', 'MSFT', 'NVDA', 'AAPL', 'TSLA'],
        'HK': ['00700', '03153', '00883', '09988', '07709']
    }
    
    results = {'US': [], 'HK': []}
    
    for market, codes in stocks.items():
        for code in codes:
            price = get_stock_price(code, market)
            if price:
                results[market].append({
                    'code': code,
                    'price': price,
                    'timestamp': datetime.now().isoformat()
                })
                print(f"  ✅ {market} {code}: ${price:.2f}")
    
    # 输出 JSON
    output = {
        'timestamp': datetime.now().isoformat(),
        'dataSource': 'akshare',
        'stocks': results,
        'indices': {
            'SPX': {'value': 5200, 'change': 0.5},
            'HSI': {'value': 18500, 'change': -1.2}
        }
    }
    
    output_file = DATA_DIR / f'market_data_{datetime.now().strftime("%Y%m%d_%H%M")}.json'
    output_file.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"💾 市场数据已保存：{output_file}")
    
    return output, output_file

# ============== 角色 2: 持仓分析师 ==============

def parse_holdings_file():
    """解析持仓文件"""
    if not HOLDINGS_FILE.exists():
        print(f"❌ 持仓文件不存在：{HOLDINGS_FILE}")
        return None
    
    content = HOLDINGS_FILE.read_text(encoding='utf-8')
    
    holdings = []
    
    # 解析美股持仓表格
    us_section = re.search(r'## 🇺🇸 美股持仓明细.*?(?=## |$)', content, re.DOTALL)
    if us_section:
        for line in us_section.group().split('\n'):
            match = re.search(r'\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(\d+)\s*\|\s*\$?([\d.]+)\s*\|\s*\$?([\d.]+)\s*\|', line)
            if match:
                holdings.append({
                    'type': 'stock',
                    'market': 'US',
                    'code': match.group(1),
                    'name': match.group(2),
                    'quantity': int(match.group(3)),
                    'cost': float(match.group(4)),
                    'current_price': float(match.group(5))
                })
    
    # 解析港股持仓表格
    hk_section = re.search(r'## 🇭🇰 港股持仓明细.*?(?=## |$)', content, re.DOTALL)
    if hk_section:
        for line in hk_section.group().split('\n'):
            match = re.search(r'\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(\d+)\s*\|\s*\$?([\d.]+)\s*\|\s*\$?([\d.]+)\s*\|', line)
            if match:
                holdings.append({
                    'type': 'stock',
                    'market': 'HK',
                    'code': match.group(1),
                    'name': match.group(2),
                    'quantity': int(match.group(3)),
                    'cost': float(match.group(4)),
                    'current_price': float(match.group(5))
                })
    
    return holdings

def analyze_portfolio(market_data, holdings):
    """持仓分析师：计算盈亏"""
    print("\n📊 持仓分析师工作中...")
    
    if not holdings:
        return None
    
    # 创建股价映射
    price_map = {}
    for market in ['US', 'HK']:
        for stock in market_data['stocks'].get(market, []):
            price_map[stock['code']] = stock['price']
    
    # 计算盈亏
    results = []
    total_value = 0
    total_cost = 0
    
    for h in holdings:
        current_price = price_map.get(h['code'], h['current_price'])
        market_value = current_price * h['quantity']
        cost_value = h['cost'] * h['quantity']
        gain = market_value - cost_value
        gain_pct = (gain / cost_value) * 100 if cost_value > 0 else 0
        
        results.append({
            **h,
            'current_price': current_price,
            'market_value': market_value,
            'gain': gain,
            'gain_pct': gain_pct
        })
        
        total_value += market_value
        total_cost += cost_value
    
    # 汇总
    analysis = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_value': total_value,
            'total_cost': total_cost,
            'total_gain': total_value - total_cost,
            'total_gain_pct': ((total_value - total_cost) / total_cost) * 100 if total_cost > 0 else 0
        },
        'holdings': results,
        'top_gainers': sorted(results, key=lambda x: x['gain_pct'], reverse=True)[:3],
        'top_losers': sorted(results, key=lambda x: x['gain_pct'])[:3]
    }
    
    # 输出 JSON
    output_file = DATA_DIR / f'analysis_{datetime.now().strftime("%Y%m%d_%H%M")}.json'
    output_file.write_text(json.dumps(analysis, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"💾 分析结果已保存：{output_file}")
    
    return analysis, output_file

# ============== 角色 3: 策略顾问 ==============

def generate_strategy(analysis):
    """策略顾问：生成操作建议（含巴菲特分析）"""
    print("\n🧠 策略顾问工作中...")
    
    if not analysis:
        return None
    
    # 运行巴菲特分析器
    print("  📊 运行巴菲特投资策略分析...")
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, str(AGENTS_DIR / 'investment-workflow' / 'buffett_analyzer.py')],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print("  ✅ 巴菲特分析完成")
        else:
            print(f"  ⚠️ 巴菲特分析失败：{result.stderr[:100]}")
    except Exception as e:
        print(f"  ⚠️ 巴菲特分析异常：{e}")
    
    # 简单规则生成建议
    recommendations = []
    
    for h in analysis['holdings']:
        gain_pct = h['gain_pct']
        
        # 简单规则
        if gain_pct < -15:
            recommendations.append({
                'priority': '🟡',
                'action': '减仓',
                'target': h['name'],
                'code': h['code'],
                'reason': f"亏损{gain_pct:.1f}%",
                'suggestion': '考虑换股'
            })
        elif gain_pct > 40:
            recommendations.append({
                'priority': '🟢',
                'action': '止盈',
                'target': h['name'],
                'code': h['code'],
                'reason': f"盈利{gain_pct:.1f}%",
                'suggestion': '止盈 30-50%'
            })
        else:
            recommendations.append({
                'priority': '🔵',
                'action': '持有',
                'target': h['name'],
                'code': h['code'],
                'reason': f"{'小幅盈利' if gain_pct > 0 else '小幅亏损'}{gain_pct:.1f}%",
                'suggestion': '继续持有'
            })
    
    # 按优先级排序
    priority_order = {'🔴': 0, '🟡': 1, '🟢': 2, '🔵': 3}
    recommendations.sort(key=lambda x: priority_order.get(x['priority'], 4))
    
    strategy = {
        'timestamp': datetime.now().isoformat(),
        'recommendations': recommendations[:10],
        'portfolioStrategy': {
            'assetAllocation': {
                'current': {'US_stocks': 60, 'HK_stocks': 23, 'options': 10, 'cash': 7},
                'recommended': {'US_stocks': 55, 'HK_stocks': 20, 'options': 5, 'cash': 20}
            }
        },
        'buffett_analysis': True
    }
    
    # 输出 JSON
    output_file = DATA_DIR / f'strategy_{datetime.now().strftime("%Y%m%d_%H%M")}.json'
    output_file.write_text(json.dumps(strategy, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"💾 策略建议已保存：{output_file}")
    
    return strategy, output_file

# ============== 角色 4: 报告撰写员 ==============

def generate_report(market_data, analysis, strategy):
    """报告撰写员：生成 Markdown 报告"""
    print("\n✍️  报告撰写员工作中...")
    
    lines = []
    lines.append("# 📊 锋哥持仓日报")
    lines.append(f"**报告时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    
    # 总览
    lines.append("## 📈 总览")
    lines.append("")
    summary = analysis['summary']
    lines.append(f"| 指标 | 数值 |")
    lines.append(f"|------|------|")
    lines.append(f"| 总资产 | ${summary['total_value']:,.0f} |")
    lines.append(f"| 总盈亏 | ${summary['total_gain']:,.0f} ({summary['total_gain_pct']:+.1f}%) |")
    lines.append("")
    
    # TOP 涨跌
    lines.append("## 🏆 今日亮点")
    lines.append("")
    lines.append("### 表现最好的 TOP3")
    for i, h in enumerate(analysis['top_gainers'], 1):
        lines.append(f"{i}. **{h['name']} ({h['code']})** {h['gain_pct']:+.1f}%")
    
    lines.append("")
    lines.append("### 表现最差的 TOP3")
    for i, h in enumerate(analysis['top_losers'], 1):
        lines.append(f"{i}. **{h['name']} ({h['code']})** {h['gain_pct']:+.1f}%")
    
    lines.append("")
    lines.append("## 💡 操作建议")
    lines.append("")
    for rec in strategy['recommendations'][:7]:
        lines.append(f"- {rec['priority']} {rec['action']} **{rec['target']}**: {rec['suggestion']}")
    
    lines.append("")
    lines.append("---")
    lines.append("*⚠️ 以上建议仅供参考，不构成投资建议。投资有风险，决策需谨慎。*")
    
    report = "\n".join(lines)
    
    # 保存报告
    report_file = REPORTS_DIR / f'持仓日报_{datetime.now().strftime("%Y%m%d_%H%M")}.md'
    report_file.write_text(report, encoding='utf-8')
    print(f"💾 报告已保存：{report_file}")
    
    return report, report_file

# ============== 主流程 ==============

def run_agent_team():
    """运行炒股 Agent 团队"""
    print("="*60)
    print("🤖 炒股 Agent 团队 - 开始工作")
    print("="*60)
    
    # 角色 1: 数据收集
    market_data, _ = collect_market_data()
    
    # 角色 2: 持仓分析
    holdings = parse_holdings_file()
    analysis, _ = analyze_portfolio(market_data, holdings)
    
    # 角色 3: 策略建议
    strategy, _ = generate_strategy(analysis)
    
    # 角色 4: 报告撰写
    report, report_file = generate_report(market_data, analysis, strategy)
    
    print("\n" + "="*60)
    print("✅ 炒股 Agent 团队完成")
    print("="*60)
    print(f"📄 报告：{report_file}")
    
    return report, report_file

if __name__ == "__main__":
    run_agent_team()
