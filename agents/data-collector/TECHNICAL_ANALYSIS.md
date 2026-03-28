# 技术指标分析 + 专业数据源

## 📊 技术指标分析

### 支持的指标

| 指标 | 说明 | 参数 | 信号 |
|------|------|------|------|
| **MACD** | 趋势 momentum 指标 | 12,26,9 | 金叉🟢/死叉🔴 |
| **RSI** | 相对强弱指数 | 6,12,24 | 超买>70/超卖<30 |
| **KDJ** | 随机指标 | 9,3,3 | 超买>80/超卖<20 |
| **布林带** | 波动区间 | 20,2σ | 上轨突破/下轨突破 |
| **MA** | 移动平均线 | 5,10,20,60 | 金叉/死叉 |
| **成交量均线** | 量能分析 | 5,10 | 放量/缩量 |

### 使用方法

```bash
cd /home/admin/openclaw/workspace/agents/data-collector

# 分析重点股票池
python3 technical_indicators.py

# 输出
- 终端显示详细分析
- CSV 保存：technical/technical_analysis_*.csv
```

### 综合评分系统

| 得分 | 信号 | 操作建议 |
|------|------|---------|
| ≥5 | 🟢 强烈买入 | 建仓/加仓 |
| 3~4 | 🟡 买入 | 逢低买入 |
| -2~2 | ⚪ 观望 | 持有 |
| -3~-4 | 🟠 卖出 | 逢高减仓 |
| ≤-5 | 🔴 强烈卖出 | 清仓/做空 |

### 评分规则

| 信号 | 得分 |
|------|------|
| MACD 多头 | +1 |
| RSI 超卖 | +2 |
| RSI 超买 | -1 |
| KDJ 超卖 | +2 |
| KDJ 超买 | -1 |
| 布林带下轨 | +1 |
| 布林带上轨 | -1 |
| MACD 金叉 | +3 |
| MACD 死叉 | -3 |

---

## 📈 专业数据源 - Tushare Pro

### 为什么需要专业数据源？

akshare 免费数据 limitations：
- ❌ ROIC 数据不完整
- ❌ 历史股息率需要手动计算
- ❌ 财务指标更新延迟

Tushare Pro 优势：
- ✅ 完整 ROIC、ROE 历史数据
- ✅ 准确的股息率计算
- ✅ 接口稳定，更新及时

### 注册获取 Token

1. 访问 https://tushare.pro
2. 免费注册账号
3. 个人中心 → 获取 Token
4. 基础积分：100（足够用）

### 安装配置

```bash
# 安装 tushare
pip install tushare

# 保存 Token
cd /home/admin/openclaw/workspace/agents/data-collector
python3 tushare_data.py setup

# 输入你的 Token
```

### 使用方法

```bash
# 运行高质量股票筛选（使用 Tushare 数据）
python3 tushare_data.py

# 输出
- 终端显示筛选过程
- CSV 保存：tushare_data/tushare_qualified_*.csv
```

### 数据接口

| 接口 | 功能 | 数据 |
|------|------|------|
| `stock_basic` | 股票列表 | 代码、名称、行业 |
| `fina_indicator` | 财务指标 | ROE、ROIC、毛利率 |
| `income` | 利润表 | 营收、利润 |
| `balancesheet` | 资产负债表 | 资产、负债 |
| `dividend` | 分红数据 | 股息、分红方案 |
| `daily` | 日线行情 | 开高低收、成交量 |

---

## 🔄 Workflow 整合

### 每日自动执行

```cron
# 20:00 - 投资分析 Workflow（含技术指标）
0 12 * * * cd /home/admin/openclaw/workspace/agents/investment-workflow && python3 workflow.py full >> /tmp/investment-workflow.log 2>&1
```

### 手动运行

```bash
# 完整 Workflow
python3 workflow.py full

# 仅技术指标
python3 technical_indicators.py

# 仅 Tushare 筛选
python3 tushare_data.py
```

---

## 📊 输出示例

### 技术指标报告

```
============================================================
分析：601088 (A 股)
============================================================
当前价格：35.20 (+1.50%)

📊 MACD:
  DIF: 0.52
  DEA: 0.38
  MACD: 0.28
  信号：bullish
  🟢 金叉！

📊 RSI:
  RSI6: 45.2
  RSI12: 52.1
  RSI24: 48.5
  信号：neutral

📊 KDJ:
  K: 55.2
  D: 48.5
  J: 68.5
  信号：neutral

📊 布林带:
  上轨：38.50
  中轨：35.00
  下轨：31.50
  信号：neutral

📈 综合评分:
  得分：4/10
  信号：MACD 多头，MACD 金叉
  🟡 买入信号
```

### Tushare 筛选结果

```
============================================================
🔍 Tushare 高质量股票筛选
============================================================
[1] 601088 中国神华... ✅ ROE:18.5% ROIC:15.2% 股息:7.2%
[2] 601225 陕西煤业... ✅ ROE:19.2% ROIC:16.8% 股息:6.5%

✅ 筛选完成：2 只符合
```

---

## 🎯 下一步

1. **每日查看** - 技术指标报告（飞书推送）
2. **季度更新** - Tushare 财务数据筛选
3. **年度回测** - 验证技术指标有效性

---

*数据来源：AKShare（免费）+ Tushare Pro（专业）*
