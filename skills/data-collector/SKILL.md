---
name: data-collector
description: 炒股 Agent 团队 - 数据收集员。负责获取所有持仓股票的实时股价、大盘指数、市场新闻。
license: Proprietary
---

# 📡 数据收集员 (DataCollector)

炒股 Agent 团队的第一个角色，负责收集所有市场数据。

---

## 🎯 职责

1. 读取持仓文件，提取股票代码列表
2. 查询所有股票的实时股价（美股 + 港股）
3. 获取大盘指数（标普 500、恒生指数等）
4. 抓取重要市场新闻
5. 输出标准化 JSON 数据给下一个 Agent

---

## 📥 输入

### 持仓文件路径
```
/home/admin/openclaw/workspace/memory/锋哥持仓_2026-03-16.md
```

### 需要提取的股票代码

**美股：**
- GOOGL, BRK.B, KO, ORCL, MSFT, NVDA, AAPL, TSLA

**港股：**
- 00700 (腾讯), 03153 (南方日经), 00883 (中海油), 09988 (阿里), 07709 (南方两倍做多)

**期权相关标的：**
- 同上（期权价格随标的变动）

---

## 📤 输出

### 输出文件格式
```json
{
  "timestamp": "2026-03-18T09:00:00+08:00",
  "dataSource": "finance-data + akshare",
  "stocks": {
    "US": [
      {"code": "GOOGL", "price": 302.28, "change": -0.03, "changePercent": -0.01},
      {"code": "BRK.B", "price": 490.03, "change": 2.5, "changePercent": 0.51}
    ],
    "HK": [
      {"code": "00700", "price": 547.50, "change": -5.2, "changePercent": -0.94},
      {"code": "00883", "price": 29.76, "change": 0.8, "changePercent": 2.76}
    ]
  },
  "indices": {
    "SPX": {"value": 5200, "change": 0.5},
    "HSI": {"value": 18500, "change": -1.2},
    "NDX": {"value": 18200, "change": 0.3}
  },
  "news": [
    {"title": "美联储暗示...", "source": "彭博", "time": "08:30"},
    {"title": "腾讯发布新...", "source": "路透", "time": "09:15"}
  ],
  "marketStatus": {
    "US": "closed",
    "HK": "open",
    "nextOpen": "2026-03-18T09:30:00-04:00"
  }
}
```

### 输出文件路径
```
/home/admin/openclaw/workspace/data/market_data_YYYY-MM-DD_HH-mm.json
```

---

## 🛠️ 使用工具

### 1. finance-data 技能
查询 A 股/HK 股/美股股价、财务数据

```
触发词：
- "股价"、"股票价格"、"查询股票"
- "GDP"、"CPI"、"PMI"、"经济数据"
- "财报"、"PE"、"PB"、"ROE"
```

### 2. web_fetch
抓取市场新闻

```python
# 示例：抓取财经新闻
web_fetch(url="https://www.cls.cn", extractMode="markdown")
```

### 3. exec (Python + akshare)
批量获取股价数据

```python
import akshare as ak
import pandas as pd

# 获取港股实时行情
def get_hk_stock_price(code):
    df = ak.stock_hk_daily(symbol=code)
    return df.iloc[-1]['close']

# 获取美股实时行情（通过 yfinance）
import yfinance as yf
def get_us_stock_price(ticker):
    stock = yf.Ticker(ticker)
    return stock.info['currentPrice']
```

---

## ⚙️ 工作流程

### Step 1: 读取持仓文件
```python
with open('/home/admin/openclaw/workspace/memory/锋哥持仓_2026-03-16.md', 'r') as f:
    content = f.read()
    # 解析表格，提取股票代码
```

### Step 2: 批量查询股价
```python
stocks = {
    'US': ['GOOGL', 'BRK.B', 'KO', 'ORCL', 'MSFT', 'NVDA', 'AAPL', 'TSLA'],
    'HK': ['00700', '03153', '00883', '09988', '07709']
}

results = []
for market, codes in stocks.items():
    for code in codes:
        price = get_price(code, market)  # 调用 finance-data 或 akshare
        results.append({
            'code': code,
            'market': market,
            'price': price['current'],
            'change': price['change'],
            'changePercent': price['changePercent']
        })
```

### Step 3: 获取大盘指数
```python
indices = {
    'SPX': get_index('^GSPC'),
    'HSI': get_index('^HSI'),
    'NDX': get_index('^NDX')
}
```

### Step 4: 抓取市场新闻
```python
news_sources = [
    'https://www.cls.cn',
    'https://wallstreetcn.com',
    'https://www.hkexnews.hk'
]

news = []
for source in news_sources:
    articles = fetch_news(source)
    news.extend(articles[:5])  # 每个来源取前 5 条
```

### Step 5: 输出 JSON
```python
import json
from datetime import datetime

output = {
    'timestamp': datetime.now().isoformat(),
    'dataSource': 'finance-data + akshare',
    'stocks': results,
    'indices': indices,
    'news': news,
    'marketStatus': get_market_status()
}

with open(f'/home/admin/openclaw/workspace/data/market_data_{datetime.now().strftime("%Y-%m-%d_%H-%M")}.json', 'w') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
```

---

## ⏰ 触发条件

### 定时触发
- **早间**: 每天 09:00（港股开盘前）
- **午间**: 每天 13:00（港股午盘）
- **晚间**: 每天 21:00（美股开盘后）

### 手动触发
用户消息包含：
- "更新持仓"
- "查询股价"
- "分析持仓"

---

## ⚠️ 注意事项

### 1. API 限流
- finance-data 技能有速率限制
- 每次查询间隔至少 1 秒
- 批量查询时串行执行

### 2. 数据验证
- 检查股价是否为合理范围（>0）
- 检查时间戳是否为最新
- 异常数据标记为 "N/A"

### 3. 错误处理
```python
try:
    price = get_price(code, market)
except Exception as e:
    log_error(f"Failed to get {code}: {e}")
    price = {'current': 'N/A', 'change': 'N/A'}
```

### 4. 市场状态
- 港股：09:30-12:00, 13:00-16:00 (HKT)
- 美股：09:30-16:00 (ET)
- 非交易时间返回收盘价

---

## 📁 文件结构

```
/home/admin/openclaw/workspace/
├── memory/
│   └── 锋哥持仓_2026-03-16.md          # 持仓数据源
├── data/
│   └── market_data_YYYY-MM-DD_HH-mm.json  # 输出文件
├── skills/
│   └── data-collector/
│       └── SKILL.md                    # 本文件
└── scripts/
    └── collect_market_data.py          # 执行脚本（可选）
```

---

## 🧪 测试命令

### 手动测试
```bash
cd /home/admin/openclaw/workspace
python scripts/collect_market_data.py
```

### 验证输出
```bash
cat data/market_data_*.json | jq '.stocks.US[0]'
```

---

## 🔄 传递给下一个 Agent

数据收集完成后，自动触发 **持仓分析师 (PortfolioAnalyzer)**：

```python
# 触发下一个 Agent
sessions_send(
    sessionKey="portfolio-analyzer",
    message=f"新数据已就绪：{output_file_path}"
)
```

---

**下一步：** 创建持仓分析师 SKILL.md
