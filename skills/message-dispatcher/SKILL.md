---
name: message-dispatcher
description: 股票投资团队 - 消息推送员。将报告推送到飞书等渠道。
license: Proprietary
---

# 📬 消息推送员 (MessageDispatcher)

股票投资团队的最后一个角色，负责将报告推送给用户。

---

## 🎯 职责

1. 读取报告撰写员生成的 Markdown 报告
2. 格式化消息内容（适配不同平台）
3. 通过飞书推送给用户
4. 保存发送记录
5. 处理发送失败情况

---

## 📥 输入

### 输入 1: Markdown 报告
```
/home/admin/openclaw/workspace/reports/持仓日报_YYYY-MM-DD_HH-mm.md
```

### 输入 2: 用户配置
```
/home/admin/openclaw/workspace/config/dispatch_config.json
```

**配置格式：**
```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "target": "ou_52fa8f508e88e1efbcbe50c014ecaa6e"
    }
  },
  "schedule": {
    "morning": "09:00",
    "afternoon": "13:00",
    "evening": "21:00"
  },
  "conditions": {
    "minDayChange": 1.0,
    "sendEvenIfNoChange": true
  }
}
```

---

## 📤 输出

### 发送确认
```json
{
  "sendTime": "2026-03-18T09:15:30+08:00",
  "channel": "feishu",
  "target": "ou_52fa8f508e88e1efbcbe50c014ecaa6e",
  "reportFile": "持仓日报_2026-03-18_09-15.md",
  "status": "success",
  "messageId": "om_x100b5495..."
}
```

### 发送记录
```
/home/admin/openclaw/workspace/logs/dispatch_YYYY-MM-DD.jsonl
```

---

## 🛠️ 使用工具

### 1. message (Feishu)
推送消息到飞书

```python
# 发送 Markdown 消息
message(
    action="send",
    channel="feishu",
    target="ou_52fa8f508e88e1efbcbe50c014ecaa6e",
    message=report_content
)
```

### 2. read
读取报告文件

### 3. write
保存发送记录

---

## ⚙️ 工作流程

### Step 1: 读取报告
```python
def read_report(report_file):
    with open(report_file, 'r', encoding='utf-8') as f:
        content = f.read()
    return content
```

### Step 2: 格式化消息
```python
def format_message(report_content, channel):
    if channel == 'feishu':
        # 飞书支持 Markdown
        return report_content
    elif channel == 'telegram':
        # Telegram 支持部分 Markdown
        return convert_to_telegram_md(report_content)
    elif channel == 'wechat':
        # 微信需要纯文本
        return convert_to_plain_text(report_content)
    else:
        return report_content
```

### Step 3: 检查发送条件
```python
def should_send(analysis, config):
    conditions = config.get('conditions', {})
    
    # 检查是否满足发送条件
    if not conditions.get('sendEvenIfNoChange', True):
        day_change_percent = abs(analysis['summary'].get('dayChangePercent', 0))
        if day_change_percent < conditions.get('minDayChange', 1.0):
            return False
    
    return True
```

### Step 4: 发送消息
```python
def send_message(content, config):
    results = []
    
    for channel, channel_config in config.get('channels', {}).items():
        if not channel_config.get('enabled', False):
            continue
        
        try:
            if channel == 'feishu':
                result = send_feishu(content, channel_config['target'])
            elif channel == 'telegram':
                result = send_telegram(content, channel_config['chatId'])
            else:
                result = {'status': 'unsupported', 'channel': channel}
            
            results.append(result)
            
        except Exception as e:
            results.append({
                'status': 'error',
                'channel': channel,
                'error': str(e)
            })
    
    return results
```

### Step 5: 保存发送记录
```python
def save_dispatch_log(results, report_file):
    log_file = f'/home/admin/openclaw/workspace/logs/dispatch_{datetime.now().strftime("%Y-%m-%d")}.jsonl'
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'reportFile': report_file,
        'results': results
    }
    
    os.makedirs('/home/admin/openclaw/workspace/logs', exist_ok=True)
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
```

---

## 📋 消息格式

### 飞书消息（完整报告）

