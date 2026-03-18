# CLI 工具生成计划

**创建时间：** 2026-03-19  
**目标：** 使用 CLI-Anything 生成 4 个投资分析专用 CLI 工具

---

## 📋 生成清单

| # | CLI 工具 | 用途 | 优先级 | 状态 |
|---|---------|------|--------|------|
| 1 | LibreOffice CLI | 自动生成投资报告 PDF | 🔴 | ⏳ 待生成 |
| 2 | Draw.io CLI | 绘制投资流程图 | 🟡 | ⏳ 待生成 |
| 3 | GIMP CLI | 批量处理图表截图 | 🟢 | ⏳ 待生成 |
| 4 | ComfyUI CLI | AI 生成投资可视化 | 🟢 | ⏳ 待生成 |

---

## 📁 需求文档

所有需求文档已准备就绪：

| 文件 | 内容 |
|------|------|
| `LibreOffice_CLI 需求.md` | ✅ 已创建（2,580 bytes） |
| `Draw.io_CLI 需求.md` | ✅ 已创建（2,134 bytes） |
| `GIMP_CLI 需求.md` | ✅ 已创建（2,402 bytes） |
| `ComfyUI_CLI 需求.md` | ✅ 已创建（2,356 bytes） |

---

## 🚀 生成方法

### 方法 1：逐个生成（推荐）

在 OpenClaw 中依次执行：

```
1. @cli-anything 为 LibreOffice 构建 CLI
   用途：投资报告生成
   
2. @cli-anything 为 Draw.io 构建 CLI
   用途：流程图绘制
   
3. @cli-anything 为 GIMP 构建 CLI
   用途：图表批量处理
   
4. @cli-anything 为 ComfyUI 构建 CLI
   用途：AI 可视化
```

### 方法 2：批量生成

一次性命令：
```
使用 CLI-Anything 依次生成 LibreOffice、Draw.io、GIMP、ComfyUI 的 CLI 工具，用于投资分析系统
```

---

## ⏱️ 预计时间

| CLI | 预计时间 | 测试时间 |
|-----|---------|---------|
| LibreOffice | 15 分钟 | 10 分钟 |
| Draw.io | 10 分钟 | 5 分钟 |
| GIMP | 10 分钟 | 10 分钟 |
| ComfyUI | 15 分钟 | 10 分钟 |
| **总计** | **50 分钟** | **35 分钟** |

---

## 📊 生成后验证

### 1. 安装验证

```bash
# 进入生成的目录
cd libreoffice/agent-harness

# 安装
pip install -e .

# 验证
cli-anything-libreoffice --help
```

### 2. 功能测试

```bash
# LibreOffice CLI 测试
cli-anything-libreoffice document new --type writer -o 测试.json
cli-anything-libreoffice export render 测试.pdf --type pdf

# Draw.io CLI 测试
cli-anything-drawio diagram new -o 测试.drawio
cli-anything-drawio export render 测试.png --format png

# GIMP CLI 测试
cli-anything-gimp image open 测试.png -o 测试.xcf
cli-anything-gimp export render 测试_out.png

# ComfyUI CLI 测试
cli-anything-comfyui generate chart --type bar --data '{"A": 100}' --output 测试.png
```

---

## 🎯 集成到投资分析系统

### 当前流程
```
数据收集 → 分析 → Markdown 报告 → 飞书文字
```

### 新流程
```
数据收集 → 分析 → 
  ├─ LibreOffice → PDF 报告
  ├─ Draw.io → 流程图
  ├─ GIMP → 优化图表
  └─ ComfyUI → AI 可视化
      ↓
飞书文字 + PDF 附件 + 图表
```

---

## 📝 下一步行动

| 步骤 | 操作 | 预计时间 |
|------|------|---------|
| 1 | 生成 LibreOffice CLI | 15 分钟 |
| 2 | 测试 LibreOffice CLI | 10 分钟 |
| 3 | 生成 Draw.io CLI | 10 分钟 |
| 4 | 生成 GIMP CLI | 10 分钟 |
| 5 | 生成 ComfyUI CLI | 15 分钟 |
| 6 | 集成测试 | 30 分钟 |

---

## ✅ 验收标准

| CLI | 功能验收 | 集成验收 | 状态 |
|-----|---------|---------|------|
| LibreOffice | 能生成 PDF | 能插入报告 | ⏳ |
| Draw.io | 能绘制图表 | 能导出 PNG | ⏳ |
| GIMP | 能批量处理 | 能添加水印 | ⏳ |
| ComfyUI | 能生成图表 | 能 AI 美化 | ⏳ |

---

*创建时间：2026-03-19*  
*状态：📋 准备就绪，等待执行*
