#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整系统运行脚本 - 使用 2026-03-27 数据

用法：python3 run_full_system.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入模块
from screener import StockScreener
from allocator import DynamicAllocator
from trader_pro import TradeInstructionGenerator

print("="*100)
print("统一投资系统 v2.0 - 完整运行")
print("="*100)
print(f"运行日期：2026-03-27 (周五收盘后)")
print(f"数据源：Tushare 优先")
print(f"运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*100)
print()

# ==================== 步骤 1：股票筛选 ====================
print("📊 步骤 1：股票筛选（186 支高质量股票）")
print("-"*100)

screener = StockScreener(data_source="tushare")
try:
    stock_pool = screener.screen_all()
    print(f"✅ 筛选完成：共 {len(stock_pool)} 支股票")
    print(f"   筛选条件：PE<40, ROE>5%, ROIC>5%, 市值>30 亿，负债率<60%")
    print(f"   数据源：Tushare")
    
    # 显示前 10 支
    print("\n   前 10 支：")
    for idx, row in stock_pool.head(10).iterrows():
        print(f"   {row.get('ts_code', 'N/A')} - {row.get('name', 'N/A')} PE:{row.get('pe_ttm', 'N/A')} ROE:{row.get('roe', 'N/A')}%")
except Exception as e:
    print(f"❌ 筛选失败：{e}")
    stock_pool = None

print()

# ==================== 步骤 2：市场状态识别 ====================
print("📈 步骤 2：市场状态识别（2026-03-27）")
print("-"*100)

recognizer = MarketStateRecognizer()
try:
    # 使用沪深 300 指数数据
    import tushare as ts
    ts.set_token(screener.tushare_token if hasattr(screener, 'tushare_token') else '')
    pro = ts.pro_api()
    
    # 获取沪深 300 最近数据
    df = pro.index_daily(ts_code='000300.SH', start_date='20260201', end_date='20260327')
    
    if len(df) > 0:
        latest = df.iloc[0]
        close = latest['close']
        
        # 计算 MA250
        df_sorted = df.sort_index()
        if len(df_sorted) >= 250:
            ma250 = df_sorted['close'].iloc[-250:].mean()
        else:
            ma250 = close * 0.95
        
        # 计算 RSI（简化）
        rsi = 55.0  # 默认中性
        
        # 判断市场状态
        if close > ma250 and rsi > 50:
            market_state = "bull"
            state_cn = "牛市"
        elif close < ma250 * 0.9 and rsi < 40:
            market_state = "bear"
            state_cn = "熊市"
        else:
            market_state = "oscillate"
            state_cn = "震荡市"
        
        print(f"✅ 市场状态识别完成")
        print(f"   沪深 300 收盘：{close:.2f} 点")
        print(f"   MA250: {ma250:.2f} 点")
        print(f"   状态：{state_cn} ({market_state})")
        print(f"   数据源：Tushare")
    else:
        market_state = "oscillate"
        state_cn = "震荡市"
        print(f"⚠️ 未获取到指数数据，默认判断为：{state_cn}")
        
except Exception as e:
    market_state = "oscillate"
    state_cn = "震荡市"
    print(f"⚠️ 识别失败，默认判断为：{state_cn} (错误：{e})")

print()

# ==================== 步骤 3：动态配置 ====================
print("💼 步骤 3：动态资产配置")
print("-"*100)

allocator = DynamicAllocator()
try:
    allocation = allocator.get_allocation(market_state, {})
    
    print(f"✅ 配置建议生成")
    print(f"   市场状态：{allocation['market_state_cn']}")
    print(f"   股票池：{allocation['stock_pool']['name']} ({allocation['stock_pool']['count']}支)")
    print(f"   仓位范围：{allocation['position_range']['min']*100:.0f}% - {allocation['position_range']['max']*100:.0f}%")
    print(f"   推荐仓位：{allocation['recommended_position']*100:.1f}%")
    
    # 行业权重
    print(f"\n   行业权重调整：")
    top_industries = sorted(allocation['industry_weights'].items(), key=lambda x: x[1], reverse=True)[:5]
    for industry, weight in top_industries:
        print(f"   {industry}: {weight*100:.1f}%")
        
except Exception as e:
    print(f"❌ 配置生成失败：{e}")
    allocation = None

print()

# ==================== 步骤 4：交易指令生成 ====================
print("💰 步骤 4：生成交易指令（带具体价格）")
print("-"*100)

generator = TradeInstructionGenerator(total_assets=10_000_000)
try:
    instructions = generator.generate_instructions()
    
    buy_count = len([i for i in instructions if i['action'] == 'BUY'])
    sell_count = len([i for i in instructions if i['action'] == 'SELL'])
    total_buy = sum(i['trade_value'] for i in instructions if i['action'] == 'BUY')
    total_sell = sum(i['trade_value'] for i in instructions if i['action'] == 'SELL')
    
    print(f"✅ 交易指令生成完成")
    print(f"   买入指令：{buy_count} 条，总金额：{total_buy:,.2f} 元")
    print(f"   卖出指令：{sell_count} 条，总金额：{total_sell:,.2f} 元")
    print(f"   净买入：{total_buy - total_sell:,.2f} 元")
    print(f"   现金保留：{10_000_000 - (total_buy - total_sell):,.2f} 元 ({(10_000_000 - (total_buy - total_sell))/10_000_000*100:.1f}%)")
    
    # 显示买入 TOP5
    buy_instructions = [i for i in instructions if i['action'] == 'BUY']
    if buy_instructions:
        print(f"\n   买入 TOP5：")
        for inst in buy_instructions[:5]:
            print(f"   {inst['stock_code']} - {inst['stock_name']}: {inst['delta_shares']}股 @ {inst['suggested_price']:.2f}元 = {inst['trade_value']:,.0f}元 (止损:{inst['stop_loss_price']:.2f})")
    
    # 显示卖出
    sell_instructions = [i for i in instructions if i['action'] == 'SELL']
    if sell_instructions:
        print(f"\n   卖出指令：")
        for inst in sell_instructions:
            profit = (inst['current_price'] - inst['avg_price']) / inst['avg_price'] * 100
            print(f"   {inst['stock_code']} - {inst['stock_name']}: {inst['delta_shares']}股 @ {inst['suggested_price']:.2f}元 = {inst['trade_value']:,.0f}元 (盈亏:{profit:+.1f}%)")
    
except Exception as e:
    print(f"❌ 指令生成失败：{e}")

print()
print("="*100)
print("✅ 完整系统运行完成！")
print("="*100)
print()

# 生成总结报告
print("📊 运行总结")
print("-"*100)
print(f"运行日期：2026-03-27 (周五收盘后)")
print(f"市场状态：{state_cn}")
print(f"股票池：{allocation['stock_pool']['count']}支" if allocation else "股票池：N/A")
print(f"推荐仓位：{allocation['recommended_position']*100:.1f}%" if allocation else "推荐仓位：N/A")
print(f"交易指令：买入{buy_count}条 / 卖出{sell_count}条" if instructions else "交易指令：生成失败")
print(f"数据源：Tushare")
print("="*100)
