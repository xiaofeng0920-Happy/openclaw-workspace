# Draw.io CLI - 投资分析图表工具

## 📋 概述

这是一个基于 CLI-Anything 方法论构建的 Draw.io 命令行工具，专为投资分析系统设计。支持创建流程图、资产配置图、股价走势图等投资相关图表。

---

## 🎯 核心功能

### 1. 图表创建
- ✅ 创建流程图 (flowchart)
- ✅ 创建组织结构图 (org chart)
- ✅ 创建思维导图 (mindmap)
- ✅ 投资图表模板

### 2. 元素操作
- ✅ 添加形状 (rectangle, ellipse, rhombus, etc.)
- ✅ 添加连接线 (connector)
- ✅ 添加文本 (text)
- ✅ 自定义样式

### 3. 投资模板
- ✅ 资产配置图 (asset-allocation)
- ✅ 股价走势图 (price-chart)
- ✅ 投资流程图 (investment-flow)

### 4. 导出功能
- ✅ PNG 导出 (需要 Draw.io CLI)
- ✅ SVG 导出 (需要 Draw.io CLI)
- ✅ PDF 导出 (需要 Draw.io CLI)
- ✅ JSON 输出模式

---

## 📦 安装

```bash
cd /home/admin/openclaw/workspace/drawio/agent-harness
pip install -e .
```

验证安装:
```bash
cli-anything-drawio --help
```

---

## 🚀 快速开始

### 创建新图表

```bash
# 创建空白图表
cli-anything-drawio diagram new -o 投资流程.drawio

# 使用模板创建
cli-anything-drawio --template asset-allocation -o 资产配置.drawio

# 使用模板 + 数据
cli-anything-drawio --template asset-allocation --data 持仓数据.json -o 资产配置.drawio
```

### 添加元素

```bash
# 添加形状
cli-anything-drawio --project 投资流程.drawio \
  shape add --type rectangle --label "财报发布" --x 100 --y 100

# 添加连接线
cli-anything-drawio --project 投资流程.drawio \
  connector add --from shape1 --to shape2 --label "下一步"

# 添加文本
cli-anything-drawio --project 投资流程.drawio \
  text add -t "投资决策流程" --font-size 24 --bold
```

### 导出图表

```bash
# 导出 PNG
cli-anything-drawio --project 资产配置图.drawio \
  export render 资产配置图.png --format png --dpi 300

# 导出 SVG
cli-anything-drawio --project 投资流程.drawio \
  export render 投资流程.svg --format svg

# 导出 PDF
cli-anything-drawio --project 投资流程.drawio \
  export render 投资流程.pdf --format pdf
```

---

## 📊 模板说明

### 资产配置图 (asset-allocation)

创建资产配置饼图，显示各资产类别占比。

```bash
# 默认配置
cli-anything-drawio --template asset-allocation -o 资产配置.drawio

# 自定义数据
# 持仓数据.json: {"美股": "60%", "港股": "23%", "现金": "17%"}
cli-anything-drawio --template asset-allocation --data 持仓数据.json -o 资产配置.drawio
```

### 股价走势图 (price-chart)

创建股价趋势图表。

```bash
# 示例图表
cli-anything-drawio --template price-chart -o 股价走势.drawio

# 带数据
# 股价数据.json: {"prices": [100, 105, 102, 108, 110]}
cli-anything-drawio --template price-chart --data 股价数据.json -o 股价走势.drawio
```

### 投资流程图 (investment-flow)

创建投资决策流程图。

```bash
cli-anything-drawio --template investment-flow -o 投资流程.drawio
```

流程图结构:
```
财报发布 → 数据分析 → 持仓评估 → 操作建议 → 执行交易
   ↓          ↓          ↓          ↓          ↓
业绩会    盈亏计算    风险评级    止盈止损    飞书通知
```

---

## 🔧 命令参考

### diagram 命令组

| 命令 | 说明 | 示例 |
|------|------|------|
| `diagram new` | 创建新图表 | `diagram new -o test.drawio` |

### shape 命令组

| 命令 | 说明 | 示例 |
|------|------|------|
| `shape add` | 添加形状 | `shape add --type rectangle --label "文本"` |

