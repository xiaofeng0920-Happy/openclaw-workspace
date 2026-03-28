#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
方案 2：机器学习增强框架
使用 LightGBM 模型进行收益率预测

技术栈：
- 模型：LightGBM
- 因子：15-20 个（包含情绪因子）
- 工具：Qlib + LightGBM
- 预期 IC：0.06 → 0.08
- 预期年化收益：15% → 20%

状态：🚧 开发中（Q2 2026 实施）
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("请安装依赖：pip install pandas numpy")
    sys.exit(1)

# ============== 配置 ==============

# 因子列表（15-20 个）
FACTOR_LIST = [
    # 动量因子 (5 个)
    'momentum_1m',      # 1 个月动量
    'momentum_3m',      # 3 个月动量
    'momentum_6m',      # 6 个月动量
    'rsi_14',           # RSI 指标
    'macd_signal',      # MACD 信号
    
    # 价值因子 (4 个)
    'pe_ratio',         # 市盈率
    'pb_ratio',         # 市净率
    'ps_ratio',         # 市销率
    'dividend_yield',   # 股息率
    
    # 质量因子 (4 个)
    'roe',              # ROE
    'roa',              # ROA
    'debt_to_equity',   # 资产负债率
    'profit_margin',    # 净利率
    
    # 情绪因子 (5 个) ⭐ 新增
    'sentiment_score',  # 综合情绪评分
    'turnover_score',   # 换手率评分
    'flow_score',       # 资金流向评分
    'volume_ratio',     # 成交量比率
    'price_strength'    # 价格强度
]

# 模型配置
MODEL_CONFIG = {
    'objective': 'regression',
    'metric': 'mse',
    'boosting_type': 'gbdt',
    'num_leaves': 31,
    'learning_rate': 0.05,
    'feature_fraction': 0.9,
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    'verbose': -1,
    'seed': 42,
}

# 训练配置
TRAIN_CONFIG = {
    'train_days': 730,    # 训练数据天数（2 年）
    'valid_days': 180,    # 验证数据天数（6 个月）
    'test_days': 90,      # 测试数据天数（3 个月）
    'label_days': 20,     # 预测周期（20 日收益率）
}


