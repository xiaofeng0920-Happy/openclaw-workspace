#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实盘交易模块 - 自动生成买入/卖出指令清单

功能：
1. 根据目标持仓配置生成交易指令
2. 计算买入/卖出数量和金额
3. 风险控制（单只股票权重、行业集中度）
4. 输出可执行的交易指令清单

作者：OpenClaw AgentSkill
日期：2026-03-28
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
import json

# ==================== 配置参数 ====================

# 总资产规模（元）
TOTAL_ASSETS = 10_000_000

# 目标股票池（60 支优质股精选）
TARGET_STOCKS = {
    # 核心仓位（50%）
    '600519.SH': {'name': '贵州茅台', 'target_weight': 0.08, 'industry': '白酒'},
    '000858.SZ': {'name': '五粮液', 'target_weight': 0.06, 'industry': '白酒'},
    '000333.SZ': {'name': '美的集团', 'target_weight': 0.06, 'industry': '家电'},
    '601088.SH': {'name': '中国神华', 'target_weight': 0.06, 'industry': '煤炭'},
    '600938.SH': {'name': '中国海油', 'target_weight': 0.05, 'industry': '石油'},
    '300760.SZ': {'name': '迈瑞医疗', 'target_weight': 0.05, 'industry': '医疗设备'},
    '603259.SH': {'name': '药明康德', 'target_weight': 0.05, 'industry': '医药'},
    '000568.SZ': {'name': '泸州老窖', 'target_weight': 0.04, 'industry': '白酒'},
    '601899.SH': {'name': '紫金矿业', 'target_weight': 0.03, 'industry': '有色'},
    '002594.SZ': {'name': '比亚迪', 'target_weight': 0.02, 'industry': '汽车'},
    
    # 卫星仓位（30%）
    '600660.SH': {'name': '福耀玻璃', 'target_weight': 0.04, 'industry': '汽配'},
    '002027.SZ': {'name': '分众传媒', 'target_weight': 0.04, 'industry': '广告'},
    '300628.SZ': {'name': '亿联网络', 'target_weight': 0.04, 'industry': '通信'},
    '603195.SH': {'name': '公牛集团', 'target_weight': 0.03, 'industry': '电气'},
    '002690.SZ': {'name': '美亚光电', 'target_weight': 0.03, 'industry': '机械'},
    '603025.SH': {'name': '大豪科技', 'target_weight': 0.03, 'industry': '电气'},
    '000786.SZ': {'name': '北新建材', 'target_weight': 0.03, 'industry': '建材'},
    '601225.SH': {'name': '陕西煤业', 'target_weight': 0.02, 'industry': '煤炭'},
    '600809.SH': {'name': '山西汾酒', 'target_weight': 0.02, 'industry': '白酒'},
    '002351.SZ': {'name': '漫步者', 'target_weight': 0.02, 'industry': '消费电子'},
}

# 当前持仓（示例）
CURRENT_HOLDINGS = {
    '600519.SH': {'name': '贵州茅台', 'shares': 500, 'avg_price': 1650.00, 'industry': '白酒'},
    '000858.SZ': {'name': '五粮液', 'shares': 2000, 'avg_price': 145.00, 'industry': '白酒'},
    '000333.SZ': {'name': '美的集团', 'shares': 3000, 'avg_price': 62.00, 'industry': '家电'},
    '601088.SH': {'name': '中国神华', 'shares': 4000, 'avg_price': 38.50, 'industry': '煤炭'},
    '300760.SZ': {'name': '迈瑞医疗', 'shares': 800, 'avg_price': 285.00, 'industry': '医疗设备'},
    '002690.SZ': {'name': '美亚光电', 'shares': 5000, 'avg_price': 28.00, 'industry': '机械'},
}

