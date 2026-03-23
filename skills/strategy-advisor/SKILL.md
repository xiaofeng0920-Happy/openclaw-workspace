---
name: strategy-advisor
description: 股票投资团队 - 策略顾问。基于分析结果生成操作建议（买入/卖出/持有）。
license: Proprietary
---

# 🧠 策略顾问 (StrategyAdvisor)

股票投资团队的第三个角色，负责生成投资策略建议。

---

## 🎯 职责

1. 读取持仓分析师的盈亏数据
2. 结合市场新闻和技术指标
3. 为每个头寸生成操作建议（买入/卖出/持有/减仓/止盈/止损）
4. 设置建议优先级（🔴紧急/🟡重要/🟢一般/🔵长期）
5. 给出具体理由和目标价位
6. 输出建议列表给报告撰写员

---

## 📥 输入

### 输入 1: 分析数据 JSON
```
/home/admin/openclaw/workspace/data/analysis_YYYY-MM-DD_HH-mm.json
```

### 输入 2: 市场新闻（可选）
```
/home/admin/openclaw/workspace/data/market_data_YYYY-MM-DD_HH-mm.json
```

---

## 📤 输出

### 输出文件格式
```json
{
  "adviceTime": "2026-03-18T09:10:00+08:00",
  "analysisFile": "analysis_2026-03-18_09-05.json",
  
  "recommendations": [
    {
      "priority": "🔴",
      "action": "止损",
      "target": "AAPL CALL 285",
      "code": "AAPL",
      "type": "option",
      "currentLoss": -1232,
      "lossPercent": -60,
      "reason": "期权亏损 60%，剩余 58 天到期，时间价值衰减加速",
      "suggestion": "立即止损，回收残值$768",
      "targetPrice": null,
      "deadline": "2026-05-15",
      "confidence": "high"
    },
    {
      "priority": "🔴",
      "action": "止损",
      "target": "NVDA CALL 220",
      "code": "NVDA",
      "type": "option",
      "currentLoss": -485,
      "lossPercent": -37,
      "reason": "期权亏损 37%，剩余 58 天到期，NVDA 波动大",
      "suggestion": "立即止损，回收残值$815",
      "targetPrice": null,
      "deadline": "2026-05-15",
      "confidence": "high"
    },
    {
      "priority": "🟡",
      "action": "减仓",
      "target": "微软",
      "code": "MSFT",
      "type": "stock",
      "currentLoss": -9910,
      "lossPercent": -13.8,
      "reason": "科技股调整，MSFT 跌破关键支撑位$400",
      "suggestion": "减持 50% 仓位，换到走势更强的 GOOGL",
      "targetPrice": 420,
      "deadline": null,
      "confidence": "medium"
    },
    {
      "priority": "🟢",
      "action": "止盈",
      "target": "中海油",
      "code": "00883",
      "type": "stock",
      "currentGain": 99154,
      "gainPercent": 43.4,
      "reason": "能源股大涨，盈利 43%，油价高位震荡",
      "suggestion": "止盈 50%，锁定利润$50,000，剩余仓位继续持有",
      "targetPrice": 32,
      "deadline": null,
      "confidence": "medium"
    },
    {
      "priority": "🟢",
      "action": "止盈",
      "target": "南方两倍做多",
      "code": "07709",
      "type": "etf",
      "currentGain": 63745,
      "gainPercent": 9.6,
      "reason": "杠杆 ETF 波动大，盈利 10% 建议部分止盈",
      "suggestion": "止盈 50%，降低风险",
      "targetPrice": null,
      "deadline": null,
      "confidence": "low"
    },
    {
      "priority": "🔵",
      "action": "持有",
      "target": "伯克希尔-B",
      "code": "BRK.B",
      "type": "stock",
      "currentGain": 10306,
      "gainPercent": 11.3,
      "reason": "价值股稳健，巴菲特持仓分散风险",
      "suggestion": "继续持有，长期配置",
      "targetPrice": 520,
      "deadline": null,
      "confidence": "high"
    },
    {
      "priority": "🔵",
      "action": "持有",
      "target": "可口可乐",
      "code": "KO",
      "type": "stock",
      "currentGain": 7268,
      "gainPercent": 9.9,
      "reason": "防御性股票，分红稳定",
      "suggestion": "继续持有，收息",
      "targetPrice": 80,
      "deadline": null,
      "confidence": "high"
    }
  ],
  
  "portfolioStrategy": {
    "assetAllocation": {
      "current": {
        "US_stocks": 60,
        "HK_stocks": 23,
        "options": 10,
        "cash": 7
      },
      "recommended": {
        "US_stocks": 55,
        "HK_stocks": 20,
        "options": 5,
        "cash": 20
      }
    },
    "riskLevel": "medium-high",
    "suggestions": [
      "降低期权仓位至 5% 以下",
      "增加现金/债券配置到 20%",
      "考虑增加防御性股票比例"
    ]
  },
  
  "marketOutlook": {
    "shortTerm": "震荡",
    "mediumTerm": "谨慎乐观",
    "keyRisks": [
      "美联储利率政策",
      "地缘政治风险",
      "科技股估值压力"
    ],
    "keyOpportunities": [
      "能源股延续涨势",
      "价值股轮动",
      "港股估值修复"
    ]
  }
}
```

