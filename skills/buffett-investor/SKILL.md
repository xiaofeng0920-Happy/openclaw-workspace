---
name: buffett-investor
description: 巴菲特价值投资自动化技能。股票筛选、市场状态识别、动态配置、调仓 rebalance。
version: 1.0.0
---

# SKILL.md - buffett-investor 技能说明

## 技能名称
**buffett-investor** - 巴菲特价值投资自动化技能

## 技能描述
基于巴菲特价值投资理念，自动执行股票筛选、市场状态识别、动态配置、调仓 rebalance、绩效监控的全流程投资技能。

## 触发条件
当用户提到以下关键词时自动激活：
- "巴菲特投资"、"价值投资"
- "股票筛选"、"选股"
- "调仓"、"rebalance"
- "持仓分析"、"投资组合"
- "市场状态"、"牛市"、"熊市"、"震荡市"
- "回测"、"绩效分析"

## 核心功能

### 1. 股票筛选 (`screen_stocks`)
**功能**：根据巴菲特价值投资标准筛选优质股票

**参数**：
- `pe_max`: PE 上限（默认 30）
- `roe_min`: ROE 下限%（默认 8）
- `roic_min`: ROIC 下限%（默认 8）
- `market_cap_min`: 市值下限亿（默认 30）
- `debt_ratio_max`: 资产负债率上限%（默认 50，60 支池使用）
- `fcf_positive_years`: 连续正现金流年数（默认 5，60 支池使用）

**返回**：
```json
{
  "stock_pool": "177 支/60 支",
  "stocks": [
    {"code": "600519.SH", "name": "贵州茅台", "pe": 19.70, "roe": 26.37, "roic": 24.33, "market_cap": 17732}
  ],
  "count": 177,
  "avg_pe": 18.45,
  "avg_roe": 16.25
}
```

### 2. 市场状态识别 (`identify_market_state`)
**功能**：基于沪深 300 技术指标判断牛/熊/震荡市

**参数**：
- `index_code`: 指数代码（默认 000300.SH）
- `lookback_days`: 回看天数（默认 250）

**判断规则**：
- **牛市**：收盘价>MA250 + MA250 斜率>0 + RSI(14)>50 + 市场广度>60%
- **熊市**：满足 2 个及以上：收盘价<MA250、斜率<0、RSI<40、广度<40%
- **震荡市**：不满足牛市或熊市

**返回**：
```json
{
  "market_state": "bull/bear/oscillate",
  "confidence": 0.85,
  "indicators": {
    "price_vs_ma250": "above",
    "ma250_slope": "positive",
    "rsi14": 58.5,
    "market_breadth": 0.65
  }
}
```

### 3. 动态配置 (`get_allocation`)
**功能**：根据市场状态生成配置建议

**参数**：
- `market_state`: 市场状态（bull/bear/oscillate）
- `stock_pool`: 股票池数据
- `risk_preference`: 风险偏好（aggressive/conservative）

**配置规则**：
| 市场状态 | 股票池 | 仓位 | 行业策略 |
|---------|--------|------|---------|
| 牛市 | 177 支 | 90-100% | 超配周期 +20%、成长 +15% |
| 熊市 | 60 支 | 50-70% | 超配防御 +25%、高股息 |
| 震荡市 | 120 支 | 70-85% | 均衡配置 |

**返回**：
```json
{
  "market_state": "oscillate",
  "position": 0.75,
  "stock_pool": "60 支",
  "industry_weights": {"消费": 0.15, "医药": 0.12, ...},
  "top_picks": ["600519.SH", "000858.SZ", ...]
}
```

### 4. 调仓计划 (`generate_rebalance_plan`)
**功能**：生成调仓交易指令

**参数**：
- `allocation`: 配置建议
- `current_holdings`: 当前持仓
- `rebalance_frequency`: 调仓频率（monthly/quarterly）

**返回**：
```json
{
  "action": "rebalance",
  "date": "2026-03-28",
  "trades": [
    {"action": "buy", "code": "600519.SH", "weight": 0.05},
    {"action": "sell", "code": "000xxx.SZ", "weight": 0.03}
  ],
  "total_trades": 8,
  "estimated_cost": 0.0015
}
```

### 5. 绩效监控 (`monitor_performance`)
**功能**：实时跟踪投资组合绩效

**参数**：
- `portfolio_id`: 组合 ID
- `start_date`: 起始日期
- `benchmark`: 基准（默认 000300.SH）

