#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术指标分析 - MACD、RSI、KDJ、布林带等

全部本地计算，无需外部 API
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

try:
    import akshare as ak
except ImportError:
    print("❌ 请安装 akshare: pip install akshare")
    sys.exit(1)

# ============== 工具函数 ==============

def fetch_stock_data(symbol, market='A'):
    """获取股票历史数据"""
    try:
        if market == 'A':
            df = ak.stock_zh_a_hist(symbol=symbol, period="daily")
        elif market == 'HK':
            df = ak.stock_hk_hist(symbol=symbol, period="daily")
        elif market == 'US':
            df = ak.stock_us_hist(symbol=symbol, period="daily")
        else:
            return None
        
        if df is not None and len(df) > 0:
            # 标准化列名
            df = df.rename(columns={
                '日期': 'date',
                '收盘': 'close',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount'
            })
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            return df
    except Exception as e:
        print(f"获取数据失败：{e}")
    return None

# ============== 技术指标计算 ==============

def calc_ma(df, periods=[5, 10, 20, 60]):
    """计算移动平均线"""
    for p in periods:
        df[f'ma{p}'] = df['close'].rolling(window=p).mean()
    return df

def calc_ema(df, periods=[12, 26]):
    """计算指数移动平均线"""
    for p in periods:
        df[f'ema{p}'] = df['close'].ewm(span=p, adjust=False).mean()
    return df

def calc_macd(df, fast=12, slow=26, signal=9):
    """
    计算 MACD
    
    DIF = EMA12 - EMA26
    DEA = DIF 的 9 日 EMA
    MACD = (DIF - DEA) × 2
    """
    df = calc_ema(df, [fast, slow])
    
    df['dif'] = df['ema12'] - df['ema26']
    df['dea'] = df['dif'].ewm(span=signal, adjust=False).mean()
    df['macd'] = (df['dif'] - df['dea']) * 2
    
    # 信号
    df['macd_signal'] = 'neutral'
    df.loc[df['macd'] > 0, 'macd_signal'] = 'bullish'
    df.loc[df['macd'] < 0, 'macd_signal'] = 'bearish'
    
    # 金叉/死叉
    df['golden_cross'] = False
    df['death_cross'] = False
    
    for i in range(1, len(df)):
        if df.iloc[i-1]['dif'] < df.iloc[i-1]['dea'] and df.iloc[i]['dif'] > df.iloc[i]['dea']:
            df.loc[df.index[i], 'golden_cross'] = True
        elif df.iloc[i-1]['dif'] > df.iloc[i-1]['dea'] and df.iloc[i]['dif'] < df.iloc[i]['dea']:
            df.loc[df.index[i], 'death_cross'] = True
    
    return df

def calc_rsi(df, periods=[6, 12, 24]):
    """
    计算 RSI（相对强弱指数）
    
    RSI = 100 - (100 / (1 + RS))
    RS = N 日内涨幅平均值 / N 日内跌幅平均值
    """
    for p in periods:
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = (-delta).where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=p).mean()
        avg_loss = loss.rolling(window=p).mean()
        
        rs = avg_gain / avg_loss.replace(0, np.inf)
        df[f'rsi{p}'] = 100 - (100 / (1 + rs))
    
    # 信号
    df['rsi_signal'] = 'neutral'
    df.loc[df['rsi6'] > 70, 'rsi_signal'] = 'overbought'  # 超买
    df.loc[df['rsi6'] < 30, 'rsi_signal'] = 'oversold'    # 超卖
    
    return df

