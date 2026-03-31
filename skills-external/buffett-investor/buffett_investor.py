#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
巴菲特价值投资技能实现
"""

import sys
import os
sys.path.insert(0, '/home/admin/openclaw/workspace')

from data.financial_data import FinancialData
from strategies.buffett_strategy import BuffettStrategy
from datetime import datetime


def analyze_stock(code: str) -> str:
    """分析单只股票"""
    fd = FinancialData(source='akshare')
    strategy = BuffettStrategy()
    
    # 获取真实数据
    data = fd.get_financials(code)
    
    if not data:
        return f"❌ 无法获取 {code} 的财务数据"
    
    # 分析股票
    stock = strategy.analyze_stock(
        code=code,
        name=data.get('name', code),
        market=data.get('market', 'HK'),
        current_price=data.get('current_price', 0),
        financial_data=data
    )
    
    if not stock:
        return f"❌ {code} 不符合基本筛选标准"
    
    # 生成报告
    report = []
    report.append(f"# 📊 {stock.name} ({code}) 巴菲特分析报告")
    report.append(f"\n**分析时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\n## 📈 核心指标")
    report.append(f"- **综合评分:** {stock.buffett_score}/100 {'⭐'*int(stock.buffett_score/20)}")
    report.append(f"- **投资建议:** {stock.recommendation}")
    report.append(f"- **当前价格:** {stock.current_price:.2f} 港元")
    report.append(f"- **内在价值:** {stock.fair_value:.2f} 港元")
    report.append(f"- **安全边际:** {stock.margin_of_safety:+.1f}%")
    report.append(f"\n## 💰 财务指标")
    report.append(f"- **ROE (5 年平均):** {stock.roe_5y_avg:.1f}%")
    report.append(f"- **毛利率:** {stock.gross_margin:.1f}%")
    report.append(f"- **净利率:** {stock.net_margin:.1f}%")
    report.append(f"- **负债/权益:** {stock.debt_to_equity:.2f}")
    report.append(f"- **市盈率:** {stock.pe_ratio:.1f}")
    report.append(f"- **护城河评分:** {stock.moat_score}/10")
    
    return "\n".join(report)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        code = sys.argv[1]
        print(analyze_stock(code))
    else:
        print("用法：python3 buffett_investor.py [股票代码]")
        print("示例：python3 buffett_investor.py HK.00700")
