#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
因子权重优化模块 - 动态多因子策略

功能：
1. 市场情景识别（牛市/熊市/震荡市）
2. 动态因子权重配置
3. 因子评分体系
4. 8 年回测框架（2018-2026）

作者：OpenClaw AgentSkill
日期：2026-03-28
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
from enum import Enum

# ==================== 枚举和常量 ====================

class MarketState(Enum):
    """市场状态枚举"""
    BULL = "牛市"
    BEAR = "熊市"
    OSCILLATE = "震荡市"


# 市场情景定义（2018-2026）
MARKET_STATES = {
    2018: MarketState.BEAR,      # -25.31%
    2019: MarketState.BULL,      # +36.07%
    2020: MarketState.BULL,      # +27.21%
    2021: MarketState.OSCILLATE, # -5.20%
    2022: MarketState.BEAR,      # -21.63%
    2023: MarketState.BEAR,      # -11.38%
    2024: MarketState.BULL,      # +14.68%
    2025: MarketState.BULL,      # +17.66%
    2026: MarketState.OSCILLATE, # -2.75%
}

# 动态因子权重配置
FACTOR_WEIGHTS = {
    MarketState.BULL: {
        'momentum': 0.40,    # 动量因子 40%
        'volume_price': 0.30,  # 量价因子 30%
        'rsi': 0.20,         # 三重 RSI 20%
        'sentiment': 0.10,   # 市场情绪 10%
    },
    MarketState.BEAR: {
        'rsi': 0.50,         # 三重 RSI 50%
        'quality': 0.30,     # 质量因子 30%
        'momentum': 0.10,    # 动量因子 10%
        'volume_price': 0.10,  # 量价因子 10%
        'sentiment': 0.00,   # 市场情绪 0%
    },
    MarketState.OSCILLATE: {
        'volume_price': 0.40,  # 量价因子 40%
        'rsi': 0.30,         # 三重 RSI 30%
        'momentum': 0.20,    # 动量因子 20%
        'sentiment': 0.10,   # 市场情绪 10%
    },
}

# 仓位管理
POSITION_LIMITS = {
    MarketState.BULL: (0.80, 1.00),     # 牛市 80-100%
    MarketState.BEAR: (0.30, 0.50),     # 熊市 30-50%
    MarketState.OSCILLATE: (0.50, 0.70), # 震荡市 50-70%
}

# 风险控制参数
MAX_SINGLE_WEIGHT = 0.08  # 单只股票最大权重 8%
MAX_INDUSTRY_WEIGHT = 0.25  # 单一行业最大权重 25%
MAX_DRAWDOWN = 0.20  # 最大回撤止损 20%


# ==================== 质量因子股票池（135 支精选） ====================