def calc_kdj(df, n=9, m1=3, m2=3):
    """
    计算 KDJ（随机指标）
    
    RSV = (收盘价 - N 日最低价) / (N 日最高价 - N 日最低价) × 100
    K = RSV 的 M1 日 SMA
    D = K 的 M2 日 SMA
    J = 3K - 2D
    """
    low_n = df['low'].rolling(window=n).min()
    high_n = df['high'].rolling(window=n).max()
    
    rsv = (df['close'] - low_n) / (high_n - low_n) * 100
    rsv = rsv.fillna(50)  # 初始值
    
    df['k'] = rsv.ewm(com=m1-1, adjust=False).mean()
    df['d'] = df['k'].ewm(com=m2-1, adjust=False).mean()
    df['j'] = 3 * df['k'] - 2 * df['d']
    
    # 信号
    df['kdj_signal'] = 'neutral'
    df.loc[(df['k'] > 80) | (df['d'] > 80), 'kdj_signal'] = 'overbought'
    df.loc[(df['k'] < 20) | (df['d'] < 20), 'kdj_signal'] = 'oversold'
    
    return df

def calc_bollinger(df, period=20, std_dev=2):
    """
    计算布林带
    
    中轨 = 20 日 MA
    上轨 = 中轨 + 2 × 标准差
    下轨 = 中轨 - 2 × 标准差
    """
    df['boll_mid'] = df['close'].rolling(window=period).mean()
    std = df['close'].rolling(window=period).std()
    df['boll_upper'] = df['boll_mid'] + std_dev * std
    df['boll_lower'] = df['boll_mid'] - std_dev * std
    
    # 布林带宽
    df['boll_width'] = (df['boll_upper'] - df['boll_lower']) / df['boll_mid'] * 100
    
    # 信号
    df['boll_signal'] = 'neutral'
    df.loc[df['close'] > df['boll_upper'], 'boll_signal'] = 'overbought'
    df.loc[df['close'] < df['boll_lower'], 'boll_signal'] = 'oversold'
    
    return df

def calc_volume_ma(df, periods=[5, 10]):
    """计算成交量均线"""
    for p in periods:
        df[f'vol_ma{p}'] = df['volume'].rolling(window=p).mean()
    return df

def calc_all_indicators(df):
    """计算所有技术指标"""
    df = calc_ma(df)
    df = calc_macd(df)
    df = calc_rsi(df)
    df = calc_kdj(df)
    df = calc_bollinger(df)
    df = calc_volume_ma(df)
    return df

# ============== 分析函数 ==============

def analyze_stock(symbol, market='A'):
    """分析单只股票"""
    print(f"\n{'='*60}")
    print(f"分析：{symbol} ({market}股)")
    print(f"{'='*60}")
    
    # 获取数据
    df = fetch_stock_data(symbol, market)
    if df is None or len(df) < 60:
        print("❌ 数据不足")
        return None
    
    print(f"数据范围：{df['date'].min()} 至 {df['date'].max()}")
    print(f"数据点数：{len(df)}")
    
    # 计算指标
    df = calc_all_indicators(df)
    
    # 获取最新数据
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # 当前价格
    current_price = latest['close']
    price_change = ((current_price - prev['close']) / prev['close']) * 100
    
    print(f"\n当前价格：{current_price:.2f} ({price_change:+.2f}%)")
    
    # MACD 分析
    print("\n📊 MACD:")
    print(f"  DIF: {latest['dif']:.2f}")
    print(f"  DEA: {latest['dea']:.2f}")
    print(f"  MACD: {latest['macd']:.2f}")
    print(f"  信号：{latest['macd_signal']}")
    if latest['golden_cross']:
        print(f"  🟢 金叉！")
    if latest['death_cross']:
        print(f"  🔴 死叉！")
    
    # RSI 分析
    print("\n📊 RSI:")
    print(f"  RSI6: {latest['rsi6']:.1f}")
    print(f"  RSI12: {latest['rsi12']:.1f}")
    print(f"  RSI24: {latest['rsi24']:.1f}")
    print(f"  信号：{latest['rsi_signal']}")
    
    # KDJ 分析
    print("\n📊 KDJ:")
    print(f"  K: {latest['k']:.1f}")
    print(f"  D: {latest['d']:.1f}")
    print(f"  J: {latest['j']:.1f}")
    print(f"  信号：{latest['kdj_signal']}")
    
    # 布林带分析
    print("\n📊 布林带:")
    print(f"  上轨：{latest['boll_upper']:.2f}")
    print(f"  中轨：{latest['boll_mid']:.2f}")
    print(f"  下轨：{latest['boll_lower']:.2f}")
    print(f"  带宽：{latest['boll_width']:.1f}%")
    print(f"  信号：{latest['boll_signal']}")
    
    # 综合评分
    score = 0
    signals = []
    
    if latest['macd_signal'] == 'bullish':
        score += 1
        signals.append("MACD 多头")
    if latest['rsi_signal'] == 'oversold':
        score += 2
        signals.append("RSI 超卖")
    elif latest['rsi_signal'] == 'overbought':
        score -= 1
        signals.append("RSI 超买")
    if latest['kdj_signal'] == 'oversold':
        score += 2
        signals.append("KDJ 超卖")
    elif latest['kdj_signal'] == 'overbought':
        score -= 1
        signals.append("KDJ 超买")
    if latest['boll_signal'] == 'oversold':
        score += 1
        signals.append("布林带下轨")
    elif latest['boll_signal'] == 'overbought':
        score -= 1
        signals.append("布林带上轨")
    if latest['golden_cross']:
        score += 3
        signals.append("MACD 金叉")
    if latest['death_cross']:
        score -= 3
        signals.append("MACD 死叉")
    
    print("\n📈 综合评分:")
    print(f"  得分：{score}/10")
    if signals:
        print(f"  信号：{', '.join(signals)}")
    
    if score >= 5:
        print(f"  🟢 强烈买入信号")
    elif score >= 3:
        print(f"  🟡 买入信号")
    elif score <= -5:
        print(f"  🔴 强烈卖出信号")
    elif score <= -3:
        print(f"  🟠 卖出信号")
    else:
        print(f"  ⚪ 观望")
    
    return {
        'symbol': symbol,
        'market': market,
        'price': current_price,
        'change': price_change,
        'score': score,
        'signals': signals,
        'macd': latest['macd_signal'],
        'rsi': latest['rsi_signal'],
        'kdj': latest['kdj_signal'],
        'bollinger': latest['boll_signal']
    }

