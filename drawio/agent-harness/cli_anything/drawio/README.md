# Draw.io CLI

A Click-based command-line interface for creating and editing Draw.io diagrams programmatically, designed for investment analysis workflows.

## Features

- ✅ Create diagrams (flowcharts, org charts, mindmaps)
- ✅ Add shapes, connectors, and text
- ✅ Investment chart templates (asset allocation, price charts, investment flows)
- ✅ Export to PNG/SVG/PDF (requires Draw.io CLI)
- ✅ JSON output mode for automation
- ✅ Stateful operations with project files

## Installation

```bash
cd /home/admin/openclaw/workspace/drawio/agent-harness
pip install -e .
```

## Quick Start

### Create a New Diagram

```bash
# Create a new flowchart
cli-anything-drawio diagram new -o 投资流程.drawio

# Create using template
cli-anything-drawio --template asset-allocation -o 资产配置.drawio

# Create with data
cli-anything-drawio --template asset-allocation --data 持仓数据.json -o 资产配置.drawio
```

### Add Elements

```bash
# Add a shape
cli-anything-drawio --project 投资流程.drawio \
  shape add --type rectangle --label "财报发布" --x 100 --y 100

# Add a connector
cli-anything-drawio --project 投资流程.drawio \
  connector add --from shape1 --to shape2 --label "下一步"

# Add text
cli-anything-drawio --project 投资流程.drawio \
  text add -t "投资决策流程" --font-size 24 --bold
```

### Export

```bash
# Export to PNG
cli-anything-drawio --project 图表.drawio \
  export render 图表.png --format png --dpi 300

# Export to SVG
cli-anything-drawio --project 图表.drawio \
  export render 图表.svg --format svg

# Export to PDF
cli-anything-drawio --project 图表.drawio \
  export render 图表.pdf --format pdf
```

### JSON Output

```bash
# Get machine-readable output
cli-anything-drawio --json diagram new -o test.drawio
cli-anything-drawio --json info
```

## Templates

| Template | Description |
|----------|-------------|
| `asset-allocation` | Asset allocation pie chart |
| `price-chart` | Stock price trend chart |
| `investment-flow` | Investment decision flowchart |
| `org` | Organization chart |
| `mindmap` | Mind map structure |

## Available Commands

```bash
cli-anything-drawio --help

# Diagram operations
cli-anything-drawio diagram new -o file.drawio

# Shape operations
cli-anything-drawio shape add --type rectangle --label "Text"

# Connector operations
cli-anything-drawio connector add --from id1 --to id2

# Text operations
cli-anything-drawio text add -t "Title" --bold

# Export operations
cli-anything-drawio export render output.png --format png

# Info
cli-anything-drawio info
cli-anything-drawio list-templates
```

## Requirements

- Python 3.8+
- Click 8.0+
- Draw.io CLI (for actual export operations)

## License

MIT License
