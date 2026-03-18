# 🤖 炒股 Agent 团队

锋哥持仓自动分析系统 - 由 5 个专业 Agent 组成的投资分析团队

---

## 📋 团队组成

| 角色 | Agent 名称 | 职责 | 触发条件 |
|------|-----------|------|----------|
| 📡 数据收集员 | `data-collector` | 获取实时股价、大盘指数、市场新闻 | 定时/手动 |
| 📊 持仓分析师 | `portfolio-analyzer` | 计算盈亏、识别 TOP3 涨跌、生成警报 | 收到市场数据后 |
| 🧠 策略顾问 | `strategy-advisor` | 生成操作建议（买入/卖出/持有） | 收到分析数据后 |
| ✍️ 报告撰写员 | `report-writer` | 整合数据生成 Markdown 报告 | 收到策略建议后 |
| 📬 消息推送员 | `message-dispatcher` | 将报告推送到飞书 | 报告完成后 |

---

## 🔄 工作流程

```
定时触发器 (每天 9:00 / 13:00 / 21:00)
    │
    ▼
┌─────────────────────────────────┐
│  1️⃣ 数据收集员                  │
│  - 读取持仓文件                 │
│  - 查询实时股价                 │
│  - 获取市场新闻                 │
│  - 输出：market_data.json       │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  2️⃣ 持仓分析师                  │
│  - 对比股价 vs 成本             │
│  - 计算盈亏变化                 │
│  - 识别涨跌 TOP3                │
│  - 输出：analysis.json          │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  3️⃣ 策略顾问                    │
│  - 生成操作建议                 │
│  - 设置优先级                   │
│  - 输出：strategy.json          │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  4️⃣ 报告撰写员                  │
│  - 整合所有数据                 │
│  - 生成 Markdown 报告            │
│  - 输出：持仓日报.md            │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  5️⃣ 消息推送员                  │
│  - 推送到飞书                   │
│  - 保存发送记录                 │
│  - 输出：dispatch log           │
└─────────────────────────────────┘
```

---

## 📁 目录结构

```
/home/admin/openclaw/workspace/
├── skills/                          # Agent 技能目录
│   ├── README.md                    # 本文件
│   ├── data-collector/
│   │   └── SKILL.md                 # 数据收集员规范
│   ├── portfolio-analyzer/
│   │   └── SKILL.md                 # 持仓分析师规范
│   ├── strategy-advisor/
│   │   └── SKILL.md                 # 策略顾问规范
│   ├── report-writer/
│   │   └── SKILL.md                 # 报告撰写员规范
│   └── message-dispatcher/
│       └── SKILL.md                 # 消息推送员规范
│
├── scripts/
│   └── run_portfolio_agent.py       # 主执行脚本
│
├── memory/
│   └── 锋哥持仓_2026-03-16.md       # 持仓数据源
│
├── data/                            # 中间数据（自动生成）
│   ├── market_data_*.json           # 市场数据
│   ├── analysis_*.json              # 分析结果
│   └── strategy_*.json              # 策略建议
│
├── reports/                         # 报告输出（自动生成）
│   └── 持仓日报_*.md                # Markdown 报告
│
├── logs/                            # 日志（自动生成）
│   └── dispatch_*.jsonl             # 发送记录
│
└── config/
    └── dispatch_config.json         # 推送配置
```

---

## 🚀 使用方法

### 手动运行

```bash
cd /home/admin/openclaw/workspace
python3 scripts/run_portfolio_agent.py
```

### 定时运行（待配置）

```bash
# 添加到 crontab
0 9 * * * cd /home/admin/openclaw/workspace && python3 scripts/run_portfolio_agent.py
0 13 * * * cd /home/admin/openclaw/workspace && python3 scripts/run_portfolio_agent.py
0 21 * * * cd /home/admin/openclaw/workspace && python3 scripts/run_portfolio_agent.py
```

### 查看生成的报告

```bash
cat reports/持仓日报_*.md
```

### 查看发送记录

```bash
cat logs/dispatch_*.jsonl | jq .
```

---

## ⚙️ 配置说明

### 推送配置 (`config/dispatch_config.json`)

```json
{
  "channels": {
    "feishu": {
      "enabled": true,              // 是否启用飞书推送
      "target": "ou_xxx",           // 飞书用户 ID
      "name": "赵小锋"              // 用户名称
    }
  },
  "schedule": {
    "morning": "09:00",             // 早间报告时间
    "afternoon": "13:00",           // 午间报告时间
    "evening": "21:00"              // 晚间报告时间
  },
  "conditions": {
    "minDayChange": 1.0,            // 最小变化触发阈值（%）
    "sendEvenIfNoChange": true      // 无变化也发送
  }
}
```

---

## 📊 输出示例

### 市场数据 (`market_data.json`)

```json
{
  "timestamp": "2026-03-18T09:00:00+08:00",
  "stocks": {
    "US": [
      {"code": "GOOGL", "price": 302.28, "change": -0.03}
    ],
    "HK": [
      {"code": "00700", "price": 547.50, "change": -5.2}
    ]
  }
}
```

### 分析报告 (`analysis.json`)

```json
{
  "summary": {
    "totalValue": 1879000,
    "totalGain": 222907,
    "totalGainPercent": 13.5
  },
  "topGainers": [
    {"code": "00883", "name": "中海油", "gainPercent": 43.4}
  ],
  "topLosers": [
    {"code": "03153", "name": "南方日经", "gainPercent": -10.4}
  ]
}
```

### 策略建议 (`strategy.json`)

```json
{
  "recommendations": [
    {
      "priority": "🔴",
      "action": "止损",
      "target": "AAPL CALL 285",
      "reason": "期权亏损 60%，临近到期",
      "suggestion": "立即止损"
    }
  ]
}
```

---

## ⚠️ 注意事项

### 1. 免责声明
所有输出必须包含：
> ⚠️ 以上建议仅供参考，不构成投资建议。投资有风险，决策需谨慎。

### 2. 数据延迟
- 美股数据延迟 15 分钟
- 港股数据实时
- 不要在交易时间内完全依赖自动建议

### 3. API 限流
- finance-data 技能有速率限制
- 批量查询时串行执行
- 每次查询间隔至少 1 秒

### 4. 推送限制
- 飞书主动消息有限制
- 避免在休息时间发送（23:00-07:00）
- 同用户每天不超过 10 条

---

## 🔧 下一步优化

### 短期（1-2 周）
- [ ] 接入真实股价 API（finance-data 技能）
- [ ] 实现飞书推送（message 工具）
- [ ] 添加期权到期提醒
- [ ] 完善错误处理

### 中期（2-4 周）
- [ ] 添加技术指标分析
- [ ] 支持更多推送渠道（微信/Telegram）
- [ ] 实现回测功能
- [ ] 添加持仓变动追踪

### 长期（1-2 月）
- [ ] AI 智能调仓建议
- [ ] 风险预警系统
- [ ] 多用户支持
- [ ] Web 仪表盘

---

## 📞 问题反馈

如有问题或建议，请联系：
- 飞书：赵小锋
- 工作空间：`/home/admin/openclaw/workspace`

---

*最后更新：2026-03-18*
*版本：v1.0.0*
