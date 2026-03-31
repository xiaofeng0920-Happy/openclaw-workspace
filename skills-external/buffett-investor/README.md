# 📊 巴菲特价值投资技能

> "价格是你付出的，价值是你得到的。" —— 巴菲特

## 安装

本技能已预装到 OpenClaw 技能系统。

位置：`~/.openclaw/skills/buffett-investor/`

## 使用方法

### 1. 通过命令调用

```bash
# 分析单只股票
buffett-investor analyze HK.00700

# 分析持仓组合
buffett-investor portfolio

# 回测策略
buffett-investor backtest HK.00700 2023-01-01 2026-03-21

# 检查预警
buffett-investor alerts
```

### 2. 在对话中使用

直接对 OpenClaw 说：
- "分析腾讯控股的巴菲特评分"
- "查看我的持仓分析"
- "回测腾讯过去 3 年的表现"
- "检查有没有触发预警"

### 3. Python API

```python
from skills.buffett-investor import analyze_stock, analyze_portfolio

# 分析股票
report = analyze_stock('HK.00700')
print(report)

# 分析持仓
report = analyze_portfolio()
print(report)
```

## 功能列表

| 功能 | 命令 | 说明 |
|------|------|------|
| 股票分析 | `analyze [代码]` | 巴菲特评分、内在价值 |
| 持仓分析 | `portfolio` | 组合分析报告 |
| 策略回测 | `backtest [代码] [开始] [结束]` | 历史回测 |
| 价格预警 | `alerts` | 检查预警信号 |
| 选股扫描 | `scan [市场]` | 扫描符合条件的股票 |

## 依赖

- AKShare（财务数据）
- 富途 OpenD（实时行情）
- pandas, numpy, matplotlib

## 配置

编辑 `~/.openclaw/skills/buffett-investor/config.json`:

```json
{
  "data_source": "akshare",
  "default_market": "HK",
  "notify_feishu": true,
  "alert_cooldown": 3600
}
```

## 示例输出

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

- 策略实现：`/home/admin/openclaw/workspace/strategies/buffett_strategy.py`
- 回测系统：`/home/admin/openclaw/workspace/backtest/backtester.py`
- 预警系统：`/home/admin/openclaw/workspace/notify/price_alert.py`
- 完整文档：`/home/admin/openclaw/workspace/BUFFETT_SYSTEM.md`

---

**版本**: v1.0  
**更新**: 2026-03-21
