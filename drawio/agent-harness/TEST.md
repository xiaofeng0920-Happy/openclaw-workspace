# Draw.io CLI - Test Plan

## Test Strategy

This test suite validates the Draw.io CLI harness across multiple dimensions:

1. **Unit Tests** - Core backend functionality
2. **Integration Tests** - CLI command execution
3. **End-to-End Tests** - Full workflow validation
4. **Template Tests** - Investment chart templates

---

## Test Categories

### 1. Backend Unit Tests (`test_backend.py`)

| Test | Description | Expected |
|------|-------------|----------|
| `test_create_new` | Create new diagram structure | Valid XML root |
| `test_add_shape` | Add shape to diagram | Shape ID returned |
| `test_add_connector` | Connect two shapes | Connector ID returned |
| `test_add_text` | Add text element | Text ID returned |
| `test_save_load` | Save and reload file | Data preserved |
| `test_export_info` | Export metadata creation | JSON info file |

### 2. CLI Command Tests (`test_cli_commands.py`)

| Test | Description | Expected |
|------|-------------|----------|
| `test_diagram_new` | Create new diagram | File created |
| `test_shape_add` | Add shape via CLI | Success message |
| `test_connector_add` | Add connector via CLI | Success message |
| `test_text_add` | Add text via CLI | Success message |
| `test_export_render` | Export diagram | Export info created |
| `test_json_output` | JSON mode output | Valid JSON |

### 3. Template Tests (`test_templates.py`)

| Test | Template | Expected |
|------|----------|----------|
| `test_asset_allocation` | Asset allocation chart | Pie chart structure |
| `test_price_chart` | Price trend chart | Axes and data points |
| `test_investment_flow` | Investment flowchart | Flow structure |
| `test_org_chart` | Organization chart | Hierarchy structure |
| `test_mindmap` | Mind map | Central topic + branches |

### 4. End-to-End Tests (`test_full_e2e.py`)

| Test | Workflow | Expected |
|------|----------|----------|
| `test_create_and_export` | Create → Add elements → Export | Complete workflow |
| `test_template_with_data` | Template + JSON data → Export | Data-driven chart |
| `test_investment_workflow` | Full investment analysis flow | All templates work |

---

## Test Execution

### Run All Tests

```bash
cd /home/admin/openclaw/workspace/drawio/agent-harness
pytest cli_anything/drawio/tests/ -v
```

### Run Specific Category

```bash
# Unit tests only
pytest cli_anything/drawio/tests/test_backend.py -v

# CLI tests only
pytest cli_anything/drawio/tests/test_cli_commands.py -v

# Template tests only
pytest cli_anything/drawio/tests/test_templates.py -v

# E2E tests only
pytest cli_anything/drawio/tests/test_full_e2e.py -v
```

### Run with Coverage

```bash
pytest cli_anything/drawio/tests/ --cov=cli_anything.drawio --cov-report=html
```

---

## Validation Commands

After installation:

```bash
# Verify installation
cli-anything-drawio --help

# List templates
cli-anything-drawio list-templates

# Create test diagram
cli-anything-drawio diagram new -o /tmp/test.drawio

# Verify file created
ls -la /tmp/test.drawio

# Add shape
cli-anything-drawio --project /tmp/test.drawio shape add -l "Test" -x 100 -y 100

# Show info
cli-anything-drawio --project /tmp/test.drawio info
```

---

## Success Criteria

- ✅ All unit tests pass (100% backend coverage)
- ✅ All CLI commands execute without errors
- ✅ All templates generate valid .drawio files
- ✅ Export info files created correctly
- ✅ JSON output mode works
- ✅ Files can be opened in Draw.io desktop/web app

---

## Known Limitations

1. **Export requires Draw.io CLI** - Actual PNG/SVG/PDF export requires separate Draw.io CLI installation
2. **No real-time collaboration** - Draw.io doesn't support collaborative editing in this version
3. **XML-based** - Complex styling may require manual XML editing

---

*Created: 2026-03-19*  
*Status: ⏳ Pending Implementation*