### 输出文件路径
```
/home/admin/openclaw/workspace/data/strategy_YYYY-MM-DD_HH-mm.json
```

---

## 🛠️ 使用工具

### 1. finance-data
查询技术指标、财务数据、分析师评级

```
触发词：
- "技术分析"、"支撑位"、"阻力位"
- "PE"、"PB"、"ROE"、"估值"
- "分析师评级"、"目标价"
```

### 2. web_fetch
获取市场研报、新闻分析

```python
# 获取分析师评级
web_fetch(url="https://finance.yahoo.com/quote/AAPL/analysis", extractMode="markdown")
```

### 3. read
读取分析数据和市场数据

---

## ⚙️ 工作流程

### Step 1: 读取分析数据
```python
import json

with open(analysis_file, 'r') as f:
    analysis = json.load(f)

holdings = analysis['stocks'] + analysis['options']
alerts = analysis['alerts']
```

### Step 2: 制定建议规则

```python
# 止损规则
STOP_LOSS_RULES = {
    'option_loss_50': {'threshold': -50, 'action': '止损', 'priority': '🔴'},
    'option_loss_30': {'threshold': -30, 'action': '止损', 'priority': '🔴'},
    'stock_loss_20': {'threshold': -20, 'action': '止损', 'priority': '🟡'},
    'stock_loss_15': {'threshold': -15, 'action': '减仓', 'priority': '🟡'},
}

# 止盈规则
TAKE_PROFIT_RULES = {
    'option_gain_100': {'threshold': 100, 'action': '止盈', 'priority': '🟢'},
    'stock_gain_40': {'threshold': 40, 'action': '止盈', 'priority': '🟢'},
    'stock_gain_20': {'threshold': 20, 'action': '止盈部分', 'priority': '🟢'},
}

# 持有规则
HOLD_RULES = {
    'gain_positive': {'threshold': 0, 'action': '持有', 'priority': '🔵'},
    'loss_small': {'threshold': -5, 'action': '持有观察', 'priority': '🔵'},
}
```

### Step 3: 生成建议
```python
def generate_recommendations(holdings, alerts):
    recommendations = []
    
    for holding in holdings:
        code = holding['code']
        gain_percent = holding['gainPercent']
        holding_type = holding['type']
        
        # 检查警报
        alert = next((a for a in alerts if code in a.get('message', '')), None)
        
        # 应用规则
        if holding_type == 'option':
            if gain_percent < -50:
                rec = create_recommendation(
                    priority='🔴',
                    action='止损',
                    holding=holding,
                    reason=f"期权亏损 {gain_percent:.1f}%，时间价值衰减",
                    suggestion="立即止损，回收残值"
                )
            elif gain_percent > 100:
                rec = create_recommendation(
                    priority='🟢',
                    action='止盈',
                    holding=holding,
                    reason=f"期权盈利 {gain_percent:.1f}%，建议锁定利润",
                    suggestion="止盈 50-100%"
                )
            else:
                rec = create_recommendation(
                    priority='🔵',
                    action='持有',
                    holding=holding,
                    reason="观望",
                    suggestion="继续持有"
                )
        
        elif holding_type == 'stock':
            if gain_percent > 40:
                rec = create_recommendation(
                    priority='🟢',
                    action='止盈',
                    holding=holding,
                    reason=f"盈利 {gain_percent:.1f}%，建议部分止盈",
                    suggestion="止盈 30-50%"
                )
            elif gain_percent < -15:
                rec = create_recommendation(
                    priority='🟡',
                    action='减仓',
                    holding=holding,
                    reason=f"亏损 {gain_percent:.1f}%，考虑换股",
                    suggestion="减持 50%，换到强势股"
                )
            else:
                rec = create_recommendation(
                    priority='🔵',
                    action='持有',
                    holding=holding,
                    reason="走势正常",
                    suggestion="继续持有"
                )
        
        recommendations.append(rec)
    
    # 按优先级排序
    priority_order = {'🔴': 0, '🟡': 1, '🟢': 2, '🔵': 3}
    recommendations.sort(key=lambda x: priority_order.get(x['priority'], 4))
    
    return recommendations
```

