#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实盘交易指令生成器 Pro - 带具体建议价格

功能：
1. 根据目标持仓生成买入/卖出指令
2. 计算具体建议价格（支撑位/阻力位/估值）
3. 考虑地缘政治等特殊因素调整
4. 输出可执行的交易指令清单

作者：OpenClaw AgentSkill
日期：2026-03-28
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from enum import Enum

# ==================== 配置参数 ====================

# 总资产规模（元）
TOTAL_ASSETS = 10_000_000

# 当前持仓（示例）
CURRENT_HOLDINGS = {
    '600519.SH': {'name': '贵州茅台', 'shares': 500, 'avg_price': 1650.00, 'industry': '白酒'},
    '000858.SZ': {'name': '五粮液', 'shares': 2000, 'avg_price': 145.00, 'industry': '白酒'},
    '000333.SZ': {'name': '美的集团', 'shares': 3000, 'avg_price': 62.00, 'industry': '家电'},
    '601088.SH': {'name': '中国神华', 'shares': 4000, 'avg_price': 38.50, 'industry': '煤炭'},
    '300760.SZ': {'name': '迈瑞医疗', 'shares': 800, 'avg_price': 285.00, 'industry': '医疗设备'},
    '603259.SH': {'name': '药明康德', 'shares': 2000, 'avg_price': 155.00, 'industry': '医药'},
    '002690.SZ': {'name': '美亚光电', 'shares': 5000, 'avg_price': 28.00, 'industry': '机械'},
    '600036.SH': {'name': '招商银行', 'shares': 3000, 'avg_price': 38.50, 'industry': '银行'},
}

# 目标股票池（考虑地缘政治因素）
TARGET_STOCKS = {
    # 能源/资源类（增持）
    '600938.SH': {'name': '中国海油', 'target_weight': 0.08, 'industry': '石油', 'special_factor': 1.10},
    '601088.SH': {'name': '中国神华', 'target_weight': 0.08, 'industry': '煤炭', 'special_factor': 1.08},
    '601899.SH': {'name': '紫金矿业', 'target_weight': 0.06, 'industry': '有色', 'special_factor': 1.05},
    
    # 新能源类（增持）
    '300750.SZ': {'name': '宁德时代', 'target_weight': 0.06, 'industry': '电池', 'special_factor': 1.05},
    '002460.SZ': {'name': '赣锋锂业', 'target_weight': 0.04, 'industry': '锂业', 'special_factor': 1.05},
    
    # 防御类（增持）
    '600036.SH': {'name': '招商银行', 'target_weight': 0.06, 'industry': '银行', 'special_factor': 1.03},
    '601398.SH': {'name': '工商银行', 'target_weight': 0.05, 'industry': '银行', 'special_factor': 1.03},
    '600900.SH': {'name': '长江电力', 'target_weight': 0.05, 'industry': '电力', 'special_factor': 1.03},
    
    # 消费类（标配）
    '600519.SH': {'name': '贵州茅台', 'target_weight': 0.08, 'industry': '白酒', 'special_factor': 1.00},
    '000858.SZ': {'name': '五粮液', 'target_weight': 0.06, 'industry': '白酒', 'special_factor': 1.00},
    '000333.SZ': {'name': '美的集团', 'target_weight': 0.05, 'industry': '家电', 'special_factor': 1.00},
    
    # 医药类（标配）
    '300760.SZ': {'name': '迈瑞医疗', 'target_weight': 0.05, 'industry': '医疗设备', 'special_factor': 1.00},
    '603259.SH': {'name': '药明康德', 'target_weight': 0.04, 'industry': '医药', 'special_factor': 1.00},
    
    # 科技类（低配）
    '002690.SZ': {'name': '美亚光电', 'target_weight': 0.03, 'industry': '机械', 'special_factor': 0.95},
}

# 当前股价（模拟实时数据）
CURRENT_PRICES = {
    '600519.SH': 1770.00,
    '000858.SZ': 165.00,
    '000333.SZ': 68.50,
    '601088.SH': 40.20,
    '300760.SZ': 295.00,
    '603259.SH': 145.00,
    '002690.SZ': 31.80,
    '600036.SH': 42.50,
    '600938.SH': 28.50,
    '601899.SH': 18.80,
    '300750.SZ': 416.18,
    '002460.SZ': 80.50,
    '601398.SH': 5.85,
    '600900.SH': 28.20,
}

