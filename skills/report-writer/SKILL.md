---
name: report-writer
description: 股票投资团队 - 报告撰写员。将数据整合成易读的 Markdown 报告。
license: Proprietary
version: 1.0.0
---

# ✍️ 报告撰写员 (ReportWriter)

股票投资团队的第四个角色，负责生成格式化的投资分析报告。

---

## 🎯 职责

1. 读取市场数据、分析数据、策略建议
2. 整合所有信息成结构化报告
3. 使用专业但易懂的语言
4. 添加 emoji 和格式美化
5. 输出 Markdown 格式报告
6. 保存报告到本地并传递给推送员

---

## 📥 输入

### 输入 1: 市场数据
```
/home/admin/openclaw/workspace/data/market_data_YYYY-MM-DD_HH-mm.json
```

### 输入 2: 分析数据
```
/home/admin/openclaw/workspace/data/analysis_YYYY-MM-DD_HH-mm.json
```

### 输入 3: 策略建议
```
/home/admin/openclaw/workspace/data/strategy_YYYY-MM-DD_HH-mm.json
```

---

## 📤 输出

### 输出文件格式（Markdown）

```markdown
# 📊 锋哥持仓日报

**报告时间：** 2026-03-18 09:15  
**数据截止：** 2026-03-18 09:00  

---

## 🌅 早安寄语

新的一天，市场继续波动。今日重点关注美联储讲话和科技股财报...

---

## 📈 总览

| 指标 | 数值 | 变化 |
|------|------|------|
| 总资产 | $1,879,000 | +$15,230 (+0.82%) |
| 总盈亏 | +$222,907 | +13.5% |
| 今日盈亏 | +$15,230 | +0.82% |

**账户分布：**
- 🇺🇸 美股账户：$1,104,000 (-$5,200)
- 🇭🇰 港股账户：$440,000 (+$18,500)
- 💰 保证金账户：$335,000 (+$1,930)

---

## 🏆 今日亮点

### 涨得最好的 TOP3
1. **中海油 (00883)** +$2,800 (+2.8%) 🛢️
   - 油价上涨，能源股受益
   
2. **腾讯认购证 (260528)** +$700 (+5.2%) 📈
   - 腾讯反弹，权证大涨
   
3. **伯克希尔 (BRK.B)** +$500 (+0.5%) 💼
   - 价值股稳健

### 跌得最多的 TOP3
1. **微软 (MSFT)** -$1,300 (-2.1%) 💻
   - 科技股调整
   
2. **南方日经 (03153)** -$1,600 (-1.2%) 🇯🇵
   - 日元走弱
   
3. **腾讯控股 (00700)** -$5,100 (-0.9%) 🐧
   - 港股整体回调

---

## ⚠️ 风险提醒

### 🔴 紧急关注
1. **AAPL CALL 285** - 期权亏损 60%，剩余 58 天到期
   - 建议：立即止损，回收残值$768

2. **NVDA CALL 220** - 期权亏损 37%，剩余 58 天到期
   - 建议：立即止损，回收残值$815

### 🟡 需要留意
1. **微软 (MSFT)** - 亏损 13.8%，跌破支撑位
   - 建议：考虑减仓 50%

---

## 💡 操作建议

### 今日必做（优先级🔴）
- [ ] 止损 AAPL CALL 285
- [ ] 止损 NVDA CALL 220

### 本周执行（优先级🟡）
- [ ] 微软减仓 50%，换到 GOOGL
- [ ] 关注阿里 Short Put 到期管理

### 本月考虑（优先级🟢）
- [ ] 中海油止盈 50%，锁定利润
- [ ] 南方两倍做多止盈 50%
- [ ] 阿里反弹到 140+ 减仓 30%

### 长期配置（优先级🔵）
- [ ] 继续持有 BRK.B、KO
- [ ] 考虑增加 20% 债券/现金配置

---

## 📰 市场新闻

1. **美联储暗示...** - 彭博 08:30
2. **腾讯发布新...** - 路透 09:15
3. **油价继续上涨...** -  CNBC 09:30

---

## 📅 重要日期

| 日期 | 事件 |
|------|------|
| 2026-05-15 | AAPL/NVDA 期权到期 |
| 2026-06-18 | GOOGL 期权到期 |
| 2026-03-20 | 美联储议息会议 |

---

## 🎯 组合策略建议

**当前配置：**
- 美股 60% | 港股 23% | 期权 10% | 现金 7%

**建议配置：**
- 美股 55% | 港股 20% | 期权 5% | 现金 20%

**风险提示：**
> ⚠️ 以上建议仅供参考，不构成投资建议。投资有风险，决策需谨慎。

---

*报告由 OpenClaw 炒股 Agent 团队自动生成*
```

