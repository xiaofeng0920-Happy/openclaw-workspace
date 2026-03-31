---
name: data-collector
description: 股票投资团队 - 数据收集员。负责获取所有持仓股票的实时股价、财报数据、大盘指数、市场新闻。
license: Proprietary
version: 1.0.0
---

# 📡 数据收集员 (DataCollector)

股票投资团队的第一个角色，负责收集所有市场数据。

---

## 🎯 职责

1. 读取持仓文件，提取股票代码列表
2. 查询所有股票的实时股价（美股 + 港股）
3. **查询所有持仓股票的最新财报数据**（营收、净利润、EPS、同比变化等）
4. 获取大盘指数（标普 500、恒生指数等）
5. 抓取重要市场新闻
6. 输出标准化 JSON 数据给下一个 Agent

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

**A 股 (可选扩展)：**
- 根据持仓动态添加（如 600519 贵州茅台、300750 宁德时代等）

**期权相关标的：**
- 同上（期权价格随标的变动）

---

## 📤 输出

### 输出文件格式
```json
{
  "timestamp": "2026-03-23T19:30:00+08:00",
  "dataSource": "QVeris + finance-data + akshare",
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
  "earnings": {
    "US": [
      {
        "code": "GOOGL",
        "reportDate": "2025-Q4",
        "revenue": "113.83B",
        "revenueYoY": "+11.22%",
        "netIncome": "34.45B",
        "netIncomeYoY": "-1.50%",
        "eps": "2.85",
        "epsYoY": "+31.34%",
        "roe": "8.59%",
        "beatExpectations": true
      }
    ],
    "HK": [
      {
        "code": "00700",
        "reportDate": "2025-Q4",
        "revenue": "1943.71 亿",
        "revenueYoY": "+12.71%",
        "netIncome": "582.60 亿",
        "netIncomeYoY": "+13.51%",
        "beatExpectations": true
      }
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

### 1. 富途 OpenD（主数据源）⭐
获取真实持仓、实时行情、账户信息

```bash
# 运行富途数据收集器
cd /home/admin/openclaw/workspace/skills/data-collector
python3 futu_collector.py --send

# Python 模块调用
from futu_collector import get_futu_holdings, check_opend_status

# 检查 OpenD 状态
if check_opend_status():
    print("OpenD 运行中")

# 获取真实持仓
data = get_futu_holdings()
```

**优势：**
- 真实持仓数据（非估算）
- 实时行情
- 账户资金、购买力
- 期权持仓

**要求：**
- OpenD 已安装并启动
- 已登录富途账户

### 2. QVeris API（备用数据源）
查询指数行情、资金流向、财经新闻

```python
# QVeris CLI 调用
node ~/.openclaw/skills/qveris-official/scripts/qveris_tool.mjs call <tool_id> --discovery-id <id> --params '{"codes":"000300.SH,HSI.HK"}'

# Python 模块调用
from qveris_data import get_index_quotes, get_stock_news, get_sector_moneyflow

# 获取指数行情
indices = get_index_quotes(['000300.SH', 'HSI.HK', '000016.SH'])

# 获取财经新闻
news = get_stock_news('general', limit=10)

# 获取资金流向
inflow, outflow = get_sector_moneyflow()
```

**优势：**
- 数据全面（指数/资金流/新闻）
- API 稳定
- 支持 A 股/港股/美股

### 2. finance-data 技能
查询 A 股/HK 股/美股股价、财务数据

```
触发词：
- "股价"、"股票价格"、"查询股票"
- "GDP"、"CPI"、"PMI"、"经济数据"
- "财报"、"PE"、"PB"、"ROE"
```

### 3. web_fetch
抓取市场新闻

```python
# 示例：抓取财经新闻
web_fetch(url="https://www.cls.cn", extractMode="markdown")
```

### 4. exec (Python + akshare)
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

### 5. 富途 OpenD（实盘数据）
获取真实持仓和实时行情

```python
from futu_data import get_stock_price, get_us_holdings, get_hk_holdings

# 获取实时股价
quote = get_stock_price('AAPL', 'US')

# 获取真实持仓
holdings = get_us_holdings()
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