# 技术指标（20 日均线等）
TECHNICAL_DATA = {
    '600519.SH': {'ma20': 1720.00, 'boll_lower': 1680.00, 'boll_upper': 1820.00, 'support': 1700.00, 'resistance': 1800.00},
    '000858.SZ': {'ma20': 160.00, 'boll_lower': 155.00, 'boll_upper': 175.00, 'support': 158.00, 'resistance': 172.00},
    '000333.SZ': {'ma20': 66.00, 'boll_lower': 63.00, 'boll_upper': 72.00, 'support': 65.00, 'resistance': 71.00},
    '601088.SH': {'ma20': 39.00, 'boll_lower': 37.50, 'boll_upper': 42.00, 'support': 38.50, 'resistance': 41.50},
    '300760.SZ': {'ma20': 285.00, 'boll_lower': 275.00, 'boll_upper': 310.00, 'support': 280.00, 'resistance': 305.00},
    '603259.SH': {'ma20': 140.00, 'boll_lower': 135.00, 'boll_upper': 155.00, 'support': 138.00, 'resistance': 152.00},
    '002690.SZ': {'ma20': 30.50, 'boll_lower': 29.00, 'boll_upper': 34.00, 'support': 30.00, 'resistance': 33.50},
    '600036.SH': {'ma20': 41.00, 'boll_lower': 40.00, 'boll_upper': 45.00, 'support': 41.00, 'resistance': 44.50},
    '600938.SH': {'ma20': 27.50, 'boll_lower': 26.50, 'boll_upper': 30.00, 'support': 27.00, 'resistance': 29.50},
    '601899.SH': {'ma20': 18.00, 'boll_lower': 17.50, 'boll_upper': 20.00, 'support': 17.80, 'resistance': 19.50},
    '300750.SZ': {'ma20': 384.79, 'boll_lower': 390.00, 'boll_upper': 440.00, 'support': 400.00, 'resistance': 430.00},
    '002460.SZ': {'ma20': 79.13, 'boll_lower': 76.00, 'boll_upper': 85.00, 'support': 77.00, 'resistance': 83.00},
    '601398.SH': {'ma20': 5.70, 'boll_lower': 5.50, 'boll_upper': 6.20, 'support': 5.65, 'resistance': 6.10},
    '600900.SH': {'ma20': 27.50, 'boll_lower': 26.50, 'boll_upper': 30.00, 'support': 27.00, 'resistance': 29.50},
}

# 特殊调整因子（地缘政治等）
SPECIAL_ADJUSTMENTS = {
    'energy': 1.10,      # 能源类 +10%（油价上涨）
    'resource': 1.08,    # 资源类 +8%
    'defense': 1.03,     # 防御类 +3%
    'consumer': 1.00,    # 消费类 0%
    'tech': 0.95,        # 科技类 -5%
    'chemical': 0.90,    # 化工类 -10%（成本压力）
}


# ==================== 价格计算器 ====================

