# 🔄 投资系统 - 完整工作流整合

> 5 个投资技能 + 4 个独立模块 = 统一自动化工作流

---

## 📊 整合架构

```
┌─────────────────────────────────────────────────────────┐
│           投资系统 - 统一工作流编排器                     │
│                   (orchestrator.py)                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📊 技能层 (5 个)                                        │
│  ├─ finance-data       → 实时数据获取                  │
│  ├─ buffett-investor   → 巴菲特分析                    │
│  ├─ stock-monitor      → 持仓监控                      │
│  ├─ finance-analysis   → 深度分析                      │
│  └─ value-investing    → 价值投资                      │
│                                                         │
│  ⚙️ 模块层 (4 个)                                        │
│  ├─ strategies/        → 选股策略 + 交易策略            │
│  ├─ backtest/          → 历史回测                      │
│  ├─ notify/            → 通知预警                      │
│  └─ data/              → 数据源管理                    │
│                                                         │
│  🎯 工作流层                                              │
│  ├─ 盘前工作流 (09:00)                                  │
│  ├─ 盘中工作流 (每 30 分钟)                               │
│  └─ 盘后工作流 (16:30)                                  │
│                                                         │
│  📱 通知层                                                │
│  └─ 飞书通知 (统一出口)                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 完整工作流示例

### 盘前工作流 (09:00)

```
1. 检查产品规模 (memory/)
   ↓
2. 调用 stock-monitor 检查价格预警
   ↓
3. 调用 notify 模块检查买入信号
   ↓
4. 触发条件 → 发送飞书通知
   ↓
5. 记录日志 → 保存状态
```

### 盘中工作流 (每 30 分钟)

```
1. 调用 finance-data 获取实时股价
   ↓
2. 调用 buffett-investor 计算安全评分
   ↓
3. 检查是否触发买入条件
   ↓
4. 触发 → 调用 notify 发送飞书
   ↓
5. 更新 watchlist 状态
```

### 盘后工作流 (16:30)

```
1. 调用 strategies 分析持仓
   ↓
2. 调用 finance-analysis 深度分析
   ↓
3. 生成交易信号
   ↓
4. 生成盘后报告
   ↓
5. 调用 notify 发送飞书报告
```

---

## 🚀 使用方式

### 方式 1: 自动运行

```bash
# 根据当前时间自动选择工作流
python3 workflow/orchestrator.py
```

### 方式 2: 手动指定

```bash
# 盘前工作流
python3 workflow/orchestrator.py --workflow pre_market

# 盘中工作流
python3 workflow/orchestrator.py --workflow intra_day

# 盘后工作流
python3 workflow/orchestrator.py --workflow post_market
```

### 方式 3: 定时任务

已配置到 crontab:
```bash
# 盘前
0 9 * * 1-5 python3 workflow/orchestrator.py --workflow pre_market

# 盘中
*/30 9-15 * * 1-5 python3 workflow/orchestrator.py --workflow intra_day

# 盘后
30 16 * * 1-5 python3 workflow/orchestrator.py --workflow post_market
```

---

## 📊 数据流整合

### 统一数据流

```
finance-data (获取数据)
    ↓
buffett-investor (分析估值)
    ↓
value-investing (评估价值)
    ↓
strategies (生成信号)
    ↓
notify (发送通知)
```

### 状态管理

```
state.json (统一状态存储)
├── last_run: 最后运行时间
├── last_screen: 最后筛选时间
├── watchlist: 监控股票池
├── portfolio: 持仓列表
└── alerts: 预警历史
```

---

## ✅ 整合效果

### Before (分散)

```
用户 → 单独调用技能
     → 单独运行模块
     → 手动整合结果
     → 手动发送通知
```

### After (整合)

```
用户 → 触发工作流
     → 自动调用所有技能
     → 自动整合结果
     → 自动发送通知
```

---

## 🎯 核心优势

| 优势 | 说明 |
|------|------|
| **统一入口** | 一个命令运行所有功能 |
| **自动调度** | 根据时间自动选择工作流 |
| **数据共享** | 统一状态管理，避免重复计算 |
| **智能决策** | 多层分析，综合判断 |
| **集中通知** | 统一飞书通知出口 |
| **完整日志** | 集中日志记录，便于追踪 |

---

## 📁 文件结构

```
workflow/
├── orchestrator.py          # 统一编排器 (新增)
├── WORKFLOW_INTEGRATION.md  # 整合文档 (新增)
└── state.json               # 状态文件 (自动生成)

skills/
├── finance-data/
├── buffett-investor/
├── stock-monitor/
├── finance-analysis/
└── value-investing/

modules/
├── strategies/
├── backtest/
├── notify/
└── data/
```

---

## 🔧 配置说明

### 工作流配置

编辑 `workflow/orchestrator.py`:

```python
class InvestmentWorkflowOrchestrator:
    # 工作时间配置
    PRE_MARKET_HOUR = 9      # 盘前时间
    POST_MARKET_HOUR = 16    # 盘后时间
    INTRA_DAY_INTERVAL = 30  # 盘中间隔 (分钟)
    
    # 通知配置
    FEISHU_TARGET = 'ou_52fa8f508e88e1efbcbe50c014ecaa6e'
```

### 状态文件

`workflow/state.json` 自动维护，无需手动编辑。

---

## 📊 监控和日志

### 查看日志

```bash
# 编排器日志
tail -f /tmp/buffett_system/orchestrator.log

# 所有日志
tail -f /tmp/buffett_system/*.log
```

### 查看状态

```bash
cat workflow/state.json
```

---

## 🎯 示例输出

```
============================================================
🌅 执行盘前工作流
============================================================
2026-03-24 09:00:00 - orchestrator - INFO - 步骤 1: 检查产品规模...
2026-03-24 09:00:01 - orchestrator - INFO - ✅ 产品规模检查完成
2026-03-24 09:00:01 - orchestrator - INFO - 步骤 2: 检查价格预警...
2026-03-24 09:00:02 - orchestrator - INFO - ✅ 价格预警检查完成
2026-03-24 09:00:02 - orchestrator - INFO - 步骤 3: 检查买入信号...
2026-03-24 09:00:03 - orchestrator - INFO - ✅ 发现 1 个买入信号
2026-03-24 09:00:03 - orchestrator - INFO - 📤 发送飞书通知...
2026-03-24 09:00:04 - orchestrator - INFO - ✅ 飞书通知发送成功
============================================================
✅ 盘前工作流完成
============================================================
```

---

**最后更新**: 2026-03-21  
**版本**: v1.0  
**状态**: ✅ 已完成整合
