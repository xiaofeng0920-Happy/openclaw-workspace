# 📊 巴菲特价值投资系统 - 完整项目总览

> "以合理的价格买入优秀的公司，远胜于以优惠的价格买入平庸的公司。" —— 沃伦·巴菲特

---

## 🎯 项目概述

本系统将沃伦·巴菲特的投资哲学量化为可执行的算法策略，提供从选股、分析、回测到监控的完整解决方案。

### 核心功能

| 功能模块 | 状态 | 说明 |
|---------|------|------|
| 📊 真实财务数据 API | ✅ 完成 | 接入 AKShare/Tushare/Yahoo |
| 📈 回测系统 | ✅ 完成 | 历史回测 + 绩效分析 |
| 🔔 价格预警 | ✅ 完成 | 实时监控 + 飞书通知 |
| 📱 飞书集成 | ✅ 完成 | 消息推送 + 交互式卡片 |
| 🤖 自动化交易 | 🟡 部分完成 | 模拟交易可用 |
| 📊 可视化报表 | 🟡 部分完成 | 基础图表可用 |

---

## 📁 项目结构

```
workspace/
├── BUFFETT_SYSTEM.md          # 项目总览（本文档）
│
├── strategies/                 # 策略模块
│   ├── buffett_strategy.py    # 核心选股策略 (18KB)
│   ├── buffett_analyzer.py    # 持仓分析器 (10KB)
│   ├── buffett_trading.py     # 交易策略 (16KB)
│   ├── auto_trade.py          # 自动交易 (14KB)
│   ├── TRADING_STRATEGY.md    # 策略文档
│   └── README.md              # 快速入门
│
├── data/                       # 数据模块
│   ├── financial_data.py      # 财务数据接口 (~15KB)
│   └── README.md              # 数据文档
│
├── backtest/                   # 回测模块
│   ├── backtester.py          # 回测系统 (~20KB)
│   └── README.md              # 回测文档
│
├── notify/                     # 通知模块
│   ├── price_alert.py         # 价格预警 (14KB)
│   ├── feishu_notifier.py     # 飞书集成 (10KB)
│   ├── cron_config.py         # 定时任务 (4KB)
│   └── README.md              # 通知文档
│
└── memory/                     # 数据记录
    ├── 锋哥持仓_2026-03-16.md  # 持仓记录
    └── 产品管理规模_2026-03-18.md # 产品规模
```

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install akshare pandas numpy matplotlib

# 确保 OpenD 已启动
~/Desktop/Futu_OpenD_*/Futu_OpenD-GUI_*.AppImage
```

### 2. 分析持仓

```bash
cd /home/admin/openclaw/workspace

# 运行巴菲特分析
python3 strategies/buffett_analyzer.py
```

### 3. 回测策略

```bash
# 回测腾讯控股
python3 backtest/backtester.py --code HK.00700 \
  --start 2023-01-01 --end 2026-03-21
```

### 4. 设置预警

```bash
# 执行价格预警检查
python3 notify/price_alert.py --check

# 配置定时任务
python3 notify/cron_config.py --setup
```

---

## 📊 核心策略

### 巴菲特选股标准

| 指标 | 标准 | 权重 |
|------|------|------|
| ROE | > 15% 持续 5 年 | 25 分 |
| 盈利增长 | > 10% 年化 | 20 分 |
| 负债/权益 | < 0.5 | 15 分 |
| 护城河 | 评分 > 6/10 | 20 分 |
| 估值 (PE) | < 15 | 20 分 |

### 交易规则

**买入条件**:
- 安全边际 ≥ 30%
- 巴菲特评分 ≥ 70
- 目标仓位：20-40%

**卖出条件**:
- 价格 > 内在价值 30%
- 基本面恶化
- 发现更好机会

---

## 📈 当前持仓分析

### 总览 (2026-03-16)

| 账户 | 市值 | 盈亏率 | 状态 |
|------|------|--------|------|
| 美股 | $1,104,000 | -3.3% | 小亏 |
| 港股 | $440,000 | +8.3% | 盈利 ✅ |
| 保证金 | $335,000 | -0.09% | 持平 |
| **总计** | **$1,879,000** | **+13.5%** | **盈利 🎉** |

### 巴菲特评分

| 股票 | 评分 | 建议 | 安全边际 |
|------|------|------|---------|
| 中国海洋石油 | 99/100 | 🎯 强力买入 | +67.5% |
| 腾讯控股 | 86/100 | ⏸️ 持有 | +2.1% |
| 阿里巴巴 | 65/100 | ⏸️ 持有 | +6.2% |

---

## 🔔 预警配置

### 价格预警

| 股票 | 上涨预警 | 下跌预警 | 当前价 |
|------|---------|---------|--------|
| 腾讯控股 | 550.00 | 480.00 | 508.00 |
| 中海油 | 32.00 | 28.00 | 30.38 |
| 阿里巴巴 | 135.00 | 115.00 | 123.70 |

### 通知渠道

- ✅ 飞书（已配置）
- ⏳ 微信（待配置）
- ⏳ 邮件（待配置）

---

## 🕐 定时任务

### Cron 配置

```bash
# 编辑 crontab
crontab -e

