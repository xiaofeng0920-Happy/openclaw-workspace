# 📱 飞书通知配置指南

## 方案 1：机器人 Webhook（推荐，简单）

### 步骤 1：创建群聊机器人

1. **打开飞书**，创建一个群聊（可以是只有你自己的群）

2. **添加机器人**：
   - 点击群聊右上角设置 ⚙️
   - 选择「添加机器人」
   - 选择「自定义机器人」

3. **配置机器人**：
   - 名称：`巴菲特预警助手`
   - 头像：可选
   - 勾选「支持文本消息」

4. **复制 Webhook 地址**：
   ```
   https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   ```

### 步骤 2：配置文件

编辑 `/home/admin/openclaw/workspace/notify/feishu_config.json`：

```json
{
  "feishu": {
    "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/你的_WEBHOOK_地址",
    "secret": "",
    "enabled": true
  }
}
```

### 步骤 3：测试

```bash
cd /home/admin/openclaw/workspace
python3 notify/price_alert.py --check
```

如果看到 `✅ 飞书通知发送成功`，说明配置成功！

---

## 方案 2：飞书开放平台（高级）

### 步骤 1：创建应用

1. 访问 https://open.feishu.cn/
2. 登录飞书开放平台
3. 点击「创建应用」
4. 选择「企业内部开发」

### 步骤 2：配置权限

在「权限管理」中添加：
- `im:message` - 发送消息
- `im:chat` - 读取群聊信息

### 步骤 3：获取凭证

在「凭证与基础信息」中获取：
- `App ID` (cli_xxxxxxxxx)
- `App Secret`

### 步骤 4：配置文件

编辑 `notify/feishu_config.json`：

```json
{
  "feishu": {
    "app_id": "cli_xxxxxxxxx",
    "app_secret": "xxxxxxxxxxxxxxxx",
    "enabled": true
  }
}
```

---

## 测试通知

### 测试 1：价格预警

```bash
python3 notify/price_alert.py --check
```

### 测试 2：持仓报告

```bash
python3 strategies/buffett_analyzer.py
```

---

## 通知示例

### 价格突破通知

```
🔔 价格预警通知
时间：2026-03-21 14:30:00

📈 腾讯控股 (00700)
突破上涨预警价 550.00 港元，现价 555.00 港元

🎯 中国海洋石油 (00883)
出现巴菲特买入信号！安全边际 67.5%，评分 99/100

---
投资有风险，决策需谨慎
```

### 持仓日报

```
📊 持仓日报
时间：2026-03-21 16:30:00

总览：
- 总资产：$1,879,000
- 今日盈亏：+$12,500 (+0.67%)

个股表现：
🟢 中国海洋石油 +2.5%
🔴 腾讯控股 -1.2%
🟢 阿里巴巴 +0.8%
```

---

## 常见问题

### Q: 收不到通知？

A: 检查以下几点：
1. Webhook 地址是否正确
2. 机器人是否在群聊中
3. 网络连接是否正常
4. 查看日志：`/tmp/price_alert.log`

### Q: 如何关闭通知？

A: 编辑 `feishu_config.json`：
```json
{
  "feishu": {
    "enabled": false
  }
}
```

### Q: 如何修改通知频率？

A: 编辑 `feishu_config.json`：
```json
{
  "notification": {
    "alert_cooldown": 3600  // 冷却时间（秒）
  }
}
```

---

## 配置完成检查清单

- [ ] 创建飞书机器人
- [ ] 复制 Webhook 地址
- [ ] 编辑 `feishu_config.json`
- [ ] 运行测试命令
- [ ] 确认收到通知

---

**配置完成后，系统将自动发送：**
- 🔔 实时价格预警
- 📊 每日持仓报告
- 📈 巴菲特买卖信号
- ⚠️ 产品规模预警
