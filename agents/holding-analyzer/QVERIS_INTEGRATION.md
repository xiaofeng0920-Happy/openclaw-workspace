# QVeris 集成指南

## 概述

QVeris 已集成到股票投资系统中，提供以下数据能力：

- 📊 **指数行情** - A 股/港股主要指数实时数据
- 💰 **资金流向** - 行业板块资金流入/流出
- 📰 **财经新闻** - 全球财经新闻聚合
- 📈 **创新高股票** - 当日创新高股票列表

## 安装配置

### 1. QVeris 技能已安装

```bash
# 技能位置
~/.openclaw/skills/qveris-official/

# 验证安装
node ~/.openclaw/skills/qveris-official/scripts/qveris_tool.mjs --help
```

### 2. API Key 配置

API Key 已配置在环境变量中：

```bash
# 当前会话
export QVERIS_API_KEY="sk-85Z4EEYSR-0A4ifflY7zcHCPOCt_b8ARlMWCQleVvMQ"

# 持久化配置（可选）
echo 'export QVERIS_API_KEY="sk-85Z4EEYSR-0A4ifflY7zcHCPOCt_b8ARlMWCQleVvMQ"' >> ~/.bashrc
```

## 使用方法

### 方法 1：运行市场日报

```bash
cd /home/admin/openclaw/workspace/agents/holding-analyzer

# 生成市场日报
python run.py --qveris

# 生成并发送飞书通知
python run.py --qveris --send
```

### 方法 2：调用 Python 模块

```python
from qveris_data import (
    get_index_quotes,      # 获取指数行情
    get_stock_quotes,      # 获取个股行情
    get_sector_moneyflow,  # 获取资金流向
    get_stock_news,        # 获取股票新闻
    get_new_high_stocks,   # 获取创新高股票
    get_market_daily_report,  # 获取完整市场日报
)

# 获取指数行情
indices = get_index_quotes(['000300.SH', 'HSI.HK'])

# 获取资金流向
inflow, outflow = get_sector_moneyflow()

# 获取完整市场日报
market_data = get_market_daily_report()
```

### 方法 3：使用 QVeris CLI 直接调用

```bash
# 发现工具
node ~/.openclaw/skills/qveris-official/scripts/qveris_tool.mjs discover "中国指数行情" --limit 5

# 调用工具
node ~/.openclaw/skills/qveris-official/scripts/qveris_tool.mjs call ths_ifind.real_time_quotation.v1 \
  --discovery-id <id> \
  --params '{"codes":"000300.SH,HSI.HK"}'
```

## 数据源对比

| 数据源 | 优势 | 适用场景 |
|--------|------|---------|
| **QVeris** | 指数/资金流/新闻全面 | 市场日报、宏观分析 |
| **富途 OpenD** | 真实持仓、实时交易 | 持仓监控、交易执行 |
| **akshare** | A 股数据丰富、免费 | 备用数据源 |
| **配置持仓** | 简单、无需依赖 | 基础监控 |

## 输出示例

### 市场日报

运行 `python run.py --qveris` 生成：

```
📄 reports/market_daily_20260323.md
```

包含：
- 主要指数表现（沪深 300、恒生指数等）
- 行业资金流向（流入/流出前 10）
- 创新高股票
- 重要财经新闻
- 市场展望与风险提示

### 飞书推送

```markdown
## 📊 A 股市场日报

**日期：** 2026-03-23

| 指数 | 收盘价 | 涨跌幅 |
|------|--------|--------|
| 📉 沪深 300 | 4,418.00 | -3.26% |
| 📉 恒生指数 | 24,404.05 | -3.45% |
...
```

## 定时任务

### HEARTBEAT.md 集成

在 `HEARTBEAT.md` 中添加：

```markdown
## A 股市场日报 - 每日 16:00

- **时间：** 每个交易日 16:00
- **脚本：** `python run.py --qveris --send`
- **发送渠道：** 飞书
```

### Cron 配置（可选）

```bash
# 每个交易日 16:00 生成市场日报
0 16 * * 1-5 cd /home/admin/openclaw/workspace/agents/holding-analyzer && python run.py --qveris --send
```

## 扩展开发

### 添加新数据源

在 `qveris_data.py` 中添加：

```python
def get_new_data():
    """获取新数据"""
    discovery = discover_tools("数据描述")
    # ... 实现逻辑
    return data
```

### 自定义报告模板

在 `analyzer.py` 中修改 `generate_market_report()` 函数。

## 常见问题

### Q: QVeris API 调用失败？
A: 检查 API Key 是否正确，网络连接是否正常。

### Q: 某些工具找不到？
A: QVeris 工具库持续更新，使用 `discover` 命令查找可用工具。

### Q: 数据延迟？
A: QVeris 数据通常有 15 分钟延迟，实时数据请使用富途 OpenD。

## 相关文档

- [README.md](README.md) - 系统总览
- [SETUP_OPEND.md](SETUP_OPEND.md) - 富途 OpenD 配置
- [qveris_data.py](qveris_data.py) - QVeris 数据模块源码