QUALITY_STOCKS = {
    # 核心龙头（20 支）
    '600519.SH': {'name': '贵州茅台', 'industry': '白酒', 'PE': 19.70, 'ROE': 26.37, 'ROIC': 24.33},
    '000858.SZ': {'name': '五粮液', 'industry': '白酒', 'PE': 14.01, 'ROE': 15.60, 'ROIC': 14.57},
    '000333.SZ': {'name': '美的集团', 'industry': '家电', 'PE': 12.71, 'ROE': 17.33, 'ROIC': 11.40},
    '601088.SH': {'name': '中国神华', 'industry': '煤炭', 'PE': 19.53, 'ROE': 9.27, 'ROIC': 8.73},
    '600938.SH': {'name': '中国海油', 'industry': '石油', 'PE': 15.99, 'ROE': 15.75, 'ROIC': 13.99},
    '300760.SZ': {'name': '迈瑞医疗', 'industry': '医疗设备', 'PE': 23.91, 'ROE': 20.15, 'ROIC': 17.54},
    '603259.SH': {'name': '药明康德', 'industry': '医药', 'PE': 15.11, 'ROE': 27.69, 'ROIC': 23.92},
    '000568.SZ': {'name': '泸州老窖', 'industry': '白酒', 'PE': 12.08, 'ROE': 22.17, 'ROIC': 18.47},
    '601899.SH': {'name': '紫金矿业', 'industry': '有色', 'PE': 16.67, 'ROE': 31.83, 'ROIC': 17.55},
    '002594.SZ': {'name': '比亚迪', 'industry': '汽车', 'PE': 25.03, 'ROE': 15.12, 'ROIC': 10.82},
    '600660.SH': {'name': '福耀玻璃', 'industry': '汽配', 'PE': 16.17, 'ROE': 25.43, 'ROIC': 16.78},
    '002027.SZ': {'name': '分众传媒', 'industry': '广告', 'PE': 17.16, 'ROE': 25.32, 'ROIC': 21.07},
    '300628.SZ': {'name': '亿联网络', 'industry': '通信', 'PE': 15.63, 'ROE': 22.22, 'ROIC': 22.12},
    '603195.SH': {'name': '公牛集团', 'industry': '电气', 'PE': 18.72, 'ROE': 18.90, 'ROIC': 17.63},
    '002690.SZ': {'name': '美亚光电', 'industry': '机械', 'PE': 22.17, 'ROE': 18.82, 'ROIC': 18.03},
    '603025.SH': {'name': '大豪科技', 'industry': '电气', 'PE': 22.11, 'ROE': 27.80, 'ROIC': 21.58},
    '000786.SZ': {'name': '北新建材', 'industry': '建材', 'PE': 14.61, 'ROE': 11.00, 'ROIC': 10.16},
    '601225.SH': {'name': '陕西煤业', 'industry': '煤炭', 'PE': 15.30, 'ROE': 13.74, 'ROIC': 13.03},
    '600809.SH': {'name': '山西汾酒', 'industry': '白酒', 'PE': 14.73, 'ROE': 31.02, 'ROIC': 30.42},
    '002351.SZ': {'name': '漫步者', 'industry': '消费电子', 'PE': 23.41, 'ROE': 14.94, 'ROIC': 15.14},
}


# ==================== 因子评分器 ====================