**返回**：
```json
{
  "portfolio_return": 0.4760,
  "benchmark_return": -0.1052,
  "excess_return": 0.5812,
  "max_drawdown": -0.2365,
  "sharpe_ratio": 0.3625,
  "annualized_return": 0.0810,
  "volatility": 0.1822
}
```

## 使用示例

### 示例 1：筛选股票
```
帮我筛选符合巴菲特标准的股票，PE<30，ROE>8%
```

**技能执行**：
1. 调用 `screen_stocks(pe_max=30, roe_min=8, roic_min=8)`
2. 返回 177 只股票清单
3. 展示 TOP 20 按 ROE 排序

### 示例 2：市场状态分析
```
当前市场是什么状态？牛市还是熊市？
```

**技能执行**：
1. 调用 `identify_market_state()`
2. 分析沪深 300 技术指标
3. 返回市场状态 + 置信度

### 示例 3：生成配置建议
```
根据当前市场状态，我应该怎么配置仓位？
```

**技能执行**：
1. 调用 `identify_market_state()` 获取市场状态
2. 调用 `get_allocation(market_state, stock_pool)`
3. 返回仓位建议 + 行业配置

### 示例 4：调仓计划
```
这个月需要调仓吗？生成调仓计划
```

**技能执行**：
1. 调用 `generate_rebalance_plan(allocation, holdings)`
2. 计算需要买入/卖出的股票
3. 返回交易指令清单

### 示例 5：绩效分析
```
我的投资组合表现怎么样？
```

**技能执行**：
1. 调用 `monitor_performance(portfolio_id)`
2. 计算收益率、回撤、夏普比率
3. 对比基准指数

## 配置参数

在 `config.py` 中可调整：

```python
# 筛选条件
PE_MAX = 30
ROE_MIN = 8  # %
ROIC_MIN = 8  # %
MARKET_CAP_MIN = 30  # 亿

# 60 支严选池额外条件
DEBT_RATIO_MAX = 50  # %
FCF_POSITIVE_YEARS = 5

# 动态配置
BULL_POSITION = 0.95  # 牛市仓位
BEAR_POSITION = 0.60  # 熊市仓位
OSCILLATE_POSITION = 0.75  # 震荡市仓位

# 调仓
REBALANCE_FREQUENCY = "monthly"  # monthly/quarterly
MAX_TURNOVER = 0.30  # 最大换手率

# 风控
MAX_DRAWDOWN_THRESHOLD = 0.15  # 回撤>15% 触发减仓
```

## 数据源

- **股票行情**：富途 OpenD API / AkShare
- **财务数据**：Tushare Pro / AkShare
- **指数数据**：沪深 300 (000300.SH)
- **市场广度**：涨跌家数比

## 回测绩效

基于 2021-03-28 至 2026-03-28 的 5 年回测：

| 策略 | 年化收益 | 最大回撤 | 夏普比率 | 超额收益 |
|------|---------|---------|---------|---------|
| 巴菲特月度 (177 支) | 13.39% | -27.08% | 63.82% | +15.68% |
| 动态配置 | 11.23% | -28.76% | 0.92 | +9.00% |
| 季度调仓 | 8.13% | -33.21% | 0.58 | +10.42% |
| 行业均衡 | 8.10% | -23.65% | 36.25% | +10.39% |
| 沪深 300 | -2.29% | -40.86% | -0.15 | - |

## 风险提示

1. **历史回测不代表未来** - 市场环境变化可能影响策略有效性
2. **交易成本** - 月度调仓会产生佣金和冲击成本
3. **流动性风险** - 部分小市值股票可能存在流动性问题
4. **财务数据滞后** - 基于历史财报数据，存在信息滞后性
5. **最大回撤** - 策略最大回撤约 -25%~-29%，需做好心理准备

## 版本历史

- **v1.0** (2026-03-28) - 初始版本，整合 8 个文档策略

## 相关文件

- `/skills/buffett-investor/README.md` - 技能说明
- `/skills/buffett-investor/screener.py` - 股票筛选模块
- `/skills/buffett-investor/market_state.py` - 市场状态识别
- `/skills/buffett-investor/allocator.py` - 动态配置策略
- `/skills/buffett-investor/rebalancer.py` - 调仓执行器
- `/skills/buffett-investor/monitor.py` - 绩效监控
- `/skills/buffett-investor/config.py` - 配置参数
