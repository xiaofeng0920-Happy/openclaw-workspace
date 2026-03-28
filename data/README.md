# 📊 财务数据接口模块

> 接入真实财务数据，让估值更准确

---

## 📖 概述

本模块提供统一的财务数据获取接口，支持多个数据源，优先使用免费数据源。

### 支持的数据源

| 数据源 | 市场 | 费用 | 需要 Token | 推荐度 |
|--------|------|------|----------|--------|
| **AKShare** | A 股/港股/美股 | 免费 | ❌ | ⭐⭐⭐⭐⭐ |
| **Tushare** | A 股/港股 | 免费/付费 | ✅ | ⭐⭐⭐⭐ |
| **Yahoo Finance** | 美股 | 免费 | ❌ | ⭐⭐⭐⭐ |
| **聚宽 JoinQuant** | A 股 | 免费/付费 | ✅ | ⭐⭐⭐ |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# AKShare（推荐，免费）
pip install akshare

# Tushare（可选，需要 token）
pip install tushare

# Yahoo Finance（可选，美股）
pip install yfinance
```

### 2. 基本使用

```python
from data.financial_data import FinancialData

# 初始化（使用 AKShare，免费）
fd = FinancialData(source='akshare')

# 获取财务数据
data = fd.get_financials('00700.HK')
print(data)
```

### 3. 在巴菲特策略中使用

```python
from strategies.buffett_analyzer import analyze_portfolio

# 自动使用真实数据
analyze_portfolio()
```

---

## 📋 API 参考

### FinancialData 类

```python
fd = FinancialData(source='akshare')  # 或 'tushare', 'yahoo'
```

#### 方法

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `get_financials(code)` | code: 股票代码 | Dict | 获取财务数据 |
| `get_history(code, start, end)` | code, 开始日期，结束日期 | DataFrame | 获取历史行情 |
| `get_industry_pe(industry)` | industry: 行业名称 | float | 获取行业平均 PE |

---

## 📊 返回数据格式

### get_financials() 返回

```python
{
    'code': 'HK.00700',           # 股票代码
    'name': '腾讯控股',            # 股票名称
    'market': 'HK',               # 市场
    'current_price': 508.00,      # 当前价格
    'pe_ratio': 12.5,             # 市盈率
    'pb_ratio': 2.8,              # 市净率
    'roe': 18.5,                  # 净资产收益率
    'roe_5y_avg': 20.3,           # 5 年平均 ROE
    'gross_margin': 42.5,         # 毛利率
    'net_margin': 25.8,           # 净利率
    'debt_to_equity': 0.35,       # 负债/权益
    'earnings_growth_5y': 18.0,   # 5 年盈利增长
    'free_cash_flow': 150000,     # 自由现金流（百万）
    'fcf_yield': 5.2,             # 自由现金流收益率
    'eps': 40.64,                 # 每股收益
    'shares_outstanding': 9500,   # 总股本（百万股）
    'market_cap': 4800000,        # 总市值（百万）
}
```

### get_history() 返回

```python
DataFrame with columns:
- date: 日期
- open: 开盘价
- high: 最高价
- low: 最低价
- close: 收盘价
- volume: 成交量
```

---

## 🔧 配置数据源

### 使用 AKShare（推荐）

```python
fd = FinancialData(source='akshare')
```

**优点**：
- ✅ 完全免费
- ✅ 无需注册
- ✅ 支持 A 股/港股/美股
- ✅ 数据更新及时

**缺点**：
- ⚠️ 部分数据可能不稳定
- ⚠️ 依赖网络

### 使用 Tushare

```python
fd = FinancialData(source='tushare', token='your_token')
```

**获取 Token**：
1. 注册 https://tushare.pro
2. 个人中心获取 token
3. 积分 > 120 可获取财务数据

**优点**：
- ✅ 数据稳定
- ✅ 数据质量高
- ✅ 有专业支持

**缺点**：
- ⚠️ 需要注册
- ⚠️ 部分数据需要积分

### 使用 Yahoo Finance

```python
fd = FinancialData(source='yahoo')
```

**优点**：
- ✅ 美股数据全
- ✅ 免费
- ✅ 无需注册

**缺点**：
- ⚠️ 仅支持美股
- ⚠️ 网络要求高

---

## 📈 实战示例

### 示例 1：获取腾讯财务数据

```python
from data.financial_data import FinancialData

fd = FinancialData(source='akshare')
data = fd.get_financials('00700.HK')

print(f"腾讯控股:")
print(f"  现价：{data['current_price']} 港元")
print(f"  PE: {data['pe_ratio']}")
print(f"  ROE: {data['roe']}%")
print(f"  毛利率：{data['gross_margin']}%")
```

### 示例 2：获取历史行情

```python
from datetime import datetime, timedelta

fd = FinancialData(source='akshare')

# 获取最近 30 天历史
end = datetime.now()
start = end - timedelta(days=30)

history = fd.get_history('00700.HK', start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))

print(f"30 天数据：{len(history)} 条")
print(f"最高价：{history['high'].max()}")
print(f"最低价：{history['low'].min()}")
```

### 示例 3：结合巴菲特策略

```python
from data.financial_data import FinancialData
from strategies.buffett_strategy import BuffettStrategy

# 获取真实数据
fd = FinancialData(source='akshare')
data = fd.get_financials('00700.HK')

# 巴菲特分析
strategy = BuffettStrategy()
stock = strategy.analyze_stock(
    code='HK.00700',
    name='腾讯控股',
    market='HK',
    current_price=508.00,
    financial_data=data
)

print(f"巴菲特评分：{stock.buffett_score}/100")
print(f"投资建议：{stock.recommendation}")
```

---

## ⚠️ 注意事项

### 数据延迟

- **实时行情**：可能有 15 分钟延迟
- **财务数据**：基于最新财报，季度更新
- **估算数据**：部分指标为估算值

### 网络依赖

- 需要稳定的网络连接
- 建议添加重试机制
- 本地缓存可减少请求

### 数据准确性

- 交叉验证多个数据源
- 重要决策前人工核对
- 注意财报发布日期

---

## 🔄 缓存机制

```python
fd = FinancialData(source='akshare')
fd._cache_timeout = 3600  # 缓存 1 小时

# 第一次请求（网络获取）
data1 = fd.get_financials('00700.HK')

# 1 小时内再次请求（使用缓存）
data2 = fd.get_financials('00700.HK')
```

---

## 📚 扩展阅读

- [AKShare 文档](https://akshare.akfamily.xyz/)
- [Tushare 文档](https://tushare.pro/document/2)
- [Yahoo Finance API](https://pypi.org/project/yfinance/)

---

**最后更新**: 2026-03-21  
**版本**: v1.0
