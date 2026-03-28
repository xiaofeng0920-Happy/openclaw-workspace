# 技能调度配置

**创建日期：** 2026-03-27  
**状态：** ✅ 已激活

---

## 🎯 调度规则

### 1. 实时信息查询 → web-search

**触发场景：**
- 询问新闻、事件、最新数据
- 需要搜索互联网信息
- 查询股票/财经新闻

**示例：**
```
用户："腾讯最新财报数据"
→ 调用：web-search
```

### 2. 网页自动化任务 → browser / playwright

**触发场景：**
- 需要登录网站
- 填写表单、点击按钮
- 截图、数据抓取
- 复杂网页交互

**示例：**
```
用户："帮我登录富途查看持仓"
→ 调用：browser 或 playwright
```

### 3. 日程/邮件管理 → gog / clippy

**触发场景：**
- 创建日历事件
- 发送邮件
- 管理 Google Workspace
- Microsoft 365 操作

**示例：**
```
用户："明天下午 3 点提醒我开会"
→ 调用：gog (Google Calendar)
```

### 4. 文档管理 → clippy / gog

**触发场景：**
- 创建/编辑 Word 文档
- Excel 数据处理
- PowerPoint 演示文稿
- Google Docs/Sheets

**示例：**
```
用户："创建一份投资报告"
→ 调用：clippy (Word) 或 gog (Google Docs)
```

---

## ⚙️ 自动判断逻辑

```python
def select_skill(user_query):
    # 实时信息
    if any(kw in user_query for kw in ['搜索', '查询', '新闻', '最新', '当前']):
        return 'web-search'
    
    # 网页操作
    if any(kw in user_query for kw in ['打开网页', '登录', '点击', '截图', '抓取']):
        return 'browser'
    
    # 日程管理
    if any(kw in user_query for kw in ['提醒', '日历', '日程', '会议', '预约']):
        return 'gog'
    
    # 邮件管理
    if any(kw in user_query for kw in ['邮件', '邮箱', '发送', '回复']):
        return 'clippy'
    
    # 默认：使用现有技能或通用回答
    return 'default'
```

---

## 📋 已安装技能

| 技能 | 类别 | 状态 | 用途 |
|------|------|------|------|
| **gog** | 日程/文档 | ✅ 已安装 | Google Workspace |
| **clippy** | 办公自动化 | ⏳ 安装中 | Microsoft 365 |
| **web-search** | 搜索 | ⏳ 安装中 | 网页搜索 |
| **perplexity** | 搜索 | ⏳ 安装中 | AI 搜索 |
| **playwright** | 自动化 | ⏳ 安装中 | 浏览器自动化 |
| **browser** | 自动化 | ✅ 内置 | 浏览器控制 |

---

## 🚀 使用示例

### 示例 1：查询实时信息
```
用户："英伟达最新股价"
→ 自动调用：web-search
→ 获取：实时股价数据
```

### 示例 2：网页操作
```
用户："打开富途官网下载 OpenD"
→ 自动调用：browser
→ 操作：打开网页、导航到下载页
```

### 示例 3：日程管理
```
用户："下周一上午 10 点提醒我查看财报"
→ 自动调用：gog
→ 操作：创建 Google Calendar 事件
```

---

## 📝 注意事项

1. **技能优先级：**
   - 内置技能 > 已安装技能 > 需安装技能
   - 如遇速率限制，自动切换到备用方案

2. **自动执行：**
   - 简单任务：直接执行
   - 敏感操作（如交易）：先确认

3. **错误处理：**
   - 技能失败时自动重试
   - 仍失败则通知用户

---

*文档版本：v1.0*  
*最后更新：2026-03-27 18:02*
