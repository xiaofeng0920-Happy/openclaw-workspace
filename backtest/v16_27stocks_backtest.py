#!/usr/bin/env python3
"""
V16 动态配置回测 - 27 只五好股票
A 股 24 只 + 港股 3 只 | 2020-2026 年 | 动态仓位/持仓/PE/ROE
"""

import sys, json
sys.path.insert(0, '/home/admin/openclaw/workspace')

import pandas as pd
import numpy as np
from datetime import datetime
import akshare as ak
from tqdm import tqdm
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

print("="*80)
print("🤖 V16 动态配置回测 - 27 只五好股票 (2020-2026)")
print("="*80)

# === 股票池 ===
A_STOCKS = ['600809','000568','300760','002304','600436','603288','000596','600750',
            '600598','601038','002832','603589','603919','600211','600285','000848',
            '600600','603198','603369','300896','002517','301004','002847','688617']
HK_STOCKS = ['00700', '00883', '00941']
ALL_STOCKS = A_STOCKS + HK_STOCKS

print(f"\n📋 股票池：{len(A_STOCKS)}只 A 股 + {len(HK_STOCKS)}只港股 = {len(ALL_STOCKS)}只")

# === V16 动态配置 ===
V16_CONFIG = {
    'bull': {'name':'🐂牛市', 'position':0.95, 'top_k':10, 'pe_max':35, 'roe_min':12, 'hold_days':20},
    'oscillate': {'name':'📊震荡市', 'position':0.65, 'top_k':5, 'pe_max':30, 'roe_min':15, 'hold_days':15},
    'bear': {'name':'🐻熊市', 'position':0.30, 'top_k':3, 'pe_max':25, 'roe_min':18, 'hold_days':30}
}

print("\n📊 V16 动态配置:")
for s, c in V16_CONFIG.items():
    print(f"  {c['name']}: 仓位{c['position']*100}% | 持仓{c['top_k']}只 | PE<{c['pe_max']} | ROE>{c['roe_min']}%")

# === 获取市场状态 ===
print("\n📈 获取沪深 300 数据并识别市场状态...")
try:
    hs300 = ak.stock_zh_index_daily(symbol="sh000300")
    hs300['date'] = pd.to_datetime(hs300['date'])
    hs300 = hs300[(hs300['date']>='2020-01-01') & (hs300['date']<='2026-12-31')].sort_values('date')
    
    close = hs300['close']
    ma250 = close.rolling(250).mean()
    slope = ma250.diff()
    
    delta = close.diff()
    gain = delta.where(delta>0, 0).rolling(14).mean()
    loss = (-delta.where(delta<0, 0)).rolling(14).mean()
    rsi = 100 - (100/(1+gain/loss))
    
    states = []
    for i in range(len(hs300)):
        if i < 250:
            states.append('oscillate')
            continue
        c, m, s, r = close.iloc[i], ma250.iloc[i], slope.iloc[i], rsi.iloc[i]
        if (c>m) and (s>0) and (r>50):
            states.append('bull')
        elif (c<m) + (s<0) + (r<40) >= 2:
            states.append('bear')
        else:
            states.append('oscillate')
    
    hs300['state'] = states
    state_counts = pd.Series(states).value_counts()
    print(f"\n  市场状态统计 ({len(hs300)}天):")
    print(f"    🐂牛市：{state_counts.get('bull',0)}天 ({state_counts.get('bull',0)/len(hs300)*100:.1f}%)")
    print(f"    📊震荡市：{state_counts.get('oscillate',0)}天 ({state_counts.get('oscillate',0)/len(hs300)*100:.1f}%)")
    print(f"    🐻熊市：{state_counts.get('bear',0)}天 ({state_counts.get('bear',0)/len(hs300)*100:.1f}%)")
    print(f"  ✅ 当前状态：{V16_CONFIG[states[-1]]['name']}")
except Exception as e:
    print(f"  ❌ 错误：{e}")
    states = ['oscillate'] * len(hs300) if 'hs300' in dir() else []

# === 获取股票数据 ===
print("\n📊 获取股票历史数据...")
stock_data = {}

