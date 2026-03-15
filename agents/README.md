# 股票日报 Agent 配置说明

## ✅ 已完成的配置

### 1. 人设文件
- **位置**: `agents/stock-daily-agent.md`
- **角色**: 小巴 - 15 年华尔街经验的高级日内交易策略师
- **任务**: 每个交易日发送《每日动量报告》

### 2. 报告格式
```
📈 每日动量报告 | Daily Momentum Report
日期：YYYY-MM-DD

━━━━━━━━━━━━━━━━━━━━━━━

🎯 Marcus 的市场立场
【激进买入 / 保守买入 / 持币观望】

核心逻辑：简要说明选择理由（VIX、期货、情绪等）

━━━━━━━━━━━━━━━━━━━━━━━

🔥 5% 观察名单

1）股票代码：XXXX
   • 胜率概率：XX%
   • 选择理由：xxxxxxxxxxxx

2）股票代码：XXXX
   • 胜率概率：XX%
   • 选择理由：xxxxxxxxxxxx

3）股票代码：XXXX
   • 胜率概率：XX%
   • 选择理由：xxxxxxxxxxxx

4）股票代码：XXXX
   • 胜率概率：XX%
   • 选择理由：xxxxxxxxxxxx

5）股票代码：XXXX
   • 胜率概率：XX%
   • 选择理由：xxxxxxxxxxxx

━━━━━━━━━━━━━━━━━━━━━━━
⚠️ 风险提示：以上分析仅供参考，不构成投资建议。
```

### 3. 定时任务配置
- **Cron 表达式**: `0 9 * * 1-5`（周一至周五 早上 9:00）
- **时区**: Asia/Shanghai
- **发送通道**: 飞书
- **接收用户**: 赵小锋 (ou_52fa8f508e88e1efbcbe50c014ecaa6e)

---

## ⚠️ 定时任务待激活

由于 Gateway WebSocket 连接问题，定时任务需要手动添加。

### 添加定时任务命令

```bash
openclaw cron add \
  --name "股票日报 - 小巴" \
  --cron "0 9 * * 1-5" \
  --tz "Asia/Shanghai" \
  --session "isolated" \
  --message "你是小巴，一名拥有超过 15 年华尔街经验的高级日内交易策略师。请生成一份《每日动量报告》，包含：1) Marcus 的市场立场（激进买入/保守买入/持币观望），基于 VIX、期货、市场情绪；2) 5% 观察名单（5 只股票，每只包含股票代码、胜率概率、选择理由）。使用 finance-data 技能获取最新市场数据。输出格式简洁专业，像交易大厅老手。" \
  --to "ou_52fa8f508e88e1efbcbe50c014ecaa6e" \
  --channel "feishu" \
  --timeout-seconds 300
```

### 测试命令（立即生成一次报告）

```bash
openclaw cron run "股票日报 - 小巴"
```

### 查看定时任务列表

```bash
openclaw cron list
```

---

## 📊 数据来源

使用 `finance-data` 技能获取：
- 美股/港股/A 股实时行情
- 市场新闻和催化事件
- 技术指标和成交量数据
- VIX 恐慌指数
- 股指期货数据

---

## 🔧 故障排除

### Gateway 连接问题

如果看到 `gateway connect failed` 错误：

1. 检查 Gateway 状态：
   ```bash
   openclaw gateway status
   ```

2. 重启 Gateway：
   ```bash
   openclaw gateway restart
   ```

3. 检查进程：
   ```bash
   ps aux | grep openclaw
   ```

### 飞书消息发送失败

检查飞书插件配置和权限。

---

## 📝 文件清单

```
agents/
├── README.md                      # 本文件
├── stock-daily-agent.md           # 小巴人设和任务说明
├── stock-daily-cron.md            # 定时任务配置说明
└── generate_stock_report.js       # 报告生成脚本
```
