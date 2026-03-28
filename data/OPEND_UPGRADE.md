# 🚀 富途 OpenD 升级指南

> 获取最新版本以使用高级功能（新闻、评级、资金流向）

---

## 📊 当前版本

**已安装版本:** 10.1.6108  
**下载地址:** https://www.futunn.com/download  
**最新状态:** ✅ 已是最新版本 (2026-03-21 检查)

---

## ⚠️ 功能限制说明

当前版本 (10.1.6108) 已包含以下功能：

### ✅ 可用功能

| 功能 | API 方法 | 状态 |
|------|---------|------|
| 实时股价 | `get_market_snapshot()` | ✅ |
| K 线数据 | `get_cur_kline()` | ✅ |
| 基本财务 | `get_market_snapshot()` | ✅ |
| 订阅推送 | `subscribe()` | ✅ |

### ⚠️ 需要额外权限的功能

以下功能**不是 OpenD 版本问题**，而是需要**富途账户权限**：

| 功能 | API 方法 | 要求 |
|------|---------|------|
| 新闻舆情 | `get_stock_news()` | 需要港股账户 |
| 分析师评级 | `get_analyst_rating()` | 需要港股账户 |
| 资金流向 | `get_broker_brokers()` | 需要港股账户 |
| 期权链 | `get_option_chain()` | 需要期权权限 |

---

## 🔧 解决方案

### 方案 1：使用富途账户登录（推荐）

如果你有富途港股账户：

1. **打开 OpenD GUI**
   ```bash
   ~/Desktop/Futu_OpenD_*/Futu_OpenD-GUI_*/Futu_OpenD-GUI*.AppImage
   ```

2. **登录富途账户**
   - 使用牛牛号/邮箱/手机号登录
   - 完成身份验证

3. **解锁高级功能**
   - 登录后自动解锁新闻、评级、资金流向

4. **测试连接**
   ```python
   python3 data/futu_data.py
   ```

### 方案 2：使用备选数据源

如果暂无富途账户，可以使用其他数据源：

```python
# 新闻：使用 AKShare
import akshare as ak
news = ak.stock_news_em(symbol="00700")

# 评级：使用 Tushare
import tushare as ts
pro = ts.pro_api('your_token')
data = pro.stk_report()

# 资金流向：使用 AKShare
flow = ak.stock_individual_fund_flow(symbol="00700")
```

### 方案 3：使用 Web 抓取

```python
# 从富途牛牛网页获取
from selenium import webdriver

driver = webdriver.Chrome()
driver.get('https://www.futunn.com/stock/00700-HK')
# 抓取新闻、评级等数据
```

---

## 📥 检查更新

### 手动检查

1. 访问 https://www.futunn.com/download
2. 查看最新版本号
3. 对比当前版本

### 自动检查脚本

```bash
#!/bin/bash
# 检查最新版本
LATEST_URL=$(curl -sI "https://www.futunn.com/download/fetch-lasted-link?name=opend-ubuntu" | grep -i "^location:" | awk '{print $2}')
LATEST_VER=$(echo "$LATEST_URL" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
CURRENT_VER="10.1.6108"

if [ "$LATEST_VER" != "$CURRENT_VER" ]; then
    echo "发现新版本：$LATEST_VER"
    echo "当前版本：$CURRENT_VER"
    echo "下载地址：$LATEST_URL"
else
    echo "已是最新版本：$CURRENT_VER"
fi
```

---

## 📊 数据源对比

| 数据源 | 新闻 | 评级 | 资金流 | 实时股价 | 推荐 |
|--------|------|------|--------|---------|------|
| **富途 OpenAPI** | ⚠️ | ⚠️ | ⚠️ | ✅✅✅ | 主力 |
| AKShare | ✅ | ❌ | ✅ | ✅✅ | 备选 |
| Tushare | ❌ | ✅ | ❌ | ✅ | 备选 |
| 新浪财经 | ✅ | ❌ | ✅ | ✅ | 备选 |

---

## 💡 推荐配置

### 当前最佳实践

```python
# 1. 优先使用富途数据（股价、K 线）
from data.futu_data import FutuDataAPI
api = FutuDataAPI()
quote = api.get_realtime_quote('HK.00700')

# 2. 新闻使用 AKShare
import akshare as ak
news = ak.stock_news_em(symbol="00700")

# 3. 评级使用 Tushare（如有 token）
import tushare as ts
pro = ts.pro_api('your_token')

# 4. 资金流向使用 AKShare
flow = ak.stock_individual_fund_flow(symbol="00700")
```

---

## 🎯 下一步建议

### 如果你有富途账户

1. ✅ 在 OpenD GUI 中登录
2. ✅ 测试高级 API 功能
3. ✅ 更新 futu_data.py 使用完整功能

### 如果暂无富途账户

1. ✅ 使用 AKShare 获取新闻
2. ✅ 使用 AKShare 获取资金流向
3. ✅ 考虑开通富途账户（可选）

---

## 📞 富途客服

- **官网:** https://www.futunn.com
- **客服:** 400-120-1200
- **邮箱:** support@futunn.com

---

**最后更新:** 2026-03-21  
**当前版本:** 10.1.6108 (最新)