**形状类型:**
- `rectangle` - 矩形
- `ellipse` - 椭圆
- `rhombus` - 菱形
- `triangle` - 三角形
- `cylinder` - 圆柱
- `document` - 文档
- `folder` - 文件夹
- `cloud` - 云朵
- `actor` - 人物
- `process` - 流程框
- `decision` - 决策框

### connector 命令组

| 命令 | 说明 | 示例 |
|------|------|------|
| `connector add` | 添加连接线 | `connector add --from shape1 --to shape2` |

### text 命令组

| 命令 | 说明 | 示例 |
|------|------|------|
| `text add` | 添加文本 | `text add -t "标题" --bold` |

### export 命令组

| 命令 | 说明 | 示例 |
|------|------|------|
| `export render` | 导出图表 | `export render output.png --format png` |

**导出格式:**
- `png` - PNG 图片 (支持 --dpi 参数)
- `svg` - SVG 矢量图
- `pdf` - PDF 文档

### 其他命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `info` | 显示图表信息 | `info` |
| `list-templates` | 列出模板 | `list-templates` |

---

## 🧪 测试

运行测试套件:

```bash
cd /home/admin/openclaw/workspace/drawio/agent-harness

# 运行所有测试
pytest cli_anything/drawio/tests/ -v

# 运行特定测试类别
pytest cli_anything/drawio/tests/test_backend.py -v
pytest cli_anything/drawio/tests/test_cli_commands.py -v
pytest cli_anything/drawio/tests/test_templates.py -v
pytest cli_anything/drawio/tests/test_full_e2e.py -v

# 带覆盖率
pytest cli_anything/drawio/tests/ --cov=cli_anything.drawio --cov-report=html
```

---

## 📁 项目结构

```
drawio/agent-harness/
├── setup.py                          # 安装脚本
├── DRAWIO.md                         # 使用说明
├── TEST.md                           # 测试计划
└── cli_anything/drawio/
    ├── __init__.py                   # 包初始化
    ├── __main__.py                   # 入口点
    ├── drawio_cli.py                 # CLI 主程序
    ├── README.md                     # 包文档
    ├── py.typed                      # 类型标记
    ├── core/
    │   └── __init__.py
    ├── utils/
    │   ├── __init__.py
    │   └── drawio_backend.py         # 后端实现
    └── tests/
        ├── __init__.py
        ├── test_backend.py           # 后端测试
        ├── test_cli_commands.py      # CLI 测试
        ├── test_templates.py         # 模板测试
        └── test_full_e2e.py          # E2E 测试
```

---

## ⚠️ 注意事项

1. **导出功能**: 实际 PNG/SVG/PDF 导出需要安装 Draw.io CLI 工具
   - 下载地址: https://github.com/jgraph/drawio-desktop/releases
   - 命令: `draw.io -x input.drawio -o output.png --dpi 300`

2. **文件格式**: .drawio 文件是 XML 格式，可以用文本编辑器查看

3. **JSON 模式**: 使用 `--json` 参数获取机器可读输出，适合自动化脚本

---

## 📝 示例工作流

### 完整投资分析图表创建

```bash
# 1. 创建资产配置图
cli-anything-drawio --template asset-allocation \
  --data 持仓数据.json -o 资产配置.drawio

# 2. 创建投资流程图
cli-anything-drawio --template investment-flow -o 投资流程.drawio

# 3. 添加自定义步骤
cli-anything-drawio --project 投资流程.drawio \
  shape add --type decision --label "规模预警" --x 500 --y 400

# 4. 导出所有图表
cli-anything-drawio --project 资产配置.drawio \
  export render 资产配置.png --format png

cli-anything-drawio --project 投资流程.drawio \
  export render 投资流程.png --format png
```

---

## 🔗 相关链接

- [Draw.io 官网](https://app.diagrams.net/)
- [Draw.io GitHub](https://github.com/jgraph/drawio)
- [CLI-Anything 方法论](https://github.com/jgraph/drawio)

---

*版本：1.0.0*  
*创建时间：2026-03-19*  
*用途：投资分析系统 - 图表绘制工具*
