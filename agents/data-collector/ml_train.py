#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
方案 2：机器学习增强 - 完整训练流程
使用 LightGBM 模型进行收益率预测

**技术栈：**
- 模型：LightGBM
- 因子：18 个（动量 5 + 价值 4 + 质量 4 + 情绪 5）
- 预期 IC：0.06 → 0.08
- 预期年化：15% → 20%

**状态：** 🚀 实施中
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, '/home/admin/openclaw/workspace')

try:
    import pandas as pd
    import numpy as np
    import lightgbm as lgb
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
except ImportError as e:
    print(f"请安装依赖：pip install {str(e).split()[-1]}")
    sys.exit(1)

# ============== 配置 ==============

FACTOR_LIST = [
    'momentum_1m', 'momentum_3m', 'momentum_6m', 'rsi_14', 'macd_signal',
    'pe_ratio', 'pb_ratio', 'ps_ratio', 'dividend_yield',
    'roe', 'roa', 'debt_to_equity', 'profit_margin',
    'sentiment_score', 'turnover_score', 'flow_score', 'volume_ratio', 'price_strength'
]

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
    'n_estimators': 1000,
    'early_stopping_rounds': 50,
}

HOLDINGS_US = ['GOOGL', 'BRK.B', 'KO', 'ORCL', 'MSFT', 'AAPL', 'TSLA', 'NVDA']
HOLDINGS_HK = ['00700', '00883', '09988', '03153', '07709', '03355']


def get_stock_history(symbol: str, market: str = "US", days: int = 730) -> pd.DataFrame:
    """获取股票历史行情"""
    try:
        import akshare as ak
        
        if market == "US":
            df = ak.stock_us_daily(symbol=symbol)
            if df is not None and len(df) > 0:
                df = df.tail(days).copy()
                df['symbol'] = symbol
                df['market'] = 'US'
                return df
        else:
            df = ak.stock_hk_daily(symbol=symbol, adjust="qfq")
            if df is not None and len(df) > 0:
                df = df.tail(days).copy()
                df['symbol'] = symbol
                df['market'] = 'HK'
                return df
    except Exception as e:
        print(f"获取 {symbol} 数据失败：{e}")
    
    return pd.DataFrame()


def calculate_factors(df: pd.DataFrame) -> pd.DataFrame:
    """计算技术因子"""
    close = df['close']
    volume = df['volume']
    
    # 动量因子
    df['momentum_1m'] = close.pct_change(20)
    df['momentum_3m'] = close.pct_change(60)
    df['momentum_6m'] = close.pct_change(120)
    
    # RSI
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi_14'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = close.ewm(span=12, adjust=False).mean()
    exp2 = close.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    df['macd_signal'] = (macd - signal) / close * 100
    
    # 成交量因子
    df['volume_ratio'] = volume / volume.rolling(5).mean()
    
    # 价格强度
    high_52w = df['high'].rolling(252).max()
    df['price_strength'] = (df['close'] - high_52w) / high_52w * 100
    
    # 财务数据（简化：使用随机值模拟）
    np.random.seed(42)
    n = len(df)
    df['pe_ratio'] = np.random.uniform(10, 40, n)
    df['pb_ratio'] = np.random.uniform(1, 10, n)
    df['ps_ratio'] = np.random.uniform(1, 15, n)
    df['dividend_yield'] = np.random.uniform(0, 5, n)
    df['roe'] = np.random.uniform(5, 30, n)
    df['roa'] = np.random.uniform(2, 15, n)
    df['debt_to_equity'] = np.random.uniform(0.1, 2.0, n)
    df['profit_margin'] = np.random.uniform(5, 30, n)
    
    # 情绪因子（简化：使用随机值模拟，实际应从 sentiment_factor 获取）
    df['sentiment_score'] = np.random.uniform(50, 80, n)
    df['turnover_score'] = np.random.uniform(40, 90, n)
    df['flow_score'] = np.random.uniform(30, 70, n)
    
    # 标签：未来 20 日收益率
    df['label'] = df['close'].shift(-20).pct_change(20)
    
    # 删除 NaN
    df = df.dropna()
    
    return df


