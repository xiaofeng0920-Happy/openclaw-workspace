# 新增功能说明

**日期：** 2026-03-22  
**需求：** 1. 接入专业数据源  2. 添加技术指标分析

---

## ✅ 已完成功能

### 1️⃣ 技术指标分析模块

**文件：** `agents/data-collector/technical_indicators.py`

**支持指标：**

| 指标 | 说明 | 信号 |
|------|------|------|
| MACD | 趋势指标（12,26,9） | 金叉🟢/死叉🔴 |
| RSI | 超买超卖（6,12,24） | >70 超买，<30 超卖 |
| KDJ | 随机指标（9,3,3） | >80 超买，<20 超卖 |
| 布林带 | 波动区间（20,2σ） | 上轨/下轨突破 |
| MA | 移动平均（5,10,20,60） | 金叉/死叉 |
| 成交量均线 | 量能分析（5,10） | 放量/缩量 |

**综合评分系统：**

- 得分范围：-10 ~ +10
- ≥5 分：🟢 强烈买入
- 3~4 分：🟡 买入
- -2~2 分：⚪ 观望
- -3~-4 分：🟠 卖出
- ≤-5 分：🔴 强烈卖出

**使用方法：**
```bash
cd /home/admin/openclaw/workspace/agents/data-collector
python3 technical_indicators.py
```

**输出：**
- 终端显示详细分析
- CSV 保存：`technical/technical_analysis_*.csv`

---

### 2️⃣ 专业数据源接口（Tushare Pro）

**文件：** `agents/data-collector/tushare_data.py`

**优势：**
- ✅ 完整 ROIC、ROE 历史数据
- ✅ 准确的股息率计算
- ✅ 接口稳定，更新及时

**注册步骤：**
1. 访问 https://tushare.pro
2. 免费注册账号
3. 个人中心 → 获取 Token
4. 基础积分 100（足够用）

**配置方法：**
```bash
cd /home/admin/openclaw/workspace/agents/data-collector
python3 tushare_data.py setup
# 输入 Token
```

**使用方法：**
```bash
# 运行高质量股票筛选
python3 tushare_data.py
```

**数据接口：**
- `stock_basic` - 股票列表
- `fina_indicator` - ROE、ROIC 等财务指标
- `income` - 利润表
- `balancesheet` - 资产负债表
- `dividend` - 分红数据
- `daily` - 日线行情

---

### 3️⃣ Workflow 整合

**更新：** `agents/investment-workflow/workflow.py`

步骤 3 现在包含：
- 股票池检查
- 技术指标分析（自动运行）

**每日自动执行：**
```cron
0 12 * * * cd /home/admin/openclaw/workspace/agents/investment-workflow && python3 workflow.py full >> /tmp/investment-workflow.log 2>&1
```

---

## 📁 文件清单

```
/home/admin/openclaw/workspace/agents/
├── data-collector/
│   ├── technical_indicators.py    # 【新增】技术指标分析
│   ├── tushare_data.py            # 【新增】Tushare Pro 接口
│   ├── TECHNICAL_ANALYSIS.md      # 【新增】使用说明
│   ├── technical/                 # 【新增】技术指标输出
│   └── tushare_data/              # 【新增】Tushare 输出
│
├── investment-workflow/
│   ├── workflow.py                # 【更新】整合技术指标
│   └── README.md                  # 【更新】说明文档
│
└── FEATURES_ADDED.md              # 【新增】本文档
```

---

## 📊 输出示例

### 技术指标分析报告

```
分析：601088 中国神华
当前价格：35.20 (+1.50%)

📊 MACD:
  DIF: 0.52, DEA: 0.38, MACD: 0.28
  信号：bullish 🟢 金叉！

📊 RSI:
  RSI6: 45.2, RSI12: 52.1
  信号：neutral

📊 KDJ:
  K: 55.2, D: 48.5, J: 68.5
  信号：neutral

📈 综合评分：4/10 🟡 买入信号
```

### Tushare 筛选结果

```
🔍 Tushare 高质量股票筛选

[1] 601088 中国神华
    ROE: 18.5%, ROIC: 15.2%, 股息率：7.2% ✅

[2] 601225 陕西煤业
    ROE: 19.2%, ROIC: 16.8%, 股息率：6.5% ✅
```

---

## ⚠️ 注意事项

### 网络问题

akshare 依赖东方财富/新浪财经 API，可能不稳定。解决方案：

1. **重试机制** - 脚本已内置 3 次重试
2. **本地缓存** - 建议添加本地数据缓存（待实现）
3. **备用数据源** - Tushare Pro 更稳定

### Tushare 积分

- 基础积分：100（注册即送）
- 获取方式：签到、分享、付费
- 100 积分足够：
  - ✅ 股票列表（免费）
  - ✅ 日线行情（免费）
  - ✅ 财务指标（免费）
  - ⚠️ 高频调用需要更多积分

---

## 🎯 使用建议

### 每日工作流

1. **早盘前（09:00）** - 持仓监控（自动）
2. **晚间（20:00）** - Workflow 综合日报（自动，含技术指标）

### 季度工作流

1. **季度初** - 运行 Tushare 筛选，更新股票池
2. **季度末** - 回测技术指标有效性

### 手动分析

```bash
# 分析单只股票技术指标
python3 technical_indicators.py

# 用 Tushare 筛选高质量股票
python3 tushare_data.py
```

---

## 📈 下一步优化

1. **本地缓存** - 缓存历史数据，减少 API 调用
2. **图表生成** - 添加 K 线图、指标图
3. **自动交易信号** - 基于技术指标生成买卖点
4. **多因子选股** - 结合基本面 + 技术面

---

*最后更新：2026-03-22*