### Step 3: 查询财报数据（新增）
```python
# 使用 finance-data 技能查询财报
earnings = []
for stock in stocks:
    try:
        # 调用 finance-data 查询财报
        earnings_data = query_earnings(stock['code'], stock['market'])
        earnings.append({
            'code': stock['code'],
            'reportDate': earnings_data['quarter'],
            'revenue': earnings_data['revenue'],
            'revenueYoY': earnings_data['revenueYoY'],
            'netIncome': earnings_data['netIncome'],
            'netIncomeYoY': earnings_data['netIncomeYoY'],
            'eps': earnings_data['eps'],
            'epsYoY': earnings_data['epsYoY'],
            'roe': earnings_data.get('roe', 'N/A'),
            'beatExpectations': earnings_data.get('beat', None)
        })
    except Exception as e:
        log_error(f"Failed to get earnings for {stock['code']}: {e}")
        earnings.append({'code': stock['code'], 'error': str(e)})

# 保存到 memory/持仓股票_财报跟踪总表_YYYY-MM-DD.md
save_earnings_report(earnings)
```

### Step 4: 获取大盘指数（QVeris 优先）
```python
# 方法 1：使用 QVeris API（推荐）
from qveris_data import get_index_quotes

indices_data = get_index_quotes([
    '000300.SH',  # 沪深 300
    '000016.SH',  # 上证 50
    'HSI.HK',     # 恒生指数
    '399050.SZ',  # 创业板 50
])

indices = {}
for idx in indices_data:
    indices[idx['code']] = {
        'value': idx['price'],
        'change': idx['change'],
        'change_pct': idx['change_pct']
    }

# 方法 2：传统方式（备选）
indices = {
    'SPX': get_index('^GSPC'),
    'HSI': get_index('^HSI'),
    'NDX': get_index('^NDX')
}
```

### Step 5: 抓取市场新闻（QVeris 优先）
```python
# 方法 1：使用 QVeris API（推荐）
from qveris_data import get_stock_news

news = get_stock_news('general', limit=10)

# 方法 2：传统 web_fetch（备选）
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

### Step 6: 输出 JSON
```python
import json
from datetime import datetime

