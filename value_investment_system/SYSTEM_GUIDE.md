# 🎯 价值投资运行系统

> Value Investment Operating System (VIOS)

**统一整合 5 个投资技能 + 4 个独立模块的自动化工作流系统**

---

## 📊 系统概述

**价值投资运行系统**是一个完整的自动化投资平台，整合了：

- ✅ **5 个投资技能**: finance-data, buffett-investor, stock-monitor, finance-analysis, value-investing
- ✅ **4 个独立模块**: 选股策略、持仓分析、回测系统、价格预警
- ✅ **统一工作流**: 盘前/盘中/盘后自动化执行
- ✅ **智能通知**: 飞书实时推送

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│              价值投资运行系统 (VIOS)                      │
│           Value Investment Operating System             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🎯 用户接口层                                          │
│  ├─ 自然语言对话 (OpenClaw 技能)                        │
│  ├─ 命令行工具 (CLI)                                    │
│  └─ 定时任务 (Cron)                                     │
│                                                         │
│  🧠 智能编排层                                          │
│  └─ orchestrator.py (统一工作流编排器)                  │
│                                                         │
│  💼 业务技能层 (5 个)                                    │
│  ├─ finance-data       → 实时数据获取                  │
│  ├─ buffett-investor   → 巴菲特价值分析                │
│  ├─ stock-monitor      → 持仓监控预警                  │
│  ├─ finance-analysis   → 财务深度分析                  │
│  └─ value-investing    → 价值投资评估                  │
│                                                         │
│  ⚙️ 功能模块层 (4 个)                                    │
│  ├─ strategies/        → 选股 + 交易策略                │
│  ├─ backtest/          → 历史回测验证                  │
│  ├─ notify/            → 通知预警推送                  │
│  └─ data/              → 多源数据管理                  │
│                                                         │
│  📊 数据源层                                              │
│  ├─ 富途 OpenAPI (主力)                                 │
│  ├─ AKShare (备选)                                      │
│  └─ Tushare (可选)                                      │
│                                                         │
│  📱 通知输出层                                          │
│  └─ 飞书通知 (实时推送)                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 方式 1: 自动运行

```bash
cd /home/admin/openclaw/workspace

# 根据当前时间自动执行对应工作流
python3 value_investment_system/orchestrator.py
```

### 方式 2: 手动指定

```bash
# 盘前工作流 (09:00)
python3 value_investment_system/orchestrator.py --workflow pre_market

# 盘中工作流 (每 30 分钟)
python3 value_investment_system/orchestrator.py --workflow intra_day

# 盘后工作流 (16:30)
python3 value_investment_system/orchestrator.py --workflow post_market
```

### 方式 3: 对话调用

直接对 OpenClaw 说：
- "运行价值投资系统"
- "检查买入信号"
- "分析我的持仓"
- "查看盘后报告"

---

## 📊 工作流详情

### 🌅 盘前工作流 (交易日 09:00)

**执行内容:**
1. ✅ 检查产品规模预警
2. ✅ 检查持仓价格预警
3. ✅ 扫描巴菲特买入信号
4. ✅ 发送早间提醒通知

**触发通知:**
- 🔴 产品规模紧急预警
- 🔔 价格突破预警
- 🎯 巴菲特买入信号

---

### 📈 盘中工作流 (交易日 09:30-16:00, 每 30 分钟)

**执行内容:**
1. ✅ 获取实时股价 (finance-data)
2. ✅ 计算巴菲特评分 (buffett-investor)
3. ✅ 评估投资价值 (value-investing)
4. ✅ 检查买入信号触发
5. ✅ 更新监控股票池

**触发通知:**
- 🎯 强力买入信号 (安全边际≥30% + 评分≥80)
- 📈 价格突破预警
- 📉 超卖信号 (单日跌幅>5%)

---

### 📊 盘后工作流 (交易日 16:30)

**执行内容:**
1. ✅ 分析持仓盈亏 (strategies)
2. ✅ 深度财务分析 (finance-analysis)
3. ✅ 生成交易信号
4. ✅ 生成盘后报告
5. ✅ 发送飞书总结

