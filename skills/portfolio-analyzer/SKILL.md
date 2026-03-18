---
name: portfolio-analyzer
description: 炒股 Agent 团队 - 持仓分析师。负责对比实时股价与持仓成本，计算盈亏变化。
license: Proprietary
---

# 📊 持仓分析师 (PortfolioAnalyzer)

炒股 Agent 团队的第二个角色，负责分析持仓盈亏。

---

## 🎯 职责

1. 读取数据收集员的股价数据
2. 读取持仓文件的成本价
3. 计算每个头寸的盈亏（金额 + 百分比）
4. 计算总盈亏和总盈亏率
5. 识别涨跌 TOP3 头寸
6. 检测异常风险（期权到期、大幅亏损等）
7. 输出分析数据给策略顾问和报告撰写员

---

## 📥 输入

### 输入 1: 市场数据 JSON
```
/home/admin/openclaw/workspace/data/market_data_YYYY-MM-DD_HH-mm.json
```

### 输入 2: 持仓文件
```
/home/admin/openclaw/workspace/memory/锋哥持仓_2026-03-16.md
```

---

## 📤 输出

### 输出文件格式
```json
{
  "analysisTime": "2026-03-18T09:05:00+08:00",
  "marketDataFile": "market_data_2026-03-18_09-00.json",
  
  "summary": {
    "totalValue": 1879000,
    "totalCost": 1656093,
    "totalGain": 222907,
    "totalGainPercent": 13.5,
    "dayChange": 15230,
    "dayChangePercent": 0.82
  },
  
  "byAccount": {
    "美股账户": {
      "value": 1104000,
      "gain": -37824,
      "gainPercent": -3.3,
      "dayChange": -5200
    },
    "港股账户": {
      "value": 440000,
      "gain": 33700,
      "gainPercent": 8.3,
      "dayChange": 18500
    },
    "保证金账户": {
      "value": 335000,
      "gain": -300,
      "gainPercent": -0.09,
      "dayChange": 1930
    }
  },
  
  "topGainers": [
    {"code": "00883", "name": "中海油", "gain": 43.4, "value": 99154, "dayChange": 2.8},
    {"code": "260528", "name": "腾讯认购", "gain": 180, "value": 8740, "dayChange": 5.2},
    {"code": "BRK.B", "name": "伯克希尔", "gain": 11.3, "value": 10306, "dayChange": 0.5}
  ],
  
  "topLosers": [
    {"code": "03153", "name": "南方日经", "loss": -10.4, "value": -152867, "dayChange": -1.2},
    {"code": "00700", "name": "腾讯控股", "loss": -6.5, "value": -95700, "dayChange": -0.9},
    {"code": "MSFT", "name": "微软", "loss": -13.8, "value": -9910, "dayChange": -2.1}
  ],
  
  "alerts": [
    {"level": "🔴", "type": "期权到期", "message": "AAPL CALL 285 剩余 58 天，亏损 60%"},
    {"level": "🔴", "type": "期权到期", "message": "NVDA CALL 220 剩余 58 天，亏损 37%"},
    {"level": "🟡", "type": "大幅亏损", "message": "MSFT 亏损 13.8%，建议关注"},
    {"level": "🟢", "type": "大幅盈利", "message": "中海油盈利 43.4%，考虑止盈"}
  ],
  
  "optionsExpiry": [
    {"code": "AAPL CALL 285", "expiry": "2026-05-15", "daysLeft": 58, "status": "OTM"},
    {"code": "NVDA CALL 220", "expiry": "2026-05-15", "daysLeft": 58, "status": "OTM"},
    {"code": "GOOGL CALL 320", "expiry": "2026-06-18", "daysLeft": 92, "status": "OTM"}
  ]
}
```

### 输出文件路径
```
/home/admin/openclaw/workspace/data/analysis_YYYY-MM-DD_HH-mm.json
```

---

## 🛠️ 使用工具

### 1. read
读取市场数据 JSON 和持仓文件

### 2. exec (Python + pandas)
数据计算和分析

```python
import pandas as pd
import json

# 读取市场数据
with open(market_data_file, 'r') as f:
    market_data = json.load(f)

# 读取持仓文件（解析 Markdown 表格）
def parse_holdings(md_file):
    # 解析 Markdown 表格，提取持仓数据
    holdings = []
    with open(md_file, 'r') as f:
        content = f.read()
        # 使用正则或 markdown 解析库提取表格
    return holdings

# 计算盈亏
def calculate_pnl(holdings, market_data):
    results = []
    for holding in holdings:
        code = holding['code']
        cost = holding['cost']
        quantity = holding['quantity']
        
        # 获取当前股价
        current_price = get_current_price(code, market_data)
        
        # 计算盈亏
        market_value = current_price * quantity
        cost_value = cost * quantity
        gain = market_value - cost_value
        gain_percent = (gain / cost_value) * 100
        
        results.append({
            'code': code,
            'name': holding['name'],
            'quantity': quantity,
            'cost': cost,
            'current': current_price,
            'marketValue': market_value,
            'gain': gain,
            'gainPercent': gain_percent
        })
    
    return results
```

---

## ⚙️ 工作流程

### Step 1: 读取输入数据
```python
import json
from datetime import datetime

# 读取最新的市场数据
market_file = get_latest_market_data()
with open(market_file, 'r') as f:
    market_data = json.load(f)

# 读取持仓文件
holdings = parse_holdings('/home/admin/openclaw/workspace/memory/锋哥持仓_2026-03-16.md')
```

