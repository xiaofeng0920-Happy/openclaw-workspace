# LibreOffice CLI 需求文档

**目标：** 为投资分析系统生成 LibreOffice CLI

---

## 🎯 核心功能

### 1. 文档创建

```bash
# 创建 Writer 文档（投资报告）
cli-anything-libreoffice document new --type writer -o 投资报告.json

# 创建 Calc 表格（持仓明细）
cli-anything-libreoffice document new --type calc -o 持仓表.json

# 创建 Impress 演示（业绩展示）
cli-anything-libreoffice document new --type impress -o 业绩演示.json
```

### 2. 内容编辑

```bash
# 添加标题
cli-anything-libreoffice --project 投资报告.json \
  writer add-heading -t "腾讯控股 4Q25 业绩报告" --level 1

# 添加段落
cli-anything-libreoffice --project 投资报告.json \
  writer add-paragraph -t "核心要点：营收 +13%，净利润 +17%..."

# 添加表格
cli-anything-libreoffice --project 投资报告.json \
  writer add-table --rows 10 --cols 5

# 填充表格数据
cli-anything-libreoffice --project 投资报告.json \
  writer fill-table --data 财报数据.json

# 添加图片
cli-anything-libreoffice --project 投资报告.json \
  writer add-image --path 走势图.png --caption "腾讯股价走势"
```

### 3. 样式设置

```bash
# 设置标题样式
cli-anything-libreoffice --project 投资报告.json \
  style heading --font-size 24 --bold --color "#1a1a1a"

# 设置表格样式
cli-anything-libreoffice --project 投资报告.json \
  style table --border 1 --header-color "#f0f0f0"
```

### 4. 导出功能

```bash
# 导出 PDF
cli-anything-libreoffice --project 投资报告.json \
  export render 投资报告.pdf --type pdf

# 导出 Word
cli-anything-libreoffice --project 投资报告.json \
  export render 投资报告.docx --type docx

# 导出 Excel
cli-anything-libreoffice --project 持仓表.json \
  export render 持仓表.xlsx --type xlsx
```

---

## 📊 投资报告模板

### 模板 1：财报报告

```
# [公司名] [季度] 业绩报告

## 📊 核心指标
| 指标 | 数值 | 同比 | 状态 |
|------|------|------|------|
| 营收 | - | - | - |
| 净利润 | - | - | - |

## 📈 业务分析
### 游戏业务
...

### 广告业务
...

## 💡 持仓影响
...

## 📝 操作建议
...
```

### 模板 2：持仓周报

```
# 持仓周报（YYYY-MM-DD）

## 📊 总览
| 账户 | 市值 | 盈亏 | 盈亏率 |
|------|------|------|--------|
| 美股 | - | - | - |
| 港股 | - | - | - |

## 🏆 表现最佳 TOP5
...

## ⚠️ 风险提醒
...
```

---

## 🔄 集成到现有流程

### 当前流程
```
财报数据 → 分析 → Markdown → 飞书文字
```

### 新流程
```
财报数据 → 分析 → LibreOffice CLI → PDF → 飞书 + 附件
```

---

## 📁 文件组织

```
workspace/
├── scripts/
│   ├── generate_report_pdf.py  # ⭐ 新增
│   └── run_portfolio_agent.py
├── templates/
│   ├── 财报报告模板.odt  # ⭐ 新增
│   └── 持仓周报模板.odt  # ⭐ 新增
├── reports/
│   ├── 腾讯业绩报告_2026-03-18.pdf
│   └── 持仓周报_2026-03-18.pdf
└── memory/
    └── ...
```

---

## ✅ 验收标准

| 功能 | 测试方法 | 状态 |
|------|----------|------|
| 文档创建 | `cli-anything-libreoffice document new` | ⏳ |
| 添加内容 | `writer add-heading/add-table` | ⏳ |
| 导出 PDF | `export render xxx.pdf` | ⏳ |
| 表格填充 | `fill-table --data` | ⏳ |
| 图片插入 | `add-image` | ⏳ |

---

*创建时间：2026-03-19*  
*状态：⏳ 等待生成*
