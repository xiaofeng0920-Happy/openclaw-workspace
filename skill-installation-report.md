# OpenClaw 技能安装报告

**生成时间:** 2026-03-13 11:56 GMT+8
**安装助手:** 技能安装助手

---

## 📊 安装状态总览

### ✅ 已安装并可用 (6/17)

以下技能已经安装完成，可以直接使用：

| 技能名称 | 状态 | 说明 |
|---------|------|------|
| weather | ✓ ready | 天气预报功能 |
| healthcheck | ✓ ready | 安全审计功能 |
| mcporter | ✓ ready | MCP 工具管理 |
| github | ✓ ready | GitHub 操作 (gh CLI 已安装) |
| finance-data | ✓ ready | A/港股数据查询 (内置功能) |
| qqbot-cron | ✓ ready | 定时任务管理 (QQ Bot 内置) |

### ⚠️ 已内置但需要配置 (4/17)

以下技能已内置但缺少外部依赖或配置：

| 技能名称 | 状态 | 需要配置 |
|---------|------|---------|
| coding-agent | ✗ missing | 需要配置 Codex/Claude Code |
| notion | ✗ missing | 需要 NOTION_TOKEN |
| obsidian | ✗ missing | 需要安装 obsidian-cli |
| model-usage | ✗ missing | 需要安装 codexbar CLI |

### ❌ 需要从 ClawHub 安装 (7/17)

以下技能需要从 ClawHub 安装，但当前未登录，受到速率限制：

| 技能名称 | 搜索到的替代技能 | 状态 |
|---------|-----------------|------|
| tavily-search | liang-tavily-search (3.693) | 需要登录 clawhub |
| kimi-search | kimi-search (3.515) | 需要登录 clawhub |
| cron | cron-mastery (3.633) | qqbot-cron 已可用 |
| project-management-guru-adhd | project-management-2 (3.452) | 需要登录 clawhub |
| finance-scraper | yahoo-finance (1.236) | 需要登录 clawhub |
| stock-portfolio-monitor | portfolio-watcher (1.283) | 需要登录 clawhub |
| company-finance-analyzer | afrexai-financial-due-diligence (1.032) | 需要登录 clawhub |

### 🔍 未找到精确匹配 (3/17)

以下技能在 ClawHub 上未找到精确匹配：

| 技能名称 | 说明 |
|---------|------|
| hk-stock-qq | 港股数据精准抓取 - 未找到 |
| eastmoney-scraper | 东方财富数据 - 未找到精确匹配 |
| token-usage-monitor | 用量监控 - model-usage 可能替代 |

---

## 🔧 手动配置步骤

### 1. 登录 ClawHub (必需)

由于 ClawHub 对未登录用户有严格的速率限制，需要先登录：

```bash
# 方式 1: 浏览器登录 (推荐)
clawhub login

# 方式 2: 使用 API Token
clawhub login --token <YOUR_TOKEN> --no-browser
```

登录后可以安装以下技能：
- tavily-search
- kimi-search
- cron-mastery (可选，qqbot-cron 已可用)
- project-management-2
- 以及其他 finance 相关技能

### 2. 配置 Notion

```bash
# 获取 Notion Token: https://www.notion.so/my-integrations
export NOTION_TOKEN="your_notion_token_here"

# 验证安装
openclaw skills list | grep notion
```

### 3. 安装 Obsidian CLI

```bash
# 安装 obsidian-cli
npm install -g obsidian-cli

# 或者使用其他方式安装
# 验证安装
obsidian --version
```

### 4. 配置 Coding Agent

coding-agent 需要配置外部代码助手：

- **Claude Code**: `npm install -g @anthropic-ai/claude-code`
- **OpenAI Codex**: 需要 API key 和配置
- **Pi Agent**: 需要相应配置

---

## 📋 建议安装顺序

1. **首先登录 ClawHub** - 解除速率限制
2. **安装搜索技能** - tavily-search, kimi-search
3. **配置 Notion/Obsidian** - 如果需要文档管理
4. **安装项目管理技能** - project-management-2
5. **配置 coding-agent** - 如果需要代码助手功能

---

## 🚨 注意事项

1. **速率限制**: 未登录 ClawHub 时，搜索/安装操作会被严格限制（约 2-5 分钟才能执行一次）
2. **技能替代**: 部分请求的技能没有找到精确匹配，已列出最接近的替代选项
3. **内置功能**: finance-data 已内置 A/港股数据查询功能，可能满足大部分金融数据需求
4. **cron 功能**: qqbot-cron 已提供定时任务功能，可能不需要额外安装 cron 技能

---

## 📞 后续步骤

请小锋哥完成以下操作：

1. 运行 `clawhub login` 登录 ClawHub
2. 告诉我是否继续安装剩余技能
3. 如果需要配置 Notion/Obsidian/coding-agent，请提供相应的 token 或配置信息

---

**报告生成完成** 🎉
