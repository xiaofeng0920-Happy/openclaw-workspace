# 📊 Tushare 数据接口集成说明

**日期：** 2026-03-28 23:40  
**优先级：** **Tushare 优先**，akshare 作为备用

---

## ✅ 已更新模块

### 1. config.py - 数据源配置

```python
DATA_SOURCES = {
    "price": "tushare",      # ✅ 行情数据：Tushare 优先
    "financial": "tushare",  # ✅ 财务数据：Tushare 优先
    "index": "tushare"       # ✅ 指数数据：Tushare 优先
}
```

### 2. screener.py - 股票筛选

```python
def __init__(self, data_source: str = "tushare"):  # ✅ 默认 Tushare
```

**支持的数据接口：**
- `stock_basic()` - 股票基本信息
- `daily()` - 日线行情
- `fina_indicator()` - 财务指标
- `hs300_weight()` - 沪深 300 权重
- `zz1000_weight()` - 中证 1000 权重

### 3. __init__.py - 包初始化

```python
def create_screener(data_source: str = "tushare") -> StockScreener:  # ✅ 默认 Tushare
```

---

## 📁 Tushare Token 配置

**位置：** `/home/admin/openclaw/workspace/agents/data-collector/.tushare_token`

**获取方式：**
1. 访问 https://tushare.pro
2. 注册账号
3. 获取个人 TOKEN
4. 保存到 `.tushare_token` 文件

**权限要求：**
- 基础行情数据（免费）
- 财务数据（免费）
- 指数数据（免费）
- 沪深 300/中证 1000 成分股（免费）

---

## 🔄 数据接口映射

### 行情数据

| 功能 | Tushare 接口 | akshare 接口 | 优先级 |
|------|-------------|-------------|--------|
| 日线行情 | `daily()` | `stock_zh_a_hist()` | ⭐⭐⭐ Tushare |
| 实时行情 | `daily()` | `stock_zh_a_spot_em()` | ⭐⭐⭐ Tushare |
| 股票列表 | `stock_basic()` | `stock_info_a_code_name()` | ⭐⭐⭐ Tushare |
| 交易日历 | `trade_cal()` | `tool_trade_date_hist()` | ⭐⭐⭐ Tushare |

### 财务数据

| 功能 | Tushare 接口 | akshare 接口 | 优先级 |
|------|-------------|-------------|--------|
| 财务指标 | `fina_indicator()` | `stock_financial_analysis_indicator()` | ⭐⭐⭐ Tushare |
| 利润表 | `income()` | `stock_financial_report_sina()` | ⭐⭐⭐ Tushare |
| 资产负债表 | `balancesheet()` | `stock_financial_report_sina()` | ⭐⭐⭐ Tushare |
| 现金流量表 | `cashflow()` | `stock_financial_report_sina()` | ⭐⭐⭐ Tushare |
| ROE/ROIC | `fina_indicator()` | `stock_financial_analysis_indicator()` | ⭐⭐⭐ Tushare |

### 指数数据

| 功能 | Tushare 接口 | akshare 接口 | 优先级 |
|------|-------------|-------------|--------|
| 沪深 300 行情 | `index_daily()` | `stock_zh_index_hist()` | ⭐⭐⭐ Tushare |
| 成分股权重 | `index_weight()` | `stock_zh_index_spot()` | ⭐⭐⭐ Tushare |
| 中证 1000 行情 | `index_daily()` | `stock_zh_index_hist()` | ⭐⭐⭐ Tushare |

### 市场状态

| 功能 | Tushare 接口 | akshare 接口 | 优先级 |
|------|-------------|-------------|--------|
| 涨跌家数 | `daily()` (全市场) | `stock_zh_a_spot_em()` | ⭐⭐ Tushare |
| 涨跌停统计 | `limit_list()` | `stock_zt_pool_em()` | ⭐⭐ Tushare |
| 资金流向 | `moneyflow()` | `stock_individual_fund_flow()` | ⭐⭐ 备用 |