output = {
    'timestamp': datetime.now().isoformat(),
    'dataSource': 'finance-data + akshare',
    'stocks': results,
    'earnings': earnings,  # 新增财报数据
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
- **早间**: 每天 09:00（港股开盘前）- 查询股价 + 大盘
- **午间**: 每天 13:00（港股午盘）- 查询股价 + 新闻
- **晚间**: 每天 21:00（美股开盘后）- 查询股价 + 美股数据
- **财报季**: 每年 1/4/7/10 月的 15 日 - 查询所有持仓财报数据 📊

### 手动触发
用户消息包含：
- "更新持仓"
- "查询股价"
- "分析持仓"
- **"查询财报"** - 触发财报数据查询
- **"财报对比"** - 对比最新财报与持仓成本

---

## ⚠️ 注意事项

### 1. API 限流
- finance-data 技能有速率限制
- 每次查询间隔至少 1 秒
- 批量查询时串行执行
- **财报查询建议分批进行**（美股一批、港股一批）

### 2. 数据验证
- 检查股价是否为合理范围（>0）
- 检查时间戳是否为最新
- 异常数据标记为 "N/A"
- **财报数据需验证季度是否正确**（如 2025-Q4、2026-Q1）

### 3. 数据源优先级

#### 股价数据
- **第一优先级**: 富途 OpenD（实盘数据）⭐ - 真实持仓、实时行情
- **第二优先级**: QVeris API（同花顺 iFinD）- 全面稳定
- **第三优先级**: finance-data 技能（MCP）
- **第四优先级**: akshare（A 股/港股/美股）
- **第五优先级**: yfinance（美股备选）

#### 指数数据
- **第一优先级**: QVeris API（ths_ifind.real_time_quotation）
- **第二优先级**: akshare（stock_zh_index_daily_em）

#### 财经新闻
- **第一优先级**: QVeris API（finnhub.news）
- **第二优先级**: web_fetch（财联社、华尔街见闻）

#### 财报数据
- **第一优先级**: finance-data 技能（MCP）
- **第二优先级**: akshare（A 股/港股/美股）
- **第三优先级**: yfinance（美股备选）
- **第四优先级**: 手动录入（官网/港交所披露易）

### 4. 财报季判断
```python
# 当前月份判断财报季
current_month = datetime.now().month
if current_month in [1, 4, 7, 10]:
    # 财报季，自动查询财报数据
    should_query_earnings = True
```

### 5. 错误处理
```python
try:
    price = get_price(code, market)
except Exception as e:
    log_error(f"Failed to get {code}: {e}")
    price = {'current': 'N/A', 'change': 'N/A'}
```

### 6. QVeris API 配置
```bash
# API Key 配置（环境变量）
export QVERIS_API_KEY="sk-85Z4EEYSR-0A4ifflY7zcHCPOCt_b8ARlMWCQleVvMQ"

# 持久化配置
echo 'export QVERIS_API_KEY="sk-85Z4EEYSR-0A4ifflY7zcHCPOCt_b8ARlMWCQleVvMQ"' >> ~/.bashrc
```

### 7. 市场状态
- 港股：09:30-12:00, 13:00-16:00 (HKT)
- 美股：09:30-16:00 (ET)
- 非交易时间返回收盘价

---

## 📁 文件结构

```
/home/admin/openclaw/workspace/
├── memory/
│   ├── 锋哥持仓_2026-03-16.md              # 持仓数据源
│   ├── 持仓股票_财报跟踪总表_YYYY-MM-DD.md  # 财报汇总报告（新增）
│   └── [股票名]_财报跟踪_YYYY-MM-DD.md     # 单只股票财报详细记录
├── data/
│   ├── market_data_YYYY-MM-DD_HH-mm.json   # 输出文件（含股价 + 财报）
│   └── earnings_data_YYYY-MM-DD.json       # 纯财报数据（新增）
├── skills/
│   └── data-collector/
│       └── SKILL.md                        # 本文件
└── scripts/
    ├── collect_market_data.py              # 执行脚本（可选）
    └── collect_earnings_data.py            # 财报查询脚本（新增）
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
# 查看股价数据
cat data/market_data_*.json | jq '.stocks.US[0]'

# 查看财报数据（新增）
cat data/market_data_*.json | jq '.earnings.US[0]'

# 查看财报汇总报告
cat memory/持仓股票_财报跟踪总表_*.md
```

### 财报查询测试
```bash
# 单独查询财报数据
python scripts/collect_earnings_data.py --stocks GOOGL,NVDA,TSLA
```

---

## 🔄 传递给下一个 Agent

### 常规数据收集完成后
触发 **持仓分析师 (PortfolioAnalyzer)**：

```python
# 触发下一个 Agent
sessions_send(
    sessionKey="portfolio-analyzer",
    message=f"新数据已就绪：{output_file_path}"
)
```

### 财报数据收集完成后
额外触发 **报告撰写员 (ReportWriter)** 创建财报汇总报告：

```python
# 创建财报汇总报告
sessions_send(
    sessionKey="report-writer",
    message=f"财报数据已就绪，请生成汇总报告：{earnings_file_path}"
)
```

---

## 📊 财报查询功能总结

### 新增功能
| 功能 | 描述 | 状态 |
|------|------|------|
| 财报数据查询 | 查询持仓股票最新财报（营收、净利润、EPS、ROE 等） | ✅ |
| 财报汇总报告 | 自动生成 `memory/持仓股票_财报跟踪总表_YYYY-MM-DD.md` | ✅ |
| 财报季自动触发 | 每年 1/4/7/10 月 15 日自动查询所有持仓财报 | ✅ |
| 超预期标记 | 标记是否超预期（beat/miss） | ✅ |
| 同比变化计算 | 自动计算营收/净利润/EPS 同比变化 | ✅ |

### 输出字段
| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 股票代码 |
| reportDate | string | 财报季度（如 2025-Q4） |
| revenue | string | 营收 |
| revenueYoY | string | 营收同比变化 |
| netIncome | string | 净利润 |
| netIncomeYoY | string | 净利润同比变化 |
| eps | string | 每股收益 |
| epsYoY | string | EPS 同比变化 |
| roe | string | 净资产收益率 |
| beatExpectations | boolean | 是否超预期 |

---

**版本：** v1.2（新增 QVeris 数据源）  
**最后更新：** 2026-03-23  
**更新内容：** 
- v1.2: 整合 QVeris API（指数/资金流/新闻）
- v1.1: 扩展 data-collector 职责，增加财报数据查询功能
