# 投资分析 Workflow

整合现有技能，创建自动化投资分析流程。

## 📊 Workflow 流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  数据采集   │ ──→ │  持仓分析   │ ──→ │  报告生成   │
│  本地脚本   │     │  本地脚本   │     │  本地脚本   │
└─────────────┘     └─────────────┘     └─────────────┘
       ↓                   ↓                   ↓
  股价/财务数据        盈亏计算            Markdown 报告
  新闻/公告            风险预警              │
                                            ↓
                                     ┌─────────────┐
                                     │  飞书推送   │
                                     │  本地 CLI   │
                                     └─────────────┘
```

## 📋 步骤说明

| 步骤 | 功能 | 脚本 | 频率 |
|------|------|------|------|
| 1. 数据采集 | 获取股价、财务数据 | holding-analyzer/run.py | 3 次/日 |
| 2. 持仓分析 | 计算盈亏、预警 | holding-analyzer/analyzer.py | 3 次/日 |
| 3. 股票池 + 技术指标 | 股票池检查 + MACD/RSI/KDJ | data-collector/technical_indicators.py | 1 次/日 |
| 4. 报告生成 | 整合为 Markdown | workflow.py | 1 次/日 |
| 5. 飞书推送 | 发送给用户 | workflow.py | 1 次/日 |

## 🆕 新增功能

### 技术指标分析

| 指标 | 说明 | 信号 |
|------|------|------|
| **MACD** | 趋势指标 | 金叉/死叉 |
| **RSI** | 超买超卖 | >70 超买，<30 超卖 |
| **KDJ** | 随机指标 | >80 超买，<20 超卖 |
| **布林带** | 波动区间 | 上轨/下轨突破 |
| **综合评分** | -10~10 分 | ≥5 买入，≤-5 卖出 |

### 专业数据源（可选）

- **Tushare Pro** - ROIC、完整财务指标
- 设置：`python3 tushare_data.py setup`

## 🚀 使用方法

### 运行完整 Workflow

```bash
cd /home/admin/openclaw/workspace/agents/investment-workflow
python3 workflow.py full
```

### 测试模式

```bash
python3 workflow.py test
```

## ⏰ Cron 配置

### 每日执行（晚间生成日报）

```cron
# 投资分析 Workflow - 每日 20:00
0 12 * * * cd /home/admin/openclaw/workspace/agents/investment-workflow && python3 workflow.py full >> /tmp/investment-workflow.log 2>&1
```

### 持仓监控（保持现有配置）

```cron
# 早盘 09:00
0 1 * * * cd /home/admin/openclaw/workspace/agents/holding-analyzer && python3 run.py --send >> /tmp/holding-analyzer.log 2>&1

# 午间 13:00
0 5 * * * cd /home/admin/openclaw/workspace/agents/holding-analyzer && python3 run.py --send >> /tmp/holding-analyzer.log 2>&1

# 晚间 19:00
0 11 * * * cd /home/admin/openclaw/workspace/agents/holding-analyzer && python3 run.py --send >> /tmp/holding-analyzer.log 2>&1
```

## 📁 文件结构

```
/home/admin/openclaw/workspace/agents/
├── investment-workflow/       # 【新增】Workflow 整合
│   ├── workflow.py            # 主脚本
│   ├── README.md              # 说明文档
│   └── reports/               # 输出报告
│       └── workflow_report_*.md
│
├── holding-analyzer/          # 【现有】持仓监控
│   ├── run.py                 # 运行脚本
│   ├── analyzer.py            # 分析引擎
│   ├── product_scale_monitor.py  # 产品规模
│   └── reports/
│
└── data-collector/            # 【现有】数据采集
    ├── manual_stock_pool.md   # 股票池
    ├── stock_screener.py      # 筛选器
    ├── backtest.py            # 回测
    └── stock_pool/
```

## 📊 输出报告示例

```markdown
# 📊 投资分析日报

## 1️⃣ 持仓监控
### 显著变化
- 📉 腾讯控股 -6.30%
- 📈 南方两倍 +22.05%

## 2️⃣ 股票池
**高质量股票池：** 20+ 只
- A 股：8 只
- 港股：6 只
- 美股：9 只

## 3️⃣ 操作建议
1. 持仓监控 - 每日 3 次自动检查
2. 股票池 - 季度更新财务数据
3. 回测 - 年度回顾策略有效性
```

## ✅ 特点

- **全本地执行** - 不调用大模型，零 API 费用
- **自动化** - Cron 定时执行，飞书自动推送
- **模块化** - 各 Agent 独立运行，Workflow 整合
- **可扩展** - 轻松添加新步骤（如技术指标、新闻分析）

## 🔧 日志查看

```bash
# 查看 Workflow 日志
tail -f /tmp/investment-workflow.log

# 查看持仓监控日志
tail -f /tmp/holding-analyzer.log
```
