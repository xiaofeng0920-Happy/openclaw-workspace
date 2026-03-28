# LibreOffice CLI - Investment Report Generation Tool

**Version:** 1.0.0  
**Created:** 2026-03-19  
**Purpose:** 为投资分析系统自动生成投资报告 PDF

---

## 🎯 Overview

LibreOffice CLI 是一个基于 CLI-Anything 方法论构建的命令行工具，用于：

- ✅ 创建 Writer 文档（投资报告、业绩总结）
- ✅ 创建 Calc 表格（持仓明细、财务数据）
- ✅ 支持导出 PDF/Word/Excel 格式
- ✅ 支持添加标题、表格、段落、图片
- ✅ 支持 JSON 数据导入

---

## 📦 Installation

### Prerequisites

- Python 3.8+
- LibreOffice 7.0+
- Click library

### Install Steps

```bash
# 1. Navigate to the harness directory
cd /home/admin/openclaw/workspace/libreoffice/agent-harness

# 2. Install dependencies
pip3 install click

# 3. Install the CLI tool
pip3 install -e .

# 4. Verify installation
cli-anything-libreoffice --version
```

---

## 🚀 Quick Start

### Create Investment Report

```bash
# 1. Create new Writer document
cli-anything-libreoffice document new --type writer -o 投资报告.json

# 2. Add heading
cli-anything-libreoffice writer add-heading \
  --project 投资报告.json \
  -t "腾讯控股 4Q25 业绩报告" \
  --level 1

# 3. Add paragraph
cli-anything-libreoffice writer add-paragraph \
  --project 投资报告.json \
  -t "核心要点：营收 +13%，净利润 +17%，游戏业务表现强劲..."

# 4. Add table
cli-anything-libreoffice writer add-table \
  --project 投资报告.json \
  --rows 5 --cols 4 --header

# 5. Fill table with data
cli-anything-libreoffice writer fill-table \
  --project 投资报告.json \
  --data 财报数据.json

# 6. Export to PDF
cli-anything-libreoffice export render \
  投资报告.pdf \
  --project 投资报告.json \
  --type pdf
```

### Create Portfolio Spreadsheet

```bash
# 1. Create new Calc document
cli-anything-libreoffice document new --type calc -o 持仓表.json

# 2. Add sheet
cli-anything-libreoffice calc add-sheet \
  --project 持仓表.json \
  --name "持仓明细"

# 3. Fill data
cli-anything-libreoffice calc fill-data \
  --project 持仓表.json \
  --data 持仓数据.json

# 4. Export to Excel
cli-anything-libreoffice export render \
  持仓表.xlsx \
  --project 持仓表.json \
  --type xlsx
```

---

## 📖 Command Reference

### Document Commands

#### `document new` - Create new document

```bash
cli-anything-libreoffice document new --type TYPE -o OUTPUT

# Options:
#   --type [writer|calc|impress]  Document type (required)
#   -o, --output PATH             Output JSON file (required)
#   --template PATH               Optional template file

# Examples:
cli-anything-libreoffice document new --type writer -o report.json
cli-anything-libreoffice document new --type calc -o portfolio.json
```

### Writer Commands

#### `writer add-heading` - Add heading

```bash
cli-anything-libreoffice writer add-heading \
  --project FILE -t TEXT [--level N] [--style STYLE]

# Options:
#   --project FILE    Project JSON file (required)
#   -t, --text TEXT   Heading text (required)
#   --level N         Heading level 1-10 (default: 1)
#   --style STYLE     Custom style name

# Example:
cli-anything-libreoffice writer add-heading \
  --project report.json -t "Quarterly Results" --level 1
```

#### `writer add-paragraph` - Add paragraph

```bash
cli-anything-libreoffice writer add-paragraph \
  --project FILE -t TEXT [--style STYLE]

# Example:
cli-anything-libreoffice writer add-paragraph \
  --project report.json -t "Revenue increased by 13%..."
```

#### `writer add-table` - Add table

```bash
cli-anything-libreoffice writer add-table \
  --project FILE --rows N --cols M [--header] [--caption TEXT]

# Example:
cli-anything-libreoffice writer add-table \
  --project report.json --rows 5 --cols 4 --header
```

#### `writer fill-table` - Fill table with data

```bash
cli-anything-libreoffice writer fill-table \
  --project FILE --data DATA.json [--table-index N]

# Example:
cli-anything-libreoffice writer fill-table \
  --project report.json --data financial_data.json
```

#### `writer add-image` - Add image

