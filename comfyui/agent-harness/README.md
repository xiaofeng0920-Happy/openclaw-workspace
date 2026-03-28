# ComfyUI CLI - AI 生成投资可视化图表

一个基于 ComfyUI 的命令行工具，用于生成投资分析可视化图表。

---

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
cd /home/admin/openclaw/workspace/comfyui/agent-harness

# 安装包
pip install -e .

# 验证安装
cli-anything-comfyui --help
```

### 前置要求

1. **ComfyUI** 已安装并运行
   ```bash
   # 启动 ComfyUI
   python main.py
   ```

2. **Python 3.10+**

3. **依赖包**
   ```bash
   pip install click requests Pillow
   ```

---

## 📖 使用指南

### 1. 工作流管理

#### 创建新工作流
```bash
# 创建空白工作流
cli-anything-comfyui workflow new -o 投资图表.json

# 使用预设模板
cli-anything-comfyui workflow new -o 财报对比.json -t 财报对比
```

#### 加载工作流
```bash
cli-anything-comfyui workflow load 投资图表.json
```

#### 导出工作流
```bash
cli-anything-comfyui workflow export 投资图表.json --output 投资图表_api.json
```

---

### 2. 图表生成

#### 生成柱状图
```bash
cli-anything-comfyui generate chart \
  --type bar \
  --title "腾讯季度营收" \
  --data '{"Q1": 1944, "Q2": 1800, "Q3": 1750, "Q4": 1944}' \
  --output 营收柱状图.png
```

#### 生成折线图
```bash
# 从 JSON 文件读取数据
cli-anything-comfyui generate chart \
  --type line \
  --title "股价走势" \
  --data 股价数据.json \
  --output 股价走势.png
```

#### 生成饼图
```bash
cli-anything-comfyui generate chart \
  --type pie \
  --title "资产配置" \
  --data '{"美股": 60, "港股": 23, "现金": 17}' \
  --output 资产配置.png
```

#### 使用模板
```bash
cli-anything-comfyui generate chart \
  --type bar \
  --title "持仓盈亏" \
  --data 持仓数据.json \
  --template 持仓盈亏 \
  --output 持仓盈亏图.png
```

**可用模板：**
- `财报对比` - 财报数据对比图
- `持仓盈亏` - 持仓盈亏可视化
- `资产配置` - 资产配置饼图

---

### 3. AI 增强

#### AI 美化图表
```bash
cli-anything-comfyui enhance chart \
  --input 基础图表.png \
  --style professional \
  --output 美化图表.png
```

**可用风格：**
- `professional` - 专业风格
- `minimalist` - 极简风格
- `colorful` - 多彩风格
- `dark` - 暗黑风格

#### AI 添加注解
```bash
cli-anything-comfyui enhance annotate \
  --input 股价走势.png \
  --prompt "标注关键转折点和事件" \
  --output annotated.png
```

#### AI 生成洞察
```bash
cli-anything-comfyui enhance insight \
  --data 财报数据.json \
  --prompt "生成 3 个关键投资洞察" \
  --output 投资洞察.txt
```

---

### 4. 批量处理

#### 批量生成图表
```bash
cli-anything-comfyui batch generate \
  --input-dir ./持仓数据/ \
  --output-dir ./图表/ \
  --template 投资图表
```

#### 批量美化
```bash
cli-anything-comfyui batch enhance \
  --input-dir ./图表/ \
  --style professional
```

---

### 5. 状态检查

```bash
cli-anything-comfyui status
```

输出示例：
```
✅ ComfyUI 运行正常
   内存：8.2 GB
   显存：18.5 GB