### 输出文件路径
```
/home/admin/openclaw/workspace/reports/持仓日报_YYYY-MM-DD_HH-mm.md
```

---

## 🛠️ 使用工具

### 1. read
读取所有输入数据文件

### 2. write
保存 Markdown 报告

### 3. exec (Python)
数据整合和模板渲染

```python
import json
from datetime import datetime
from jinja2 import Template

# 读取所有输入
def load_data():
    with open(market_file) as f:
        market = json.load(f)
    with open(analysis_file) as f:
        analysis = json.load(f)
    with open(strategy_file) as f:
        strategy = json.load(f)
    return market, analysis, strategy

# 渲染模板
def render_report(market, analysis, strategy):
    template = Template(REPORT_TEMPLATE)
    
    return template.render(
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M'),
        summary=analysis['summary'],
        byAccount=analysis['byAccount'],
        topGainers=analysis['topGainers'],
        topLosers=analysis['topLosers'],
        alerts=analysis['alerts'],
        recommendations=strategy['recommendations'],
        portfolioStrategy=strategy['portfolioStrategy'],
        news=market['news'][:5]
    )
```

---

## ⚙️ 工作流程

### Step 1: 读取所有输入
```python
def load_all_data():
    # 获取最新的数据文件
    market_file = get_latest_file('data/market_data_*.json')
    analysis_file = get_latest_file('data/analysis_*.json')
    strategy_file = get_latest_file('data/strategy_*.json')
    
    with open(market_file, 'r', encoding='utf-8') as f:
        market = json.load(f)
    with open(analysis_file, 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    with open(strategy_file, 'r', encoding='utf-8') as f:
        strategy = json.load(f)
    
    return market, analysis, strategy
```

### Step 2: 定义报告模板
```python
REPORT_TEMPLATE = """
# 📊 锋哥持仓日报

**报告时间：** {{ timestamp }}

---

## 🌅 早安寄语

新的一天，市场继续波动。保持冷静，按计划执行...

---

## 📈 总览

| 指标 | 数值 | 变化 |
|------|------|------|
| 总资产 | ${{ "%.0f"|format(summary.totalValue) }} | +${{ "%.0f"|format(summary.dayChange) }} ({{ "%.2f"|format(summary.dayChangePercent) }}%) |
| 总盈亏 | +${{ "%.0f"|format(summary.totalGain) }} | {{ "%.1f"|format(summary.totalGainPercent) }}% |

**账户分布：**
{% for account, data in byAccount.items() %}
- {{ account }}: ${{ "%.0f"|format(data.value) }} (${{ "%+.0f"|format(data.dayChange) }})
{% endfor %}

---

## 🏆 今日亮点

### 涨得最好的 TOP3
{% for item in topGainers[:3] %}
{{ loop.index }}. **{{ item.name }} ({{ item.code }})** +{{ "%.1f"|format(item.gainPercent) }}% 
   - {{ item.reason | default('表现强势') }}
{% endfor %}

### 跌得最多的 TOP3
{% for item in topLosers[:3] %}
{{ loop.index }}. **{{ item.name }} ({{ item.code }})** {{ "%.1f"|format(item.lossPercent) }}%
   - {{ item.reason | default('表现弱势') }}
{% endfor %}

---

## ⚠️ 风险提醒

{% for alert in alerts %}
### {{ alert.level }} {{ alert.type }}
{{ alert.message }}
{% endfor %}

---

## 💡 操作建议

{% for rec in recommendations[:7] %}
### {{ rec.priority }} {{ rec.action }} - {{ rec.target }}
- 理由：{{ rec.reason }}
- 建议：{{ rec.suggestion }}
{% endfor %}

---

## 📰 市场新闻

{% for news_item in news %}
{{ loop.index }}. **{{ news_item.title }}** - {{ news_item.source }} {{ news_item.time }}
{% endfor %}

---

## 🎯 组合策略建议

**当前配置：**
- 美股 {{ portfolioStrategy.assetAllocation.current.US_stocks }}%
- 港股 {{ portfolioStrategy.assetAllocation.current.HK_stocks }}%
- 期权 {{ portfolioStrategy.assetAllocation.current.options }}%
- 现金 {{ portfolioStrategy.assetAllocation.current.cash }}%

**建议配置：**
- 美股 {{ portfolioStrategy.assetAllocation.recommended.US_stocks }}%
- 港股 {{ portfolioStrategy.assetAllocation.recommended.HK_stocks }}%
- 期权 {{ portfolioStrategy.assetAllocation.recommended.options }}%
- 现金 {{ portfolioStrategy.assetAllocation.recommended.cash }}%

---

> ⚠️ 以上建议仅供参考，不构成投资建议。投资有风险，决策需谨慎。

*报告由 OpenClaw 炒股 Agent 团队自动生成*
"""
```