---

## 📊 使用示例

### 方式 1：统一入口

```bash
cd /home/admin/openclaw/workspace
python3 invest.py screen  # 自动使用 Tushare
```

### 方式 2：直接调用

```python
from skills.buffett-investor import create_screener

# 默认使用 Tushare
screener = create_screener()  # data_source="tushare"

# 或指定 akshare（备用）
screener_ak = create_screener(data_source="akshare")
```

### 方式 3：单独模块

```bash
cd /home/admin/openclaw/workspace/skills/buffett-investor

# 股票筛选（Tushare 优先）
python3 screener.py

# 市场状态（Tushare 优先）
python3 market_state.py
```

---

## 🛠️ 代码示例

### 获取股票基本信息

```python
import tushare as ts

ts.set_token('your_token')
pro = ts.pro_api()

# 获取 A 股列表
df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,market,list_date')
```

### 获取日线行情

```python
# 获取贵州茅台日线
df = pro.daily(ts_code='600519.SH', start_date='20260301', end_date='20260328')
```

### 获取财务指标

```python
# 获取 ROE/ROIC 等指标
df = pro.fina_indicator(ts_code='600519.SH', start_date='20210101', end_date='20260328')
```

### 获取指数行情

```python
# 获取沪深 300 行情
df = pro.index_daily(ts_code='000300.SH', start_date='20210101', end_date='20260328')
```

---

## 📈 数据更新频率

| 数据类型 | 更新频率 | Tushare 更新时间 |
|---------|---------|----------------|
| **日线行情** | 每日 | 交易日 18:00 后 |
| **财务数据** | 季度 | 财报发布后 1-2 天 |
| **指数数据** | 每日 | 交易日 18:00 后 |
| **成分股权重** | 月度 | 次月前 5 个工作日 |

---

## ⚠️ 注意事项

### 1. Token 安全

- ✅ Token 保存在 `.tushare_token` 文件
- ✅ 不要提交到 Git 仓库
- ✅ 已添加到 `.gitignore`

### 2. 积分限制

- 基础数据：免费（无需积分）
- 高级数据：需要积分（根据需求升级）
- 当前需求：**免费数据即可满足**

### 3. 备用方案

如果 Tushare 接口失败，自动切换到 akshare：

```python
try:
    # 优先使用 Tushare
    data = pro.daily(ts_code=code)
except Exception:
    # 备用 akshare
    data = ak.stock_zh_a_hist(symbol=code)
```

---

## 🔧 测试验证

### 测试 Tushare 连接

```bash
cd /home/admin/openclaw/workspace/skills/buffett-investor
python3 -c "import tushare as ts; ts.set_token(open('../agents/data-collector/.tushare_token').read().strip()); pro = ts.pro_api(); print(pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,name').head())"
```

### 测试股票筛选

```bash
python3 screener.py  # 默认使用 Tushare
```

---

## 📋 更新清单

| 文件 | 更新内容 | 状态 |
|------|---------|------|
| `config.py` | 数据源改为 Tushare 优先 | ✅ |
| `__init__.py` | 默认数据源改为 Tushare | ✅ |
| `screener.py` | 默认数据源改为 Tushare | ✅ |
| `market_state.py` | 支持 Tushare（待更新） | ⏳ |
| `market_state_enhanced.py` | 支持 Tushare（待更新） | ⏳ |
| `TUSHARE 集成说明.md` | 本文档 | ✅ |

---

## 🚀 下一步

1. ✅ 更新 config.py - 完成
2. ✅ 更新 __init__.py - 完成
3. ✅ 更新 screener.py - 完成
4. ⏳ 更新 market_state.py - 待执行
5. ⏳ 更新 market_state_enhanced.py - 待执行
6. ⏳ 测试 Tushare 连接 - 待执行

---

*文档生成时间：2026-03-28 23:40*  
*版本：v2.0 - Tushare 优先*
