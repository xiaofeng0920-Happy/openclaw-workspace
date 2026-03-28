#!/usr/bin/env python3
"""
V16 动态配置回测 - 27 只五好股票
=====================================
- A 股 24 只 + 港股 3 只
- 回测周期：2020-2026 年
- 动态配置：根据市场状态调整仓位、持仓数、PE/ROE 要求
- 当前市场状态：震荡市（仓位 65%、持仓 5 只、PE<30、ROE>15%）
"""

import sys
sys.path.insert(0, '/home/admin/openclaw/workspace')

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
import json
from pathlib import Path
import akshare as ak
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

print("="*100)
print("🤖 V16 动态配置回测 - 27 只五好股票")
print("="*100)
print(f"📅 回测周期：2020-01-01 至 2026-03-28")
print(f"📊 股票池：24 只 A 股 + 3 只港股")
print("="*100)

# === 第一步：定义股票池 ===
print("\n📋 第一步：定义股票池")
print("="*100)

# A 股 24 只（从五好股票筛选结果中选取）
A_STOCKS = [
    '600809',  # 山西汾酒
    '000568',  # 泸州老窖
    '300760',  # 迈瑞医疗
    '002304',  # 洋河股份
    '600436',  # 片仔癀
    '603288',  # 海天味业
    '000596',  # 古井贡酒
    '600750',  # 华润江中
    '600598',  # 北大荒
    '601038',  # 一拖股份
    '002832',  # 比音勒芬
    '603589',  # 口子窖
    '603919',  # 金徽酒
    '600211',  # 西藏药业
    '600285',  # 羚锐制药
    '000848',  # 承德露露
    '600600',  # 青岛啤酒
    '603198',  # 迎驾贡酒
    '603369',  # 今世缘
    '300896',  # 爱美客
    '002517',  # 恺英网络
    '301004',  # 嘉益股份
    '002847',  # 盐津铺子
    '688617',  # 惠泰医疗
]

# 港股 3 只
HK_STOCKS = [
    '00700',  # 腾讯控股
    '00883',  # 中国海洋石油
    '00941',  # 中国移动
]

print(f"\n  A 股：{len(A_STOCKS)}只")
for code in A_STOCKS[:5]:
    print(f"    - {code}")
print(f"    ... (共{len(A_STOCKS)}只)")

print(f"\n  港股：{len(HK_STOCKS)}只")
for code in HK_STOCKS:
    print(f"    - {code}")

# === 第二步：V16 动态配置参数 ===
print("\n📊 第二步：V16 动态配置参数")
print("="*100)

V16_CONFIG = {
    'bull': {
        'name': '🐂牛市',
        'position_limit': 0.95,      # 仓位上限 95%
        'top_k': 10,                  # 持仓 10 只
        'pe_max': 35,                 # PE<35
        'roe_min': 12,                # ROE>12%
        'rebalance_days': 20,         # 20 天调仓
        'weights': {'capital': 0.40, 'value': 0.20, 'quality': 0.20, 'sentiment': 0.20}
    },
    'oscillate': {
        'name': '📊震荡市',
        'position_limit': 0.65,       # 仓位上限 65%
        'top_k': 5,                   # 持仓 5 只
        'pe_max': 30,                 # PE<30
        'roe_min': 15,                # ROE>15%
        'rebalance_days': 15,         # 15 天调仓
        'weights': {'capital': 0.30, 'value': 0.30, 'quality': 0.30, 'sentiment': 0.10}
    },
    'bear': {
        'name': '🐻熊市',
        'position_limit': 0.30,       # 仓位上限 30%
        'top_k': 3,                   # 持仓 3 只
        'pe_max': 25,                 # PE<25
        'roe_min': 18,                # ROE>18%
        'rebalance_days': 30,         # 30 天调仓
        'weights': {'capital': 0.10, 'value': 0.40, 'quality': 0.40, 'sentiment': 0.10}
    }
}

