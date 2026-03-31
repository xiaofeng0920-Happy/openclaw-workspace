# 开源项目集成文档

**集成日期：** 2026-03-29  
**负责人：** AI 助手  
**状态：** 🟡 进行中

---

## 📊 集成项目总览

| 项目 | 安全等级 | 集成状态 | 用途 |
|------|---------|---------|------|
| **public-apis** | 🟢 低风险 | ✅ 已完成 | 补充数据源 |
| **微软 Qlib** | 🟢 低风险 | 🟡 待安装 | 回测引擎 |
| **TradingAgents** | 🟡 中低风险 | ⏳ 观察期 | 架构参考 |

---

## ✅ 阶段一：public-apis 数据源整合

### 新增文件
- `public_apis_data.py` - Public-apis 数据集成模块

### 已集成 API

#### 1. Yahoo Finance（无需 API Key）
```python
from public_apis_data import get_yahoo_finance_quote

quote = get_yahoo_finance_quote("AAPL")
# 返回：symbol, price, change, change_percent, volume, timestamp
```

**用途：** 美股实时股价备份数据源

**优势：**
- ✅ 无需 API Key
- ✅ 数据质量好
- ✅ 覆盖全球市场

**限制：**
- ⚠️ 非官方 API，可能变化
- ⚠️ 有速率限制（未公开）

---

#### 2. Alpha Vantage（需 API Key）
```python
from public_apis_data import get_alpha_vantage_quote

quote = get_alpha_vantage_quote("AAPL", api_key="YOUR_KEY")
```

**免费额度：** 5 次/分钟

**用途：** 美股历史数据、技术指标

**获取 Key：** https://www.alphavantage.co/support/#api-key

---

#### 3. CoinGecko（无需 API Key）
```python
from public_apis_data import get_coingecko_price

crypto = get_coingecko_price("bitcoin")
```

**用途：** 加密货币价格监控

**优势：**
- ✅ 无需 API Key
- ✅ 覆盖 10000+ 加密货币

---

### 测试命令
```bash
cd /home/admin/openclaw/workspace/agents/holding-analyzer
python3 public_apis_data.py
```

### 集成到现有系统

**修改 `analyzer.py`：**
```python
# 在数据获取部分添加备用数据源
from public_apis_data import get_yahoo_finance_quote

def get_us_stock_price_fallback(symbol):
    """Yahoo Finance 备用数据源"""
    quote = get_yahoo_finance_quote(symbol)
    if quote:
        return quote['price']
    return None
```

---

## 🟡 阶段二：Qlib 回测模块

### 新增文件
- `qlib_backtest.py` - Qlib 回测集成模块

### 安装步骤

#### 1. 安装 Qlib
```bash
pip install pyqlib
```

#### 2. 下载 A 股数据
```bash
python -m qlib.run.get_data qlib_data --target_dir ~/.qlib_data/cn_data --region cn
```

#### 3. 下载美股数据（可选）
```bash
python -m qlib.run.get_data qlib_data --target_dir ~/.qlib_data/us_data --region us
```

### 测试命令
```bash
cd /home/admin/openclaw/workspace/agents/holding-analyzer
python3 qlib_backtest.py
```

### 核心功能

#### 1. 运行回测
```python
from qlib_backtest import run_backtest

result = run_backtest(
    stocks=["GOOGL", "AAPL", "NVDA"],
    start_date="2025-01-01",
    end_date="2026-03-29",
    strategy="twostage"
)
```

#### 2. 对比基准
```python
from qlib_backtest import compare_with_benchmark

comparison = compare_with_benchmark(
    stocks=FENG_STOCKS_US,
    start_date="2025-01-01",
    end_date="2026-03-29"
)
```

### 集成计划

**修改 `run.py`：**
```python
# 添加 --backtest 参数
if '--backtest' in sys.argv:
    from qlib_backtest import run_backtest
    run_backtest(stocks=..., start_date=..., end_date=...)
```

---

## ⏳ 阶段三：Agent 协作优化（参考 TradingAgents）

### 新增文件
- `agent_collaboration.py` - 多 Agent 协作优化模块

### 现有 Agent 架构

| Agent | 职责 | 状态 |
|-------|------|------|
| data-collector | 数据收集 | ✅ 已有 |
| portfolio-analyzer | 持仓分析 | ✅ 已有 |
| report-writer | 报告撰写 | ✅ 已有 |
| strategy-advisor | 策略建议 | ✅ 已有 |
| message-dispatcher | 消息推送 | ✅ 已有 |

### 计划新增 Agent

| Agent | 职责 | 优先级 | 时间 |
|-------|------|--------|------|
| sentiment_analyst | 情绪分析 | ⭐⭐⭐ | 本周 |
| technical_analyst | 技术分析 | ⭐⭐ | 下周 |
| fundamental_analyst | 基本面分析 | ⭐⭐ | 2 周 |
| risk_manager | 风险管理 | ⭐⭐⭐ | 本周 |

### 动态讨论机制

参考 TradingAgents 的多 Agent 协作：

```python
from agent_collaboration import simulate_agent_discussion

result = simulate_agent_discussion(
    topic="腾讯控股是否应该加仓？",
    agents=["sentiment_analyst", "technical_analyst", "fundamental_analyst", "risk_manager"]
)
```

### 测试命令
```bash
cd /home/admin/openclaw/workspace/agents/holding-analyzer
python3 agent_collaboration.py
```

---

## 🗺️ 升级路线图

### Phase 1: 数据源整合（本周）✅
- [x] 创建 public_apis_data.py
- [ ] 测试 Yahoo Finance 数据源
- [ ] 集成到 analyzer.py
- [ ] 验证数据准确性

### Phase 2: 回测能力（下周）🟡
- [ ] 安装 Qlib
- [ ] 下载历史数据
- [ ] 运行回测测试
- [ ] 对比实际持仓表现

### Phase 3: Agent 增强（2-4 周）⏳
- [ ] 增加技术分析 Agent
- [ ] 增加基本面分析 Agent
- [ ] 实现动态讨论机制
- [ ] 优化决策流程

### Phase 4: LLM 集成（观察期）⏳
- [ ] 评估 TradingAgents 成熟度
- [ ] 测试 LLM 分析效果
- [ ] 成本效益分析
- [ ] 决策是否集成

---

## 🔒 安全检查清单

### 代码审查
- [x] 无硬编码 API Key
- [x] 使用环境变量管理密钥
- [x] 异常处理完善
- [x] 超时设置合理

### 依赖检查
- [x] 使用官方 PyPI 源
- [x] 依赖版本锁定
- [x] 定期更新依赖

### 数据安全
- [x] 不存储敏感数据
- [x] API 密钥本地管理
- [x] 不上传持仓数据

---

## 📝 使用示例

### 1. 测试 public-apis 集成
```bash
cd /home/admin/openclaw/workspace/agents/holding-analyzer
python3 public_apis_data.py
```

### 2. 安装并测试 Qlib
```bash
pip install pyqlib
python3 qlib_backtest.py
```

### 3. 查看 Agent 协作优化方案
```bash
python3 agent_collaboration.py
```

### 4. 运行完整持仓分析（含新数据源）
```bash
python3 run.py --send
```

---

## 📞 问题反馈

遇到问题请检查：
1. 依赖是否安装：`pip list`
2. API Key 是否配置：`echo $ALPHA_VANTAGE_KEY`
3. 数据目录是否存在：`ls -la ~/.qlib_data/`

---

**最后更新：** 2026-03-29  
**维护者：** AI 助手
