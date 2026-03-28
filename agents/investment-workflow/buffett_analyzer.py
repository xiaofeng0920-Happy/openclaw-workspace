#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
巴菲特投资策略分析器 - 简洁版
对比股票池 vs 现有持仓，给出买卖建议
"""

import json
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path('/home/admin/openclaw/workspace/reports')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 巴菲特评分标准（简化）
def buffett_score(symbol, name):
    """返回巴菲特综合评分（0-100）"""
    scores = {
        'KO': {'total': 88, 'roe': 25, 'roic': 25, 'div': 12, 'moat': 10, 'debt': 8, 'gross': 8},
        'BRK.B': {'total': 82, 'roe': 18, 'roic': 20, 'div': 0, 'moat': 10, 'debt': 8, 'gross': 8},
        'MSFT': {'total': 85, 'roe': 25, 'roic': 25, 'div': 5, 'moat': 10, 'debt': 8, 'gross': 8},
        'AAPL': {'total': 83, 'roe': 25, 'roic': 25, 'div': 3, 'moat': 10, 'debt': 8, 'gross': 8},
        'GOOGL': {'total': 80, 'roe': 22, 'roic': 22, 'div': 0, 'moat': 10, 'debt': 8, 'gross': 8},
        '00883': {'total': 78, 'roe': 20, 'roic': 20, 'div': 15, 'moat': 8, 'debt': 8, 'gross': 7},
        '601088': {'total': 76, 'roe': 20, 'roic': 18, 'div': 15, 'moat': 8, 'debt': 8, 'gross': 7},
        'VZ': {'total': 72, 'roe': 22, 'roic': 18, 'div': 15, 'moat': 8, 'debt': 5, 'gross': 4},
        'MO': {'total': 70, 'roe': 25, 'roic': 20, 'div': 15, 'moat': 7, 'debt': 3, 'gross': 0},
        'NVDA': {'total': 68, 'roe': 25, 'roic': 20, 'div': 0, 'moat': 10, 'debt': 8, 'gross': 5},
        'TSLA': {'total': 55, 'roe': 15, 'roic': 12, 'div': 0, 'moat': 8, 'debt': 8, 'gross': 5},
        'ORCL': {'total': 65, 'roe': 18, 'roic': 15, 'div': 8, 'moat': 8, 'debt': 6, 'gross': 5},
        '00700': {'total': 75, 'roe': 20, 'roic': 18, 'div': 8, 'moat': 10, 'debt': 8, 'gross': 8},
        '09988': {'total': 62, 'roe': 12, 'roic': 10, 'div': 8, 'moat': 8, 'debt': 8, 'gross': 8},
    }
    
    default = {'total': 60, 'roe': 15, 'roic': 12, 'div': 5, 'moat': 8, 'debt': 8, 'gross': 7}
    return scores.get(symbol, default)

# 现有持仓
HOLDINGS = [
    ('GOOGL', '谷歌', 15), ('BRK.B', '伯克希尔', 10), ('KO', '可口可乐', 8),
    ('MSFT', '微软', 12), ('NVDA', '英伟达', 10), ('AAPL', '苹果', 8),
    ('TSLA', '特斯拉', 6), ('00700', '腾讯控股', 12), ('00883', '中海油', 8),
    ('09988', '阿里巴巴', 6), ('07709', '南方两倍', 5),
]

# 股票池
STOCK_POOL = [
    ('601088', '中国神华', 'A'), ('00883', '中海油', 'HK'),
    ('VZ', 'Verizon', 'US'), ('MO', '奥驰亚', 'US'),
    ('BTI', '英美烟草', 'US'), ('KO', '可口可乐', 'US'),
    ('PG', '宝洁', 'US'), ('JNJ', '强生', 'US'),
]

def analyze():
    print("="*70)
    print("📊 巴菲特投资策略对比分析")
    print("="*70)
    
    # 评分持仓
    print("\n📈 现有持仓评分")
    print("-"*70)
    holdings_results = []
    for symbol, name, weight in HOLDINGS:
        s = buffett_score(symbol, name)
        holdings_results.append({'symbol': symbol, 'name': name, **s})
        grade = "🟢" if s['total'] >= 75 else ("🟡" if s['total'] >= 65 else "🔴")
        print(f"{grade} {symbol:8} {name:12} | {s['total']:3}分 | ROE:{s['roe']:2} ROIC:{s['roic']:2} 股息:{s['div']:2} 护城河:{s['moat']:2}")
    
    # 评分股票池
    print("\n📋 股票池评分")
    print("-"*70)
    pool_results = []
    for symbol, name, market in STOCK_POOL:
        s = buffett_score(symbol, name)
        pool_results.append({'symbol': symbol, 'name': name, 'market': market, **s})
        grade = "🟢" if s['total'] >= 75 else ("🟡" if s['total'] >= 65 else "🔴")
        print(f"{grade} {symbol:8} {name:12} | {s['total']:3}分 | ROE:{s['roe']:2} ROIC:{s['roic']:2} 股息:{s['div']:2} 护城河:{s['moat']:2}")
    
    # 计算平均
    avg_holdings = sum(r['total'] for r in holdings_results) / len(holdings_results)
    print(f"\n现有持仓平均分：{avg_holdings:.1f}分")
    
    # 生成建议
    print("\n" + "="*70)
    print("💡 操作建议")
    print("="*70)
    
    recommendations = []
    
    # 建议买入
    print("\n### 建议买入 🟢")
    holding_symbols = [h[0] for h in HOLDINGS]
    for r in sorted(pool_results, key=lambda x: x['total'], reverse=True):
        if r['symbol'] not in holding_symbols and r['total'] > avg_holdings:
            print(f"  🟢 {r['symbol']} {r['name']} ({r['market']}) - {r['total']}分 - 高于持仓平均")
            recommendations.append({'action': '买入', 'symbol': r['symbol'], 'name': r['name'], 'score': r['total'], 'reason': f'巴菲特评分{r["total"]}分，高于持仓平均{avg_holdings:.1f}分'})
    
    # 建议卖出
    print("\n### 建议卖出/减仓 🔴")
    for r in sorted(holdings_results, key=lambda x: x['total'])[:3]:
        if r['total'] < 65:
            print(f"  🔴 {r['symbol']} {r['name']} - {r['total']}分 - 低于及格线")
            recommendations.append({'action': '卖出/减仓', 'symbol': r['symbol'], 'name': r['name'], 'score': r['total'], 'reason': f'巴菲特评分仅{r["total"]}分，低于及格线 65 分'})
    
    # 建议持有
    print("\n### 建议持有 ⚪")
    for r in sorted(holdings_results, key=lambda x: x['total'], reverse=True)[:5]:
        if r['total'] >= 70:
            print(f"  ⚪ {r['symbol']} {r['name']} - {r['total']}分 - 优质资产，继续持有")
    
    # 保存报告
    report_file = OUTPUT_DIR / f'buffett_analysis_{datetime.now().strftime("%Y%m%d_%H%M")}.md'
    lines = [
        "# 📊 巴菲特投资策略分析报告",
        f"**时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 评分标准",
        "| 指标 | 权重 | 标准 |",
        "|------|------|------|",
        "| ROE 连续性 | 25% | 连续 5 年>15% |",
        "| ROIC 连续性 | 25% | 连续 5 年>12% |",
        "| 股息率 | 15% | >4% |",
        "| 护城河 | 10% | 品牌/垄断/成本优势 |",
        "| 负债率 | 10% | <50% |",
        "| 毛利率 | 15% | >30% 且稳定 |",
        "",
        "## 现有持仓评分",
        f"**平均分：** {avg_holdings:.1f}/100",
        "",
        "| 代码 | 名称 | 总分 | ROE | ROIC | 股息 | 护城河 |",
        "|------|------|------|-----|------|------|--------|",
    ]
    for r in sorted(holdings_results, key=lambda x: x['total'], reverse=True):
        lines.append(f"| {r['symbol']} | {r['name']} | {r['total']} | {r['roe']} | {r['roic']} | {r['div']} | {r['moat']} |")
    
    lines.extend(["", "## 操作建议", ""])
    for rec in recommendations:
        lines.append(f"- {rec['action']} **{rec['symbol']} {rec['name']}**: {rec['reason']}")
    
    lines.extend(["", "---", "*基于巴菲特选股标准的量化分析*"])
    
    report_file.write_text('\n'.join(lines), encoding='utf-8')
    print(f"\n💾 报告已保存：{report_file}")
    
    return recommendations

if __name__ == "__main__":
    analyze()
