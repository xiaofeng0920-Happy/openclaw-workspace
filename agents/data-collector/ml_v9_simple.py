#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
方案 2：机器学习 V9 - 简化技术因子版
只用真实有效的技术因子，去掉模拟数据
"""

import sys
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

# 只用真实技术因子（6 个）
SIMPLE_FACTORS = [
    'price_momentum_10d',  # 10 日动量
    'price_momentum_20d',  # 20 日动量
    'rsi_14',              # RSI
    'macd_signal',         # MACD
    'bollinger_position',  # 布林带位置
    'volume_ratio',        # 成交量比率
]

MODEL_CONFIG = {
    'objective': 'regression', 'metric': 'mse', 'boosting_type': 'gbdt',
    'num_leaves': 15, 'learning_rate': 0.02, 'feature_fraction': 0.8,
    'bagging_fraction': 0.8, 'bagging_freq': 10, 'verbose': -1, 'seed': 42,
    'n_estimators': 1000, 'early_stopping_rounds': 100, 'min_child_samples': 30,
    'reg_alpha': 0.2, 'reg_lambda': 0.2, 'max_depth': 8,
}

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
        code = f"sh{symbol}" if symbol.startswith('6') else f"sz{symbol}"
        df = ak.stock_zh_a_daily(symbol=code, adjust="qfq")
        if df is not None and len(df) > 0:
            df = df.tail(days).copy()
            df['symbol'] = symbol
            df['market'] = 'CN'
            return df
    except:
        pass
    return pd.DataFrame()


def calculate_simple_factors(df):
    """计算简化技术因子"""
    if len(df) == 0:
        return df
    
    close = df['close']
    volume = df['volume']
    high = df['high']
    low = df['low']
    
    # 动量因子
    df['price_momentum_10d'] = close.pct_change(10)
    df['price_momentum_20d'] = close.pct_change(20)
    
    # RSI
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['rsi_14'] = 100 - (100 / (1 + gain/loss))
    
    # MACD
    exp1 = close.ewm(span=12, adjust=False).mean()
    exp2 = close.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    df['macd_signal'] = (macd - signal) / close * 100
    
    # 布林带
    ma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    upper = ma20 + 2 * std20
    lower = ma20 - 2 * std20
    df['bollinger_position'] = (close - lower) / (upper - lower + 0.01)
    
    # 成交量
    df['volume_ratio'] = volume / volume.rolling(5).mean()
    
    # 标签
    df['label'] = df['close'].shift(-20).pct_change(20)
    
    return df


def prepare_dataset():
    """准备数据集"""
    print("📊 准备数据集（V9 简化技术因子版）...")
    print(f"  因子数量：{len(SIMPLE_FACTORS)}")
    
    all_data = []
    skip_count = 0
    
    for i, symbol in enumerate(A50_STOCKS[:50], 1):
        df = get_a_stock_history(symbol, days=730)
        if len(df) > 0:
            df = calculate_simple_factors(df)
            df = df.dropna()
            if len(df) > 0:
                all_data.append(df)
                if i % 10 == 0:
                    print(f"  [{i:3d}/50] ✓ {symbol}: {len(df)}条")
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
    """训练模型"""
    print("\n🚀 训练 LightGBM（V9 简化版）...")
    
    X = dataset[SIMPLE_FACTORS]
    y = dataset['label']
    
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=SIMPLE_FACTORS)
    
    train_size = int(len(dataset) * 0.7)
    valid_size = int(len(dataset) * 0.15)
    
    X_train, y_train = X_scaled.iloc[:train_size], y.iloc[:train_size]
    X_valid, y_valid = X_scaled.iloc[train_size:train_size+valid_size], y.iloc[train_size:train_size+valid_size]
    X_test, y_test = X_scaled.iloc[train_size+valid_size:], y.iloc[train_size+valid_size:]
    
    print(f"  训练集：{len(X_train)}条")
    print(f"  测试集：{len(X_test)}条")
    
    model = lgb.LGBMRegressor(**MODEL_CONFIG)
    model.fit(X_train, y_train, eval_set=[(X_valid, y_valid)], eval_metric='mse')
    
    y_pred = model.predict(X_test)
    
    metrics = {
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
        'r2': r2_score(y_test, y_pred),
        'ic': np.corrcoef(y_test, y_pred)[0, 1] if len(y_test) > 1 else 0,
    }
    
    print(f"\n📊 评估结果:")
    print(f"  IC:   {metrics['ic']:.4f} (目标：>0.05)")
    print(f"  R²:   {metrics['r2']:.4f}")
    
    importance = pd.DataFrame({
        'factor': SIMPLE_FACTORS,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n📋 特征重要性:")
    print(importance.to_string(index=False))
    
    return {'model': model, 'metrics': metrics, 'importance': importance}


def main():
    print("=" * 60)
    print("🤖 方案 2：机器学习 V9 - 简化技术因子版")
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
    
    result['model'].booster_.save_model(str(output_dir / f"lgbm_v9_simple_{ts}.json"))
    print(f"\n💾 模型已保存：lgbm_v9_simple_{ts}.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