# 添加任务
# 价格预警（每 5 分钟）
*/5 * * * * cd /home/admin/openclaw/workspace && python3 notify/price_alert.py --check

# 持仓监控（每 4 小时）
0 */4 * * * python3 -c "from notify.cron_config import monitor_portfolio; monitor_portfolio()"

# 产品规模检查（每日 09:00）
0 9 * * 1-5 python3 -c "from notify.cron_config import check_product_scale; check_product_scale()"

# 每日收盘分析（交易日 16:30）
30 16 * * 1-5 python3 -c "from notify.cron_config import daily_analysis; daily_analysis()"
```

---

## 📊 使用示例

### 示例 1：分析单只股票

```python
from strategies.buffett_strategy import BuffettStrategy
from data.financial_data import FinancialData

# 获取真实数据
fd = FinancialData(source='akshare')
data = fd.get_financials('00700.HK')

# 巴菲特分析
strategy = BuffettStrategy()
stock = strategy.analyze_stock(
    code='HK.00700',
    name='腾讯控股',
    market='HK',
    current_price=508.00,
    financial_data=data
)

print(f"评分：{stock.buffett_score}/100")
print(f"建议：{stock.recommendation}")
print(f"内在价值：{stock.fair_value:.2f}港元")
```

### 示例 2：回测

```python
from backtest.backtester import BuffettBacktester

backtester = BuffettBacktester()
result = backtester.run_backtest(
    code='HK.00700',
    start_date='2023-01-01',
    end_date='2026-03-21'
)

print(f"总收益：{result.total_return*100:.2f}%")
print(f"夏普比率：{result.sharpe_ratio:.2f}")
```

### 示例 3：设置预警

```python
from notify.price_alert import PriceAlertSystem

alert_system = PriceAlertSystem()
alert_system.run_check()
```

---

## 📚 文档导航

| 文档 | 说明 |
|------|------|
| [strategies/README.md](strategies/README.md) | 策略快速入门 |
| [strategies/TRADING_STRATEGY.md](strategies/TRADING_STRATEGY.md) | 交易策略详解 |
| [data/README.md](data/README.md) | 财务数据接口 |
| [backtest/README.md](backtest/README.md) | 回测系统 |
| [notify/README.md](notify/README.md) | 预警通知 |

---

## ⚠️ 风险提示

1. **本系统仅供参考**，不构成投资建议
2. **投资有风险**，入市需谨慎
3. **过往表现**不代表未来收益
4. **请独立研究**并咨询专业顾问

### 系统局限

- ⚠️ 财务数据为估算值（部分）
- ⚠️ DCF 模型对假设敏感
- ⚠️ 无法预测黑天鹅事件
- ⚠️ 需要长期持有才能体现价值

---

## 🎯 开发计划

### 已完成 ✅

1. ✅ 真实财务数据 API 接入
2. ✅ 回测功能
3. ✅ 价格预警推送
4. ✅ 飞书通知集成

### 待完成 ⏳

- [ ] 微信通知集成
- [ ] 邮件通知
- [ ] 更多估值模型（DDM、剩余收益）
- [ ] 自动调仓功能
- [ ] 完整回测报告
- [ ] 支持更多市场

---

## 🤝 贡献与反馈

欢迎提交 Issue 和 Pull Request！

---

## 📜 许可证

MIT License

---

## 📞 支持

- 问题反馈：查看日志文件 `/tmp/*.log`
- 配置修改：编辑对应配置文件
- 文档改进：欢迎贡献

---

> "我们喜欢的持有期是永远。" —— 沃伦·巴菲特

**最后更新**: 2026-03-21  
**版本**: v1.0  
**状态**: ✅ 核心功能已完成
