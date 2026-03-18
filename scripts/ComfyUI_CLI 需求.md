# ComfyUI CLI 需求文档

**目标：** AI 生成投资可视化图表

---

## 🎯 核心功能

### 1. 工作流管理

```bash
# 创建工作流
cli-anything-comfyui workflow new -o 投资图表.json

# 加载工作流
cli-anything-comfyui workflow load 投资图表.json

# 导出工作流
cli-anything-comfyui workflow export 投资图表.json --output 投资图表_api.json
```

### 2. 图表生成

```bash
# 生成柱状图
cli-anything-comfyui generate chart \
  --type bar \
  --title "腾讯季度营收" \
  --data '{"Q1": 1944, "Q2": 1800, "Q3": 1750, "Q4": 1944}' \
  --output 营收柱状图.png

# 生成折线图
cli-anything-comfyui generate chart \
  --type line \
  --title "股价走势" \
  --data 股价数据.json \
  --output 股价走势.png

# 生成饼图
cli-anything-comfyui generate chart \
  --type pie \
  --title "资产配置" \
  --data '{"美股": 60, "港股": 23, "现金": 17}' \
  --output 资产配置.png
```

### 3. AI 增强

```bash
# AI 美化图表
cli-anything-comfyui enhance chart \
  --input 基础图表.png \
  --style professional \
  --output 美化图表.png

# AI 添加注解
cli-anything-comfyui enhance annotate \
  --input 股价走势.png \
  --prompt "标注关键转折点和事件" \
  --output  annotated.png

# AI 生成洞察
cli-anything-comfyui enhance insight \
  --data 财报数据.json \
  --prompt "生成 3 个关键投资洞察" \
  --output 投资洞察.txt
```

### 4. 批量生成

```bash
# 批量生成持仓图表
cli-anything-comfyui batch generate \
  --input-dir ./持仓数据/ \
  --output-dir ./图表/ \
  --template 投资图表

# 批量美化
cli-anything-comfyui batch enhance \
  --input-dir ./图表/ \
  --style professional
```

---

## 📊 图表模板

### 模板 1：财报对比图

```
┌─────────────────────────────────┐
│     腾讯控股 季度对比              │
├─────────────────────────────────┤
│  营收    ████ 1944 亿 +13%       │
│  利润    ████ 582 亿 +17%        │
│  毛利率  ████████ 45% +4pcts     │
└─────────────────────────────────┘
```

### 模板 2：持仓盈亏图

```
盈亏
 ↑
 │  ✅ 中海油 +43%
 │  ✅ 伯克希尔 +11%
 │  ✅ 可口可乐 +10%
 │  ──────────────
 │  ❌ 微软 -14%
 │  ❌ 南方日经 -10%
 └────────────────→
```

### 模板 3：资产配置图

```
    ┌──────────────┐
    │  资产配置     │
    │              │
    │   美股 60%   │
    │  ╭─────╮     │
    │  │     │ 港股│
    │  │     │ 23% │
    │  ╰─────╯     │
    │   现金 17%   │
    └──────────────┘
```

---

## 🔄 集成到报告流程

```
1. 收集数据 → 2. ComfyUI 生成图表 → 3. GIMP 优化 → 4. LibreOffice 插入 → 5. 导出 PDF
```

---

## ✅ 验收标准

| 功能 | 测试方法 | 状态 |
|------|----------|------|
| 工作流创建 | `workflow new` | ⏳ |
| 图表生成 | `generate chart` | ⏳ |
| AI 美化 | `enhance chart` | ⏳ |
| 批量处理 | `batch generate` | ⏳ |
| 模板使用 | `--template` | ⏳ |

---

*创建时间：2026-03-19*  
*状态：⏳ 等待生成*
