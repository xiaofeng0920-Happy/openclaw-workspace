# 持仓分析 Agent

锋哥的自主持仓监控与分析助手。

## ⚡ 重要说明

**全部使用本地脚本，不调用大模型！**

- 股价数据：akshare / QVeris / 富途 OpenD（多数据源支持）
- 产品规模：解析本地 Markdown 文件
- 飞书推送：OpenClaw CLI 工具
- 零 API 费用（使用 akshare 时），低延迟

## 功能

### 持仓监控
1. **持仓监控** - 每日 3 次检查持仓变化（早/中/晚）
2. **显著波动预警** - 涨跌超 3% 自动推送
3. **期权持仓监控** - 追踪期权实值/虚值状态
4. **产品规模监控** - 预警低于 500 万的产品
5. **行业新闻推送** - 持仓相关股票的重要新闻

### 市场日报（QVeris）
6. **指数行情** - A 股/港股主要指数实时数据
7. **资金流向** - 行业板块资金流入/流出
8. **财经新闻** - 全球财经新闻聚合
9. **创新高股票** - 当日创新高股票列表

## 推送渠道

- 飞书：ou_52fa8f508e88e1efbcbe50c014ecaa6e

## 监控时间表

| 时间 | 内容 | 脚本 |
|------|------|------|
| 09:00 | 早盘监控 + 产品规模 | run.py + product_scale_monitor.py |
| 13:00 | 午间监控 | run.py |
| 19:00 | 晚间总结 | run.py |

## 数据源

### 持仓监控
- 美股/港股/A 股：akshare（免费）或 富途 OpenD（实盘）
- 财务数据：akshare
- 新闻：akshare 财经新闻
- 产品规模：本地 Markdown 文件

### 市场日报（QVeris）
- 指数行情：同花顺 iFinD（通过 QVeris）
- 资金流向：同花顺 iFinD（通过 QVeris）
- 财经新闻：Finnhub（通过 QVeris）

## 持仓基准

- 基准文件：`/home/admin/openclaw/workspace/memory/锋哥持仓_2026-03-16.md`
- 产品规模：`/home/admin/openclaw/workspace/memory/产品管理规模_*.md`

## 脚本列表

### 持仓监控
| 脚本 | 功能 | 调用大模型 |
|------|------|-----------|
| `run.py` | 持仓监控 + 期权 + 新闻 | ❌ 否 |
| `run.py --futu` | 使用富途真实持仓（需要 OpenD） | ❌ 否 |
| `run.py --qveris` | 使用 QVeris 生成市场日报 | ❌ 否 |
| `product_scale_monitor.py` | 产品规模预警 | ❌ 否 |
| `analyzer.py` | 核心分析引擎 | ❌ 否 |
| `futu_data.py` | 富途 OpenAPI 数据获取 | ❌ 否 |
| `qveris_data.py` | QVeris API 数据获取 | ❌ 否 |
| `test_futu.py` | 测试 OpenD 连接 | ❌ 否 |
| `notify_feishu.py` | 飞书推送工具 | ❌ 否 |

## 🚀 富途 OpenD 接入（实盘数据）

### 快速开始

1. **确保 OpenD 已安装并启动**
   ```bash
   # 如未安装，使用 OpenClaw 技能
   openclaw skill install-opend
   ```

2. **测试连接**
   ```bash
   cd /home/admin/openclaw/workspace/agents/holding-analyzer
   python test_futu.py
   ```

3. **使用真实持仓运行**
   ```bash
   # 单次运行
   python run.py --futu
   
   # 运行并发送飞书通知
   python run.py --futu --send
   ```

### 配置文件

- OpenD 配置：`~/.futu/futu_config.ini`
- 监听端口：11111（默认）

### 详细文档

参见 `SETUP_OPEND.md`

### 对比：配置持仓 vs 富途实盘

| 特性 | 配置持仓 | 富途实盘 |
|------|---------|---------|
| 数据来源 | 手动配置的基准文件 | OpenD API 实时获取 |
| 持仓同步 | ❌ 需手动更新 | ✅ 自动同步 |
| 盈亏计算 | 相对基准日 | 相对成本价 |
| 期权支持 | 手动配置 | 自动获取 |
| 依赖 | 无 | 需 OpenD 运行中 |