```

---

## 📊 数据格式

### JSON 数据格式

```json
{
  "title": "腾讯季度营收",
  "data": {
    "Q1": 1944,
    "Q2": 1800,
    "Q3": 1750,
    "Q4": 1944
  },
  "unit": "亿元"
}
```

### 股价数据格式

```json
{
  "symbol": "00700.HK",
  "prices": [
    {"date": "2026-01-01", "price": 380},
    {"date": "2026-01-02", "price": 385},
    {"date": "2026-01-03", "price": 390}
  ]
}
```

### 持仓数据格式

```json
{
  "portfolio": [
    {"symbol": "GOOGL", "value": 60, "pnl": -0.03},
    {"symbol": "BRK.B", "value": 20, "pnl": 11.3},
    {"symbol": "KO", "value": 15, "pnl": 9.9},
    {"symbol": "CASH", "value": 5, "pnl": 0}
  ]
}
```

---

## 🔧 配置

### 自定义 ComfyUI 地址

```bash
# 默认：http://127.0.0.1:8188
cli-anything-comfyui --host 192.168.1.100 --port 9000 status
```

### 环境变量

```bash
export COMFYUI_HOST=192.168.1.100
export COMFYUI_PORT=9000
```

---

## 🧪 测试

### 运行单元测试
```bash
pytest tests/ -v
```

### 运行集成测试
```bash
# 确保 ComfyUI 运行
python main.py

# 运行测试
pytest tests/integration/ -v
```

### 测试覆盖率
```bash
pytest --cov=src tests/ -v
```

---

## 📁 项目结构

```
comfyui/agent-harness/
├── src/
│   └── cli_comfyui.py      # 主 CLI 实现
├── tests/
│   └── test_cli.py         # 测试套件
├── templates/               # 图表模板
│   ├── earnings_comparison.json
│   ├── portfolio_pnl.json
│   └── asset_allocation.json
├── workflows/               # 工作流示例
│   └── investment_chart.json
├── setup.py                # 安装脚本
├── README.md               # 使用文档
└── TEST.md                 # 测试计划
```

---

## 🎯 使用场景

### 场景 1：财报分析
```bash
# 1. 生成财报对比图
cli-anything-comfyui generate chart \
  --type bar \
  --title "腾讯 2026 财报" \
  --data 腾讯财报.json \
  --template 财报对比 \
  --output 腾讯财报对比.png

# 2. AI 生成洞察
cli-anything-comfyui enhance insight \
  --data 腾讯财报.json \
  --output 腾讯洞察.txt

# 3. 美化图表
cli-anything-comfyui enhance chart \
  --input 腾讯财报对比.png \
  --style professional \
  --output 腾讯财报对比_美化.png
```

### 场景 2：持仓监控
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

### 场景 3：资产配置报告
```bash
# 生成资产配置图
cli-anything-comfyui generate chart \
  --type pie \
  --title "全球资产配置" \
  --data '{"美股": 60, "港股": 23, "商品": 10, "现金": 7}' \
  --output 资产配置.png

# 添加注解
cli-anything-comfyui enhance annotate \
  --input 资产配置.png \
  --prompt "标注各资产类别名称和百分比" \
  --output 资产配置_标注.png
```

---

## ⚠️ 常见问题

### ComfyUI 未运行
```
❌ 无法连接到 ComfyUI
   请确认 ComfyUI 运行在 http://127.0.0.1:8188
```

**解决方案：**
```bash
cd /path/to/ComfyUI
python main.py
```

### 数据格式错误
```
❌ 数据解析失败：Expecting value: line 1 column 1 (char 0)
```

**解决方案：** 确保 JSON 格式正确：
```bash
# 正确格式
'{"key": "value"}'

# 错误格式
'{key: value}'  # 缺少引号
```

### 文件不存在
```
❌ 文件不存在：xxx.json
```

**解决方案：** 检查文件路径是否正确，使用绝对路径。

---

## 📝 开发指南

### 添加新图表类型

1. 在 `create_chart_workflow()` 函数中添加新类型
2. 更新 `--type` 选项的 `click.Choice`
3. 添加对应的测试用例

### 添加新模板

1. 在 `CHART_TEMPLATES` 字典中添加模板
2. 创建模板工作流文件
3. 更新文档

---

## 📄 许可证

MIT License

---

## 🙏 致谢

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) - 强大的扩散模型 GUI
- [OpenClaw](https://github.com/openclaw) - AI 代理框架

---

*最后更新：2026-03-19*  
*版本：v1.0.0*