# 当前股价（模拟实时数据）
CURRENT_PRICES = {
    '600519.SH': 1770.00,
    '000858.SZ': 165.00,
    '000333.SZ': 68.50,
    '601088.SH': 40.20,
    '600938.SH': 28.50,
    '300760.SZ': 295.00,
    '603259.SH': 145.00,
    '000568.SZ': 155.00,
    '601899.SH': 18.80,
    '002594.SZ': 285.00,
    '600660.SH': 58.50,
    '002027.SZ': 6.85,
    '300628.SZ': 42.50,
    '603195.SH': 88.00,
    '002690.SZ': 31.80,
    '603025.SH': 15.20,
    '000786.SZ': 29.50,
    '601225.SH': 25.80,
    '600809.SH': 185.00,
    '002351.SZ': 18.50,
}

# 风险控制参数
MAX_SINGLE_WEIGHT = 0.10  # 单只股票最大权重 10%
MAX_INDUSTRY_WEIGHT = 0.25  # 单一行业最大权重 25%
MIN_TRADE_AMOUNT = 10000  # 最小交易金额 1 万


# ==================== 交易指令生成器 ====================

class TradeGenerator:
    """交易指令生成器"""
    
    def __init__(self, total_assets: float = TOTAL_ASSETS):
        self.total_assets = total_assets
        self.current_holdings = CURRENT_HOLDINGS
        self.target_stocks = TARGET_STOCKS
        self.current_prices = CURRENT_PRICES
        self.trade_instructions = []
        
    def get_current_value(self, stock_code: str) -> float:
        """获取当前持仓市值"""
        if stock_code not in self.current_holdings:
            return 0.0
        holding = self.current_holdings[stock_code]
        price = self.current_prices.get(stock_code, 0)
        return holding['shares'] * price
    
    def get_current_shares(self, stock_code: str) -> int:
        """获取当前持仓数量"""
        if stock_code not in self.current_holdings:
            return 0
        return self.current_holdings[stock_code]['shares']
    
    def calculate_target_shares(self, stock_code: str) -> int:
        """计算目标持仓数量"""
        if stock_code not in self.target_stocks:
            return 0
        target_weight = self.target_stocks[stock_code]['target_weight']
        price = self.current_prices.get(stock_code, 0)
        if price <= 0:
            return 0
        target_value = self.total_assets * target_weight
        target_shares = int(target_value / price / 100) * 100  # 100 股整数倍
        return target_shares
    
    def generate_instructions(self) -> List[Dict]:
        """生成交易指令清单"""
        instructions = []
        
        # 处理目标股票池中的所有股票
        for stock_code, stock_info in self.target_stocks.items():
            current_shares = self.get_current_shares(stock_code)
            target_shares = self.calculate_target_shares(stock_code)
            current_price = self.current_prices.get(stock_code, 0)
            
            if current_price <= 0:
                continue
            
            delta_shares = target_shares - current_shares
            trade_value = abs(delta_shares) * current_price
            
            # 跳过小额交易
            if trade_value < MIN_TRADE_AMOUNT:
                continue
            
            instruction = {
                'stock_code': stock_code,
                'stock_name': stock_info['name'],
                'industry': stock_info['industry'],
                'action': 'BUY' if delta_shares > 0 else 'SELL',
                'current_shares': current_shares,
                'target_shares': target_shares,
                'delta_shares': abs(delta_shares),
                'current_price': current_price,
                'trade_value': trade_value,
                'current_weight': self.get_current_value(stock_code) / self.total_assets,
                'target_weight': stock_info['target_weight'],
            }
            instructions.append(instruction)
        
        # 处理需要清仓的股票（在当前持仓但不在目标池）
        for stock_code in self.current_holdings:
            if stock_code not in self.target_stocks:
                holding = self.current_holdings[stock_code]
                current_price = self.current_prices.get(stock_code, 0)
                if current_price <= 0:
                    continue
                trade_value = holding['shares'] * current_price
                if trade_value < MIN_TRADE_AMOUNT:
                    continue
                instruction = {
                    'stock_code': stock_code,
                    'stock_name': holding['name'],
                    'industry': holding['industry'],
                    'action': 'SELL',
                    'current_shares': holding['shares'],
                    'target_shares': 0,
                    'delta_shares': holding['shares'],
                    'current_price': current_price,
                    'trade_value': trade_value,
                    'current_weight': self.get_current_value(stock_code) / self.total_assets,
                    'target_weight': 0,
                }
                instructions.append(instruction)
        
        # 排序：买入在前，卖出在后
        instructions.sort(key=lambda x: (0 if x['action'] == 'BUY' else 1, -x['trade_value']))
        
        self.trade_instructions = instructions
        return instructions
    
    def print_instructions(self):
        """打印交易指令清单"""
        if not self.trade_instructions:
            self.generate_instructions()
        
        print("="*100)
        print("实盘交易模块 - 买入/卖出指令清单")
        print("="*100)
        print(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总资产规模：{self.total_assets:,.2f} 元")
        print(f"当前股价基准日：2026-03-28")
        print(f"执行时间建议：2026-03-29 09:30")
        print("="*100)
        
        # 分类统计
        buy_instructions = [i for i in self.trade_instructions if i['action'] == 'BUY']
        sell_instructions = [i for i in self.trade_instructions if i['action'] == 'SELL']
        
        total_buy = sum(i['trade_value'] for i in buy_instructions)
        total_sell = sum(i['trade_value'] for i in sell_instructions)
        net_trade = total_buy - total_sell
        
        print(f"\n📊 交易汇总")
        print(f"  买入指令：{len(buy_instructions)} 条，总金额：{total_buy:,.2f} 元")
        print(f"  卖出指令：{len(sell_instructions)} 条，总金额：{total_sell:,.2f} 元")
        print(f"  净交易额：{net_trade:,.2f} 元（买入 - 卖出）")
        print()
        
        # 买入指令
        print("🟢 买入指令（{}条）".format(len(buy_instructions)))
        print("-"*100)
        print(f"{'序号':<4} {'代码':<10} {'名称':<12} {'行业':<12} {'数量':>8} {'现价':>10} {'金额':>12} {'目标权重':>10}")
        print("-"*100)
        for idx, inst in enumerate(buy_instructions, 1):
            print(f"{idx:<4} {inst['stock_code']:<10} {inst['stock_name']:<12} {inst['industry']:<12} "
                  f"{inst['delta_shares']:>8} {inst['current_price']:>10.2f} {inst['trade_value']:>12,.0f} {inst['target_weight']*100:>9.1f}%")
        print()
        
        # 卖出指令
        print("🔴 卖出指令（{}条）".format(len(sell_instructions)))
        print("-"*100)
        print(f"{'序号':<4} {'代码':<10} {'名称':<12} {'行业':<12} {'数量':>8} {'现价':>10} {'金额':>12} {'当前权重':>10}")
        print("-"*100)
        for idx, inst in enumerate(sell_instructions, 1):
            print(f"{idx:<4} {inst['stock_code']:<10} {inst['stock_name']:<12} {inst['industry']:<12} "
                  f"{inst['delta_shares']:>8} {inst['current_price']:>10.2f} {inst['trade_value']:>12,.0f} {inst['current_weight']*100:>9.1f}%")
        print()
        
        # 风险控制检查
        print("🛡️ 风险控制检查")
        print("-"*100)
        
        # 单只股票权重检查
        max_weight = max(i['target_weight'] for i in self.trade_instructions if i['action'] == 'BUY')
        print(f"  单只股票最大权重：{max_weight*100:.1f}%（限制：{MAX_SINGLE_WEIGHT*100:.0f}%）"
              f" {'✅' if max_weight <= MAX_SINGLE_WEIGHT else '⚠️'}")
        
        # 行业集中度检查
        industry_weights = {}
        for inst in buy_instructions:
            industry = inst['industry']
            industry_weights[industry] = industry_weights.get(industry, 0) + inst['target_weight']
        
        max_industry = max(industry_weights.items(), key=lambda x: x[1]) if industry_weights else ('N/A', 0)
        industry_check = '✅' if max_industry[1] <= MAX_INDUSTRY_WEIGHT else '⚠️'
        print(f"  行业集中度最高：{max_industry[0]} {max_industry[1]*100:.1f}%（限制：{MAX_INDUSTRY_WEIGHT*100:.0f}%） {industry_check}")
        
        print()
        print("="*100)
        print("✅ 交易指令生成完成！")
        print("="*100)


if __name__ == '__main__':
    generator = TradeGenerator()
    generator.generate_instructions()
    generator.print_instructions()