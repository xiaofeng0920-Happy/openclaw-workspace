---
name: akshare-stock
description: A 股量化数据查询技能，使用 AkShare 获取实时行情、K 线、财务数据、资金流向等。
license: MIT
---

# 📊 AkShare Stock - A 股数据查询

使用 AkShare 获取 A 股市场的实时行情、历史 K 线、财务数据等。

---

## 🔧 依赖安装

```bash
pip install akshare
```

---

## 📈 支持的功能

### 1. 实时行情查询

```python
import akshare as ak

# 个股实时行情
stock_zh_a_spot_em()
stock_zh_a_spot_em(symbol="北证A股")
```

### 2. 历史 K 线数据

```python
import akshare as ak

# 日 K 线
stock_zh_a_hist(symbol="000001", period="daily", 
                start_date="20240101", end_date="20241231", adjust="qfq")

# 周 K 线
stock_zh_a_hist(symbol="000001", period="weekly", 
                start_date="20240101", end_date="20241231", adjust="qfq")

# 月 K 线
stock_zh_a_hist(symbol="000001", period="monthly", 
                start_date="20240101", end_date="20241231", adjust="qfq")
```

### 3. 财务数据

```python
import akshare as ak

# 财务报表
stock_financial_abstract_ths(symbol="000001", indicator="按报告期")

# 主要财务指标
stock_financial_analysis_indicator(symbol="000001")
```

### 4. 板块/行业分析

```python
import akshare as ak

# 行业板块行情
stock_board_industry_name_em()

# 概念板块行情
stock_board_concept_name_em()

# 板块内个股
stock_board_industry_cons_em(symbol="半导体")
```

### 5. 资金流向

```python
import akshare as ak

# 个股资金流向
stock_individual_fund_flow(stock="000001", market="sh")

# 大单净流入
stock_individual_fund_flow(stock="000001", market="sh", symbol="大单净流入")
```

### 6. 龙虎榜

```python
import akshare as ak

# 每日龙虎榜
stock_lhb_detail_em(date="20240930")

# 机构调研
stock_zlzj_em()
```

### 7. 新股/IPO

```python
import akshare as ak

# 新股申购
stock_new_ipo_em()

# 待上市新股
stock_new_ipo_start_em()
```

### 8. 融资融券

```python
import akshare as ak

# 融资融券
stock_margin_sse(symbol="600000")

# 融资融券明细
stock_rzrq_detail_em(symbol="600000", date="20240930")
```

---

## 📋 常用股票代码

| 股票名称 | 代码 |
|---------|------|
| 平安银行 | 000001 |
| 贵州茅台 | 600519 |
| 宁德时代 | 300750 |
| 比亚迪 | 002594 |
| 招商银行 | 600036 |

---

## 🔄 与 data-collector 集成

### 添加到数据源优先级

```python
# data-collector 工作流程中添加 A 股数据源

def query_a_stock_price(code):
    """查询 A 股股价"""
    try:
        # 使用 akshare
        df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
        return {
            'code': code,
            'price': df.iloc[-1]['close'],
            'change': df.iloc[-1]['pct_chg']
        }
    except Exception as e:
        log_error(f"A 股查询失败 {code}: {e}")
        return None
```

### 数据源优先级

| 优先级 | 数据源 | 用途 |
|--------|--------|------|
| 1 | finance-data (MCP) | 美股/港股/A 股 |
| 2 | akshare | A 股主力数据源 |
| 3 | yfinance | 美股备选 |
| 4 | 手动录入 | 官网/港交所 |

---

## ⚠️ 注意事项

1. **数据仅供学术研究** - 不构成投资建议
2. **接口可能变动** - 目标网站可能更新导致接口失效
3. **添加异常处理** - 建议添加重试机制
4. **网络问题** - 当前环境网络可能影响数据获取

---

## 🧪 测试命令

```bash
cd /home/admin/openclaw/workspace/skills/akshare-stock
python test_akshare.py
```

---

**版本：** v1.0  
**最后更新：** 2026-03-20  
**数据来源：** AkShare
