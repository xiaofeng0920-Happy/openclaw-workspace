# CLI-Anything 投资分析集成方案

**创建时间：** 2026-03-19  
**目标：** 将 CLI-Anything 集成到锋哥股票分析系统

---

## 🎯 集成目标

利用 CLI-Anything 为投资分析工作流生成专用 CLI 工具，实现：
1. 自动化投资报告生成
2. 批量图表处理
3. 数据可视化
4. PDF 报告导出

---

## 📦 推荐生成的 CLI

### 1️⃣ LibreOffice CLI（优先级🔴）

**用途：** 自动生成投资报告、持仓汇总表

**功能：**
- 创建 Word 文档（持仓报告）
- 创建 Excel 表格（持仓明细）
- 导出 PDF（发送给用户）

**使用场景：**
```
@cli-anything 为 LibreOffice 构建 CLI
```

**生成后可用命令：**
```bash
# 创建持仓报告
cli-anything-libreoffice document new --type writer -o 持仓报告.json
cli-anything-libreoffice --json writer add-table --rows 30 --cols 8
cli-anything-libreoffice export render 持仓报告.pdf --type pdf
```

---

### 2️⃣ Draw.io CLI（优先级🟡）

**用途：** 绘制投资流程图、资产配置图

**功能：**
- 创建流程图
- 绘制资产配置饼图
- 导出 PNG/SVG

**使用场景：**
```
@cli-anything 为 Draw.io 构建 CLI
```

---

### 3️⃣ GIMP CLI（优先级🟢）

**用途：** 批量处理图表截图、添加水印

**功能：**
- 批量调整图片尺寸
- 添加水印/标注
- 格式转换

**使用场景：**
```
@cli-anything 为 GIMP 构建 CLI
```

---

## 🔄 集成到股票分析系统

### 当前流程

```
财报数据 → 分析 → Markdown 报告 → 发送飞书
```

### 集成后流程

```
财报数据 → 分析 → LibreOffice CLI → PDF 报告 → 发送飞书 + 附件
              ↓
         Draw.io CLI → 图表 → 插入报告
```

---

## 📁 文件组织

```
memory/
├── 持仓股票_财报跟踪总表_2026-03-18.md
├── 腾讯控股_业绩会总结_2026-03-18.md
├── CLI-Anything_投资分析集成方案.md  # ⭐ 本文件
└── ...

scripts/
├── run_portfolio_agent.py
├── monitor_product_scale.py
└── generate_report_pdf.py  # ⭐ 新增（使用 LibreOffice CLI）
```

---

## 🚀 实施步骤

### 阶段 1：LibreOffice CLI（本周）

| 步骤 | 操作 | 状态 |
|------|------|------|
| 1 | 生成 LibreOffice CLI | ⏳ |
| 2 | 测试文档创建功能 | ⏳ |
| 3 | 测试 PDF 导出功能 | ⏳ |
| 4 | 集成到报告生成流程 | ⏳ |

**命令：**
```
@cli-anything 为 LibreOffice 构建 CLI
```

### 阶段 2：Draw.io CLI（下周）

| 步骤 | 操作 | 状态 |
|------|------|------|
| 1 | 生成 Draw.io CLI | ⏳ |
| 2 | 创建资产配置图模板 | ⏳ |
| 3 | 集成到报告生成 | ⏳ |

### 阶段 3：自动化工作流（下周）

| 步骤 | 操作 | 状态 |
|------|------|------|
| 1 | 创建报告生成脚本 | ⏳ |
| 2 | 设置定时任务 | ⏳ |
| 3 | 测试完整流程 | ⏳ |

---

## 💡 使用示例

### 生成腾讯业绩报告 PDF

```python
# 1. 创建文档
cli-anything-libreoffice document new --type writer -o 腾讯业绩报告.json

# 2. 添加标题
cli-anything-libreoffice --project 腾讯业绩报告.json \
  writer add-heading -t "腾讯控股 4Q25 业绩报告" --level 1

# 3. 添加表格（财务数据）
cli-anything-libreoffice --project 腾讯业绩报告.json \
  writer add-table --rows 6 --cols 5

# 4. 填充数据
cli-anything-libreoffice --project 腾讯业绩报告.json \
  writer fill-table --data 财报数据.json

# 5. 导出 PDF
cli-anything-libreoffice --project 腾讯业绩报告.json \
  export render 腾讯业绩报告.pdf --type pdf
```

---

## 📊 预期收益

| 指标 | 当前 | 集成后 | 提升 |
|------|------|--------|------|
| 报告格式 | Markdown | PDF + Word | ✅ 更专业 |
| 图表生成 | 手动 | 自动 | ✅ 节省 80% 时间 |
| 报告分发 | 文字消息 | PDF 附件 | ✅ 更正式 |
| 归档管理 | 分散 | 统一 | ✅ 易检索 |

---

## ⚠️ 注意事项

1. **依赖安装** - 需要安装 LibreOffice、Draw.io 等软件
2. **测试验证** - 每个 CLI 生成后需要测试
3. **性能优化** - 批量处理时注意资源占用

---

## 📝 下一步行动

| 优先级 | 事项 | 预计时间 |
|--------|------|---------|
| 🔴 | 生成 LibreOffice CLI | 30 分钟 |
| 🔴 | 测试文档创建 + PDF 导出 | 30 分钟 |
| 🟡 | 集成到财报报告流程 | 1 小时 |
| 🟢 | 生成 Draw.io CLI | 30 分钟 |

---

*创建时间：2026-03-19*  
*状态：⏳ 等待实施*
