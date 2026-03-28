# 🎯 价值投资运行系统 (VIOS)

> Value Investment Operating System - 锋哥专属投资自动化系统

**创建时间:** 2026-03-21  
**系统版本:** v1.0  
**状态:** ✅ 已部署，下周一 (03-23) 开始自动运行

---

## 📊 系统概述

价值投资运行系统是一个完整的自动化投资平台，基于沃伦·巴菲特价值投资理念，整合了 5 个投资技能 + 4 个独立模块，实现从数据采集、分析、回测到监控的全流程自动化。

---

## 🏗️ 系统架构

### 技能层 (5 个 OpenClaw 技能)

1. **finance-data** - 财务数据查询
   - A/HK/美股股价查询
   - PE/PB/ROE 等财务指标
   - 市场新闻和宏观数据

2. **buffett-investor** - 巴菲特价值分析
   - 内在价值计算 (DCF 模型)
   - 安全边际评估
   - 巴菲特综合评分
   - 投资建议生成

3. **stock-monitor** - 持仓监控
   - 实时价格监控
   - 持仓盈亏计算
   - 价格突破预警

4. **finance-analysis** - 财务深度分析
   - 财务报表分析
   - 行业对比分析
   - 财务健康度评估

5. **value-investing** - 价值投资评估
   - 低估股票筛选
   - 投资风险评估
   - 长期价值判断

### 模块层 (4 个独立模块)

1. **strategies/** - 策略模块
   - buffett_strategy.py - 选股策略
   - buffett_analyzer.py - 持仓分析
   - buffett_trading.py - 交易策略
   - auto_trade.py - 自动交易

2. **backtest/** - 回测模块
   - backtester.py - 历史回测系统
   - 绩效分析、风险评估

3. **notify/** - 通知模块
   - price_alert.py - 价格预警
   - buy_signal_monitor.py - 买入信号监控
   - feishu_notifier.py - 飞书通知

4. **data/** - 数据模块
   - futu_data.py - 富途 OpenAPI 接口
   - financial_data.py - AKShare 数据接口
   - stock_screener.py - 股票筛选器

### 工作流层 (统一编排)

**orchestrator.py** - 统一工作流编排器

- 🌅 盘前工作流 (09:00)
- 📈 盘中工作流 (每 30 分钟)
- 📊 盘后工作流 (16:30)
- 💓 心跳检查 (每 4 小时)

---

## 📈 锋哥持仓监控池

### 核心持仓 (3 只)

| 股票 | 代码 | 持仓 | 成本价 | 现价 | 盈亏% | 状态 |
|------|------|------|--------|------|-------|------|
| 腾讯控股 | HK.00700 | 2,500 股 | 585.78 | 508.00 | -13.3% | ⏸️ 持有 |
| 中国海洋石油 | HK.00883 | 11,000 股 | 20.75 | 30.38 | +46.4% | 🎯 强力买入 |
| 阿里巴巴-W | HK.09988 | 5,800 股 | 143.27 | 123.70 | -13.7% | ⏸️ 持有 |

### 筛选股票池 (~30-50 只)

筛选标准:
- 市值 ≥ 50 亿
- 连续 5 年股息率 ≥ 5%
- 连续 5 年 ROE ≥ 10%
- 连续 5 年 ROIC ≥ 10%
- 非 ST 股票

---

## 🔔 买入信号条件

| 条件 | 阈值 | 优先级 |
|------|------|--------|
| 安全边际 | ≥ 30% | 🔴 高 |
| 巴菲特评分 | ≥ 80 分 | 🟡 中 |
| 跌破目标价 | ≤ 设定价 | 🔴 高 |
| 严重低估 | < 内在价值 70% | 🔴 高 |
| 超卖信号 | 单日跌幅>5% | 🟢 低 |

---

## ⏰ 自动化工作流

### 交易日时间表

| 时间 | 任务 | 说明 |
|------|------|------|
| **09:00** | 🌅 盘前检查 | 产品规模 + 价格预警 + 买入信号 |
| **09:30-16:00** | 📈 盘中监控 | 每 30 分钟检查，触发立即通知 |
| **16:30** | 📊 盘后分析 | 持仓报告 + 盈亏汇总 + 交易信号 |
| **每 4 小时** | 💓 心跳检查 | 系统状态监控 |

### 定时任务配置

```bash
# 盘前工作流
0 9 * * 1-5 python3 value_investment_system/orchestrator.py --workflow pre_market

# 盘中工作流
*/30 9-15 * * 1-5 python3 value_investment_system/orchestrator.py --workflow intra_day