**输出内容:**
- 📊 持仓盈亏汇总
- 📈 个股表现分析
- 💡 投资建议

---

## ⚙️ 系统配置

### 定时任务配置

已配置到 crontab，下周一自动开始：

```bash
# 价值投资运行系统 - 定时任务

# 盘前工作流 (09:00)
0 9 * * 1-5 cd /home/admin/openclaw/workspace && \
  python3 value_investment_system/orchestrator.py --workflow pre_market

# 盘中工作流 (每 30 分钟)
*/30 9-15 * * 1-5 cd /home/admin/openclaw/workspace && \
  python3 value_investment_system/orchestrator.py --workflow intra_day

# 盘后工作流 (16:30)
30 16 * * 1-5 cd /home/admin/openclaw/workspace && \
  python3 value_investment_system/orchestrator.py --workflow post_market

# 心跳检查 (每 4 小时)
0 */4 * * * cd /home/admin/openclaw/workspace && \
  python3 value_investment_system/orchestrator.py --workflow heartbeat
```

### 系统状态文件

```bash
# 查看系统状态
cat value_investment_system/state.json

# 系统状态包含:
{
  "last_run": "最后运行时间",
  "last_screen": "最后筛选时间",
  "watchlist": "监控股票池",
  "portfolio": "持仓列表",
  "alerts": "预警历史"
}
```

---

## 📁 系统文件结构

```
value_investment_system/          # 价值投资运行系统
├── orchestrator.py               # 统一工作流编排器
├── state.json                    # 系统状态文件
├── SYSTEM_GUIDE.md               # 系统使用指南 (本文档)
└── logs/                         # 日志目录

skills/                           # 投资技能 (5 个)
├── finance-data/
├── buffett-investor/
├── stock-monitor/
├── finance-analysis/
└── value-investing/

modules/                          # 功能模块 (4 个)
├── strategies/                   # 选股策略 + 交易策略
├── backtest/                     # 历史回测
├── notify/                       # 通知预警
└── data/                         # 数据源管理

config/                           # 配置文件
├── buffett_crontab.txt          # 定时任务配置
└── feishu_config.json           # 飞书通知配置
```

---

## 🎯 核心功能

### 1. 智能选股

**筛选标准:**
- ✅ 市值 ≥ 50 亿
- ✅ 连续 5 年股息率 ≥ 5%
- ✅ 连续 5 年 ROE ≥ 10%
- ✅ 连续 5 年 ROIC ≥ 10%
- ✅ 非 ST 股票

**执行命令:**
```bash
python3 data/stock_screener.py --scan
```

---

### 2. 巴菲特分析

**分析内容:**
- ✅ 内在价值计算 (DCF 模型)
- ✅ 安全边际评估
- ✅ 巴菲特综合评分
- ✅ 护城河分析
- ✅ 投资建议生成

**执行命令:**
```bash
python3 strategies/buffett_analyzer.py
```

---

### 3. 实时预警

**预警类型:**
- 🔔 价格突破预警
- 🎯 巴菲特买入信号
- 📉 超卖信号
- 🔴 规模预警

**通知方式:**
- 飞书实时推送
- 冷却机制 (避免重复)

---

### 4. 历史回测

**回测内容:**
- ✅ 策略历史表现
- ✅ 收益指标分析
- ✅ 风险评估
- ✅ 夏普比率计算

**执行命令:**
```bash
python3 backtest/backtester.py --code HK.00700
```

---

## 📊 监控和日志

### 查看系统状态

```bash
# 查看运行状态
cat value_investment_system/state.json

# 查看定时任务
crontab -l | grep "value_investment"
```

### 查看日志

```bash
# 系统主日志
tail -f /tmp/buffett_system/orchestrator.log

# 所有日志
tail -f /tmp/buffett_system/*.log

# 实时日志监控
watch -n 1 'tail -20 /tmp/buffett_system/orchestrator.log'
```

### 日志位置

