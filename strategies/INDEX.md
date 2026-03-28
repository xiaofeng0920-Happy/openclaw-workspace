# 📚 巴菲特价值投资系统 - 完整索引

> "以合理的价格买入优秀的公司，远胜于以优惠的价格买入平庸的公司。" —— 沃伦·巴菲特

---

## 🎯 快速导航

| 你想... | 阅读文档 | 运行脚本 |
|--------|---------|---------|
| 了解系统 | [README.md](./README.md) | - |
| 学习策略 | [TRADING_STRATEGY.md](./TRADING_STRATEGY.md) | - |
| 分析持仓 | - | `python3 buffett_analyzer.py` |
| 查看交易计划 | - | `python3 buffett_trading.py` |
| 执行交易 | - | `python3 auto_trade.py --dry-run` |

---

## 📁 文件结构

```
strategies/
├── INDEX.md                    # 本索引文件
├── README.md                   # 快速入门指南
├── TRADING_STRATEGY.md         # 交易策略详解
│
├── buffett_strategy.py         # 核心选股策略 (18KB)
│   ├── BuffettStrategy         # 主类
│   ├── BuffettStock            # 股票数据类
│   ├── calculate_fair_value_dcf()    # DCF 估值
│   ├── calculate_buffett_score()     # 综合评分
│   └── analyze_stock()               # 分析股票
│
├── buffett_analyzer.py         # 持仓分析器 (10KB)
│   ├── analyze_portfolio()     # 分析持仓组合
│   ├── estimate_financials()   # 财务数据估算
│   └── generate_report()       # 生成报告
│
├── buffett_trading.py          # 交易策略 (16KB)
│   ├── BuffettTradingStrategy  # 交易策略类
│   ├── TradeSignal             # 交易信号
│   ├── generate_signal()       # 生成信号
│   └── generate_trade_plan()   # 交易计划
│
└── auto_trade.py               # 自动交易 (14KB)
    ├── AutoTrader              # 交易执行器
    ├── connect()               # 连接 OpenD
    ├── generate_signals()      # 生成信号
    ├── place_order()           # 下单
    └── execute_trades()        # 执行交易
```

---

## 🚀 快速开始

### 1. 环境检查

```bash
# 确保 OpenD 已启动
pgrep -f "Futu_OpenD" && echo "✅ OpenD 运行中"

# 测试 Python 连接
cd /home/admin/openclaw/workspace
python3 -c "from futu import *; print('✅ 连接正常')"
```

### 2. 第一次运行

```bash
# 分析当前持仓
python3 strategies/buffett_analyzer.py
```

### 3. 查看交易计划

```bash
# 生成交易计划
python3 strategies/buffett_trading.py
```

### 4. 模拟交易

```bash
# 模拟运行（不会实际下单）
python3 strategies/auto_trade.py --dry-run
```

### 5. 实盘交易（谨慎！）

```bash
# 实盘执行（需要确认）
python3 strategies/auto_trade.py --execute
```

---

## 📊 输出示例

### 持仓分析输出

```
============================================================
📊 巴菲特价值投资分析系统
============================================================

分析中：腾讯控股 (HK.00700)...
  ✅ 评分：86/100 | 建议：HOLD

分析中：中国海洋石油 (HK.00883)...
  ✅ 评分：99/100 | 建议：STRONG_BUY

分析中：阿里巴巴-W (HK.09988)...
  ✅ 评分：65/100 | 建议：HOLD

## 🎯 强力推荐 (STRONG BUY)

### 中国海洋石油 (HK.00883)
- 综合评分：99/100
- 当前价格：30.38 港元
- 内在价值：93.46 港元
- 安全边际：+67.5%
- ROE (5 年平均): 15.8%
```

### 交易计划输出

```
# 📋 巴菲特交易计划

## 🛒 买入建议

### 中国海洋石油 (HK.00883)
- 动作：强力买入
- 现价：30.38 港元
- 内在价值：93.46 港元
- 安全边际：67.5%
- 建议仓位：40.0%
- 建议买入：3,291 股
- 预计金额：99,981 港元
```

---

## 🎓 学习路径

### 初学者

1. 阅读 [README.md](./README.md) 了解系统
2. 运行 `buffett_analyzer.py` 查看持仓分析
3. 阅读 [TRADING_STRATEGY.md](./TRADING_STRATEGY.md) 学习策略

### 进阶用户

1. 研究 `buffett_strategy.py` 源码理解算法
2. 自定义选股阈值和评分权重
3. 接入真实财务数据源

### 高级用户

1. 扩展交易策略（网格交易、定投等）
2. 添加回测功能
3. 集成到自动化交易系统

---

## 🔧 自定义配置

### 调整选股标准

编辑 `buffett_strategy.py`:

```python
class BuffettStrategy:
    MIN_ROE = 15.0              # 最低 ROE
    MAX_DEBT_TO_EQUITY = 0.5    # 最高负债比
    MAX_PE = 15.0               # 最高 PE
    MIN_MARGIN_OF_SAFETY = 30.0 # 最低安全边际
```

### 添加新股票

编辑 `buffett_analyzer.py` 的 `estimate_financials()` 函数:

```python
estimates = {
    'HK.00001': {  # 新股票代码
        'roe': 18.0,
        'roe_5y_avg': 16.5,
        'gross_margin': 45.0,
        'debt_to_equity': 0.3,
        # ... 其他指标
    },
}
```

### 调整仓位限制

编辑 `auto_trade.py`:

```python
class AutoTrader:
    MAX_POSITION_RATIO = 0.40   # 单只股票最高 40%
    MAX_ORDER_VALUE = 500000    # 单笔订单最高 50 万
    STOP_LOSS_RATIO = 0.20      # 止损线 20%
```

---

## ⚠️ 风险提示

### 重要声明

1. **本系统仅供参考**，不构成投资建议
2. **投资有风险**，入市需谨慎
3. **过往表现**不代表未来收益
4. **请独立研究**并咨询专业顾问

### 使用建议

- ✅ 先用模拟账户测试
- ✅ 从小额开始，逐步增加
- ✅ 设置止损和仓位限制
- ✅ 定期复盘和调整策略
- ❌ 不要盲目跟随信号
- ❌ 不要投入无法承受损失的资金
- ❌ 不要借钱投资

---

## 📚 扩展阅读

### 巴菲特经典

- 《巴菲特致股东的信》
- 《证券分析》- 格雷厄姆
- 《聪明的投资者》- 格雷厄姆

### 价值投资

- 《巴菲特的护城河》- 帕特·多尔西
- 《价值投资》- 布鲁斯·格林沃尔德
- 《投资最重要的事》- 霍华德·马克斯

---

## 🤝 贡献与反馈

欢迎提交 Issue 和 Pull Request！

### TODO

- [ ] 接入真实财务数据 API（Tushare/聚宽）
- [ ] 添加更多估值模型（DDM、剩余收益）
- [ ] 实现自动调仓功能
- [ ] 添加回测模块
- [ ] 支持美股、A 股市场
- [ ] 添加技术指标分析
- [ ] 实现定投策略

---

## 📞 支持

- 问题反馈：提交 GitHub Issue
- 功能建议：提交 Pull Request
- 文档改进：欢迎贡献

---

## 📜 许可证

MIT License

---

> "我们喜欢的持有期是永远。" —— 沃伦·巴菲特

**最后更新**: 2026-03-21  
**版本**: v1.0