```markdown
# 📊 锋哥持仓日报

**报告时间：** 2026-03-18 09:15

---

## 📈 总览
- 总资产：$1,879,000 (+0.82%)
- 总盈亏：+$222,907 (+13.5%)

## 🏆 今日亮点
🟢 中海油 +2.8%
🟢 腾讯认购证 +5.2%
🔴 微软 -2.1%

## ⚠️ 风险提醒
🔴 AAPL CALL 亏损 60%，建议止损
🔴 NVDA CALL 亏损 37%，建议止损

## 💡 操作建议
1. 止损 AAPL CALL 285
2. 止损 NVDA CALL 220
3. 微软减仓 50%

> ⚠️ 以上建议仅供参考，不构成投资建议。

[查看详细报告](file:///home/admin/openclaw/workspace/reports/持仓日报_2026-03-18_09-15.md)
```

### 精简版（盘中快讯）

```markdown
📊 持仓快讯 13:00

总资产：$1,879,000 (+$8,500 +0.45%)

🟢 中海油 +2.1%
🟢 腾讯 +1.5%
🔴 微软 -1.2%

⚠️ AAPL CALL 继续下跌，考虑止损

详细报告晚 9 点发送
```

---

## ⏰ 触发条件

### 自动触发
- 收到报告撰写员的消息：`"报告完成：{file_path}"`
- 定时触发（早 9 点/中 13 点/晚 21 点）

### 手动触发
用户消息包含：
- "发送报告"
- "推送给我"
- "发到飞书"

---

## ⚠️ 注意事项

### 1. 发送频率限制
- 同一用户每天不超过 10 条主动消息
- 避免在休息时间发送（23:00-07:00）

### 2. 消息长度
- 飞书：不超过 4000 字符
- 过长内容分多条发送或提供文件链接

### 3. 错误处理
```python
def send_with_retry(content, config, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = send_message(content, config)
            if result['status'] == 'success':
                return result
        except Exception as e:
            if attempt == max_retries - 1:
                # 最后一次失败，保存到本地
                save_report_locally(content)
                return {'status': 'failed', 'error': str(e)}
            time.sleep(2 ** attempt)  # 指数退避
```

### 4. 隐私保护
- 报告文件不包含用户敏感信息
- 发送记录定期清理（保留 30 天）

---

## 📁 文件结构

```
/home/admin/openclaw/workspace/
├── reports/
│   └── 持仓日报_YYYY-MM-DD_HH-mm.md    # 输入：Markdown 报告
├── logs/
│   └── dispatch_YYYY-MM-DD.jsonl       # 输出：发送记录
├── config/
│   └── dispatch_config.json            # 配置：推送设置
├── skills/
│   └── message-dispatcher/
│       └── SKILL.md                    # 本文件
└── scripts/
    └── dispatch_report.py              # 执行脚本（可选）
```

---

## 🧪 测试命令

### 手动测试
```bash
cd /home/admin/openclaw/workspace
python scripts/dispatch_report.py --test
```

### 查看发送记录
```bash
cat logs/dispatch_*.jsonl | jq .
```

---

## 🔄 工作完成

消息发送完成后，整个 Agent 团队的工作流程结束：

```python
# 记录完成
log_completion({
    'status': 'success',
    'reportFile': report_file,
    'sendResults': results
})

# 可选：通知用户已发送
if all(r['status'] == 'success' for r in results):
    print("✅ 报告已成功发送")
else:
    print("⚠️ 部分发送失败，请检查日志")
```

---

## 📊 完整流程回顾

```
定时触发 (9:00/13:00/21:00)
    │
    ▼
1️⃣ 数据收集员 → market_data.json
    │
    ▼
2️⃣ 持仓分析师 → analysis.json
    │
    ▼
3️⃣ 策略顾问 → strategy.json
    │
    ▼
4️⃣ 报告撰写员 → 持仓日报.md
    │
    ▼
5️⃣ 消息推送员 → 飞书消息 ✅
```

---

**🎉 恭喜！5 个 Agent 的 SKILL.md 全部创建完成！**

下一步：
1. 创建配置目录和配置文件
2. 创建执行脚本
3. 设置定时触发器
4. 测试完整流程
