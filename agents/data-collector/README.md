# 数据采集 Agent - 股票池

## 功能

1. **股票筛选** - 按条件筛选高质量股票
2. **数据采集** - 收集股价、财务数据
3. **股票池管理** - 维护符合条件的股票列表

## 筛选条件

| 条件 | 要求 |
|------|------|
| 市场 | A 股 + 港股 + 美股 |
| ST 状态 | 非 ST |
| 市值 | >50 亿 |
| 股息率 | 连续 5 年 >5% |
| ROE | 连续 5 年 >10% |
| ROIC | 连续 5 年 >10% |

## 使用方法

### 运行筛选器

```bash
cd /home/admin/openclaw/workspace/agents/data-collector
python3 stock_screener.py
```

### 输出

- `stock_pool/qualified_stocks_*.csv` - CSV 格式股票列表
- `stock_pool/qualified_stocks_*.md` - Markdown 报告

## 注意事项

1. **网络问题** - akshare 依赖东方财富/新浪财经 API，可能不稳定
2. **数据完整性** - 免费数据源 ROIC 数据不完整
3. **建议** - 使用专业数据源（Wind、Bloomberg）获取完整财务指标

## 替代方案

如果 akshare 不稳定，可以：
1. 手动维护股票池（见 `manual_stock_pool.md`）
2. 使用 finance-data 技能查询
3. 接入专业 API（Tushare Pro、聚宽等）