def train_model(dataset: pd.DataFrame) -> dict:
    """训练 LightGBM 模型"""
    print("\n🚀 训练 LightGBM 模型...")
    
    available_factors = [f for f in FACTOR_LIST if f in dataset.columns]
    X = dataset[available_factors]
    y = dataset['label']
    
    # 划分数据集
    train_size = int(len(dataset) * 0.7)
    valid_size = int(len(dataset) * 0.15)
    
    X_train, y_train = X.iloc[:train_size], y.iloc[:train_size]
    X_valid, y_valid = X.iloc[train_size:train_size + valid_size], y.iloc[train_size:train_size + valid_size]
    X_test, y_test = X.iloc[train_size + valid_size:], y.iloc[train_size + valid_size:]
    
    print(f"  训练集：{len(X_train)} 条")
    print(f"  验证集：{len(X_valid)} 条")
    print(f"  测试集：{len(X_test)} 条")
    
    # 训练
    model = lgb.LGBMRegressor(**MODEL_CONFIG)
    model.fit(X_train, y_train, eval_set=[(X_valid, y_valid)], eval_metric='mse')
    
    # 预测
    y_pred_test = model.predict(X_test)
    
    # 评估
    metrics = {
        'mse': mean_squared_error(y_test, y_pred_test),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
        'mae': mean_absolute_error(y_test, y_pred_test),
        'r2': r2_score(y_test, y_pred_test),
        'ic': np.corrcoef(y_test, y_pred_test)[0, 1] if len(y_test) > 1 else 0,
    }
    
    # 特征重要性
    feature_importance = pd.DataFrame({
        'factor': available_factors,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n📊 模型评估指标:")
    print(f"  R²:  {metrics['r2']:.4f}")
    print(f"  IC:  {metrics['ic']:.4f} (目标：>0.08)")
    print(f"  RMSE: {metrics['rmse']:.6f}")
    
    print("\n📋 特征重要性 Top 10:")
    print(feature_importance.head(10).to_string(index=False))
    
    return {
        'model': model,
        'metrics': metrics,
        'feature_importance': feature_importance,
        'factors': available_factors,
    }


def main():
    """主函数"""
    print("=" * 60)
    print("🤖 方案 2：机器学习增强 - 训练流程")
    print("=" * 60)
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 准备数据
    print("\n📊 准备数据集...")
    all_data = []
    
    # 获取美股
    print("  获取美股数据...")
    for symbol in HOLDINGS_US:
        df = get_stock_history(symbol, market="US", days=730)
        if len(df) > 0:
            df = calculate_factors(df)
            if len(df) > 0:
                all_data.append(df)
                print(f"    ✓ {symbol}: {len(df)} 条记录")
    
    # 获取港股
    print("  获取港股数据...")
    for symbol in HOLDINGS_HK:
        df = get_stock_history(symbol, market="HK", days=730)
        if len(df) > 0:
            df = calculate_factors(df)
            if len(df) > 0:
                all_data.append(df)
                print(f"    ✓ {symbol}: {len(df)} 条记录")
    
    if not all_data:
        print("  ⚠️  未获取到数据，使用模拟数据")
        # 创建模拟数据
        np.random.seed(42)
        n = 1000
        dataset = pd.DataFrame(np.random.randn(n, len(FACTOR_LIST)), columns=FACTOR_LIST)
        dataset['label'] = np.random.randn(n) * 0.05
    else:
        dataset = pd.concat(all_data, ignore_index=True)
        print(f"\n  总记录数：{len(dataset)}")
    
    # 训练模型
    result = train_model(dataset)
    
    # 保存模型
    print("\n💾 保存模型...")
    output_dir = Path("/home/admin/openclaw/workspace/agents/data-collector/models")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_file = output_dir / f"lgbm_model_{timestamp}.json"
    
    result['model'].booster_.save_model(str(model_file))
    print(f"  ✓ 模型已保存：{model_file}")
    
    # 保存评估结果
    metrics_file = output_dir / f"metrics_{timestamp}.json"
    with open(metrics_file, 'w') as f:
        json.dump({
            'metrics': result['metrics'],
            'feature_importance': result['feature_importance'].to_dict('records'),
            'factors': result['factors'],
            'timestamp': timestamp,
        }, f, indent=2, ensure_ascii=False)
    print(f"  ✓ 评估结果：{metrics_file}")
    
    print("\n" + "=" * 60)
    print("✅ 训练完成")
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    main()
