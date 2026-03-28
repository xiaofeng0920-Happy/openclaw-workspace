#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
巴菲特价值投资分析器
====================

结合富途 OpenAPI 实时数据，对持仓股票进行巴菲特式分析。

使用方法:
    python3 buffett_analyzer.py
    
功能:
1. 获取持仓股票的实时价格和财务数据
2. 应用巴菲特选股标准进行评估
3. 计算内在价值和安全边际
4. 生成投资建议报告
"""

import sys
sys.path.insert(0, '/home/admin/openclaw/workspace')

from futu import *
from strategies.buffett_strategy import BuffettStrategy, BuffettStock
from data.financial_data import FinancialData
from datetime import datetime
import pandas as pd


def get_stock_financials(quote_ctx, code: str) -> dict:
    """
    从富途 API 获取股票财务数据
    
    注意：富途 OpenAPI 的财务数据接口有限，部分数据需要估算或从其他来源获取
    """
    # 获取基本行情
    ret, data = quote_ctx.get_market_snapshot([code])
    
    if ret != RET_OK or data.empty:
        return None
    
    row = data.iloc[0]
    
    # 从行情数据中提取
    financials = {
        'pe_ratio': row.get('pe_ratio', 0),
        'pb_ratio': row.get('pb_ratio', 0),
        'total_market_val': row.get('total_market_val', 0),  # 总市值
        'circular_market_val': row.get('circular_market_val', 0),  # 流通市值
        'outstanding_shares': row.get('outstanding_shares', 0),  # 总股本
    }
    
    # 获取财务指标（需要订阅财务数据）
    # 注意：富途 OpenAPI 的财务数据接口需要额外权限
    # 这里使用估算值，实际应用中应接入更完整的财务数据源
    
    return financials


def get_financials_from_api(code: str, name: str) -> dict:
    """
    从 API 获取真实财务数据
    
    使用 AKShare 免费数据源
    """
    try:
        # 初始化财务数据接口（AKShare 免费）
        fd = FinancialData(source='akshare')
        
        # 转换代码格式
        if code.startswith('HK.'):
            hk_code = code.replace('HK.', '')
            data = fd.get_financials(f'{hk_code}.HK')
        elif code.startswith('CN.'):
            cn_code = code.replace('CN.', '')
            data = fd.get_financials(cn_code)
        elif code.startswith('US.'):
            us_code = code.replace('US.', '')
            data = fd.get_financials(us_code)
        else:
            data = None
        
        if data:
            print(f"   ✅ 从 API 获取成功")
            return data
        else:
            print(f"   ⚠️ API 获取失败，使用估算数据")
    
    except Exception as e:
        print(f"   ⚠️ API 获取异常：{e}")
    
    # 回退到估算数据
    return estimate_financials(code, name)


def analyze_portfolio():
    """
    分析当前持仓组合
    """
    print("=" * 60)
    print("📊 巴菲特价值投资分析系统")
    print("=" * 60)
    print()
    
    # 连接 OpenD
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 验证连接
    ret, data = quote_ctx.get_global_state()
    if ret != RET_OK:
        print("❌ 无法连接到 OpenD，请确保 OpenD 已启动并登录")
        return
    
    print("✅ OpenD 连接成功")
    print()
    
    # 持仓股票列表（来自锋哥持仓）
    portfolio = [
        {'code': 'HK.00700', 'name': '腾讯控股', 'shares': 2500, 'cost': 585.78},
        {'code': 'HK.00883', 'name': '中国海洋石油', 'shares': 11000, 'cost': 20.75},
        {'code': 'HK.09988', 'name': '阿里巴巴-W', 'shares': 5800, 'cost': 143.27},
        # ETF 不适用巴菲特个股分析
        # {'code': 'HK.03153', 'name': '南方日经 225', 'shares': 12330, 'cost': 119.50},
        # {'code': 'HK.07709', 'name': '南方两倍做多', 'shares': 27500, 'cost': 24.08},
    ]
    
    strategy = BuffettStrategy()
    analyzed_stocks = []
    
    print("📈 分析持仓股票...\n")
    
    for stock_info in portfolio:
        code = stock_info['code']
        name = stock_info['name']
        shares = stock_info['shares']
        cost = stock_info['cost']
        
        print(f"分析中：{name} ({code})...")
        
        # 获取实时价格
        ret, data = quote_ctx.get_market_snapshot([code])
        if ret != RET_OK or data.empty:
            print(f"  ❌ 无法获取行情数据")
            continue
        
        current_price = data.iloc[0]['last_price']
        
        # 获取真实财务数据（从 API）
        financials = get_financials_from_api(code, name)
        
        if not financials:
            print(f"  ⚠️ 无财务数据，跳过")
            continue
        
        # 分析股票
        stock = strategy.analyze_stock(
            code=code,
            name=name,
            market='HK',
            current_price=current_price,
            financial_data=financials
        )
        
        if stock:
            stock.shares = shares
            stock.cost_basis = cost
            stock.market_value = current_price * shares
            stock.cost_value = cost * shares
            stock.unrealized_pnl = (current_price - cost) * shares
            stock.unrealized_pnl_pct = ((current_price - cost) / cost) * 100
            analyzed_stocks.append(stock)
            
            print(f"  ✅ 评分：{stock.buffett_score}/100 | 建议：{stock.recommendation}")
        else:
            print(f"  ❌ 不符合基本筛选标准")
    
    print()
    quote_ctx.close()
    
    # 生成报告
    if analyzed_stocks:
        print("=" * 60)
        print(strategy.generate_report(analyzed_stocks))
        
        # 持仓汇总
        print("\n" + "=" * 60)
        print("💰 持仓盈亏汇总")
        print("=" * 60)
        print()
        print(f"{'股票':<15} {'数量':>10} {'成本':>10} {'现价':>10} {'盈亏':>12} {'盈亏率':>10} {'建议':>12}")
        print("-" * 85)
        
        for stock in analyzed_stocks:
            rec_symbol = {
                'STRONG_BUY': '🎯',
                'BUY': '✅',
                'HOLD': '⏸️',
                'SELL': '❌'
            }.get(stock.recommendation, '')
            
            print(
                f"{stock.name:<15} {stock.shares:>10,.0f} {stock.cost_basis:>10.2f} "
                f"{stock.current_price:>10.2f} {stock.unrealized_pnl:>12,.0f} "
                f"{stock.unrealized_pnl_pct:>9.2f}% {rec_symbol:>6} {stock.recommendation}"
            )
        
        # 总计
        total_cost = sum(s.cost_value for s in analyzed_stocks)
        total_market = sum(s.market_value for s in analyzed_stocks)
        total_pnl = sum(s.unrealized_pnl for s in analyzed_stocks)
        total_pnl_pct = ((total_market - total_cost) / total_cost) * 100 if total_cost > 0 else 0
        
        print("-" * 85)
        print(
            f"{'总计':<15} {'':>10} {total_cost:>10,.0f} {total_market:>10,.0f} "
            f"{total_pnl:>12,.0f} {total_pnl_pct:>9.2f}%"
        )
        
        # 巴菲特建议
        print("\n" + "=" * 60)
        print("💡 巴菲特投资建议")
        print("=" * 60)
        print()
        
        strong_buys = [s for s in analyzed_stocks if s.recommendation == 'STRONG_BUY']
        sells = [s for s in analyzed_stocks if s.recommendation == 'SELL']
        holds = [s for s in analyzed_stocks if s.recommendation == 'HOLD']
        
        if strong_buys:
            print("🎯 **强力推荐加仓**:")
            for s in strong_buys:
                print(f"   - {s.name}: 内在价值 {s.fair_value:.2f}, 安全边际 {s.margin_of_safety:+.1f}%")
        
        if sells:
            print("\n❌ **考虑减持**:")
            for s in sells:
                print(f"   - {s.name}: 评分 {s.buffett_score}, 安全边际 {s.margin_of_safety:+.1f}%")
        
        if holds:
            print("\n⏸️ **继续持有**:")
            for s in holds:
                print(f"   - {s.name}: 等待更好的买入/卖出时机")
        
        # 名言
        import random
        from strategies.buffett_strategy import BUFFETT_QUOTES
        print(f"\n📖 巴菲特名言：\"{random.choice(BUFFETT_QUOTES)}\"")
    
    else:
        print("❌ 没有股票符合分析条件")


if __name__ == "__main__":
    analyze_portfolio()