```bash
cli-anything-libreoffice writer add-image \
  --project FILE --path IMAGE.png [--caption TEXT] [--width N] [--height M]

# Example:
cli-anything-libreoffice writer add-image \
  --project report.json --path chart.png --caption "Stock Performance"
```

### Calc Commands

#### `calc add-sheet` - Add sheet

```bash
cli-anything-libreoffice calc add-sheet \
  --project FILE [--name NAME]

# Example:
cli-anything-libreoffice calc add-sheet \
  --project portfolio.json --name "Holdings"
```

#### `calc fill-data` - Fill sheet with data

```bash
cli-anything-libreoffice calc fill-data \
  --project FILE --data DATA.json [--sheet N|NAME]

# Example:
cli-anything-libreoffice calc fill-data \
  --project portfolio.json --data holdings.json
```

### Style Commands

#### `style heading` - Style headings

```bash
cli-anything-libreoffice style heading \
  --project FILE [--font-size N] [--bold] [--italic] [--color HEX]

# Example:
cli-anything-libreoffice style heading \
  --project report.json --font-size 24 --bold --color "#1a1a1a"
```

#### `style table` - Style tables

```bash
cli-anything-libreoffice style table \
  --project FILE [--border N] [--header-color HEX] [--alternating]

# Example:
cli-anything-libreoffice style table \
  --project report.json --border 1 --header-color "#f0f0f0"
```

### Export Commands

#### `export render` - Export to PDF/Word/Excel

```bash
cli-anything-libreoffice export render OUTPUT \
  --project FILE --type FORMAT [--template FILE] [--output-dir DIR]

# Options:
#   OUTPUT          Output file path (required)
#   --project FILE  Project JSON file (required)
#   --type FORMAT   Output format: pdf|docx|odt|xlsx|xls|csv (required)
#   --template FILE Optional template
#   --output-dir DIR Output directory (default: .)

# Examples:
cli-anything-libreoffice export render report.pdf \
  --project report.json --type pdf

cli-anything-libreoffice export render portfolio.xlsx \
  --project portfolio.json --type xlsx
```

### Template Commands

#### `template list` - List templates

```bash
cli-anything-libreoffice template list [--folder FOLDER]

# Example:
cli-anything-libreoffice template list --folder templates
```

#### `template create` - Create template

```bash
cli-anything-libreoffice template create \
  --type TYPE --name NAME [--output FILE]

# Example:
cli-anything-libreoffice template create \
  --type writer --name earnings_report
```

### Shortcut Command

#### `build` - Quick build (alias for export render)

```bash
cli-anything-libreoffice build \
  --project FILE --output FILE

# Example:
cli-anything-libreoffice build \
  --project report.json --output report.pdf
```

---

## 📊 Data Format

### Table Data JSON

```json
[
  ["指标", "数值", "同比", "状态"],
  ["营收", "1000 亿", "+13%", "✅"],
  ["净利润", "500 亿", "+17%", "✅"],
  ["毛利率", "45%", "+2%", "✅"]
]
```

### Spreadsheet Data JSON

```json
[
  ["股票代码", "名称", "持仓", "成本", "现价", "盈亏率"],
  ["00700", "腾讯控股", "2500", "450", "420", "-6.5%"],
  ["00883", "中海油", "11000", "12", "17", "+43.4%"]
]
```

---

## 🔄 Integration Workflow

### Current Flow
```
财报数据 → 分析 → Markdown → 飞书文字
```

### New Flow with LibreOffice CLI
```
财报数据 → 分析 → LibreOffice CLI → PDF → 飞书 + 附件
```

### Example: Automated Report Generation

```python
#!/usr/bin/env python3
"""Generate investment report from financial data"""

import json
import subprocess

def generate_report(company: str, quarter: str, data: dict):
    # Create document
    subprocess.run([
        "cli-anything-libreoffice", "document", "new",
        "--type", "writer", "-o", f"{company}_report.json"
    ])
    
    # Add title
    subprocess.run([
        "cli-anything-libreoffice", "writer", "add-heading",
        "--project", f"{company}_report.json",
        "-t", f"{company} {quarter} 业绩报告",
        "--level", "1"
    ])
    
    # Add financial table
    subprocess.run([
        "cli-anything-libreoffice", "writer", "add-table",
        "--project", f"{company}_report.json",
        "--rows", "5", "--cols", "4", "--header"
    ])
    
    # Save table data
    with open("table_data.json", "w") as f:
        json.dump(data["table"], f)
    
    # Fill table
    subprocess.run([
        "cli-anything-libreoffice", "writer", "fill-table",
        "--project", f"{company}_report.json",
        "--data", "table_data.json"
    ])
    
    # Export to PDF
    subprocess.run([
        "cli-anything-libreoffice", "export", "render",
        f"{company}_report.pdf",
        "--project", f"{company}_report.json",
        "--type", "pdf"
    ])
    
    return f"{company}_report.pdf"
```