def get_data(code, is_hk=False):
    try:
        if is_hk:
            df = ak.stock_hk_daily(symbol=f"hk{code}", adjust='qfq')
        else:
            df = ak.stock_zh_a_hist(symbol=code, period='daily', adjust='qfq')
        if df is None or len(df)<100: return None
        df = df.rename(columns={'日期':'date','收盘':'close','开盘':'open','最高':'high','最低':'low'})
        df['date'] = pd.to_datetime(df['date'])
        df = df[(df['date']>='2020-01-01') & (df['date']<='2026-12-31')].sort_values('date')
        return df if len(df)>=100 else None
    except: return None

for code in tqdm(A_STOCKS, desc="A 股"):
    d = get_data(code, False)
    if d is not None: stock_data[code] = d

for code in tqdm(HK_STOCKS, desc="港股"):
    d = get_data(code, True)
    if d is not None: stock_data[code] = d

print(f"  ✅ 成功获取 {len(stock_data)}只股票数据")

# === 基本面数据 ===
print("\n📊 加载基本面数据...")
fundamental = {}
try:
    df = pd.read_csv('/home/admin/openclaw/workspace/agents/data-collector/backtest_results/五好股票_PE50_20260328_182328.csv')
    for _, r in df.iterrows():
        fundamental[str(r['代码'])] = {'pe':float(r['PE']),'roe':float(r['ROE_平均'])}
except: pass

# 港股基本面
fundamental.update({'00700':{'pe':20,'roe':21.1},'00883':{'pe':5,'roe':15.7},'00941':{'pe':11,'roe':9.7}})
print(f"  ✅ 加载 {len(fundamental)}只股票基本面")

# === 回测引擎 ===
print("\n📈 执行动态配置回测...")

initial_capital = 1000000
capital = initial_capital
portfolio = {}
daily_values = []
trades = []

dates = sorted(set(hs300['date'].values))
state_returns = {'bull':[], 'oscillate':[], 'bear':[]}

for idx, date in enumerate(tqdm(dates[:-15], desc="回测")):
    if idx < 250: continue
    
    current_state = states[idx]
    cfg = V16_CONFIG[current_state]
    
    # 调仓日
    if idx % cfg['hold_days'] == 0:
        # 筛选符合条件的股票
        qualified = []
        for code in stock_data:
            if code not in fundamental: continue
            if date not in stock_data[code]['date'].values: continue
            f = fundamental[code]
            if f['pe'] <= cfg['pe_max'] and f['roe'] >= cfg['roe_min']:
                # 计算动量
                stock_df = stock_data[code][stock_data[code]['date']<=date]
                if len(stock_df) >= 20:
                    mom = stock_df['close'].iloc[-1] / stock_df['close'].iloc[-20] - 1
                    qualified.append((code, mom))
        
        # 按动量排序选 top_k
        qualified.sort(key=lambda x: x[1], reverse=True)
        selected = [x[0] for x in qualified[:cfg['top_k']]]
        
        # 调整仓位
        target_position = capital * cfg['position']
        position_per_stock = target_position / len(selected) if selected else 0
        
        # 记录交易
        for code in selected:
            if code not in portfolio or portfolio[code]['shares'] == 0:
                price = stock_data[code][stock_data[code]['date']==date]['close'].iloc[0]
                shares = int(position_per_stock / price / 100) * 100
                if shares > 0:
                    portfolio[code] = {'shares':shares, 'cost':price}
                    trades.append({'date':date,'code':code,'action':'BUY','price':price,'shares':shares})
        
        # 卖出未选中的
        for code in list(portfolio.keys()):
            if code not in selected and portfolio[code]['shares'] > 0:
                price = stock_data[code][stock_data[code]['date']==date]['close'].iloc[0]
                trades.append({'date':date,'code':code,'action':'SELL','price':price,'shares':portfolio[code]['shares']})
                portfolio[code] = {'shares':0,'cost':0}
    
    # 计算当日净值
    total_value = 0
    for code in portfolio:
        if portfolio[code]['shares'] > 0 and date in stock_data[code]['date'].values:
            price = stock_data[code][stock_data[code]['date']==date]['close'].iloc[0]
            total_value += portfolio[code]['shares'] * price
    
    cash = capital - sum(portfolio[c]['shares']*portfolio[c]['cost'] for c in portfolio if portfolio[c]['shares']>0)
    daily_values.append({'date':date,'value':total_value+cash,'state':current_state})
    
    # 记录收益
    if idx > 0 and idx % 5 == 0:
        ret = (daily_values[-1]['value'] - initial_capital) / initial_capital
        state_returns[current_state].append(ret)