# ============== 批量分析 ==============

def analyze_portfolio(stocks):
    """批量分析股票池"""
    print("="*60)
    print("📊 投资组合技术分析")
    print("="*60)
    
    results = []
    
    for symbol, name, market in stocks:
        result = analyze_stock(symbol, market)
        if result:
            result['name'] = name
            results.append(result)
    
    # 排序
    results_sorted = sorted(results, key=lambda x: x['score'], reverse=True)
    
    # 输出汇总
    print("\n" + "="*60)
    print("📊 汇总排名")
    print("="*60)
    print(f"{'排名':<4} {'代码':<8} {'名称':<12} {'得分':<6} {'信号':<20}")
    print("-"*60)
    
    for i, r in enumerate(results_sorted, 1):
        score_emoji = "🟢" if r['score'] >= 5 else ("🟡" if r['score'] >= 3 else ("🟠" if r['score'] <= -3 else "⚪"))
        print(f"{i:<4} {r['symbol']:<8} {r['name']:<12} {r['score']:<6} {score_emoji} {r['signals'][0] if r['signals'] else '无'}")
    
    return results_sorted

# ============== 主函数 ==============

def main():
    """主函数"""
    # 重点股票池
    stocks = [
        # A 股
        ('601088', '中国神华', 'A'),
        ('601225', '陕西煤业', 'A'),
        ('601006', '大秦铁路', 'A'),
        ('600036', '招商银行', 'A'),
        # 港股
        ('00883', '中国海洋石油', 'HK'),
        ('00941', '中国移动', 'HK'),
        # 美股
        ('KO', '可口可乐', 'US'),
        ('VZ', 'Verizon', 'US'),
        ('XOM', '埃克森美孚', 'US'),
    ]
    
    results = analyze_portfolio(stocks)
    
    # 保存结果
    if results:
        df = pd.DataFrame(results)
        output_dir = Path('/home/admin/openclaw/workspace/agents/data-collector/technical')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = output_dir / f'technical_analysis_{timestamp}.csv'
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        print(f"\n💾 结果已保存：{csv_file}")

if __name__ == "__main__":
    main()
