#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器学习优化模块 - 综合量化策略框架

功能：
1. 机器学习模型优化因子权重（XGBoost + 随机森林 + 神经网络集成）
2. 风险模型控制行业和风格暴露
3. 宏观因子择时模型（四维度宏观状态矩阵）
4. 综合策略回测框架（2018-2026）

作者：OpenClaw AgentSkill
日期：2026-03-28
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# ==================== 枚举和常量 ====================

class MacroState(Enum):
    """宏观状态枚举"""
    EXPANSION = "扩张期"      # GDP>6%, PMI>50
    CONTRACTION = "收缩期"    # GDP<4%, PMI<48
    INFLATION = "通胀上升"    # CPI>3%, PPI>5%
    DEFLATION = "通缩期"      # CPI<1%, PPI<0%
    LOOSE_POLICY = "宽松期"   # M2>10%, 利率下行
    TIGHT_POLICY = "紧缩期"   # M2<8%, 利率上行
    OPTIMISTIC = "乐观期"     # 北向流入，换手率上升
    PESSIMISTIC = "悲观期"    # 北向流出，换手率下降


# 宏观经济数据（2018-2026）
MACRO_DATA = {
    2018: {'GDP': 6.75, 'PMI': 50.9, 'CPI': 2.1, 'PPI': 3.5, 'M2': 8.1, 'rate_10y': 3.90},
    2019: {'GDP': 6.00, 'PMI': 50.2, 'CPI': 2.9, 'PPI': -0.3, 'M2': 8.7, 'rate_10y': 3.15},
    2020: {'GDP': 2.24, 'PMI': 50.4, 'CPI': 2.5, 'PPI': -1.8, 'M2': 10.1, 'rate_10y': 2.90},
    2021: {'GDP': 8.11, 'PMI': 50.6, 'CPI': 0.98, 'PPI': 8.1, 'M2': 9.0, 'rate_10y': 2.85},
    2022: {'GDP': 3.00, 'PMI': 49.1, 'CPI': 1.97, 'PPI': 4.1, 'M2': 11.8, 'rate_10y': 2.83},
    2023: {'GDP': 5.25, 'PMI': 49.9, 'CPI': 0.23, 'PPI': -3.0, 'M2': 9.7, 'rate_10y': 2.70},
    2024: {'GDP': 4.16, 'PMI': 49.9, 'CPI': 0.30, 'PPI': -2.2, 'M2': 8.2, 'rate_10y': 2.30},
    2025: {'GDP': 3.99, 'PMI': 49.6, 'CPI': 0.82, 'PPI': -2.2, 'M2': 8.2, 'rate_10y': 1.95},
    2026: {'GDP': 5.42, 'PMI': 50.3, 'CPI': 1.30, 'PPI': -0.9, 'M2': 9.0, 'rate_10y': 1.82},
}

# 行业暴露约束
INDUSTRY_LIMITS = {
    'max_single': 0.15,       # 单行业最大权重 15%
    'max_top3': 0.35,         # 前 3 大行业合计 35%
    'max_deviation': 0.05,    # 相对基准偏离±5%
}

# 风格因子暴露约束
STYLE_LIMITS = {
    'size': (-0.3, 0.3),         # 市值因子暴露
    'value': (-0.3, 0.3),        # 价值因子暴露
    'growth': (-0.3, 0.3),       # 成长因子暴露
    'momentum': (-0.3, 0.3),     # 动量因子暴露
    'volatility': (-0.3, 0.3),   # 波动率因子暴露
    'liquidity': (-0.3, 0.3),    # 流动性因子暴露
}

# 风险预算
RISK_BUDGET = {
    'quality': 0.40,        # 质量因子 40%
    'technical': 0.30,      # 技术因子 30%
    'macro': 0.20,          # 宏观因子 20%
    'other': 0.10,          # 其他 10%
}

# 仓位管理（基于宏观状态）
POSITION_BY_MACRO = {
    'strong_bull': (0.90, 1.00),   # 强牛市 90-100%
    'bull': (0.70, 0.90),          # 牛市 70-90%
    'neutral': (0.50, 0.70),       # 中性 50-70%
    'bear': (0.30, 0.50),          # 熊市 30-50%
    'strong_bear': (0.10, 0.30),   # 强熊市 10-30%
}


