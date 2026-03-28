# Phase 2: 📐 Design - Command Structure

## CLI Command Hierarchy

```
cli-anything-gimp/
├── batch/                  # 批量处理命令组
│   ├── resize              # 批量调整尺寸
│   ├── watermark           # 批量添加水印
│   └── convert             # 批量格式转换
├── image/                  # 单图操作命令组
│   ├── open                # 打开图片为 XCF
│   └── process             # 单图处理
├── project/                # XCF 项目操作 (需要 --project)
│   ├── text/               # 文字标注
│   │   └── add             # 添加文字
│   ├── arrow/              # 箭头标注
│   │   └── add             # 添加箭头
│   ├── highlight/          # 高亮框
│   │   └── add             # 添加高亮框
│   ├── adjust/             # 调整
│   │   ├── brightness      # 亮度/对比度
│   │   └── color           # 色彩调整
│   ├── filter/             # 滤镜
│   │   └── sharpen         # 锐化
│   └── border/             # 边框
│       └── add             # 添加边框
└── export/                 # 导出命令组
    └── render              # 导出为指定格式
```

## Command Examples

### Batch Commands
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
  --position bottom-right \
  --font-size 24 \
  --color "#ffffff"

# 批量格式转换
cli-anything-gimp batch convert \
  --input-dir ./图表/ \
  --output-dir ./处理后/ \
  --format png
```

### Project Commands (with --project)
```bash
# 添加文字标注
cli-anything-gimp --project 走势图.xcf \
  project text add \
  -t "+13.5%" \
  --x 100 --y 50 \
  --font-size 24 \
  --color "#00aa00"

# 添加箭头
cli-anything-gimp --project 走势图.xcf \
  project arrow add \
  --from 100,100 \
  --to 200,200 \
  --color "#ff0000"

# 添加高亮框
cli-anything-gimp --project 走势图.xcf \
  project highlight add \
  --x 150 --y 150 \
  --width 100 --height 50 \
  --color "#ffff00" \
  --opacity 0.3

# 调整亮度/对比度
cli-anything-gimp --project 走势图.xcf \
  project adjust brightness \
  --brightness 10 --contrast 5

# 锐化
cli-anything-gimp --project 走势图.xcf \
  project filter sharpen \
  --radius 2

# 添加边框
cli-anything-gimp --project 走势图.xcf \
  project border add \
  --width 5 --color "#000000"
```

### Export Commands
```bash
# 导出 PNG
cli-anything-gimp --project 走势图.xcf \
  export render 走势图.png \
  --format png

# 导出 JPG
cli-anything-gimp --project 走势图.xcf \
  export render 走势图.jpg \
  --format jpg --quality 95

# 批量导出
cli-anything-gimp --project 走势图.xcf \
  export all \
  --output-dir ./导出/ \
  --formats png,jpg,pdf
```

## Script-Fu Templates

### Resize Template
```scheme
(define (batch-resize input-dir output-dir width height)
  (let* ((files (cadr (file-glob (string-append input-dir "/*") 1))))
    (while (not (null? files))
      (let* ((filename (car files))
             (basename (car (gimp_filename_basename filename)))
             (image (car (gimp-file-load RUN-NONINTERACTIVE filename filename)))
             (drawable (car (gimp-image-get-active-layer image))))
        (gimp-image-scale image width height)
        (file-png-save RUN-NONINTERACTIVE image drawable 
                       (string-append output-dir "/" basename) 
                       (string-append output-dir "/" basename) 
                       0 9 0 0 0 0 0)
        (gimp-image-delete image))
      (set! files (cdr files)))))
```

### Watermark Template
```scheme
(define (batch-watermark input-dir output-dir text position)
  (let* ((files (cadr (file-glob (string-append input-dir "/*") 1))))
    (while (not (null? files))
      (let* ((filename (car files))
             (basename (car (gimp_filename_basename filename)))
             (image (car (gimp-file-load RUN-NONINTERACTIVE filename filename)))
             (drawable (car (gimp-image-get-active-layer image)))
             (width (car (gimp-image-width image)))
             (height (car (gimp-image-height image))))
        ; Add text layer logic here
        (file-png-save RUN-NONINTERACTIVE image drawable 
                       (string-append output-dir "/" basename) 
                       (string-append output-dir "/" basename) 
                       0 9 0 0 0 0 0)
        (gimp-image-delete image))
      (set! files (cdr files)))))
```

## Implementation Strategy

1. **Python Click CLI** - User-facing commands
2. **Script-Fu Generator** - Convert CLI args to Script-Fu code
3. **GIMP Batch Executor** - Run Script-Fu via `gimp -i -b`
4. **Error Handler** - Capture and report GIMP errors

## Next Steps
- Phase 3: Implement Click CLI with all commands
- Create Script-Fu templates for each operation
- Wire up CLI → Script-Fu → GIMP pipeline
