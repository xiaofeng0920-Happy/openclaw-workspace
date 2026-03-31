# buffett-investor - 巴菲特价值投资技能

## 描述

基于沃伦·巴菲特投资哲学的量化选股和交易系统。提供选股分析、估值计算、回测验证、价格预警等完整功能。

## 触发条件

当用户提到以下内容时激活此技能：
- "巴菲特选股"
- "价值投资"
- "股票分析"
- "持仓分析"
- "内在价值"
- "安全边际"
- "ROE 分析"
- "股票回测"
- "价格预警"
- "锋哥持仓"

## 命令

### /buffett-analyze [股票代码]
分析单只股票的巴菲特评分、内在价值、投资建议。

**示例：**
```
/buffett-analyze HK.00700
/buffett-analyze 腾讯控股
```

### /buffett-portfolio
分析当前持仓组合，生成巴菲特式投资报告。

**示例：**
```
/buffett-portfolio
```

### /buffett-backtest [股票代码] [开始日期] [结束日期]
回测巴菲特策略在指定股票上的历史表现。

**示例：**
```
/buffett-backtest HK.00700 2023-01-01 2026-03-21
```

### /buffett-alerts
查看/设置价格预警和巴菲特买卖信号预警。

**示例：**
```
/buffett-alerts
```

## 实现方式

本技能通过调用工作区的巴菲特策略模块实现：

```bash
# 分析股票
python3 /home/admin/openclaw/workspace/strategies/buffett_analyzer.py

# 回测
python3 /home/admin/openclaw/workspace/backtest/backtester.py --code HK.00700

# 预警检查
python3 /home/admin/openclaw/workspace/notify/price_alert.py --check
```

## 依赖模块

- `/home/admin/openclaw/workspace/strategies/buffett_strategy.py` - 选股策略
- `/home/admin/openclaw/workspace/strategies/buffett_analyzer.py` - 持仓分析
- `/home/admin/openclaw/workspace/backtest/backtester.py` - 回测系统
- `/home/admin/openclaw/workspace/notify/price_alert.py` - 价格预警
- `/home/admin/openclaw/workspace/data/financial_data.py` - 财务数据

## 配置

预警配置文件：`/home/admin/openclaw/workspace/notify/alerts_config.json`

## 输出示例

```
# 📊 腾讯控股 (HK.00700) 巴菲特分析报告

**分析时间:** 2026-03-21 12:45:00

## 📈 核心指标
- **综合评分:** 86/100 ⭐⭐⭐⭐
- **投资建议:** HOLD
- **当前价格:** 508.00 港元
- **内在价值:** 518.78 港元
- **安全边际:** +2.1%

## 💰 财务指标
- **ROE (5 年平均):** 20.3%
- **毛利率:** 42.5%
- **市盈率:** 12.5
- **护城河评分:** 8/10
```

## 相关文件

- 技能位置：`~/.openclaw/skills/buffett-investor/`
- 工作区：`/home/admin/openclaw/workspace/`
- 完整文档：`/home/admin/openclaw/workspace/BUFFETT_SYSTEM.md`

---

**版本**: v1.0  
**创建**: 2026-03-21