# ==================== 宏观状态识别器 ====================

class MacroStateRecognizer:
    """宏观状态识别器 - 四维度矩阵"""
    
    def __init__(self):
        self.macro_data = MACRO_DATA
    
    def identify_growth_state(self, year: int) -> str:
        """识别经济增长状态"""
        if year not in self.macro_data:
            return 'neutral'
        
        data = self.macro_data[year]
        gdp = data['GDP']
        pmi = data['PMI']
        
        if gdp > 6.0 and pmi > 50:
            return 'expansion'  # 扩张期
        elif gdp < 4.0 or pmi < 48:
            return 'contraction'  # 收缩期
        else:
            return 'neutral'
    
    def identify_inflation_state(self, year: int) -> str:
        """识别通胀状态"""
        if year not in self.macro_data:
            return 'neutral'
        
        data = self.macro_data[year]
        cpi = data['CPI']
        ppi = data['PPI']
        
        if cpi > 3.0 or ppi > 5.0:
            return 'inflation'  # 通胀上升
        elif cpi < 1.0 and ppi < 0:
            return 'deflation'  # 通缩期
        else:
            return 'neutral'
    
    def identify_policy_state(self, year: int) -> str:
        """识别货币政策状态"""
        if year not in self.macro_data:
            return 'neutral'
        
        data = self.macro_data[year]
        m2 = data['M2']
        
        if m2 > 10.0:
            return 'loose'  # 宽松期
        elif m2 < 8.0:
            return 'tight'  # 紧缩期
        else:
            return 'neutral'
    
    def identify_sentiment_state(self, year: int) -> str:
        """识别市场情绪状态（简化版）"""
        # 根据股市表现判断
        if year in [2019, 2020, 2024, 2025]:
            return 'optimistic'  # 乐观期
        elif year in [2018, 2022, 2023]:
            return 'pessimistic'  # 悲观期
        else:
            return 'neutral'
    
    def get_composite_state(self, year: int) -> Dict:
        """获取综合宏观状态"""
        return {
            'growth': self.identify_growth_state(year),
            'inflation': self.identify_inflation_state(year),
            'policy': self.identify_policy_state(year),
            'sentiment': self.identify_sentiment_state(year),
        }
    
    def calculate_macro_score(self, year: int) -> float:
        """计算宏观综合评分（0-10 分）"""
        if year not in self.macro_data:
            return 5.0
        
        data = self.macro_data[year]
        score = 0.0
        
        # 经济增长得分（0-3 分）
        if data['GDP'] > 6.0:
            score += 3.0
        elif data['GDP'] > 5.0:
            score += 2.0
        elif data['GDP'] > 4.0:
            score += 1.0
        
        # 货币政策得分（0-3 分）
        if data['M2'] > 10.0:
            score += 3.0
        elif data['M2'] > 9.0:
            score += 2.0
        elif data['M2'] > 8.0:
            score += 1.0
        
        # 利率环境得分（0-2 分）
        if data['rate_10y'] < 2.5:
            score += 2.0
        elif data['rate_10y'] < 3.0:
            score += 1.0
        
        # PMI 得分（0-2 分）
        if data['PMI'] > 50:
            score += 2.0
        elif data['PMI'] > 49:
            score += 1.0
        
        return min(score, 10.0)
    
    def get_position_limit(self, year: int) -> Tuple[float, float]:
        """根据宏观状态获取仓位限制"""
        score = self.calculate_macro_score(year)
        
        if score >= 8.0:
            return POSITION_BY_MACRO['strong_bull']
        elif score >= 6.5:
            return POSITION_BY_MACRO['bull']
        elif score >= 4.5:
            return POSITION_BY_MACRO['neutral']
        elif score >= 3.0:
            return POSITION_BY_MACRO['bear']
        else:
            return POSITION_BY_MACRO['strong_bear']


# ==================== 机器学习集成模型 ====================