# 盘后工作流
30 16 * * 1-5 python3 value_investment_system/orchestrator.py --workflow post_market
```

---

## 📱 通知配置

### 飞书通知

- **接收人:** 锋哥 (ou_52fa8f508e88e1efbcbe50c014ecaa6e)
- **通知类型:**
  - 🔴 产品规模紧急预警
  - 🔔 价格突破预警
  - 🎯 巴菲特买入信号
  - 📊 盘后总结报告

### 通知冷却

- 冷却时间：1 小时
- 避免重复通知

---

## 📊 数据源配置

| 数据源 | 用途 | 状态 |
|--------|------|------|
| **富途 OpenAPI** | 实时股价、财务数据 | ✅ 主力 |
| **AKShare** | 新闻、资金流、行业数据 | ✅ 备选 |
| **Tushare** | 分析师评级、专业财务 | ⏳ 可选 (需 token) |

---

## 📁 系统文件位置

```
/home/admin/openclaw/workspace/
├── value_investment_system/     # 价值投资运行系统
│   ├── orchestrator.py          # 统一编排器
│   ├── state.json               # 系统状态
│   └── SYSTEM_GUIDE.md          # 使用指南
│
├── strategies/                  # 策略模块
│   ├── buffett_strategy.py
│   ├── buffett_analyzer.py
│   ├── buffett_trading.py
│   └── auto_trade.py
│
├── backtest/                    # 回测模块
│   └── backtester.py
│
├── notify/                      # 通知模块
│   ├── price_alert.py
│   ├── buy_signal_monitor.py
│   └── feishu_notifier.py
│
├── data/                        # 数据模块
│   ├── futu_data.py
│   ├── financial_data.py
│   └── stock_screener.py
│
└── memory/                      # 记忆文件
    ├── 锋哥持仓_2026-03-16.md
    ├── 产品管理规模_2026-03-18.md
    └── 价值投资运行系统_VIOS.md (本文件)
```

---

## 🎯 使用方式

### 方式 1: 对话调用

直接对 AI 说:
- "运行价值投资系统"
- "检查买入信号"
- "分析腾讯控股"
- "查看我的持仓"
- "有没有巴菲特买入机会"

### 方式 2: 命令行

```bash
# 自动运行 (根据时间选择工作流)
python3 value_investment_system/orchestrator.py

# 指定工作流
python3 value_investment_system/orchestrator.py --workflow pre_market
python3 value_investment_system/orchestrator.py --workflow intra_day
python3 value_investment_system/orchestrator.py --workflow post_market

# 单独功能
python3 strategies/buffett_analyzer.py           # 持仓分析
python3 notify/buy_signal_monitor.py --check    # 买入信号检查
python3 data/stock_screener.py --scan           # 股票筛选
```

### 方式 3: 定时任务

已配置 crontab，自动执行

---

## 📊 日志管理

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

### 查看日志

```bash
# 实时查看
tail -f /tmp/buffett_system/orchestrator.log

# 查看最新 50 行
tail -n 50 /tmp/buffett_system/post_market.log
```

---

## ⚠️ 说明：公司债券产品

**前锋 6 号** 和 **前锋 8 号** 是公司的债券型产品，**不在价值投资运行系统监控范围内**。

### 债券信息 (独立管理)

| 产品 | 规模 (万元) | 低于 500 万天数 | 停止申购日 | 状态 |
|------|-----------|--------------|-----------|------|
| 前锋 8 号 | 224.64 | 11 天 | 2026-05-29 | 🔴 紧急 |
| 前锋 6 号 | 191.18 | 9 天 | 2026-06-02 | 🔴 紧急 |

**管理方式:** 独立于价值投资系统，需单独关注

---

### 价值投资系统监控范围

**系统仅监控:**
- ✅ 锋哥个人股票持仓 (腾讯/中海油/阿里等)
- ✅ 筛选的股票池 (A 股/港股/美股)
- ❌ 不包含公司债券产品

---

## 📅 重要日期

| 日期 | 事项 | 备注 |
|------|------|------|
| 2026-03-21 | 系统创建 | 价值投资运行系统上线 |
| 2026-03-23 | 首次运行 | 下周一开始自动监控 |
| 2026-03-16 | 持仓基准日 | 总市值$1.879M，+13.5% |

---

## 🎯 锋哥投资原则

1. **全球分散配置** - 美股、港股、A 股多元布局
2. **长期持有优质资产** - 腾讯、谷歌、伯克希尔等
3. **适度使用期权增强收益** - Covered Call 等策略
4. **定期复盘调仓** - 止损亏损期权，止盈大幅盈利
5. **关注行业趋势** - AI、机器人、存储芯片等

---

## 📞 系统维护

### 每周任务

```bash
# 周日 20:00 更新股票池
python3 data/stock_screener.py --scan
```

### 每月任务

```bash
# 每月第一个工作日 10:00
# 提醒用户上传最新管理规模 Excel
```

### 系统检查

```bash
# 检查 cron 状态
systemctl status cron

# 检查 OpenD 状态
pgrep -f "Futu_OpenD"

# 查看系统状态
cat value_investment_system/state.json
```

---

## 📖 相关文档

- `value_investment_system/SYSTEM_GUIDE.md` - 系统使用指南
- `BUFFETT_SYSTEM.md` - 巴菲特系统总览
- `HEARTBEAT.md` - 心跳检查配置
- `memory/锋哥持仓_2026-03-16.md` - 持仓基准

---

**系统名称:** 价值投资运行系统 (VIOS)  
**创建时间:** 2026-03-21  
**首次运行:** 2026-03-23 (周一)  
**维护者:** AI 助手  
**用户:** 锋哥 (赵小锋)
