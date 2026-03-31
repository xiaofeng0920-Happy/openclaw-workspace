---
name: tushare-data
description: 面向中文自然语言的 Tushare 数据研究技能。用于把"看看这只股票最近怎么样""帮我查财报趋势""最近哪个板块最强""北向资金在买什么""给我导出一份行情数据"这类请求，转成可执行的数据获取、清洗、对比、筛选、导出与简要分析流程。适用于 A 股、指数、ETF/基金、财务、估值、资金流、公告新闻、板块概念与宏观数据等研究场景。
author: tushare.pro
version: 1.1.12
credentials:
  - name: TUSHARE_TOKEN
    description: Tushare Token，用于认证和授权访问 Tushare 数据服务。
    how_to_get: "https://tushare.pro/register"
requirements:
  python: 3.7+
  packages:
    - name: tushare
  environment_variables:
    - name: TUSHARE_TOKEN
      required: false
      sensitive: true
  network_access: true
---

# tushare-data

把自然语言财经数据请求，转成可执行的 Tushare 数据工作流。

## 配置

Tushare Token 已配置：`1dbdfba7c672d47f22db86f586d5aff9730124b321c2ebdda91890d3`

## 使用示例

```python
import tushare as ts

# 配置 Token
ts.set_token('1dbdfba7c672d47f22db86f586d5aff9730124b321c2ebdda91890d3')
pro = ts.pro_api()

# 获取港股行情
data = pro.hk_daily(ts_code='00700.HK')
```

## 支持的数据类型

- A 股行情、指数、ETF
- 港股行情
- 财务数据、估值指标
- 资金流、北向资金
- 公告新闻、研报
- 宏观数据（CPI/PPI/PMI 等）
