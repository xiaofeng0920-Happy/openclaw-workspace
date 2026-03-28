# 投资分析 Workflow - 完整版

整合所有投资分析技能，创建自动化工作流。

---

## 📊 Workflow 流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    投资分析 Workflow                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  步骤 1: 数据采集                                                 │
│  └─ holding-analyzer/run.py                                     │
│     • 获取股价、期权数据                                         │
│     • 识别显著变化（>3%）                                        │
│                                                                 │
│  步骤 2: 持仓分析                                                 │
│  └─ holding-analyzer/analyzer.py                                │
│     • 对比基准计算盈亏                                           │
│     • 期权状态监控                                               │
│                                                                 │
│  步骤 3: 股票池 + 技术指标                                         │
│  └─ data-collector/technical_indicators.py                      │
│     • 股票池检查                                                 │
│     • MACD、RSI、KDJ、布林带                                     │
│     • 综合评分                                                   │
│                                                                 │
│  步骤 4: 炒股 Agent 团队     【新增】                              │
│  └─ investment-workflow/agent_team.py                           │
│     • 数据收集员 → 持仓分析师 → 策略顾问 → 报告撰写员             │
│     • 生成持仓日报                                               │
│                                                                 │
│  步骤 5: 综合报告生成                                              │
│  └─ workflow.py                                                 │
│     • 整合所有分析结果                                           │
│     • 生成 Markdown 报告                                          │
│                                                                 │
│  步骤 6: 飞书推送                                                  │
│  └─ OpenClaw CLI                                                │
│     • 自动发送到飞书                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 步骤详情

| 步骤 | 功能 | 脚本 | 输出 |
|------|------|------|------|
| 1. 数据采集 | 获取股价、期权、新闻 | holding-analyzer/run.py | reports/report_*.md |
| 2. 持仓分析 | 盈亏计算、预警 | holding-analyzer/analyzer.py | 同上 |
| 3. 股票池 + 技术指标 | 股票池 + MACD/RSI/KDJ | technical_indicators.py | technical/*.csv |
| 4. 炒股 Agent 团队 | 数据→分析→策略→报告 | agent_team.py | reports/持仓日报_*.md |
| 5. 综合报告 | 整合所有结果 | workflow.py | workflow/workflow_report_*.md |
| 6. 飞书推送 | 发送通知 | workflow.py | 飞书消息 |

---

## ⏰ 定时任务

### 持仓监控（每日 3 次）

```cron
# 早盘 09:00
0 1 * * * cd /home/admin/openclaw/workspace/agents/holding-analyzer && python3 run.py --send >> /tmp/holding-analyzer.log 2>&1

# 午间 13:00
0 5 * * * cd /home/admin/openclaw/workspace/agents/holding-analyzer && python3 run.py --send >> /tmp/holding-analyzer.log 2>&1

# 晚间 19:00
0 11 * * * cd /home/admin/openclaw/workspace/agents/holding-analyzer && python3 run.py --send >> /tmp/holding-analyzer.log 2>&1
```

### 产品规模监控（交易日）

```cron
5 1 * * 1-5 cd /home/admin/openclaw/workspace/agents/holding-analyzer && python3 product_scale_monitor.py --send >> /tmp/holding-analyzer.log 2>&1
```

### Workflow 综合日报（每日 1 次）

```cron
0 12 * * * cd /home/admin/openclaw/workspace/agents/investment-workflow && python3 workflow.py full >> /tmp/investment-workflow.log 2>&1
```

---

## 🚀 使用方法

### 运行完整 Workflow

```bash
cd /home/admin/openclaw/workspace/agents/investment-workflow
python3 workflow.py full
```

### 仅运行炒股 Agent 团队

```bash
python3 agent_team.py
```

### 仅运行技术指标分析

```bash
cd ../data-collector
python3 technical_indicators.py
```

### 测试模式

```bash
python3 workflow.py test
```

---

## 📁 输出文件

### 持仓监控报告

- 路径：`agents/holding-analyzer/reports/report_*.md`
- 频率：每日 3 次
- 内容：股价变化、期权状态、新闻

### 技术指标报告

- 路径：`agents/data-collector/technical/technical_analysis_*.csv`
- 频率：每日 1 次（Workflow 内）
- 内容：MACD、RSI、KDJ、综合评分

### 持仓日报（Agent 团队）

- 路径：`reports/持仓日报_*.md`
- 频率：每日 1 次（Workflow 内）
- 内容：总览、TOP 涨跌、操作建议

### Workflow 综合报告

- 路径：`reports/workflow/workflow_report_*.md`
- 频率：每日 1 次
- 内容：整合所有分析结果

---

## 📊 输出示例

### 飞书推送消息

```markdown
## 📊 投资分析日报

**生成时间：** 2026-03-22 20:00

### ✅ 今日完成
- 持仓监控（3 次/日）
- 股票池检查 + 技术指标
- 炒股 Agent 团队分析
- 综合报告生成

详细报告：workflow_report_20260322_200000.md
```

### 持仓日报（摘要）

```markdown
# 📊 锋哥持仓日报

**报告时间：** 2026-03-22 20:00

## 📈 总览
| 指标 | 数值 |
|------|------|
| 总资产 | $1,879,000 |
| 总盈亏 | +$222,907 (+13.5%) |

## 🏆 今日亮点
### 表现最好的 TOP3
1. **中海油 (00883)** +43.4%
2. **腾讯认购证 (260528)** +180%
3. **伯克希尔 (BRK.B)** +11.3%

## 💡 操作建议
- 🟡 减仓 微软：考虑换股
- 🟢 止盈 中海油：止盈 30-50%
- 🔵 持有 可口可乐：继续持有
```

---

## 🔧 日志查看

```bash
# Workflow 日志
tail -f /tmp/investment-workflow.log

# 持仓监控日志
tail -f /tmp/holding-analyzer.log

# 查看最新报告
ls -lt reports/workflow/
cat reports/workflow/workflow_report_*.md | tail -50
```

---

## ✅ 特点总结

| 特点 | 说明 |
|------|------|
| **全本地执行** | 不调用大模型，零 API 费用 |
| **自动化** | Cron 定时执行，飞书自动推送 |
| **模块化** | 6 个步骤独立运行，Workflow 整合 |
| **完整覆盖** | 持仓监控 + 技术分析 + 基本面 + 策略建议 |
| **可扩展** | 轻松添加新步骤（如新闻情感分析） |

---

## 🎯 下一步优化

1. **Tushare Pro 集成** - 完整 ROIC 数据
2. **图表生成** - K 线图、指标图
3. **自动回测** - 验证技术指标有效性
4. **多账户支持** - 扩展到期权、期货

---

*最后更新：2026-03-22*