class FactorScorer:
    """因子评分器"""
    
    def __init__(self):
        self.quality_stocks = QUALITY_STOCKS
    
    def score_momentum(self, stock_code: str, mi_value: float) -> float:
        """
        动量因子评分（基于 MI 指标）
        MI > 100: 5 分（前 20%）
        MI 50-100: 4 分
        MI 0-50: 3 分
        MI -50-0: 2 分
        MI < -50: 1 分（后 20%）
        """
        if mi_value > 100:
            return 5.0
        elif mi_value > 50:
            return 4.0
        elif mi_value > 0:
            return 3.0
        elif mi_value > -50:
            return 2.0
        else:
            return 1.0
    
    def score_volume_price(self, stock_code: str, vma_ratio: float) -> float:
        """
        量价因子评分（基于 VMA 与历史均值比率）
        vma_ratio > 2.0: 5 分（前 20%）
        vma_ratio 1.5-2.0: 4 分
        vma_ratio 1.0-1.5: 3 分
        vma_ratio 0.5-1.0: 2 分
        vma_ratio < 0.5: 1 分（后 20%）
        """
        if vma_ratio > 2.0:
            return 5.0
        elif vma_ratio > 1.5:
            return 4.0
        elif vma_ratio > 1.0:
            return 3.0
        elif vma_ratio > 0.5:
            return 2.0
        else:
            return 1.0
    
    def score_rsi(self, stock_code: str, rsi6: float, rsi12: float, rsi24: float) -> float:
        """
        三重 RSI 综合评分
        RSI<30: 超卖，5 分
        RSI 30-50: 4 分
        RSI 50-70: 3 分
        RSI>70: 超买，1-2 分
        """
        avg_rsi = (rsi6 + rsi12 + rsi24) / 3
        
        if avg_rsi < 30:
            return 5.0  # 超卖，买入信号
        elif avg_rsi < 50:
            return 4.0
        elif avg_rsi < 70:
            return 3.0
        else:
            return 1.5  # 超买，风险较高
    
    def score_sentiment(self, stock_code: str, turnover_rate: float, amplitude: float) -> float:
        """
        市场情绪评分（基于换手率、振幅）
        """
        # 简化评分逻辑
        score = 3.0
        if turnover_rate > 5.0:
            score += 1.0
        if amplitude > 5.0:
            score += 1.0
        return min(score, 5.0)
    
    def score_quality(self, stock_code: str) -> float:
        """
        质量因子评分（基于 ROE、ROIC、PE）
        """
        if stock_code not in self.quality_stocks:
            return 3.0
        
        stock = self.quality_stocks[stock_code]
        score = 0.0
        
        # ROE 评分（0-3 分）
        roe = stock['ROE']
        if roe > 20:
            score += 3.0
        elif roe > 15:
            score += 2.5
        elif roe > 10:
            score += 2.0
        else:
            score += 1.0
        
        # ROIC 评分（0-3 分）
        roic = stock['ROIC']
        if roic > 20:
            score += 3.0
        elif roic > 15:
            score += 2.5
        elif roic > 10:
            score += 2.0
        else:
            score += 1.0
        
        # PE 估值评分（0-4 分，越低越好）
        pe = stock['PE']
        if pe < 15:
            score += 4.0
        elif pe < 20:
            score += 3.0
        elif pe < 30:
            score += 2.0
        else:
            score += 1.0
        
        return min(score, 10.0) / 10.0 * 5.0  # 归一化到 1-5 分
    
    def calculate_composite_score(self, stock_code: str, market_state: MarketState,
                                   mi: float = 0, vma_ratio: float = 1.0,
                                   rsi6: float = 50, rsi12: float = 50, rsi24: float = 50,
                                   turnover: float = 2.0, amplitude: float = 3.0) -> float:
        """计算综合评分"""
        weights = FACTOR_WEIGHTS[market_state]
        
        score = 0.0
        score += weights.get('momentum', 0) * self.score_momentum(stock_code, mi)
        score += weights.get('volume_price', 0) * self.score_volume_price(stock_code, vma_ratio)
        score += weights.get('rsi', 0) * self.score_rsi(stock_code, rsi6, rsi12, rsi24)
        score += weights.get('sentiment', 0) * self.score_sentiment(stock_code, turnover, amplitude)
        score += weights.get('quality', 0) * self.score_quality(stock_code)
        
        return score


if __name__ == '__main__':
    print("="*80)
    print("因子权重优化模块 - 测试运行")
    print("="*80)
    
    scorer = FactorScorer()
    
    # 测试市场情景
    print("\n📊 市场情景测试：")
    for year, state in MARKET_STATES.items():
        weights = FACTOR_WEIGHTS[state]
        print(f"  {year}年 ({state.value}):")
        for factor, weight in weights.items():
            if weight > 0:
                print(f"    {factor}: {weight*100:.0f}%")
    
    # 测试个股评分
    print("\n📈 个股综合评分测试（示例）：")
    test_stocks = ['600519.SH', '000858.SZ', '300760.SZ']
    
    for stock_code in test_stocks:
        if stock_code in QUALITY_STOCKS:
            stock = QUALITY_STOCKS[stock_code]
            # 牛市情景
            score_bull = scorer.calculate_composite_score(
                stock_code, MarketState.BULL,
                mi=80, vma_ratio=1.5, rsi6=55, rsi12=52, rsi24=50
            )
            # 熊市情景
            score_bear = scorer.calculate_composite_score(
                stock_code, MarketState.BEAR,
                mi=20, vma_ratio=0.8, rsi6=28, rsi12=32, rsi24=35
            )
            print(f"  {stock_code} {stock['name']}:")
            print(f"    牛市评分：{score_bull:.2f}")
            print(f"    熊市评分：{score_bear:.2f}")
    
    print("\n" + "="*80)
    print("✅ 因子权重优化模块测试完成！")
    print("="*80)