class PriceCalculator:
    """价格计算器 - 计算买入/卖出建议价格"""
    
    def __init__(self):
        self.current_prices = CURRENT_PRICES
        self.technical_data = TECHNICAL_DATA
        self.special_adjustments = SPECIAL_ADJUSTMENTS
    
    def calculate_buy_price(self, stock_code: str, industry: str, 
                           special_factor: float = 1.0) -> Tuple[float, float, str]:
        """
        计算买入建议价格
        
        Returns:
            (建议价格，止损价格，价格类型)
        """
        if stock_code not in self.current_prices:
            return 0.0, 0.0, '无数据'
        
        current_price = self.current_prices[stock_code]
        tech = self.technical_data.get(stock_code, {})
        
        # 获取技术支撑位
        ma20 = tech.get('ma20', current_price * 0.95)
        boll_lower = tech.get('boll_lower', current_price * 0.93)
        support = tech.get('support', current_price * 0.95)
        
        # 特殊调整（地缘政治等）
        industry_type = self._get_industry_type(industry)
        geo_adjustment = self.special_adjustments.get(industry_type, 1.0)
        
        # 计算建议价格（取支撑位和当前价的中间值，考虑特殊因子）
        if current_price <= ma20:
            # 当前价低于 20 日均线，可以现价买入
            suggested_price = current_price * special_factor
            price_type = '现价买入'
        else:
            # 当前价高于 20 日均线，等待回调
            suggested_price = max(ma20, support) * special_factor
            price_type = '回调买入'
        
        # 考虑地缘政治调整
        suggested_price *= geo_adjustment
        
        # 计算止损价格（-12%）
        stop_loss_price = suggested_price * 0.88
        
        return round(suggested_price, 2), round(stop_loss_price, 2), price_type
    
    def calculate_sell_price(self, stock_code: str, industry: str,
                            current_shares: int, avg_price: float) -> Tuple[float, float, str]:
        """
        计算卖出建议价格
        
        Returns:
            (建议价格，止盈价格，价格类型)
        """
        if stock_code not in self.current_prices:
            return 0.0, 0.0, '无数据'
        
        current_price = self.current_prices[stock_code]
        tech = self.technical_data.get(stock_code, {})
        
        # 获取技术阻力位
        ma20 = tech.get('ma20', current_price * 1.05)
        boll_upper = tech.get('boll_upper', current_price * 1.08)
        resistance = tech.get('resistance', current_price * 1.05)
        
        # 计算盈亏比例
        profit_rate = (current_price - avg_price) / avg_price * 100
        
        # 计算建议价格
        if current_price >= resistance:
            # 当前价接近阻力位，建议卖出
            suggested_price = current_price
            price_type = '现价卖出'
        else:
            # 等待反弹
            suggested_price = min(resistance, boll_upper)
            price_type = '反弹卖出'
        
        # 计算止盈价格（+20%）
        target_price = avg_price * 1.20
        
        return round(suggested_price, 2), round(target_price, 2), price_type
    
    def _get_industry_type(self, industry: str) -> str:
        """获取行业类型"""
        if industry in ['石油', '煤炭', '电池', '锂业']:
            return 'energy'
        elif industry in ['有色', '钢铁']:
            return 'resource'
        elif industry in ['银行', '电力', '公用事业']:
            return 'defense'
        elif industry in ['白酒', '家电', '食品']:
            return 'consumer'
        elif industry in ['机械', '电子', '科技']:
            return 'tech'
        elif industry in ['化工', '航空']:
            return 'chemical'
        else:
            return 'consumer'


# ==================== 交易指令生成器 ====================