print("\n  配置参数:")
for state, cfg in V16_CONFIG.items():
    print(f"\n  {cfg['name']}:")
    print(f"    仓位上限：{cfg['position_limit']*100}%")
    print(f"    持仓数量：{cfg['top_k']}只")
    print(f"    PE 上限：{cfg['pe_max']}")
    print(f"    ROE 下限：{cfg['roe_min']}%")
    print(f"    调仓周期：{cfg['rebalance_days']}天")

# === 第三步：获取市场状态（使用沪深 300） ===
print("\n📈 第三步：识别市场状态 (2020-2026)")
print("="*100)

def get_market_state_data():
    """获取沪深 300 历史数据并识别市场状态"""
    try:
        # 获取沪深 300 历史数据
        print("  获取沪深 300 历史数据...")
        hs300_data = ak.stock_zh_index_daily(symbol="sh000300")
        
        if hs300_data is None or len(hs300_data) == 0:
            print("  ❌ 获取数据失败")
            return None
        
        # 筛选 2020-2026 数据
        hs300_data['date'] = pd.to_datetime(hs300_data['date'])
        hs300_data = hs300_data[(hs300_data['date'] >= '2020-01-01') & 
                                (hs300_data['date'] <= '2026-12-31')]
        hs300_data = hs300_data.sort_values('date')
        
        print(f"  ✅ 获取{len(hs300_data)}个交易日数据")
        
        # 计算指标
        close = hs300_data['close']
        
        # MA250 及斜率
        ma250 = close.rolling(250).mean()
        ma250_slope = ma250.diff()
        
        # RSI(14)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + gain/loss))
        
        # 市场广度（简化：用上涨比例）
        # 实际应该获取全市场涨跌家数，这里用沪深 300 成分股简化
        breadth = pd.Series(50, index=hs300_data.index)
        
        # 判断市场状态
        market_states = []
        for i in range(len(hs300_data)):
            if i < 250:
                market_states.append('oscillate')
                continue
            
            c = close.iloc[i]
            m = ma250.iloc[i]
            slope = ma250_slope.iloc[i]
            r = rsi.iloc[i]
            b = breadth.iloc[i]
            
            # 牛市条件
            is_bull = (c > m) and (slope > 0) and (r > 50) and (b > 60)
            
            # 熊市条件（满足 2 个及以上）
            bear_count = 0
            if c < m: bear_count += 1
            if slope < 0: bear_count += 1
            if r < 40: bear_count += 1
            if b < 40: bear_count += 1
            
            if is_bull:
                market_states.append('bull')
            elif bear_count >= 2:
                market_states.append('bear')
            else:
                market_states.append('oscillate')
        
        hs300_data['market_state'] = market_states
        
        # 统计
        state_counts = hs300_data['market_state'].value_counts()
        print(f"\n  市场状态统计:")
        print(f"    🐂牛市：{state_counts.get('bull', 0)}天 ({state_counts.get('bull', 0)/len(hs300_data)*100:.1f}%)")
        print(f"    📊震荡市：{state_counts.get('oscillate', 0)}天 ({state_counts.get('oscillate', 0)/len(hs300_data)*100:.1f}%)")
        print(f"    🐻熊市：{state_counts.get('bear', 0)}天 ({state_counts.get('bear', 0)/len(hs300_data)*100:.1f}%)")
        
        current_state = market_states[-1]
        print(f"\n  ✅ 当前市场状态：{V16_CONFIG[current_state]['name']}")
        
        return hs300_data
        
    except Exception as e:
        print(f"  ❌ 错误：{e}")
        return None

market_data = get_market_state_data()

# === 第四步：获取股票历史数据 ===
print("\n📊 第四步：获取股票历史数据")
print("="*100)

