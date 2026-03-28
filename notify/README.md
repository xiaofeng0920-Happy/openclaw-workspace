# 🔔 价格预警与通知系统

> "别人贪婪时我恐惧，别人恐惧时我贪婪。" —— 巴菲特

---

## 📖 概述

本系统实时监控股票价格，当达到预设条件时自动发送通知到飞书/微信。

### 功能

- ✅ 价格突破预警（上涨/下跌）
- ✅ 涨跌幅预警
- ✅ 巴菲特买入/卖出信号
- ✅ 飞书通知推送
- ✅ 定时任务调度
- ✅ 通知冷却机制

---

## 🚀 快速开始

### 1. 创建预警配置

```bash
cd /home/admin/openclaw/workspace

# 首次运行会自动创建默认配置
python3 notify/price_alert.py --demo
```

### 2. 执行预警检查

```bash
# 手动检查
python3 notify/price_alert.py --check

# 或运行定时任务
python3 notify/cron_config.py --check-alerts
```

### 3. 配置飞书通知

编辑 `notify/price_alert.py` 或创建配置文件:

```python
# 方式 1: Webhook（群聊）
webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"

# 方式 2: 开放平台 API（私聊）
app_id = "cli_xxx"
app_secret = "xxx"
```

---

## 📋 预警条件

### 价格预警

| 类型 | 条件 | 示例 |
|------|------|------|
| 突破上涨 | 现价 ≥ 预警价 | 腾讯突破 550 港元 |
| 跌破下跌 | 现价 ≤ 预警价 | 腾讯跌破 480 港元 |

### 涨跌幅预警

| 类型 | 条件 | 示例 |
|------|------|------|
| 单日大涨 | 涨幅 ≥ 5% | 腾讯单日 +7% |
| 单日大跌 | 跌幅 ≥ 5% | 腾讯单日 -6% |

### 巴菲特策略预警

| 类型 | 条件 | 示例 |
|------|------|------|
| 买入信号 | 安全边际 ≥ 30% | 中海油安全边际 67% |
| 卖出信号 | 溢价 ≥ 30% | 某股票溢价 45% |

---

## ⚙️ 配置说明

### 预警配置文件

位置：`notify/alerts_config.json`

```json
{
  "alerts": [
    {
      "code": "HK.00700",
      "name": "腾讯控股",
      "current_price": 508.00,
      "price_alert_up": 550.00,
      "price_alert_down": 480.00,
      "change_pct_alert": 5.0,
      "buy_margin_alert": 30.0,
      "sell_premium_alert": 30.0,
      "notify_feishu": true,
      "notify_cooldown": 3600
    }
  ]
}
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `price_alert_up` | 突破上涨预警价 | null |
| `price_alert_down` | 跌破下跌预警价 | null |
| `change_pct_alert` | 涨跌幅预警阈值 (%) | 5.0 |
| `buy_margin_alert` | 买入安全边际阈值 (%) | 30.0 |
| `sell_premium_alert` | 卖出溢价阈值 (%) | 30.0 |
| `notify_cooldown` | 通知冷却时间 (秒) | 3600 |

---

## 🕐 定时任务

### Cron 配置

```bash
# 编辑 crontab
crontab -e

# 添加以下配置
# 价格预警（每 5 分钟）
*/5 * * * * cd /home/admin/openclaw/workspace && python3 notify/price_alert.py --check

# 持仓监控（每 4 小时）
0 */4 * * * python3 -c "from notify.cron_config import monitor_portfolio; monitor_portfolio()"

# 产品规模检查（每日 09:00）
0 9 * * 1-5 python3 -c "from notify.cron_config import check_product_scale; check_product_scale()"

# 每日收盘分析（交易日 16:30）
30 16 * * 1-5 python3 -c "from notify.cron_config import daily_analysis; daily_analysis()"
```

### 任务说明

| 任务 | 频率 | 说明 |
|------|------|------|
| 价格预警 | 每 5 分钟 | 实时监控股价 |
| 持仓监控 | 每 4 小时 | 检查持仓盈亏 |
| 产品规模 | 每日 09:00 | 检查基金规模 |
| 收盘分析 | 交易日 16:30 | 每日复盘 |

---

## 📤 通知示例

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

### 飞书卡片消息

```json
{
  "config": {"wide_screen_mode": true},
  "header": {
    "template": "red",
    "title": {"content": "🔔 价格预警通知"}
  },
  "elements": [
    {
      "tag": "div",
      "text": {
        "tag": "lark_md",
        "content": "**腾讯控股**\n突破上涨预警价 550.00 港元"
      }
    }
  ]
}
```

---

## ⚠️ 注意事项

### 通知冷却

- 默认冷却时间：1 小时
- 避免重复通知骚扰
- 可在配置中调整

### 数据延迟

- 实时行情可能有 15 分钟延迟
- 重要决策前请确认实时价格

### 网络依赖

- 需要稳定的网络连接
- 建议配置备用通知渠道

---

## 🔧 高级配置

### 自定义预警条件

```python
from notify.price_alert import StockAlert

# 创建自定义预警
alert = StockAlert(
    code='HK.00700',
    name='腾讯控股',
    current_price=508.00,
    price_alert_up=550.00,
    price_alert_down=480.00,
    volume_alert=50000000,  # 成交量预警
    notify_feishu=True,
    notify_wechat=False
)
```

### 多通知渠道

```python
# 同时发送到飞书和微信
alert.notify_feishu = True
alert.notify_wechat = True
alert.notify_email = True
```

---

## 📚 相关文件

| 文件 | 功能 |
|------|------|
| `notify/price_alert.py` | 价格预警核心 |
| `notify/feishu_notifier.py` | 飞书通知集成 |
| `notify/cron_config.py` | 定时任务配置 |
| `notify/alerts_config.json` | 预警配置（自动生成） |
| `notify/alert_history.json` | 预警历史 |

---

**最后更新**: 2026-03-21  
**版本**: v1.0