### Step 2: 解析持仓数据
```python
def parse_holdings(md_file):
    """解析 Markdown 格式的持仓文件"""
    holdings = []
    
    with open(md_file, 'r') as f:
        content = f.read()
    
    # 解析美股持仓表格
    us_holdings = parse_table(content, '美股持仓明细')
    holdings.extend(us_holdings)
    
    # 解析港股持仓表格
    hk_holdings = parse_table(content, '港股持仓明细')
    holdings.extend(hk_holdings)
    
    # 解析期权持仓表格
    options = parse_table(content, '美股期权持仓')
    holdings.extend(options)
    
    return holdings
```

### Step 3: 计算盈亏
```python
def calculate_all_pnl(holdings, market_data):
    results = {
        'stocks': [],
        'options': [],
        'summary': {
            'totalValue': 0,
            'totalCost': 0,
            'totalGain': 0
        }
    }
    
    for holding in holdings:
        if holding['type'] == 'option':
            pnl = calculate_option_pnl(holding, market_data)
            results['options'].append(pnl)
        else:
            pnl = calculate_stock_pnl(holding, market_data)
            results['stocks'].append(pnl)
        
        # 累计总计
        results['summary']['totalValue'] += pnl['marketValue']
        results['summary']['totalCost'] += pnl['costValue']
        results['summary']['totalGain'] += pnl['gain']
    
    results['summary']['totalGainPercent'] = (
        results['summary']['totalGain'] / results['summary']['totalCost'] * 100
    )
    
    return results
```

### Step 4: 识别 TOP3 涨跌
```python
def get_top_gainers_and_losers(results, n=3):
    # 按盈亏率排序
    sorted_by_gain = sorted(results['stocks'], key=lambda x: x['gainPercent'], reverse=True)
    
    top_gainers = sorted_by_gain[:n]
    top_losers = sorted_by_gain[-n:]
    
    return {
        'gainers': top_gainers,
        'losers': top_losers
    }
```

### Step 5: 生成风险警报
```python
def generate_alerts(results):
    alerts = []
    
    # 检查期权到期
    for option in results['options']:
        days_to_expiry = (option['expiry'] - datetime.now()).days
        if days_to_expiry < 60:
            alerts.append({
                'level': '🔴',
                'type': '期权到期',
                'message': f"{option['code']} 剩余 {days_to_expiry} 天，亏损 {option['gainPercent']:.1f}%"
            })
    
    # 检查大幅亏损
    for stock in results['stocks']:
        if stock['gainPercent'] < -10:
            alerts.append({
                'level': '🟡',
                'type': '大幅亏损',
                'message': f"{stock['name']} 亏损 {stock['gainPercent']:.1f}%，建议关注"
            })
    
    # 检查大幅盈利
    for stock in results['stocks']:
        if stock['gainPercent'] > 40:
            alerts.append({
                'level': '🟢',
                'type': '大幅盈利',
                'message': f"{stock['name']} 盈利 {stock['gainPercent']:.1f}%，考虑止盈"
            })
    
    return alerts
```

### Step 6: 输出分析结果
```python
def save_analysis(analysis):
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    output_file = f'/home/admin/openclaw/workspace/data/analysis_{timestamp}.json'
    
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    return output_file
```

---

## ⏰ 触发条件

### 自动触发
- 收到数据收集员的消息：`"新数据已就绪：{file_path}"`
- 检测到新的市场数据文件生成

### 手动触发
用户消息包含：
- "分析持仓"
- "计算盈亏"
- "我的持仓怎么样"

---

## ⚠️ 注意事项

### 1. 数据一致性
- 确保市场数据和持仓文件的时间戳匹配
- 汇率转换使用统一汇率（HKD/USD）

### 2. 期权计算
- 期权盈亏计算考虑合约乘数（通常 100 股/手）
- Short Put 和 Long Call 计算方式不同

### 3. 精度控制
- 金额保留 2 位小数
- 百分比保留 1 位小数

### 4. 错误处理
```python
try:
    analysis = analyze_holdings(market_data, holdings)
except Exception as e:
    log_error(f"Analysis failed: {e}")
    # 发送错误通知
    alerts.append({
        'level': '❌',
        'type': '分析失败',
        'message': f"无法完成分析：{str(e)}"
    })
```

---

## 📁 文件结构

```
/home/admin/openclaw/workspace/
├── memory/
│   └── 锋哥持仓_2026-03-16.md          # 持仓数据源
├── data/
│   ├── market_data_YYYY-MM-DD_HH-mm.json  # 输入：市场数据
│   └── analysis_YYYY-MM-DD_HH-mm.json     # 输出：分析结果
├── skills/
│   └── portfolio-analyzer/
│       └── SKILL.md                    # 本文件
└── scripts/
    └── analyze_portfolio.py            # 执行脚本（可选）
```

---

## 🧪 测试命令

### 手动测试
```bash
cd /home/admin/openclaw/workspace
python scripts/analyze_portfolio.py
```

### 验证输出
```bash
cat data/analysis_*.json | jq '.summary'
cat data/analysis_*.json | jq '.topGainers'
```

---

## 🔄 传递给下一个 Agent

分析完成后，同时触发两个 Agent：

```python
# 触发策略顾问
sessions_send(
    sessionKey="strategy-advisor",
    message=f"分析完成：{analysis_file}"
)

# 触发报告撰写员（可选，等策略建议后再写报告）
# sessions_send(
#     sessionKey="report-writer",
#     message=f"分析完成：{analysis_file}"
# )
```

---

**下一步：** 创建策略顾问 SKILL.md
