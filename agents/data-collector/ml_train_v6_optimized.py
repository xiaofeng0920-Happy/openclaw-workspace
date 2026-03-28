#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
方案 2：机器学习 V6 - 优化版
优化策略：
1. 只用 Top 5 因子（减少过拟合）
2. 增加正则化强度
3. 降低学习率
4. 目标：提升泛化能力
"""

import sys
import json
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, '/home/admin/openclaw/workspace')

try:
    import pandas as pd
    import numpy as np
    import lightgbm as lgb
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_squared_error, r2_score
except ImportError as e:
    print(f"请安装依赖：pip install {str(e).split()[-1]}")
    sys.exit(1)

# 只用 Top 5 因子（减少过拟合）
TOP5_FACTORS = [
    'price_strength',    # 价格强度（最重要）
    'momentum_3m',       # 3 月动量
    'momentum_6m',       # 6 月动量
    'momentum_1m',       # 1 月动量
    'macd_signal',       # MACD 信号
]

# 优化后的模型配置（更强正则化）
MODEL_CONFIG = {
    'objective': 'regression',
    'metric': 'mse',
    'boosting_type': 'gbdt',
    'num_leaves': 15,          # 降低复杂度（原 50）
    'learning_rate': 0.01,     # 降低学习率（原 0.03）
    'feature_fraction': 0.6,   # 降低特征采样（原 0.8）
    'bagging_fraction': 0.6,   # 降低样本采样（原 0.8）
    'bagging_freq': 10,        # 增加 bagging 频率（原 5）
    'verbose': -1,
    'seed': 42,
    'n_estimators': 2000,      # 增加树数量
    'early_stopping_rounds': 150,
    'min_child_samples': 50,   # 增加最小样本数（原 20）
    'reg_alpha': 0.5,          # 增加 L1 正则（原 0.1）
    'reg_lambda': 0.5,         # 增加 L2 正则（原 0.1）
    'max_depth': 8,            # 限制树深度
}

# A 股股票池（95 只）
A50_STOCKS = [
    '000001', '000002', '000063', '000100', '000157',
    '000333', '000538', '000568', '000596', '000651',
    '000661', '000725', '000776', '000858', '000895',
    '002001', '002007', '002027', '002049', '002129',
    '002142', '002230', '002236', '002252', '002304',
    '002352', '002415', '002475', '002594', '002714',
    '300014', '300015', '300059', '300122', '300124',
    '300142', '300274', '300312', '300347', '300413',
    '300433', '300498', '300601', '300628', '300750',
    '300759', '300760', '300782', '300896', '600000',
    '600009', '600016', '600028', '600030', '600031',
    '600036', '600048', '600050', '600104', '600276',
    '600309', '600346', '600436', '600519', '600585',
    '600588', '600690', '600809', '600887', '600900',
    '600905', '601012', '601066', '601088', '601166',
    '601225', '601288', '601318', '601328', '601398',
    '601601', '601628', '601633', '601668', '601688',
    '601728', '601766', '601816', '601857', '601888',
    '601899', '601919', '601995', '603259', '603288',
]


def get_a_stock_history(symbol, days=730):
    """获取 A 股历史行情"""
    try:
        import akshare as ak
        if symbol.startswith('6'):
            code = f"sh{symbol}"
        else:
            code = f"sz{symbol}"
        
        df = ak.stock_zh_a_daily(symbol=code, adjust="qfq")
        if df is not None and len(df) > 0:
            df = df.tail(days).copy()
            df['symbol'] = symbol
            df['market'] = 'CN'
            return df
    except:
        pass
    
    return pd.DataFrame()


def calculate_factors(df):
    """计算因子（只计算 Top 5）"""
    if len(df) == 0:
        return df
    
    close = df['close']
    volume = df['volume']
    
    # Top 5 因子
    df['momentum_1m'] = close.pct_change(20)
    df['momentum_3m'] = close.pct_change(60)
    df['momentum_6m'] = close.pct_change(120)
    
    exp1 = close.ewm(span=12, adjust=False).mean()
    exp2 = close.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    df['macd_signal'] = (macd - signal) / close * 100
    
    high_52w = df['high'].rolling(252).max()
    df['price_strength'] = (df['close'] - high_52w) / high_52w * 100
    
    # 标签：未来 20 日收益率
    df['label'] = df['close'].shift(-20).pct_change(20)
    
    return df


def prepare_dataset():
    """准备数据集"""
    print("📊 准备数据集（V6 优化版）...")
    print(f"  因子数量：{len(TOP5_FACTORS)}（简化）")
    print(f"  股票池：{len(A50_STOCKS)}只 A 股")
    
    all_data = []
    skip_count = 0
    
    for i, symbol in enumerate(A50_STOCKS, 1):
        df = get_a_stock_history(symbol, days=730)
        if len(df) > 0:
            df = calculate_factors(df)
            df = df.dropna()
            if len(df) > 0:
                all_data.append(df)
                if i % 20 == 0:
                    print(f"  [{i:3d}/95] ✓ {symbol}: {len(df)}条")
            else:
                skip_count += 1
        else:
            skip_count += 1
    
    if not all_data:
        return pd.DataFrame()
    
    dataset = pd.concat(all_data, ignore_index=True)
    print(f"\n  总计：{len(dataset)}条记录")
    print(f"  跳过：{skip_count}只")
    return dataset


def train_model(dataset):
    """训练优化模型"""
    print("\n🚀 训练 LightGBM（优化版）...")
    print(f"  使用因子：{TOP5_FACTORS}")
    
    X = dataset[TOP5_FACTORS]
    y = dataset['label']
    
    # 标准化
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=TOP5_FACTORS)
    
    # 时间序列划分（避免前视偏差）
    train_size = int(len(dataset) * 0.7)
    valid_size = int(len(dataset) * 0.15)
    
    X_train, y_train = X_scaled.iloc[:train_size], y.iloc[:train_size]
    X_valid, y_valid = X_scaled.iloc[train_size:train_size+valid_size], y.iloc[train_size:train_size+valid_size]
    X_test, y_test = X_scaled.iloc[train_size+valid_size:], y.iloc[train_size+valid_size:]
    
    print(f"  训练集：{len(X_train)}条")
    print(f"  验证集：{len(X_valid)}条")
    print(f"  测试集：{len(X_test)}条")
    
    # 训练
    model = lgb.LGBMRegressor(**MODEL_CONFIG)
    model.fit(
        X_train, y_train,
        eval_set=[(X_valid, y_valid)],
        eval_metric='mse',
    )
    
    # 预测
    y_pred = model.predict(X_test)
    
    # 评估
    metrics = {
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
        'r2': r2_score(y_test, y_pred),
        'ic': np.corrcoef(y_test, y_pred)[0, 1] if len(y_test) > 1 else 0,
    }
    
    print(f"\n📊 评估结果:")
    print(f"  IC:   {metrics['ic']:.4f} (V5: 0.1561, 目标：>0.05)")
    print(f"  R²:   {metrics['r2']:.4f} (V5: -0.0075)")
    print(f"  RMSE: {metrics['rmse']:.6f}")
    
    if metrics['ic'] > 0.08:
        print("  ✅ IC 达标！")
    elif metrics['ic'] > 0.05:
        print("  🟡 达到预期！")
    else:
        print("  ⚠️ 仍需提升")
    
    # 特征重要性
    importance = pd.DataFrame({
        'factor': TOP5_FACTORS,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n📋 特征重要性:")
    print(importance.to_string(index=False))
    
    return {'model': model, 'metrics': metrics, 'importance': importance}


def main():
    print("=" * 60)
    print("🤖 方案 2：机器学习 V6 - 优化版")
    print("=" * 60)
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    dataset = prepare_dataset()
    if len(dataset) == 0:
        print("数据集为空，退出")
        return
    
    result = train_model(dataset)
    
    # 保存
    output_dir = Path("/home/admin/openclaw/workspace/agents/data-collector/models")
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    result['model'].booster_.save_model(str(output_dir / f"lgbm_v6_opt_{ts}.json"))
    with open(output_dir / f"metrics_v6_opt_{ts}.json", 'w') as f:
        json.dump({
            'version': 'v6',
            'optimization': 'simplified_factors',
            'metrics': result['metrics'],
            'data_size': len(dataset),
            'timestamp': ts
        }, f, indent=2)
    
    print(f"\n💾 模型已保存")
    print("=" * 60)


if __name__ == "__main__":
    main()
