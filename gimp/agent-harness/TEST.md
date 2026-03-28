# CLI-Anything GIMP - Test Plan

## Test Environment

- **GIMP Version:** 2.10.30
- **Python:** 3.10+
- **OS:** Linux (Ubuntu 22.04)
- **Test Directory:** `/home/admin/openclaw/workspace/gimp/agent-harness/test_data/`

## Test Categories

### 1. Installation Tests
- [ ] Package installs without errors
- [ ] CLI commands are accessible
- [ ] Help text displays correctly

### 2. Batch Processing Tests
- [ ] Batch resize works on multiple images
- [ ] Batch watermark adds text correctly
- [ ] Batch convert changes format properly

### 3. Project Operation Tests
- [ ] Text annotation adds correctly
- [ ] Arrow annotation draws properly
- [ ] Highlight box appears with correct opacity
- [ ] Brightness/contrast adjustment works
- [ ] Sharpen filter applies correctly
- [ ] Border addition works

### 4. Export Tests
- [ ] PNG export works
- [ ] JPG export with quality control
- [ ] PDF export works
- [ ] Multi-format export works

### 5. Error Handling Tests
- [ ] Missing input directory handled
- [ ] Invalid coordinates handled
- [ ] Missing --project flag handled
- [ ] GIMP timeout handled

## Test Commands

### Installation Test
```bash
# Verify installation
cli-anything-gimp --help
cli-anything-gimp batch --help
cli-anything-gimp project --help
cli-anything-gimp export --help
```

### Batch Resize Test
```bash
# Create test directory
mkdir -p test_data/input test_data/output

# Generate test images (using ImageMagick or sample images)
# Then run:
cli-anything-gimp batch resize \
  --input-dir test_data/input \
  --output-dir test_data/output \
  --width 800 --height 600 \
  --verbose

# Verify output
ls -la test_data/output/
```

### Batch Watermark Test
```bash
cli-anything-gimp batch watermark \
  --input-dir test_data/input \
  --output-dir test_data/output \
  --text "Test Watermark" \
  --position bottom-right \
  --verbose
```

### Batch Convert Test
```bash
cli-anything-gimp batch convert \
  --input-dir test_data/input \
  --output-dir test_data/output_jpg \
  --format jpg \
  --verbose
```

### Image Open Test
```bash
cli-anything-gimp image open \
  test_data/input/sample.png \
  -o test_data/sample.xcf \
  --verbose
```

### Project Operations Test
```bash
# Add text
cli-anything-gimp --project test_data/sample.xcf \
  project text add \
  -t "Test Text" \
  --x 50 --y 50 \
  --verbose

# Add arrow
cli-anything-gimp --project test_data/sample.xcf \
  project arrow add \
  --from 100,100 \
  --to 200,200 \
  --verbose

# Add highlight
cli-anything-gimp --project test_data/sample.xcf \
  project highlight add \
  --x 150 --y 150 \
  --width 100 --height 50 \
  --verbose

# Adjust brightness
cli-anything-gimp --project test_data/sample.xcf \
  project adjust brightness \
  --brightness 10 --contrast 5 \
  --verbose

# Sharpen
cli-anything-gimp --project test_data/sample.xcf \
  project filter sharpen \
  --radius 2 \
  --verbose

# Add border
cli-anything-gimp --project test_data/sample.xcf \
  project border add \
  --width 5 \
  --verbose
```

### Export Test
```bash
# Export PNG
cli-anything-gimp --project test_data/sample.xcf \
  export render test_data/output.png \
  --format png \
  --verbose

# Export JPG
cli-anything-gimp --project test_data/sample.xcf \
  export render test_data/output.jpg \
  --format jpg --quality 90 \
  --verbose

# Export all formats
cli-anything-gimp --project test_data/sample.xcf \
  export all \
  --output-dir test_data/export_all \
  --formats png,jpg \
  --verbose
```

## Acceptance Criteria

| Test | Expected Result | Status |
|------|----------------|--------|
| Installation | CLI accessible | ⏳ |
| Batch Resize | Images resized to 800x600 | ⏳ |
| Batch Watermark | Text visible on images | ⏳ |
| Batch Convert | Format changed correctly | ⏳ |
| Text Add | Text appears at coordinates | ⏳ |
| Arrow Add | Arrow drawn between points | ⏳ |
| Highlight Add | Box with opacity visible | ⏳ |
| Brightness | Image brighter/darker | ⏳ |
| Sharpen | Image sharper | ⏳ |
| Border | Border visible | ⏳ |
| Export PNG | PNG file created | ⏳ |
| Export JPG | JPG file created | ⏳ |
| Export All | Multiple files created | ⏳ |

## Performance Benchmarks

- **Batch Resize:** < 5 seconds per image
- **Batch Watermark:** < 5 seconds per image
- **Batch Convert:** < 3 seconds per image
- **Project Operations:** < 2 seconds per operation
- **Export:** < 3 seconds per format

## Cleanup

```bash
# Remove test data
rm -rf test_data/
```
