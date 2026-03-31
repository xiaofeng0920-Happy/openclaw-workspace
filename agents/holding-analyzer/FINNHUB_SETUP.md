# Finnhub API Key 配置指南

**创建时间：** 2026-03-31 10:29

---

## 🔑 获取 API Key

### 1. 注册 Finnhub（免费）

访问：https://finnhub.io/register

- 使用邮箱注册
- 或使用 Google/GitHub 快捷登录

### 2. 获取 API Key

登录后访问：https://finnhub.io/dashboard

复制你的 API Key（类似：`xxxxxxxxxxxxxxxxxxxxxxxx`）

---

## 📝 配置方法

### 方法 1：环境变量（推荐）

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export FINNHUB_API_KEY=your_api_key_here

# 立即生效
source ~/.bashrc
```

### 方法 2：配置文件

创建 `~/.futu/finnhub_config.json`：

```bash
mkdir -p ~/.futu
cat > ~/.futu/finnhub_config.json << 'EOF'
{
  "api_key": "your_api_key_here",
  "updated": "2026-03-31"
}
EOF
```

---

## ✅ 测试配置

```bash
cd /home/admin/openclaw/workspace/agents/holding-analyzer
python3 finnhub_data.py
```

预期输出：
```
✅ API 正常
📈 AAPL: $xxx.xx (+x.xx%)
📈 GOOGL: $xxx.xx (+x.xx%)
...
```

---

## 📊 免费套餐限制

| 项目 | 限制 |
|------|------|
| API 调用 | 60 次/分钟 |
| 实时股价 | ✅ 支持 |
| 历史数据 | ✅ 支持 |
| 财报数据 | ✅ 支持 |
| 新闻 | ✅ 支持 |

---

## 💡 使用示例

### 获取单支股票价格

```python
from finnhub_data import get_quote

quote = get_quote("AAPL")
print(f"AAPL: ${quote['price']:.2f} ({quote['change_pct']:+.2f}%)")
```

### 批量获取持仓股票

```python
from finnhub_data import get_multiple_quotes

symbols = ["AAPL", "GOOGL", "TSLA", "NVDA", "MSFT"]
quotes = get_multiple_quotes(symbols)

for symbol, data in quotes.items():
    print(f"{symbol}: ${data['price']:.2f} ({data['change_pct']:+.2f}%)")
```

### 获取财报数据

```python
from finnhub_data import get_earnings

earnings = get_earnings("AAPL")
for eps in earnings:
    print(f"{eps['period']}: EPS ${eps['epsActual']} (预期：${eps['epsEstimate']})")
```

---

## 🚀 集成到持仓监控

修改 `run.py`，添加 `--finnhub` 参数支持：

```bash
python3 run.py --finnhub --send
```

---

## 📞 升级套餐

如需更高调用限制：

- Pro: $59/月 (180 次/分钟)
- Business: $169/月 (900 次/分钟)

访问：https://finnhub.io/pricing

---

**下一步：** 获取 API Key 后配置，然后运行持仓监控。