### Step 4: 生成组合策略
```python
def generate_portfolio_strategy(analysis):
    current_allocation = analysis['byAccount']
    
    total_value = analysis['summary']['totalValue']
    
    strategy = {
        'assetAllocation': {
            'current': {
                'US_stocks': round(current_allocation.get('美股账户', {}).get('value', 0) / total_value * 100),
                'HK_stocks': round(current_allocation.get('港股账户', {}).get('value', 0) / total_value * 100),
                'options': 10,  # 估算
                'cash': 7
            },
            'recommended': {
                'US_stocks': 55,
                'HK_stocks': 20,
                'options': 5,
                'cash': 20
            }
        },
        'riskLevel': 'medium-high',
        'suggestions': [
            '降低期权仓位至 5% 以下',
            '增加现金/债券配置到 20%',
            '考虑增加防御性股票比例'
        ]
    }
    
    return strategy
```

### Step 5: 输出策略建议
```python
def save_strategy(strategy):
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    output_file = f'/home/admin/openclaw/workspace/data/strategy_{timestamp}.json'
    
    with open(output_file, 'w') as f:
        json.dump(strategy, f, indent=2, ensure_ascii=False)
    
    return output_file
```

---

## ⏰ 触发条件

### 自动触发
- 收到持仓分析师的消息：`"分析完成：{file_path}"`
- 检测到新的分析数据文件生成

### 手动触发
用户消息包含：
- "给点建议"
- "该怎么操作"
- "要不要卖出"
- "推荐什么策略"

---

## ⚠️ 注意事项

### 1. 免责声明
**所有建议必须包含：**
> ⚠️ 以上建议仅供参考，不构成投资建议。投资有风险，决策需谨慎。

### 2. 避免绝对化
- ❌ "必须卖出"、"一定涨"
- ✅ "可以考虑"、"建议关注"、"可能"

### 3. 置信度标注
- `high`: 基于明确规则（如止损线）
- `medium`: 基于技术分析
- `low`: 基于主观判断

### 4. 风险提示
- 期权到期风险
- 杠杆 ETF 风险
- 单一股票集中风险
- 汇率风险（港股）

---

## 📁 文件结构

```
/home/admin/openclaw/workspace/
├── data/
│   ├── analysis_YYYY-MM-DD_HH-mm.json     # 输入：分析数据
│   └── strategy_YYYY-MM-DD_HH-mm.json     # 输出：策略建议
├── skills/
│   └── strategy-advisor/
│       └── SKILL.md                    # 本文件
└── scripts/
    └── generate_strategy.py            # 执行脚本（可选）
```

---

## 🧪 测试命令

### 手动测试
```bash
cd /home/admin/openclaw/workspace
python scripts/generate_strategy.py
```

### 验证输出
```bash
cat data/strategy_*.json | jq '.recommendations[0]'
cat data/strategy_*.json | jq '.portfolioStrategy'
```

---

## 🔄 传递给下一个 Agent

策略生成完成后，触发报告撰写员：

```python
# 触发报告撰写员
sessions_send(
    sessionKey="report-writer",
    message=f"策略完成：{strategy_file}"
)
```

---

**下一步：** 创建报告撰写员 SKILL.md