```
/tmp/buffett_system/
├── orchestrator.log       # 系统主日志
├── pre_market.log         # 盘前工作流
├── intra_day.log          # 盘中工作流
├── post_market.log        # 盘后工作流
├── buy_signals.log        # 买入信号
└── heartbeat.log          # 心跳检查
```

---

## 🎯 使用场景

### 场景 1: 盘前准备

**时间:** 交易日 09:00

**系统自动执行:**
```
1. 检查产品规模 → 发现前锋 8 号/6 号预警
2. 检查价格预警 → 无触发
3. 检查买入信号 → 发现中海油买入信号
4. 发送飞书通知 → 盘前提醒
```

---

### 场景 2: 盘中监控

**时间:** 交易日 10:30

**系统自动执行:**
```
1. 获取腾讯实时股价 → 508 港元
2. 计算巴菲特评分 → 86 分
3. 评估安全边际 → +2.1%
4. 未触发买入条件 → 继续观望
5. 更新监控股票池
```

---

### 场景 3: 买入信号触发

**时间:** 交易日 14:00

**系统自动执行:**
```
1. 监测到中海油股价下跌 → 28 港元
2. 计算安全边际 → 70% (≥30% ✅)
3. 巴菲特评分 → 99 分 (≥80 ✅)
4. 触发强力买入信号
5. 立即发送飞书通知
```

**通知内容:**
```
🎯 强力买入 - 中国海洋石油

当前价格：28.00 港元
内在价值：93.46 港元
安全边际：+70.0%
巴菲特评分：99/100
建议仓位：40%
```

---

### 场景 4: 盘后总结

**时间:** 交易日 16:30

**系统自动执行:**
```
1. 分析持仓盈亏 → 腾讯 -13%, 中海油 +46%
2. 生成交易信号 → 持有/买入/卖出建议
3. 生成盘后报告
4. 发送飞书总结
```

---

## ⚠️ 注意事项

### 1. 系统依赖

- ✅ Python 3.10+
- ✅ 富途 OpenD (已安装)
- ✅ cron 服务 (已配置)
- ✅ 网络连接

### 2. 数据源

- **主力:** 富途 OpenAPI
- **备选:** AKShare
- **可选:** Tushare

### 3. 通知配置

- 飞书通知已配置
- 接收人：锋哥 (ou_52fa8f508e88e1efbcbe50c014ecaa6e)

---

## 📞 系统维护

### 更新股票池

```bash
# 每周日运行筛选器
python3 data/stock_screener.py --scan
```

### 查看系统健康

```bash
# 检查 cron 状态
systemctl status cron

# 检查 OpenD 状态
pgrep -f "Futu_OpenD"

# 检查日志
tail -100 /tmp/buffett_system/orchestrator.log
```

### 系统重启

```bash
# 重新安装 crontab
cat value_investment_system/config/buffett_crontab.txt | crontab -

# 验证
crontab -l
```

---

## 📊 系统统计

### 监控范围

| 类别 | 数量 |
|------|------|
| 核心持仓 | 3 只 |
| 筛选股票池 | ~30-50 只 |
| 监控频率 | 每 30 分钟 |
| 通知渠道 | 飞书 |

### 工作负载

| 任务 | 频率 | 执行时间 |
|------|------|---------|
| 盘前检查 | 每日 1 次 | ~3 秒 |
| 盘中监控 | 每 30 分钟 | ~5 秒 |
| 盘后分析 | 每日 1 次 | ~10 秒 |
| 心跳检查 | 每 4 小时 | ~2 秒 |

---

## 🎯 系统愿景

**价值投资运行系统**致力于：

1. **自动化** - 减少人工干预，自动执行监控
2. **智能化** - 基于巴菲特价值投资理念
3. **实时化** - 实时监控股价，及时通知
4. **系统化** - 统一整合所有投资工具
5. **可视化** - 完整日志，便于追踪分析

---

**系统名称:** 价值投资运行系统 (VIOS)  
**版本:** v1.0  
**创建时间:** 2026-03-21  
**状态:** ✅ 已部署，下周一自动运行

---

> "价格是你付出的，价值是你得到的。" —— 沃伦·巴菲特
