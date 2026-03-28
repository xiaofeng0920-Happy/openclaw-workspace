# 投资分析系统 - 总览

**锋哥的投资分析系统** - 全本地执行，零大模型调用

---

## 📊 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     投资分析系统                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ 持仓监控     │    │ 数据采集     │    │ Workflow     │      │
│  │ Agent        │    │ Agent        │    │ 整合         │      │
│  │              │    │              │    │              │      │
│  │ • 股价监控   │    │ • 股票筛选   │    │ • 数据采集   │      │
│  │ • 期权监控   │    │ • 回测       │    │ • 持仓分析   │      │
│  │ • 产品规模   │    │ • 股票池     │    │ • 报告生成   │      │
│  │ • 新闻推送   │    │              │    │ • 飞书推送   │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│           ↓                   ↓                   ↓             │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                    本地脚本执行                         │    │
│  │              akshare + Python + OpenClaw CLI           │    │
│  └────────────────────────────────────────────────────────┘    │
│                              ↓                                  │
│                    ┌──────────────┐                            │
│                    │   飞书推送   │                            │
│                    └──────────────┘                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 文件结构

```
/home/admin/openclaw/workspace/
├── agents/
│   ├── holding-analyzer/          # 持仓监控 Agent
│   │   ├── run.py                 # 运行脚本（含推送）
│   │   ├── analyzer.py            # 核心分析引擎
│   │   ├── product_scale_monitor.py  # 产品规模监控
│   │   ├── reports/               # 持仓报告
│   │   └── README.md
│   │
│   ├── data-collector/            # 数据采集 Agent
│   │   ├── manual_stock_pool.md   # 高质量股票池（20+ 只）
│   │   ├── stock_screener.py      # 股票筛选器
│   │   ├── backtest.py            # 回测脚本
│   │   ├── CONFIG.md              # 配置说明
│   │   └── README.md
│   │
│   └── investment-workflow/       # Workflow 整合【新增】
│       ├── workflow.py            # 主脚本
│       ├── README.md
│       └── reports/               # 综合报告
│
├── memory/
│   ├── 锋哥持仓_2026-03-16.md     # 持仓基准
│   └── 产品管理规模_2026-03-18.md # 产品规模
│
└── HEARTBEAT.md                   # 任务配置
```

---

## ⏰ 定时任务

| 时间 | 任务 | 脚本 | 内容 |
|------|------|------|------|
| **09:00** | 持仓监控 | run.py --send | 股价、期权、新闻 |
| **09:05** | 产品规模 | product_scale_monitor.py | 预警<500 万产品 |
| **13:00** | 持仓监控 | run.py --send | 股价、期权、新闻 |
| **19:00** | 持仓监控 | run.py --send | 股价、期权、新闻 |
| **20:00** | Workflow | workflow.py full | 综合日报 |

---

## 📊 数据流

```
 akshare API
     ↓
┌─────────────┐
│ 股价/财务数据 │
└─────────────┘
     ↓
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  持仓分析   │ ──→ │  报告生成   │ ──→ │  飞书推送   │
│  (盈亏计算)  │     │  (Markdown)  │     │  (CLI)     │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## ✅ 特点

| 特点 | 说明 |
|------|------|
| **全本地** | 不调用大模型，零 API 费用 |
| **自动化** | Cron 定时执行，飞书自动推送 |
| **模块化** | 3 个 Agent 独立运行，Workflow 整合 |
| **可扩展** | 轻松添加新步骤 |
| **低延迟** | <5 秒完成单次检查 |

---

## 🔧 管理命令

### 手动运行

```bash
# 持仓监控
cd /home/admin/openclaw/workspace/agents/holding-analyzer
python3 run.py --send

# 产品规模
python3 product_scale_monitor.py --send

# Workflow
cd /home/admin/openclaw/workspace/agents/investment-workflow
python3 workflow.py full
```

### 查看日志

```bash
# 持仓监控日志
tail -f /tmp/holding-analyzer.log

# Workflow 日志
tail -f /tmp/investment-workflow.log
```

### 管理 Cron

```bash
# 查看任务
crontab -l

# 编辑任务
crontab -e

# 删除所有任务
crontab -r
```

---

## 📈 输出报告

### 持仓监控报告

- 位置：`agents/holding-analyzer/reports/report_*.md`
- 内容：股价变化、期权状态、新闻

### 综合日报

- 位置：`reports/workflow/workflow_report_*.md`
- 内容：持仓概览、股票池、操作建议

---

## 🎯 下一步优化

1. **技术指标** - 添加 MACD、RSI 等
2. **新闻情感分析** - 自动分析新闻正面/负面
3. **自动调仓建议** - 基于规则生成买卖建议
4. **专业数据源** - 接入 Wind/Tushare Pro

---

*最后更新：2026-03-22*