---

## 🧪 Testing

### Run Test Suite

```bash
# Navigate to harness directory
cd /home/admin/openclaw/workspace/libreoffice/agent-harness

# Run automated tests
python3 test_cli_lo.py

# Or with pytest
pytest test_cli_lo.py -v
```

### Manual Testing

```bash
# Create test directory
mkdir -p /tmp/lo-test && cd /tmp/lo-test

# Test document creation
cli-anything-libreoffice document new --type writer -o test.json

# Add content
cli-anything-libreoffice writer add-heading --project test.json -t "Test" --level 1
cli-anything-libreoffice writer add-paragraph --project test.json -t "Content"

# Export
cli-anything-libreoffice export render test.pdf --project test.json --type pdf

# Verify
ls -la *.pdf
```

---

## 📁 Project Structure

```
libreoffice/
└── agent-harness/
    ├── cli_lo.py              # Main CLI tool
    ├── test_cli_lo.py         # Test suite
    ├── setup.py               # Installation script
    ├── README.md              # This file
    ├── TEST.md                # Test plan
    └── templates/             # Document templates
        ├── 财报报告模板.odt
        └── 持仓周报模板.odt
```

---

## ⚠️ Known Limitations

1. **ODT/ODS Generation**: Current implementation creates simplified text/CSV files. For production use with proper ODF formatting, install `odfpy`:
   ```bash
   pip3 install odfpy
   ```

2. **Image Embedding**: Images are referenced by path. Full embedding requires ODF library.

3. **Headless Mode**: Requires LibreOffice properly configured for headless operation. Test with:
   ```bash
   soffice --headless --version
   ```

4. **Template Application**: Basic template support. Advanced template merging requires UNO API integration.

---

## 🛠️ Troubleshooting

### LibreOffice not found
```bash
# Install LibreOffice
sudo apt-get install libreoffice  # Ubuntu/Debian
sudo yum install libreoffice      # CentOS/RHEL
```

### Headless conversion fails
```bash
# Test headless mode
soffice --headless --version

# Check permissions
ls -la /usr/bin/soffice
```

### Export produces empty file
- Ensure content was added to project before export
- Check project JSON structure is valid
- Verify LibreOffice has write permissions to output directory

---

## 📝 Examples

### Example 1: Quarterly Earnings Report

```bash
# Create report
cli-anything-libreoffice document new --type writer -o tencent_4q25.json

# Add sections
cli-anything-libreoffice writer add-heading --project tencent_4q25.json -t "腾讯控股 4Q25 业绩报告" --level 1
cli-anything-libreoffice writer add-heading --project tencent_4q25.json -t "📊 核心指标" --level 2
cli-anything-libreoffice writer add-table --project tencent_4q25.json --rows 5 --cols 4 --header

# Fill data
echo '[["指标","数值","同比","状态"],["营收","1000 亿","+13%","✅"],["净利润","500 亿","+17%","✅"]]' > data.json
cli-anything-libreoffice writer fill-table --project tencent_4q25.json --data data.json

# Export
cli-anything-libreoffice export render tencent_4q25.pdf --project tencent_4q25.json --type pdf
```

### Example 2: Portfolio Holdings

```bash
# Create spreadsheet
cli-anything-libreoffice document new --type calc -o holdings.json

# Add sheet and data
cli-anything-libreoffice calc add-sheet --project holdings.json --name "持仓明细"
echo '[["代码","名称","持仓","盈亏率"],["00700","腾讯","2500","-6.5%"],["00883","中海油","11000","+43.4%"]]' > holdings_data.json
cli-anything-libreoffice calc fill-data --project holdings.json --data holdings_data.json

# Export to Excel
cli-anything-libreoffice export render holdings.xlsx --project holdings.json --type xlsx
```

---

## 📞 Support

For issues or feature requests, refer to:
- Test plan: `TEST.md`
- Test suite: `test_cli_lo.py`
- Source code: `cli_lo.py`

---

*Built with CLI-Anything methodology*  
*Last Updated: 2026-03-19*