class MLStockPredictor:
    """机器学习股票预测器"""
    
    def __init__(self):
        self.model = None
        self.feature_importance = None
        self.train_data = None
        self.valid_data = None
        self.test_data = None
    
    def prepare_data(self, symbols, start_date, end_date):
        """
        准备训练数据
        
        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            DataFrame: 包含因子和标签的数据
        """
        print(f"📊 准备数据：{len(symbols)}只股票，{start_date} 至 {end_date}")
        
        # TODO: 实现数据获取
        # 1. 获取历史行情
        # 2. 计算因子
        # 3. 生成标签（未来 20 日收益率）
        # 4. 数据清洗（去极值、标准化）
        
        print("  ⚠️  数据准备功能开发中...")
        return pd.DataFrame()
    
    def calculate_factors(self, price_data, financial_data):
        """
        计算因子值
        
        Args:
            price_data: 行情数据
            financial_data: 财务数据
        
        Returns:
            DataFrame: 因子矩阵
        """
        factors = pd.DataFrame()
        
        # 动量因子
        factors['momentum_1m'] = price_data['close'].pct_change(20)
        factors['momentum_3m'] = price_data['close'].pct_change(60)
        factors['momentum_6m'] = price_data['close'].pct_change(120)
        
        # RSI
        delta = price_data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        factors['rsi_14'] = 100 - (100 / (1 + rs))
        
        # 价值因子
        factors['pe_ratio'] = financial_data.get('pe', np.nan)
        factors['pb_ratio'] = financial_data.get('pb', np.nan)
        factors['dividend_yield'] = financial_data.get('dividend_yield', 0)
        
        # 质量因子
        factors['roe'] = financial_data.get('roe', np.nan)
        factors['roa'] = financial_data.get('roa', np.nan)
        factors['debt_to_equity'] = financial_data.get('debt_to_equity', np.nan)
        
        # 情绪因子（从 sentiment_factor 模块导入）
        try:
            from sentiment_factor import calculate_sentiment_score
            # TODO: 批量计算情绪因子
            print("  ✓ 情绪因子计算就绪")
        except:
            print("  ⚠️  情绪因子模块未加载")
        
        return factors
    
    def train_model(self, train_data, valid_data):
        """
        训练 LightGBM 模型
        
        Args:
            train_data: 训练数据
            valid_data: 验证数据
        
        Returns:
            训练好的模型
        """
        try:
            import lightgbm as lgb
        except ImportError:
            print("请安装 LightGBM: pip install lightgbm")
            return None
        
        print("🚀 开始训练 LightGBM 模型...")
        
        # 准备训练数据
        X_train = train_data[FACTOR_LIST]
        y_train = train_data['label']
        X_valid = valid_data[FACTOR_LIST]
        y_valid = valid_data['label']
        
        # 创建数据集
        train_set = lgb.Dataset(X_train, label=y_train)
        valid_set = lgb.Dataset(X_valid, label=y_valid, reference=train_set)
        
        # 训练模型
        self.model = lgb.train(
            MODEL_CONFIG,
            train_set,
            num_boost_round=1000,
            valid_sets=[train_set, valid_set],
            valid_names=['train', 'valid'],
            callbacks=[
                lgb.early_stopping(stopping_rounds=50),
                lgb.log_evaluation(period=100)
            ]
        )
        
        # 特征重要性
        self.feature_importance = pd.DataFrame({
            'factor': FACTOR_LIST,
            'importance': self.model.feature_importance(importance_type='gain')
        }).sort_values('importance', ascending=False)
        
        print("\n📊 特征重要性 Top 10:")
        print(self.feature_importance.head(10).to_string(index=False))
        
        return self.model
    
    def predict(self, data):
        """
        预测收益率
        
        Args:
            data: 输入数据（包含因子）
        
        Returns:
            预测收益率
        """
        if self.model is None:
            print("错误：模型未训练")
            return None
        
        X = data[FACTOR_LIST]
        predictions = self.model.predict(X)
        return predictions
    
    def evaluate(self, test_data):
        """
        评估模型表现
        
        Args:
            test_data: 测试数据
        
        Returns:
            评估指标字典
        """
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        
        y_true = test_data['label']
        y_pred = self.predict(test_data)
        
        metrics = {
            'mse': mean_squared_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred),
            'ic': np.corrcoef(y_true, y_pred)[0, 1],  # 信息系数
        }
        
        print("\n📊 模型评估指标:")
        print(f"  MSE:  {metrics['mse']:.6f}")
        print(f"  RMSE: {metrics['rmse']:.6f}")
        print(f"  MAE:  {metrics['mae']:.6f}")
        print(f"  R²:   {metrics['r2']:.4f}")
        print(f"  IC:   {metrics['ic']:.4f} (目标：>0.08)")
        
        return metrics


def main():
    """主函数 - 演示流程"""
    print("=" * 60)
    print("🤖 机器学习增强框架 - 方案 2")
    print("=" * 60)
    print("状态：🚧 开发中（Q2 2026 实施）")
    print("=" * 60)
    print()
    
    # 创建预测器
    predictor = MLStockPredictor()
    
    # 演示因子计算
    print("📐 因子计算演示:")
    print(f"  因子数量：{len(FACTOR_LIST)}")
    print(f"  因子类别：动量 (5) + 价值 (4) + 质量 (4) + 情绪 (5)")
    print()
    
    # 显示因子列表
    print("📋 因子列表:")
    for i, factor in enumerate(FACTOR_LIST, 1):
        category = "动量" if i <= 5 else "价值" if i <= 9 else "质量" if i <= 13 else "情绪"
        print(f"  {i:2d}. {factor:20s} [{category}]")
    print()
    
    print("=" * 60)
    print("下一步:")
    print("  1. 收集历史因子数据（2 年）")
    print("  2. 搭建 Qlib 回测框架")
    print("  3. 训练/验证模型")
    print("  4. 模拟盘测试")
    print("=" * 60)


if __name__ == "__main__":
    main()
