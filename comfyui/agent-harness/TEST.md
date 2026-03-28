# ComfyUI CLI 测试计划

## 测试环境

- **ComfyUI 版本：** 最新稳定版
- **Python 版本：** 3.10+
- **测试地址：** http://127.0.0.1:8188

---

## 测试用例

### 1. 工作流管理

#### 1.1 创建工作流
```bash
# 测试命令
cli-anything-comfyui workflow new -o 投资图表.json

# 预期结果
✅ 工作流已创建：投资图表.json
✅ 文件包含有效的 JSON 工作流数据
```

#### 1.2 使用模板创建工作流
```bash
# 测试命令
cli-anything-comfyui workflow new -o 财报对比.json -t 财报对比

# 预期结果
✅ 使用财报对比模板创建工作流
✅ 工作流包含正确的节点配置
```

#### 1.3 加载工作流
```bash
# 测试命令
cli-anything-comfyui workflow load 投资图表.json

# 预期结果
✅ 工作流成功提交到 ComfyUI
✅ 返回 prompt_id
✅ 工作流执行完成
```

#### 1.4 导出工作流
```bash
# 测试命令
cli-anything-comfyui workflow export 投资图表.json --output 投资图表_api.json

# 预期结果
✅ 导出为 API 格式
✅ 包含 client_id 字段
```

---

### 2. 图表生成

#### 2.1 生成柱状图
```bash
# 测试命令
cli-anything-comfyui generate chart \
  --type bar \
  --title "腾讯季度营收" \
  --data '{"Q1": 1944, "Q2": 1800, "Q3": 1750, "Q4": 1944}' \
  --output 营收柱状图.png

# 预期结果
✅ 图表生成成功
✅ 输出文件存在
✅ 图片尺寸正确（1024x1024）
```

#### 2.2 生成折线图
```bash
# 测试命令
cli-anything-comfyui generate chart \
  --type line \
  --title "股价走势" \
  --data 股价数据.json \
  --output 股价走势.png

# 预期结果
✅ 从 JSON 文件读取数据
✅ 生成折线图
```

#### 2.3 生成饼图
```bash
# 测试命令
cli-anything-comfyui generate chart \
  --type pie \
  --title "资产配置" \
  --data '{"美股": 60, "港股": 23, "现金": 17}' \
  --output 资产配置.png

# 预期结果
✅ 生成饼图
✅ 百分比正确
```

#### 2.4 使用模板生成
```bash
# 测试命令
cli-anything-comfyui generate chart \
  --type bar \
  --title "持仓盈亏" \
  --data 持仓数据.json \
  --template 持仓盈亏 \
  --output 持仓盈亏图.png

# 预期结果
✅ 使用预设模板样式
✅ 图表符合模板设计
```

---

### 3. AI 增强

#### 3.1 AI 美化图表
```bash
# 测试命令
cli-anything-comfyui enhance chart \
  --input 基础图表.png \
  --style professional \
  --output 美化图表.png

# 预期结果
✅ 图片上传成功
✅ 美化处理完成
✅ 输出图片质量提升
```

#### 3.2 AI 添加注解
```bash
# 测试命令
cli-anything-comfyui enhance annotate \
  --input 股价走势.png \
  --prompt "标注关键转折点和事件" \
  --output annotated.png

# 预期结果
✅ 注解添加成功
✅ 关键位置正确标注
```

#### 3.3 AI 生成洞察
```bash
# 测试命令
cli-anything-comfyui enhance insight \
  --data 财报数据.json \
  --prompt "生成 3 个关键投资洞察" \
  --output 投资洞察.txt

# 预期结果
✅ 生成 3 条洞察
✅ 洞察基于实际数据
✅ 输出为文本文件
```

---

### 4. 批量处理

#### 4.1 批量生成图表
```bash
# 测试命令
cli-anything-comfyui batch generate \
  --input-dir ./持仓数据/ \
  --output-dir ./图表/ \
  --template 投资图表

# 预期结果
✅ 处理所有 JSON 文件
✅ 输出到指定目录
✅ 显示进度
```

#### 4.2 批量美化
```bash
# 测试命令
cli-anything-comfyui batch enhance \
  --input-dir ./图表/ \
  --style professional

# 预期结果
✅ 处理所有图片文件
✅ 应用统一风格
✅ 显示进度
```

---

### 5. 状态检查

#### 5.1 检查 ComfyUI 状态
```bash
# 测试命令
cli-anything-comfyui status

# 预期结果
✅ 显示 ComfyUI 运行状态
✅ 显示内存和显存信息
✅ 连接失败时显示友好错误
```

---

### 6. 错误处理

#### 6.1 文件不存在
```bash
# 测试命令
cli-anything-comfyui workflow load 不存在的文件.json

# 预期结果
✅ 显示友好错误信息
✅ 不崩溃
```

#### 6.2 数据格式错误
```bash
# 测试命令
cli-anything-comfyui generate chart \
  --type bar \
  --title "测试" \
  --data "无效 JSON" \
  --output 测试.png

# 预期结果
✅ 显示数据解析错误
✅ 提供正确格式示例
```

#### 6.3 ComfyUI 未运行
```bash
# 测试命令
cli-anything-comfyui status

# 预期结果
✅ 显示连接错误
✅ 提示启动 ComfyUI
```

---

## 测试执行

### 单元测试
```bash
pytest tests/ -v
```

### 集成测试
```bash
# 确保 ComfyUI 运行
python main.py

# 运行测试
pytest tests/integration/ -v
```

### 端到端测试
```bash
# 完整流程测试
bash tests/e2e/full_workflow_test.sh
```

---

## 验收标准

| 功能 | 测试状态 | 通过率 |
|------|----------|--------|
| 工作流创建 | ⏳ | 0/2 |
| 工作流加载 | ⏳ | 0/1 |
| 工作流导出 | ⏳ | 0/1 |
| 柱状图生成 | ⏳ | 0/1 |
| 折线图生成 | ⏳ | 0/1 |
| 饼图生成 | ⏳ | 0/1 |
| AI 美化 | ⏳ | 0/1 |
| AI 注解 | ⏳ | 0/1 |
| AI 洞察 | ⏳ | 0/1 |
| 批量生成 | ⏳ | 0/1 |
| 批量美化 | ⏳ | 0/1 |
| 状态检查 | ⏳ | 0/1 |
| 错误处理 | ⏳ | 0/3 |

**总计：** 0/15 通过

---

*创建时间：2026-03-19*  
*状态：⏳ 等待测试*