# === 结果分析 ===
print("\n"+"="*80)
print("📊 回测结果")
print("="*80)

df_values = pd.DataFrame(daily_values)
df_values['date'] = pd.to_datetime(df_values['date'])
df_values = df_values.set_index('date')

# 各市场状态收益
print("\n  各市场状态下收益表现:")
for state in ['bull','oscillate','bear']:
    rets = state_returns[state]
    if rets:
        avg_ret = np.mean(rets)
        state_data = df_values[df_values['state']==state]
        if len(state_data) > 1:
            period_ret = (state_data['value'].iloc[-1] / state_data['value'].iloc[0] - 1) if len(state_data)>1 else 0
            days = len(state_data)
            ann_ret = (1+period_ret)**(252/days) - 1 if days>0 else 0
        else:
            ann_ret = avg_ret * (252/15)
        print(f"    {V16_CONFIG[state]['name']}: 期间收益{period_ret*100:+.1f}% | 年化{ann_ret*100:+.1f}% | {days}天")

# 总体收益
total_return = (df_values['value'].iloc[-1] - initial_capital) / initial_capital
days_total = len(df_values)
ann_return = (1+total_return)**(252/days_total) - 1 if days_total>0 else 0

# 最大回撤
rolling_max = df_values['value'].cummax()
drawdown = (df_values['value'] - rolling_max) / rolling_max
max_dd = drawdown.min()

# 波动率
daily_rets = df_values['value'].pct_change().dropna()
volatility = daily_rets.std() * np.sqrt(252)

# 夏普比率
rf = 0.03  # 无风险利率 3%
sharpe = (ann_return - rf) / volatility if volatility > 0 else 0

print(f"\n  📈 总体表现:")
print(f"    初始资金：¥{initial_capital:,.0f}")
print(f"    期末净值：¥{df_values['value'].iloc[-1]:,.0f}")
print(f"    总收益率：{total_return*100:+.1f}%")
print(f"    年化收益：{ann_return*100:+.1f}%")
print(f"    最大回撤：{max_dd*100:.1f}%")
print(f"    波动率：{volatility*100:.1f}%")
print(f"    夏普比率：{sharpe:.2f}")

# 对比基准（沪深 300）
hs300_period = hs300[hs300['date'].isin(df_values.index)]
if len(hs300_period) > 1:
    benchmark_return = (hs300_period['close'].iloc[-1] / hs300_period['close'].iloc[0] - 1)
    ann_benchmark = (1+benchmark_return)**(252/len(hs300_period)) - 1
    alpha = ann_return - ann_benchmark
    print(f"\n  📊 对比沪深 300:")
    print(f"    基准收益：{benchmark_return*100:+.1f}% (年化{ann_benchmark*100:+.1f}%)")
    print(f"    超额收益：{alpha*100:+.1f}%")

# === 可视化 ===
print("\n📊 生成图表...")

fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# 净值曲线
ax1 = axes[0]
ax1.plot(df_values.index, df_values['value']/initial_capital*1000000, label='V16 策略', linewidth=2)
ax1.plot(hs300_period['date'], hs300_period['close']/hs300_period['close'].iloc[0]*initial_capital, 
         label='沪深 300', linewidth=2, alpha=0.7)
ax1.set_title('V16 动态配置策略 vs 沪深 300', fontsize=14, fontweight='bold')
ax1.set_ylabel('净值 (元)')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_axisbelow(True)