class TradeInstructionGenerator:
    """交易指令生成器 - 带具体价格建议"""
    
    def __init__(self, total_assets: float = TOTAL_ASSETS):
        self.total_assets = total_assets
        self.current_holdings = CURRENT_HOLDINGS
        self.target_stocks = TARGET_STOCKS
        self.current_prices = CURRENT_PRICES
        self.price_calculator = PriceCalculator()
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
    
    def get_avg_price(self, stock_code: str) -> float:
        """获取持仓成本价"""
        if stock_code not in self.current_holdings:
            return 0.0
        return self.current_holdings[stock_code]['avg_price']
    
    def generate_instructions(self) -> List[Dict]:
        """生成交易指令清单"""
        instructions = []
        
        # 处理目标股票池中的所有股票
        for stock_code, stock_info in self.target_stocks.items():
            current_shares = self.get_current_shares(stock_code)
            target_weight = stock_info['target_weight']
            target_value = self.total_assets * target_weight
            current_price = self.current_prices.get(stock_code, 0)
            
            if current_price <= 0:
                continue
            
            target_shares = int(target_value / current_price / 100) * 100
            delta_shares = target_shares - current_shares
            
            if abs(delta_shares) * current_price < 10000:
                continue
            
            if delta_shares > 0:
                buy_price, stop_loss, price_type = self.price_calculator.calculate_buy_price(
                    stock_code, stock_info['industry'], stock_info.get('special_factor', 1.0))
                instruction = {
                    'action': 'BUY',
                    'stock_code': stock_code,
                    'stock_name': stock_info['name'],
                    'industry': stock_info['industry'],
                    'current_shares': current_shares,
                    'target_shares': target_shares,
                    'delta_shares': delta_shares,
                    'current_price': current_price,
                    'suggested_price': buy_price,
                    'stop_loss_price': stop_loss,
                    'price_type': price_type,
                    'trade_value': delta_shares * buy_price,
                    'target_weight': target_weight,
                }
            else:
                avg_price = self.get_avg_price(stock_code)
                sell_price, target_price, price_type = self.price_calculator.calculate_sell_price(
                    stock_code, stock_info['industry'], current_shares, avg_price)
                instruction = {
                    'action': 'SELL',
                    'stock_code': stock_code,
                    'stock_name': stock_info['name'],
                    'industry': stock_info['industry'],
                    'current_shares': current_shares,
                    'target_shares': 0,
                    'delta_shares': abs(delta_shares),
                    'current_price': current_price,
                    'suggested_price': sell_price,
                    'target_price': target_price,
                    'price_type': price_type,
                    'trade_value': abs(delta_shares) * sell_price,
                    'avg_price': avg_price,
                    'profit_rate': (current_price - avg_price) / avg_price * 100,
                }
            
            instructions.append(instruction)
        
        instructions.sort(key=lambda x: (0 if x['action'] == 'BUY' else 1, -x['trade_value']))
        self.trade_instructions = instructions
        return instructions
    
    def print_instructions(self):
        """打印交易指令清单"""
        if not self.trade_instructions:
            self.generate_instructions()
        
        print("="*120)
        print("实盘交易指令清单 - 带具体建议价格")
        print("="*120)
        print(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总资产规模：{self.total_assets:,.2f} 元")
        print(f"执行时间建议：2026-03-29 09:30-10:00")
        print("="*120)
        
        buy_instructions = [i for i in self.trade_instructions if i['action'] == 'BUY']
        sell_instructions = [i for i in self.trade_instructions if i['action'] == 'SELL']
        
        total_buy = sum(i['trade_value'] for i in buy_instructions)
        total_sell = sum(i['trade_value'] for i in sell_instructions)
        
        print(f"\n📊 交易汇总")
        print(f"  买入指令：{len(buy_instructions)} 条，总金额：{total_buy:,.2f} 元")
        print(f"  卖出指令：{len(sell_instructions)} 条，总金额：{total_sell:,.2f} 元")
        print(f"  净买入：{total_buy - total_sell:,.2f} 元")
        print()
        
        print("🟢 买入指令（{}条）".format(len(buy_instructions)))
        print("-"*120)
        print(f"{'序号':<4} {'代码':<10} {'名称':<12} {'数量':>8} {'现价':>10} {'建议价':>10} {'止损价':>10} {'类型':<10} {'金额':>12}")
        print("-"*120)
        for idx, inst in enumerate(buy_instructions, 1):
            print(f"{idx:<4} {inst['stock_code']:<10} {inst['stock_name']:<12} {inst['delta_shares']:>8} "
                  f"{inst['current_price']:>10.2f} {inst['suggested_price']:>10.2f} {inst['stop_loss_price']:>10.2f} "
                  f"{inst['price_type']:<10} {inst['trade_value']:>12,.0f}")
        print()
        
        print("🔴 卖出指令（{}条）".format(len(sell_instructions)))
        print("-"*120)
        print(f"{'序号':<4} {'代码':<10} {'名称':<12} {'数量':>8} {'现价':>10} {'建议价':>10} {'成本价':>10} {'盈亏':>8} {'金额':>12}")
        print("-"*120)
        for idx, inst in enumerate(sell_instructions, 1):
            print(f"{idx:<4} {inst['stock_code']:<10} {inst['stock_name']:<12} {inst['delta_shares']:>8} "
                  f"{inst['current_price']:>10.2f} {inst['suggested_price']:>10.2f} {inst['avg_price']:>10.2f} "
                  f"{inst['profit_rate']:>7.1f}% {inst['trade_value']:>12,.0f}")
        print()
        print("="*120)
        print("✅ 交易指令生成完成！")
        print("="*120)


if __name__ == '__main__':
    generator = TradeInstructionGenerator()
    generator.generate_instructions()
    generator.print_instructions()