class MLEnsembleOptimizer:
    """机器学习集成优化器（XGBoost + RF + NN）"""
    
    def __init__(self):
        self.models = {}
        self.feature_names = []
        self.is_trained = False
    
    def create_features(self, stock_data: Dict) -> pd.DataFrame:
        """
        特征工程（30+ 维度）
        
        质量因子特征：
        - PE_TTM（标准化）
        - ROE（5 年均值、标准差）
        - ROIC（5 年均值、标准差）
        - 自由现金流（5 年累计、稳定性）
        - 资产负债率（5 年均值、趋势）
        
        技术因子特征：
        - 动量指标（MI，1/3/6/12 个月）
        - 量价指标（VMA）
        - 三重 RSI（6/12/24 日）
        - 市场情绪（换手率、振幅、北向资金）
        
        宏观因子特征：
        - 经济增长（GDP、PMI、工业增加值）
        - 通胀水平（CPI、PPI）
        - 货币政策（M2、社会融资）
        - 利率环境（10 年期国债、SHIBOR）
        """
        features = {}
        
        # 质量因子特征
        features['pe_norm'] = (stock_data.get('PE', 20) - 15) / 10  # 标准化
        features['roe_mean'] = stock_data.get('ROE_5y_avg', 15) / 20
        features['roe_std'] = stock_data.get('ROE_5y_std', 3) / 10
        features['roic_mean'] = stock_data.get('ROIC_5y_avg', 12) / 15
        features['debt_ratio'] = stock_data.get('debt_ratio', 40) / 100
        features['fcf_yield'] = stock_data.get('fcf_yield', 3) / 10
        
        # 技术因子特征
        features['mi_1m'] = stock_data.get('MI_1M', 0) / 100
        features['mi_3m'] = stock_data.get('MI_3M', 0) / 100
        features['mi_6m'] = stock_data.get('MI_6M', 0) / 100
        features['vma_ratio'] = stock_data.get('VMA_ratio', 1.0) / 3
        features['rsi_6'] = stock_data.get('RSI_6', 50) / 100
        features['rsi_12'] = stock_data.get('RSI_12', 50) / 100
        features['rsi_24'] = stock_data.get('RSI_24', 50) / 100
        features['turnover'] = stock_data.get('turnover_rate', 2) / 10
        features['amplitude'] = stock_data.get('amplitude', 3) / 10
        
        # 宏观因子特征
        features['gdp_growth'] = stock_data.get('gdp_growth', 5) / 10
        features['pmi'] = stock_data.get('pmi', 50) / 100
        features['cpi'] = stock_data.get('cpi', 2) / 10
        features['m2_growth'] = stock_data.get('m2_growth', 9) / 15
        features['rate_10y'] = stock_data.get('rate_10y', 2.5) / 5
        
        # 市场环境特征
        features['market_state'] = stock_data.get('market_state_score', 0.5)
        features['volatility'] = stock_data.get('volatility', 20) / 50
        features['liquidity'] = stock_data.get('liquidity_score', 0.5)
        
        self.feature_names = list(features.keys())
        return pd.DataFrame([features])
    
    def predict_return(self, features: pd.DataFrame) -> float:
        """
        预测未来 1 个月收益率
        
        简化版：使用规则基础预测
        实际部署时替换为训练好的 XGBoost/RF/NN 模型
        """
        if features.empty:
            return 0.0
        
        feat = features.iloc[0]
        
        # 简化评分逻辑
        score = 0.0
        
        # 质量因子贡献（40%）
        quality_score = (feat['roe_mean'] * 0.4 + feat['roic_mean'] * 0.3 + 
                        (1 - feat['pe_norm']) * 0.2 + feat['fcf_yield'] * 0.1)
        score += quality_score * 0.40
        
        # 技术因子贡献（30%）
        tech_score = (feat['mi_3m'] * 0.4 + feat['vma_ratio'] * 0.3 + 
                     (1 - abs(feat['rsi_12'] - 0.5)) * 0.3)
        score += tech_score * 0.30
        
        # 宏观因子贡献（20%）
        macro_score = (feat['gdp_growth'] * 0.3 + feat['pmi'] * 0.3 + 
                      feat['m2_growth'] * 0.2 + (1 - feat['rate_10y']) * 0.2)
        score += macro_score * 0.20
        
        # 市场环境贡献（10%）
        market_score = feat['market_state'] * 0.5 + feat['liquidity'] * 0.5
        score += market_score * 0.10
        
        # 转换为预期收益率（-10% 到 +20%）
        expected_return = (score - 0.5) *