# 市场状态分布
ax2 = axes[1]
colors = {'bull':'#ff4444','oscillate':'#ffaa00','bear':'#4444ff'}
for state in ['bull','oscillate','bear']:
    state_data = df_values[df_values['state']==state]
    ax2.scatter(state_data.index, state_data['value']/initial_capital*1000000, 
               c=colors[state], label=V16_CONFIG[state]['name'], alpha=0.5, s=10)
ax2.set_title('不同市场状态下的净值分布', fontsize=14, fontweight='bold')
ax2.set_ylabel('净值 (元)')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_axisbelow(True)

plt.tight_layout()
output_path = '/home/admin/openclaw/workspace/backtest/v16_27stocks_result.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f"  ✅ 图表已保存：{output_path}")

# === 生成报告 ===
print("\n"+"="*80)
print("📄 生成回测报告")
print("="*80)

report = f"""# V16 动态配置回测报告 - 27 只五好股票

## 回测概况
- **回测周期**: 2020-01-01 至 2026-03-28
- **股票池**: {len(A_STOCKS)}只 A 股 + {len(HK_STOCKS)}只港股 = {len(stock_data)}只
- **初始资金**: ¥{initial_capital:,.0f}
- **当前市场状态**: {V16_CONFIG[states[-1]]['name']}

## V16 动态配置参数
| 市场状态 | 仓位上限 | 持仓数量 | PE 上限 | ROE 下限 | 调仓周期 |
|---------|---------|---------|--------|---------|---------|
| 🐂牛市 | 95% | 10 只 | <35 | >12% | 20 天 |
| 📊震荡市 | 65% | 5 只 | <30 | >15% | 15 天 |
| 🐻熊市 | 30% | 3 只 | <25 | >18% | 30 天 |

## 市场状态统计
- 🐂牛市：{state_counts.get('bull',0)}天 ({state_counts.get('bull',0)/len(hs300)*100:.1f}%)
- 📊震荡市：{state_counts.get('oscillate',0)}天 ({state_counts.get('oscillate',0)/len(hs300)*100:.1f}%)
- 🐻熊市：{state_counts.get('bear',0)}天 ({state_counts.get('bear',0)/len(hs300)*100:.1f}%)

## 回测结果

### 总体表现
| 指标 | 数值 |
|------|------|
| 初始资金 | ¥{initial_capital:,.0f} |
| 期末净值 | ¥{df_values['value'].iloc[-1]:,.0f} |
| 总收益率 | {total_return*100:+.1f}% |
| 年化收益 | {ann_return*100:+.1f}% |
| 最大回撤 | {max_dd*100:.1f}% |
| 波动率 | {volatility*100:.1f}% |
| 夏普比率 | {sharpe:.2f} |

### 各市场状态下收益
| 市场状态 | 天数 | 期间收益 | 年化收益 |
|---------|------|---------|---------|
| 🐂牛市 | {state_counts.get('bull',0)} | - | - |
| 📊震荡市 | {state_counts.get('oscillate',0)} | - | - |
| 🐻熊市 | {state_counts.get('bear',0)} | - | - |

### 对比基准
- 沪深 300 收益：{benchmark_return*100:+.1f}% (年化{ann_benchmark*100:+.1f}%)
- 超额收益 (Alpha): {alpha*100:+.1f}%

## 结论
V16 动态配置策略通过根据市场状态调整仓位、持仓数量和选股标准，实现了在不同市场环境下的适应性配置。当前震荡市环境下，策略采用 65% 仓位、持有 5 只 PE<30 且 ROE>15% 的优质股票。

---
*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

# 保存报告
report_path = '/home/admin/openclaw/workspace/backtest/v16_27stocks_report.md'
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report)
print(f"  ✅ 报告已保存：{report_path}")

# 保存详细数据
df_values.to_csv('/home/admin/openclaw/workspace/backtest/v16_27stocks_daily_values.csv')
with open('/home/admin/openclaw/workspace/backtest/v16_27stocks_trades.json', 'w', encoding='utf-8') as f:
    json.dump(trades[:100], f, ensure_ascii=False, default=str)  # 只保存前 100 笔交易

print(f"  ✅ 详细数据已保存")
print("\n"+"="*80)
print("✅ V16 动态配置回测完成!")
print("="*80)
