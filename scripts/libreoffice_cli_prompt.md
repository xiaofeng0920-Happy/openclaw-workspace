# LibreOffice CLI 生成提示词

**请复制以下内容到对话框：**

---

@cli-anything 为 LibreOffice 构建 CLI

**用途：** 投资分析系统 - 自动生成投资报告 PDF

**需求说明：**

1. **核心功能：**
   - 创建 Writer 文档（投资报告）
   - 创建 Calc 表格（持仓明细）
   - 导出 PDF/Word/Excel 格式

2. **关键命令：**
   - `document new --type writer/calc/impress`
   - `writer add-heading/add-table/add-paragraph`
   - `export render --type pdf/docx/xlsx`

3. **使用场景：**
   - 财报报告自动生成
   - 持仓周报导出
   - 业绩演示文稿

4. **特殊要求：**
   - 支持 JSON 数据导入
   - 支持表格样式设置
   - 支持批量导出

**参考文档：** `/workspace/scripts/LibreOffice_CLI 需求.md`

---

**生成后验证命令：**

```bash
cd libreoffice/agent-harness
pip install -e .
cli-anything-libreoffice --help
cli-anything-libreoffice document new --type writer -o 测试.json
cli-anything-libreoffice export render 测试.pdf --type pdf
```

---

*创建时间：2026-03-19 00:09*
