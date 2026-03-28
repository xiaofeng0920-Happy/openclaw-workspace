# ComfyUI CLI 快速入门

## 🚀 5 分钟上手指南

### 1. 安装（1 分钟）

```bash
cd /home/admin/openclaw/workspace/comfyui/agent-harness
pip install -e .
```

### 2. 启动 ComfyUI（1 分钟）

```bash
# 在另一个终端窗口
cd /path/to/ComfyUI
python main.py
```

### 3. 验证安装（30 秒）

```bash
cli-anything-comfyui --help
```

### 4. 生成第一个图表（2 分钟）

```bash
# 创建工作流
cli-anything-comfyui workflow new -o 测试图表.json

# 生成柱状图
cli-anything-comfyui generate chart \
  --type bar \
  --title "我的第一个图表" \
  --data '{"A": 100, "B": 150, "C": 200}' \
  --output 测试图表.png
```

---

## 📋 常用命令速查

### 工作流
```bash
# 创建
cli-anything-comfyui workflow new -o 工作流.json

# 使用模板
cli-anything-comfyui workflow new -o 财报对比.json -t 财报对比

# 加载
cli-anything-comfyui workflow load 工作流.json

# 导出
cli-anything-comfyui workflow export 工作流.json --output api 格式.json
```

### 图表生成
```bash
# 柱状图
cli-anything-comfyui generate chart \
  --type bar \
  --title "标题" \
  --data '{"key": value}' \
  --output 输出.png

# 折线图
cli-anything-comfyui generate chart \
  --type line \
  --title "标题" \
  --data 数据.json \
  --output 输出.png

# 饼图
cli-anything-comfyui generate chart \
  --type pie \
  --title "标题" \
  --data '{"A": 60, "B": 40}' \
  --output 输出.png
```

### AI 增强
```bash
# 美化
cli-anything-comfyui enhance chart \
  --input 输入.png \
  --style professional \
  --output 输出.png

# 注解
cli-anything-comfyui enhance annotate \
  --input 输入.png \
  --prompt "标注关键点" \
  --output 输出.png

# 洞察
cli-anything-comfyui enhance insight \
  --data 数据.json \
  --output 洞察.txt
```

### 批量处理
```bash
# 批量生成
cli-anything-comfyui batch generate \
  --input-dir ./数据/ \
  --output-dir ./图表/

# 批量美化
cli-anything-comfyui batch enhance \
  --input-dir ./图表/ \
  --style professional
```

### 状态检查
```bash
cli-anything-comfyui status
```

---

## 🎯 实战示例

### 示例 1：财报分析
```bash
# 1. 准备数据
cat > 腾讯财报.json << 'EOF'
{
  "title": "腾讯 2026 财报",
  "revenue": {"Q1": 1944, "Q2": 1800, "Q3": 1750, "Q4": 1944},
  "profit": {"Q1": 582, "Q2": 550, "Q3": 530, "Q4": 582}
}
EOF

# 2. 生成图表
cli-anything-comfyui generate chart \
  --type bar \
  --title "腾讯季度营收" \
  --data 腾讯财报.json \
  --template 财报对比 \
  --output 腾讯财报.png

# 3. 生成洞察
cli-anything-comfyui enhance insight \
  --data 腾讯财报.json \
  --output 腾讯洞察.txt
```

### 示例 2：持仓监控
```bash
# 批量生成所有持仓图表
cli-anything-comfyui batch generate \
  --input-dir ./持仓数据/ \
  --output-dir ./图表/ \
  --template 持仓盈亏

# 批量美化
cli-anything-comfyui batch enhance \
  --input-dir ./图表/ \
  --style professional
```

### 示例 3：资产配置
```bash
# 生成饼图
cli-anything-comfyui generate chart \
  --type pie \
  --title "全球资产配置" \
  --data '{"美股": 60, "港股": 23, "商品": 10, "现金": 7}' \
  --output 资产配置.png

# 添加注解
cli-anything-comfyui enhance annotate \
  --input 资产配置.png \
  --prompt "标注各资产类别和百分比" \
  --output 资产配置_标注.png
```

---

## ⚠️ 常见问题

### Q: 无法连接到 ComfyUI
```
❌ 无法连接到 ComfyUI
```

**解决：**
```bash
# 启动 ComfyUI
cd /path/to/ComfyUI
python main.py
```

### Q: 数据格式错误
```
❌ 数据解析失败
```

**解决：** 确保 JSON 格式正确：
```bash
# ✅ 正确
'{"key": 123}'

# ❌ 错误
'{key: 123}'
```

### Q: 文件不存在
```
❌ 文件不存在：xxx.json
```

**解决：** 检查路径，使用绝对路径。

---

## 📖 下一步

- 阅读完整文档：`README.md`
- 查看测试计划：`TEST.md`
- 学习模板使用：`templates/` 目录

---

*最后更新：2026-03-19*
