# LibreOffice CLI - Test Plan

## Test Overview

This document outlines the comprehensive test plan for the LibreOffice CLI tool.

---

## 🧪 Test Categories

### 1. Document Creation Tests

| Test ID | Description | Command | Expected Result |
|---------|-------------|---------|-----------------|
| TC-001 | Create Writer document | `document new --type writer -o test_writer.json` | JSON file created with type="writer" |
| TC-002 | Create Calc document | `document new --type calc -o test_calc.json` | JSON file created with type="calc" |
| TC-003 | Create Impress document | `document new --type impress -o test_impress.json` | JSON file created with type="impress" |
| TC-004 | Create with template | `document new --type writer -o test.json --template template.odt` | JSON includes template path |

### 2. Writer Content Tests

| Test ID | Description | Command | Expected Result |
|---------|-------------|---------|-----------------|
| TW-001 | Add heading level 1 | `writer add-heading --project test.json -t "Title" --level 1` | Heading added to content array |
| TW-002 | Add heading level 2 | `writer add-heading --project test.json -t "Section" --level 2` | Heading with level=2 |
| TW-003 | Add paragraph | `writer add-paragraph --project test.json -t "Content..."` | Paragraph added |
| TW-004 | Add table | `writer add-table --project test.json --rows 5 --cols 3` | Table with 5x3 dimensions |
| TW-005 | Fill table | `writer fill-table --project test.json --data data.json` | Table data populated |
| TW-006 | Add image | `writer add-image --project test.json --path image.png` | Image reference added |

### 3. Calc Content Tests

| Test ID | Description | Command | Expected Result |
|---------|-------------|---------|-----------------|
| TC-101 | Add sheet | `calc add-sheet --project test.json --name "Data"` | Sheet added to sheets array |
| TC-102 | Fill data | `calc fill-data --project test.json --data spreadsheet.json` | Sheet data populated |

### 4. Style Tests

| Test ID | Description | Command | Expected Result |
|---------|-------------|---------|-----------------|
| TS-001 | Style heading | `style heading --project test.json --font-size 24 --bold` | Heading style updated |
| TS-002 | Style table | `style table --project test.json --border 1 --header-color "#f0f0f0"` | Table style updated |

### 5. Export Tests

| Test ID | Description | Command | Expected Result |
|---------|-------------|---------|-----------------|
| TE-001 | Export to PDF | `export render output.pdf --project test.json --type pdf` | PDF file created |
| TE-002 | Export to DOCX | `export render output.docx --project test.json --type docx` | DOCX file created |
| TE-003 | Export to XLSX | `export render output.xlsx --project test.json --type xlsx` | XLSX file created |
| TE-004 | Export with template | `export render output.pdf --project test.json --type pdf --template template.odt` | PDF with template styling |

### 6. Template Tests

| Test ID | Description | Command | Expected Result |
|---------|-------------|---------|-----------------|
| TT-001 | List templates | `template list --folder templates` | Template list displayed |
| TT-002 | Create template | `template create --type writer --name report` | Template file created |

### 7. Integration Tests

| Test ID | Description | Steps | Expected Result |
|---------|-------------|-------|-----------------|
| TI-001 | Full report workflow | 1. Create Writer doc<br>2. Add heading<br>3. Add table<br>4. Fill data<br>5. Export PDF | Complete PDF report |
| TI-002 | Full spreadsheet workflow | 1. Create Calc doc<br>2. Add sheet<br>3. Fill data<br>4. Export XLSX | Complete XLSX file |
| TI-003 | Investment report | Use real 财报 data to generate report | Professional PDF report |

---

## 📋 Test Data Files

### test_data_heading.json
```json
{
  "type": "heading",
  "text": "Test Heading",
  "level": 1
}
```

### test_data_table.json
```json
[
  ["指标", "数值", "同比", "状态"],
  ["营收", "1000 万", "+10%", "✅"],
  ["净利润", "500 万", "+15%", "✅"],
  ["毛利率", "45%", "+2%", "✅"]
]
```

### test_data_spreadsheet.json
```json
{
  "sheets": [
    {
      "name": "持仓明细",
      "data": [
        ["股票代码", "名称", "持仓", "成本", "现价", "盈亏率"],
        ["00700", "腾讯控股", "2500", "450", "420", "-6.5%"],
        ["00883", "中海油", "11000", "12", "17", "+43.4%"]
      ]
    }
  ]
}
```

---

## 🚀 Running Tests

### Manual Testing

```bash
# 1. Create test directory
mkdir -p /tmp/lo-cli-test
cd /tmp/lo-cli-test

# 2. Test document creation
python3 cli_lo.py document new --type writer -o test.json

# 3. Test content addition
python3 cli_lo.py writer add-heading --project test.json -t "Test Report" --level 1
python3 cli_lo.py writer add-paragraph --project test.json -t "This is a test paragraph."
python3 cli_lo.py writer add-table --project test.json --rows 4 --cols 4

# 4. Test export
python3 cli_lo.py export render test.pdf --project test.json --type pdf

# 5. Verify output
ls -la *.pdf
```

### Automated Testing

```bash
# Run test script
./run_tests.sh

# Or with pytest (if pytest tests are created)
pytest test_cli_lo.py -v
```

---

## ✅ Acceptance Criteria

### Must Pass
- [ ] All document creation tests (TC-001 to TC-004)
- [ ] All Writer content tests (TW-001 to TW-006)
- [ ] Export to PDF (TE-001)
- [ ] Full report workflow (TI-001)

### Should Pass
- [ ] All Calc content tests (TC-101 to TC-102)
- [ ] Export to DOCX and XLSX (TE-002, TE-003)
- [ ] Full spreadsheet workflow (TI-002)

### Nice to Have
- [ ] Template tests (TT-001, TT-002)
- [ ] Style tests (TS-001, TS-002)
- [ ] Investment report integration (TI-003)

---

## 🐛 Known Issues & Limitations

1. **ODT/ODS Generation**: Current implementation creates simplified text/CSV files. For production, use `odfpy` library for proper ODF format.

2. **Image Embedding**: Image support is limited to file references. Full embedding requires ODF library.

3. **Template Support**: Template application is basic. Advanced template merging requires UNO API.

4. **Headless Mode**: Requires LibreOffice installed and configured for headless operation.

---

## 📊 Test Results Template

```markdown
## Test Run: YYYY-MM-DD

**Environment:**
- LibreOffice Version: 7.3.7.2
- Python Version: 3.10.12
- OS: Linux

**Results:**
| Category | Passed | Failed | Skipped |
|----------|--------|--------|---------|
| Document Creation | X/4 | 0 | 0 |
| Writer Content | X/6 | 0 | 0 |
| Calc Content | X/2 | 0 | 0 |
| Export | X/4 | 0 | 0 |
| Integration | X/3 | 0 | 0 |
| **Total** | **X/19** | **0** | **0** |

**Notes:**
- ...
```

---

*Last Updated: 2026-03-19*  
*Version: 1.0*