def get_stock_data(code: str, is_hk: bool = False) -> pd.DataFrame:
    """获取单只股票历史数据"""
    try:
        if is_hk:
            # 港股使用 akshare
            code_formatted = f"hk{code}"
            data = ak.stock_hk_daily(symbol=code_formatted, adjust='qfq')
        else:
            # A 股
            if code.startswith('6'):
                code_formatted = f"sh{code}"
            else:
                code_formatted = f"sz{code}"
            data = ak.stock_zh_a_hist(symbol=code, period='daily', adjust='qfq')
        
        if data is None or len(data) == 0:
            return None
        
        # 标准化列名
        if is_hk:
            data = data.rename(columns={'日期': 'date', '收盘': 'close', '开盘': 'open', 
                                       '最高': 'high', '最低': 'low', '成交量': 'volume'})
        else:
            data = data.rename(columns={'日期': 'date', '收盘': 'close', '开盘': 'open',
                                       '最高': 'high', '最低': 'low', '成交量': 'volume'})
        
        data['date'] = pd.to_datetime(data['date'])
        data = data[(data['date'] >= '2020-01-01') & (data['date'] <= '2026-12-31')]
        data = data.sort_values('date')
        
        if len(data) < 100:
            return None
        
        return data
        
    except Exception as e:
        return None

# 获取所有股票数据
stock_data = {}
print("\n  获取 A 股数据...")
for code in tqdm(A_STOCKS, desc="A 股"):
    data = get_stock_data(code, is_hk=False)
    if data is not None:
        stock_data[code] = data

print(f"  ✅ 成功获取 {len(stock_data)} 只 A 股数据")

print("\n  获取港股数据...")
for code in tqdm(HK_STOCKS, desc="港股"):
    data = get_stock_data(code, is_hk=True)
    if data is not None:
        stock_data[code] = data

print(f"  ✅ 成功获取 {len(stock_data) - len(A_STOCKS)} 只港股数据")
print(f"  📊 总计：{len(stock_data)}只股票")

# === 第五步：获取基本面数据 ===
print("\n📊 第五步：获取基本面数据 (PE, ROE)")
print("="*100)

fundamental_data = {}

# 从已知的五好股票数据加载
print("  加载基本面数据...")
try:
    # A 股基本面
    a_stock_fundamental = pd.read_csv('/home/admin/openclaw/workspace/agents/data-collector/backtest_results/五好股票_PE50_20260328_182328.csv')
    for _, row in a_stock_fundamental.iterrows():
        code = str(row['代码'])
        fundamental_data[code] = {
            'pe': float(row['PE']),
            'roe_avg': float(row['ROE_平均']),
            'roe_min': float(row['ROE_最低']) if 'ROE_最低' in row else float(row['ROE_平均']) * 0.7
        }
    print(f"  ✅ 加载 {len(a_stock_fundamental)} 只 A 股基本面数据")
except Exception as e:
    print(f"  ⚠️  A 股基本面加载失败：{e}")

# 港股基本面
hk_fundamental = {
    '00700': {'pe': 20.0, 'roe_avg': 21.1, 'roe_min': 18.0},
    '00883': {'pe': 5.0, 'roe_avg': 15.7, 'roe_min': 12.0},
    '00941': {'pe': 11.0, 'roe_avg': 9.7, 'roe_min': 8.0},
}
for code, data in hk_fundamental.items():
    fundamental_data[code] = data
print(f"  ✅ 加载 3 只港股基本面数据")

# === 第六步：动态配置回测 ===
print("\n📈 第六步：执行动态配置回测")
print("="*100)

def filter_by_fundamentals(codes: List[str], state: str) -> List[str]:
    """根据基本面条件筛选股票"""
    cfg = V16_CONFIG[state]
    qualified = []
    
    for code in codes:
        if code not in fundamental_data:
            continue
        
        fund = fundamental_data[code]
        pe = fund['pe']
        roe = fund['roe_avg']
        
        if pe <= cfg['pe_max'] and roe >= cfg['roe_min']:
            qualified.append(code)
    
    return qualified

def calculate_momentum(data: pd.DataFrame, lookback: int = 20) -> float:
    """计算动量"""
    if len(data)