### Step 3: 生成报告
```python
def generate_report(market, analysis, strategy):
    template = Template(REPORT_TEMPLATE)
    
    report = template.render(
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M'),
        summary=analysis['summary'],
        byAccount=analysis['byAccount'],
        topGainers=analysis['topGainers'],
        topLosers=analysis['topLosers'],
        alerts=analysis['alerts'],
        recommendations=strategy['recommendations'],
        portfolioStrategy=strategy['portfolioStrategy'],
        news=market.get('news', [])
    )
    
    return report
```

### Step 4: 保存报告
```python
def save_report(report):
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    output_file = f'/home/admin/openclaw/workspace/reports/持仓日报_{timestamp}.md'
    
    # 创建目录
    os.makedirs('/home/admin/openclaw/workspace/reports', exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return output_file
```

---

## ⏰ 触发条件

### 自动触发
- 收到策略顾问的消息：`"策略完成：{file_path}"`
- 检测到所有输入文件就绪（market + analysis + strategy）

### 手动触发
用户消息包含：
- "生成报告"
- "写日报"
- "持仓报告"

---

## ⚠️ 注意事项

### 1. 报告长度
- 控制在 2000 字以内
- 重点信息前置
- 使用表格和列表提高可读性

### 2. 语气风格
- 专业但不枯燥
- 用 emoji 点缀（但不过度）
- 避免恐吓性语言

### 3. 数据一致性
- 确保所有数据来自同一时间点
- 金额单位统一（USD/HKD 标注清楚）

### 4. 免责声明
**每份报告必须包含：**
> ⚠️ 以上建议仅供参考，不构成投资建议。投资有风险，决策需谨慎。

---

## 📁 文件结构

```
/home/admin/openclaw/workspace/
├── data/
│   ├── market_data_*.json              # 输入：市场数据
│   ├── analysis_*.json                 # 输入：分析数据
│   └── strategy_*.json                 # 输入：策略建议
├── reports/
│   └── 持仓日报_YYYY-MM-DD_HH-mm.md    # 输出：Markdown 报告
├── skills/
│   └── report-writer/
│       └── SKILL.md                    # 本文件
└── scripts/
    └── generate_report.py              # 执行脚本（可选）
```

---

## 🧪 测试命令

### 手动测试
```bash
cd /home/admin/openclaw/workspace
python scripts/generate_report.py
```

### 预览报告
```bash
cat reports/持仓日报_*.md
```

---

## 🔄 传递给下一个 Agent

报告生成完成后，触发消息推送员：

```python
# 触发消息推送员
sessions_send(
    sessionKey="message-dispatcher",
    message=f"报告完成：{report_file}"
)
```

---

**下一步：** 创建消息推送员 SKILL.md
