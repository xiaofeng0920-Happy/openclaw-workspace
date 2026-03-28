# 📊 数据源集成配置文档

> 多数据源融合：富途 OpenAPI + AKShare + Tushare

---

## ✅ 已配置数据源

### 1️⃣ 富途 OpenAPI（主力）

**状态:** ✅ 已配置  
**位置:** `data/futu_data.py`  
**优势:** 实时股价、K 线、财务数据

**可用功能:**
- ✅ 实时股价
- ✅ K 线数据（日/周/月/分钟）
- ✅ 基本财务指标（PE/PB/ROE 等）
- ✅ 订阅推送
- ⚠️ 新闻舆情（需登录富途账户）
- ⚠️ 分析师评级（需登录富途账户）
- ⚠️ 资金流向（需登录富途账户）

---

### 2️⃣ AKShare（备选）

**状态:** ✅ 已集成  
**位置:** 自动回退  
**优势:** 免费、无需注册、数据全面

**可用功能:**
- ✅ 实时股价（A 股/港股/美股）
- ✅ 财务指标
- ✅ 新闻舆情
- ✅ 资金流向（A 股）
- ✅ 行业数据
- ✅ 宏观经济数据

---

### 3️⃣ Tushare（可选）

**状态:** ⏳ 需配置 token  
**位置:** 环境变量  
**优势:** 专业财务数据、分析师评级

**配置方法:**
```bash
export TUSHARE_TOKEN='your_token_here'
```

---

## 🔄 数据源优先级

### 自动回退机制

```python
def get_news(code):
    # 1. 优先尝试富途
    try:
        news = futu.get_stock_news(code)
        if news:
            return news
    except:
        pass
    
    # 2. 回退到 AKShare
    try:
        news = akshare.stock_news_em(code)
        return news
    except:
        pass
    
    # 3. 返回空
    return []
```

---

## 📊 功能对比表

| 功能 | 富途 | AKShare | Tushare | 使用建议 |
|------|------|---------|---------|---------|
| **实时股价** | ✅✅✅ | ✅✅ | ✅ | 富途优先 |
| **K 线数据** | ✅✅✅ | ✅✅ | ✅ | 富途优先 |
| **财务指标** | ✅✅ | ✅✅ | ✅✅✅ | 相当 |
| **新闻舆情** | ⚠️ | ✅✅ | ❌ | AKShare |
| **分析师评级** | ⚠️ | ❌ | ✅✅ | Tushare |
| **资金流向** | ⚠️ | ✅(A 股) | ❌ | AKShare |
| **行业数据** | ✅ | ✅✅✅ | ✅✅ | AKShare |
| **宏观数据** | ❌ | ✅✅✅ | ✅✅ | AKShare |

---

## 🚀 使用示例

### 示例 1: 获取完整股票数据

```python
from data.futu_data import FutuDataAPI

api = FutuDataAPI()
api.connect()

# 自动使用最佳数据源
quote = api.get_realtime_quote('HK.00700')  # 富途
news = api.get_news('HK.00700')             # 富途 → AKShare
flow = api.get_capital_flow('HK.00700')     # 富途 → AKShare

api.close()
```

### 示例 2: 直接使用 AKShare

```python
import akshare as ak

# 新闻
news = ak.stock_news_em(symbol="00700")

# 资金流向（A 股）
flow = ak.stock_individual_fund_flow(stock="600519", market="沪")

# 行业数据
industry = ak.stock_board_industry_name_em()
```

### 示例 3: 使用 Tushare（需 token）

```python
import tushare as ts

ts.set_token('your_token')
pro = ts.pro_api()

# 分析师评级
ratings = pro.stk_report(start_date='20260101', end_date='20260321')

# 财务指标
fina = pro.fina_indicator(ts_code='00700.HK')
```

---

## ⚙️ 配置说明

### 环境变量（可选）

```bash
# Tushare token
export TUSHARE_TOKEN='xxxxxxxxxxxxxxxx'

# 富途 OpenD 配置
export FUTU_HOST='127.0.0.1'
export FUTU_PORT='11111'
```

### 配置文件

```json
// notify/feishu_config.json
{
  "data_sources": {
    "primary": "futu",
    "fallback": ["akshare", "tushare"]
  },
  "tushare_token": "your_token"
}
```

---

## 📈 数据质量对比

### 实时性

| 数据源 | A 股 | 港股 | 美股 |
|--------|------|------|------|
| 富途 | 实时 | 15 分钟 | 实时 |
| AKShare | 实时 | 15 分钟 | 15 分钟 |
| Tushare | 实时 | 15 分钟 | ❌ |

### 准确性

| 数据源 | 股价 | 财务 | 新闻 | 评级 |
|--------|------|------|------|------|
| 富途 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| AKShare | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ |
| Tushare | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ | ⭐⭐⭐⭐ |

---

## 🎯 最佳实践

### 1. 股价和 K 线

```python
# 始终使用富途
api = FutuDataAPI()
quote = api.get_realtime_quote(code)
kline = api.get_kline(code)
```

### 2. 新闻舆情

```python
# 优先富途，回退 AKShare
news = api.get_news(code)
if not news:
    import akshare as ak
    news = ak.stock_news_em(symbol)
```

### 3. 财务数据

```python
# 多数据源交叉验证
futu_data = api.get_financials(code)
ak_data = akshare.get_finance_data(code)

# 取平均值或最新值
roe = max(futu_data['roe'], ak_data['roe'])
```

### 4. 错误处理

```python
try:
    data = api.get_realtime_quote(code)
except Exception as e:
    print(f"富途失败：{e}")
    # 回退到 AKShare
    data = akshare.get_quote(code)
```

---

## 📝 注意事项

### 1. 数据延迟

- **富途港股:** 15 分钟延迟
- **AKShare 美股:** 15 分钟延迟
- **Tushare:** 取决于积分等级

### 2. API 限制

- **富途:** 需要 OpenD 运行
- **AKShare:** 频率限制，建议缓存
- **Tushare:** 积分限制

### 3. 数据一致性

- 不同数据源可能有差异
- 建议交叉验证关键数据
- 重要决策前人工核对

---

## 🔧 故障排查

### 问题 1: 富途连接失败

```bash
# 检查 OpenD 状态
pgrep -f "Futu_OpenD"

# 重启 OpenD
~/Desktop/Futu_OpenD*/Futu_OpenD-GUI*.AppImage
```

### 问题 2: AKShare 数据为空

```python
# 检查网络连接
import requests
requests.get('https://www.akshare.xyz')

# 更新 AKShare
pip install -U akshare
```

### 问题 3: Tushare 权限不足

```bash
# 检查 token
echo $TUSHARE_TOKEN

# 获取积分
# 访问 https://tushare.pro
```

---

## 📞 支持资源

- **富途文档:** https://openapi.futunn.com
- **AKShare 文档:** https://akshare.akfamily.xyz
- **Tushare 文档:** https://tushare.pro

---

**最后更新:** 2026-03-21  
**版本:** v1.0
