# 📊 富途 OpenAPI 数据使用指南

> 使用富途 OpenAPI 获取实时股价、财务数据、新闻舆情

---

## ✅ 已实现功能

### 1️⃣ 实时股价

```python
from data.futu_data import FutuDataAPI

api = FutuDataAPI()
api.connect()

# 获取实时行情
quote = api.get_realtime_quote('HK.00700')
print(f"现价：{quote['last_price']} 港元")
print(f"涨跌：{quote['change_pct']:+.2f}%")
print(f"市盈率：{quote['pe_ratio']}")
print(f"市值：{quote['market_cap']} 港元")
```

**返回数据:**
- 最新价、开盘价、最高价、最低价
- 涨跌幅、成交量、成交额
- 市盈率 (PE)、市净率 (PB)
- 股息率、市值、股本

---

### 2️⃣ K 线数据

```python
# 获取日 K 线
kline = api.get_kline('HK.00700', ktype='K_DAY', count=100)
print(kline[['time_key', 'open', 'close', 'high', 'low', 'volume']])
```

**支持类型:**
- K_DAY (日 K)
- K_WEEK (周 K)
- K_MON (月 K)
- K_5M, K_15M, K_30M, K_60M (分钟 K)

---

### 3️⃣ 财务数据

```python
# 获取财务指标
financials = api.get_financials('HK.00700')
print(f"ROE: {financials['roe']}%")
print(f"毛利率：{financials['gross_margin']}%")
```

**返回数据:**
- PE、PB、股息率
- ROE（估算）
- 毛利率（估算）
- 市值、股本

---

## ⚠️ 功能限制

### 需要更高权限的功能

以下功能需要富途 OpenD 更高版本或额外权限：

| 功能 | API 方法 | 状态 |
|------|---------|------|
| 实时股价 | `get_realtime_quote()` | ✅ 可用 |
| K 线数据 | `get_kline()` | ✅ 可用 |
| 财务数据 | `get_financials()` | ✅ 可用 (部分估算) |
| 新闻舆情 | `get_stock_news()` | ⚠️ 需升级 |
| 分析师评级 | `get_analyst_rating()` | ⚠️ 需升级 |
| 资金流向 | `get_broker_brokers()` | ⚠️ 需升级 |
| 期权链 | `get_option_chain()` | ⚠️ 需升级 |

---

## 🔧 升级 OpenD

如需使用高级功能，请升级富途 OpenD:

1. 访问 https://www.futunn.com/download
2. 下载最新版 OpenD
3. 安装并重启

---

## 📊 使用示例

### 完整股票分析

```python
from data.futu_data import FutuDataAPI

api = FutuDataAPI()
api.connect()

# 获取所有数据
quote = api.get_realtime_quote('HK.00700')
financials = api.get_financials('HK.00700')
kline = api.get_kline('HK.00700', count=30)

# 分析
print(f"现价：{quote['last_price']}")
print(f"ROE: {financials['roe']}%")
print(f"30 日涨幅：{(kline['close'].iloc[-1] / kline['close'].iloc[0] - 1) * 100:.2f}%")

api.close()
```

---

## 🔄 与现有系统集成

### 更新 buffett_analyzer.py

```python
from data.futu_data import FutuDataAPI

# 使用富途数据
api = FutuDataAPI()
api.connect()

# 获取真实数据
quote = api.get_realtime_quote('HK.00700')
financials = api.get_financials('HK.00700')

# 巴菲特分析
stock = strategy.analyze_stock(
    code='HK.00700',
    current_price=quote['last_price'],
    financial_data=financials
)
```

---

## 📈 数据对比

| 数据源 | 实时性 | 准确性 | 功能 | 推荐 |
|--------|--------|--------|------|------|
| **富途 OpenAPI** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ 推荐 |
| AKShare | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 备选 |
| Tushare | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 备选 |

---

## 🎯 最佳实践

### 1. 优先使用富途数据

```python
# 主数据源
try:
    from data.futu_data import FutuDataAPI
    api = FutuDataAPI()
    data = api.get_realtime_quote(code)
except:
    # 备选 AKShare
    from data.financial_data import FinancialData
    fd = FinancialData(source='akshare')
    data = fd.get_financials(code)
```

### 2. 缓存数据

```python
# 避免频繁请求
from functools import lru_cache

@lru_cache(maxsize=100)
def get_quote_cached(code: str):
    return api.get_realtime_quote(code)
```

### 3. 错误处理

```python
try:
    quote = api.get_realtime_quote(code)
    if quote:
        # 处理数据
        pass
except Exception as e:
    print(f"获取数据失败：{e}")
```

---

## 📝 注意事项

1. **OpenD 必须运行**
   - 确保富途 OpenD 已启动
   - 确保已登录

2. **数据延迟**
   - 港股：15 分钟延迟
   - 美股：实时（已登录）

3. **权限限制**
   - 部分功能需要更高版本
   - 某些数据需要额外权限

---

**最后更新**: 2026-03-21  
**版本**: v1.0
