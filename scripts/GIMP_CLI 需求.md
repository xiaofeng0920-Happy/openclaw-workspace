# GIMP CLI 需求文档

**目标：** 批量处理投资图表截图

---

## 🎯 核心功能

### 1. 批量处理

```bash
# 批量调整尺寸
cli-anything-gimp batch resize \
  --input-dir ./图表/ \
  --output-dir ./处理后/ \
  --width 1920 --height 1080

# 批量添加水印
cli-anything-gimp batch watermark \
  --input-dir ./图表/ \
  --output-dir ./处理后/ \
  --text "锋哥持仓 © 2026" \
  --position bottom-right

# 批量格式转换
cli-anything-gimp batch convert \
  --input-dir ./图表/ \
  --output-dir ./处理后/ \
  --format png
```

### 2. 图片编辑

```bash
# 打开图片
cli-anything-gimp image open 走势图.png -o 走势图.xcf

# 添加文字标注
cli-anything-gimp --project 走势图.xcf \
  text add -t "+13.5%" --x 100 --y 50 --font-size 24 --color "#00aa00"

# 添加箭头
cli-anything-gimp --project 走势图.xcf \
  arrow add --from 100,100 --to 200,200 --color "#ff0000"

# 添加高亮框
cli-anything-gimp --project 走势图.xcf \
  highlight add --x 150 --y 150 --width 100 --height 50 \
  --color "#ffff00" --opacity 0.3
```

### 3. 图表优化

```bash
# 调整亮度/对比度
cli-anything-gimp --project 走势图.xcf \
  adjust brightness --value 10 --contrast 5

# 锐化
cli-anything-gimp --project 走势图.xcf \
  filter sharpen --radius 2

# 添加边框
cli-anything-gimp --project 走势图.xcf \
  border add --width 5 --color "#000000"
```

### 4. 导出功能

```bash
# 导出 PNG
cli-anything-gimp --project 走势图.xcf \
  export render 走势图.png --format png

# 导出 JPG
cli-anything-gimp --project 走势图.xcf \
  export render 走势图.jpg --format jpg --quality 95

# 批量导出
cli-anything-gimp --project 走势图.xcf \
  export all --formats png,jpg,pdf
```

---

## 📊 使用场景

### 场景 1：财报截图处理

```bash
# 1. 截取财报数据
# 2. 批量添加水印
cli-anything-gimp batch watermark \
  --input-dir ./财报截图/ \
  --text "腾讯 4Q25 业绩"

# 3. 调整尺寸
cli-anything-gimp batch resize \
  --width 1200 --height 800

# 4. 插入到报告
cli-anything-libreoffice --project 投资报告.json \
  writer add-image --path 处理后/腾讯业绩.png
```

### 场景 2：走势图标注

```bash
# 1. 打开走势图
cli-anything-gimp image open 腾讯走势.png -o 腾讯走势.xcf

# 2. 添加关键点标注
cli-anything-gimp --project 腾讯走势.xcf \
  text add -t "业绩发布 +3%" --x 300 --y 200

# 3. 添加箭头指示
cli-anything-gimp --project 腾讯走势.xcf \
  arrow add --from 300,200 --to 400,250

# 4. 导出
cli-anything-gimp --project 腾讯走势.xcf \
  export render 腾讯走势_标注.png
```

---

## ✅ 验收标准

| 功能 | 测试方法 | 状态 |
|------|----------|------|
| 批量处理 | `batch resize/watermark` | ⏳ |
| 图片编辑 | `text add/arrow add` | ⏳ |
| 滤镜效果 | `filter sharpen` | ⏳ |
| 格式转换 | `export render` | ⏳ |
| 水印添加 | `batch watermark` | ⏳ |

---

*创建时间：2026-03-19*  
*状态：⏳ 等待生成*
