# 数据采集 Agent - 配置说明

## 股票池来源

### 方案 1：手动维护（推荐，稳定）

**文件：** `manual_stock_pool.md`

**优点：**
- 不依赖网络 API
- 数据准确，经过人工核实
- 执行速度快（<1 秒）
- 零失败率

**缺点：**
- 需要定期手动更新（建议每季度）

**使用方法：**
```bash
# 直接读取 Markdown 文件
cat manual_stock_pool.md
```

### 方案 2：自动筛选（备用）

**脚本：** `stock_screener.py`

**优点：**
- 自动获取最新数据
- 可以批量筛选

**缺点：**
- 依赖 akshare API（不稳定）
- 免费数据 ROIC 不完整
- 执行时间长（3-5 分钟）

**使用方法：**
```bash
python3 stock_screener.py
```

### 方案 3：finance-data 技能（推荐用于实时数据）

使用 OpenClaw 的 finance-data 技能获取实时股价和财务数据。

**优点：**
- 数据准确
- 支持 A 股/港股/美股

**缺点：**
- 需要调用 MCP 接口

---

## 推荐工作流程

### 日常数据采集（每天）

1. **读取股票池** - 从 `manual_stock_pool.md` 获取股票列表
2. **获取实时股价** - 使用 akshare 或 finance-data
3. **计算盈亏** - 对比持仓成本
4. **采集新闻** - 获取持仓股票相关新闻

### 股票池更新（每季度）

1. 运行 `stock_screener.py` 初筛
2. 人工核实财务指标（ROE、ROIC、股息率）
3. 更新 `manual_stock_pool.md`

---

## 股票池（重点 6 只）

| 市场 | 代码 | 名称 | 股息率 | ROE | 状态 |
|------|------|------|--------|-----|------|
| 港股 | 00883 | 中国海洋石油 | ~8% | >10% | ✅ 锋哥已持仓 |
| 美股 | VZ | Verizon | ~7% | >25% | ⚠️ 可关注 |
| 美股 | MO | 奥驰亚 | ~8% | >100% | ⚠️ 可关注 |
| 美股 | BTI | 英美烟草 | ~9% | >40% | ⚠️ 可关注 |
| A 股 | 601088 | 中国神华 | ~7% | >10% | ⚠️ 可关注 |
| A 股 | 601225 | 陕西煤业 | ~6% | >10% | ⚠️ 可关注 |

---

## 数据采集频率

| 数据类型 | 频率 | 脚本 |
|---------|------|------|
| 股价 | 实时 | akshare |
| 财务指标 | 季度 | 手动更新 |
| 股息率 | 年度 | 手动更新 |
| 新闻 | 每日 | akshare |

---

## 输出路径

- 股票池：`/home/admin/openclaw/workspace/agents/data-collector/manual_stock_pool.md`
- 筛选结果：`/home/admin/openclaw/workspace/agents/data-collector/stock_pool/`
- 采集日志：`/tmp/data-collector.log`
