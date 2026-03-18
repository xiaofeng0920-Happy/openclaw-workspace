# Draw.io CLI 需求文档

**目标：** 为投资分析生成图表绘制 CLI

---

## 🎯 核心功能

### 1. 创建图表

```bash
# 创建流程图
cli-anything-drawio diagram new -o 投资流程.drawio

# 创建组织结构图
cli-anything-drawio diagram new --type org -o 组织架构.drawio

# 创建思维导图
cli-anything-drawio diagram new --type mindmap -o 投资逻辑.drawio
```

### 2. 添加元素

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

### 3. 投资图表模板

```bash
# 资产配置饼图
cli-anything-drawio --template asset-allocation \
  --data 持仓数据.json -o 资产配置图.drawio

# 股价走势图
cli-anything-drawio --template price-chart \
  --data 股价数据.json -o 股价走势.drawio

# 投资流程图
cli-anything-drawio --template investment-flow \
  -o 投资流程.drawio
```

### 4. 导出功能

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

## 📊 图表模板

### 模板 1：资产配置图

```
┌─────────────────────────────────┐
│        资产配置（2026-03-18）     │
├─────────────────────────────────┤
│                                 │
│         🥧 饼图                  │
│    美股 60% / 港股 23% / 现金 17%  │
│                                 │
└─────────────────────────────────┘
```

### 模板 2：投资流程图

```
财报发布 → 数据分析 → 持仓评估 → 操作建议 → 执行交易
   ↓          ↓          ↓          ↓          ↓
业绩会    盈亏计算    风险评级    止盈止损    飞书通知
```

### 模板 3：股价走势图

```
股价
 ↑
 │     /\      /\
 │    /  \    /  \
 │   /    \__/    \___
 │  /                \
 │ /                  \
 └────────────────────────→ 时间
   3 月   4 月   5 月
```

---

## ✅ 验收标准

| 功能 | 测试方法 | 状态 |
|------|----------|------|
| 图表创建 | `diagram new` | ⏳ |
| 添加形状 | `shape add` | ⏳ |
| 添加连接 | `connector add` | ⏳ |
| 模板使用 | `--template` | ⏳ |
| 导出 PNG | `export render xxx.png` | ⏳ |

---

*创建时间：2026-03-19*  
*状态：⏳ 等待生成*
