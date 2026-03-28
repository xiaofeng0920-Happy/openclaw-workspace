# ⚙️ 交易日自动化调度配置

> "时间是好公司的朋友，是坏公司的敌人。" —— 巴菲特

---

## 📅 自动化任务时间表

### 交易日（周一至周五）

| 时间 | 任务 | 说明 | 日志 |
|------|------|------|------|
| **09:00** | 🌅 盘前检查 | 产品规模 + 价格预警 | `pre_market.log` |
| **09:30-16:00** | 📊 盘中监控 | 每 30 分钟检查价格 | `intra_day.log` |
| **16:30** | 📈 盘后分析 | 持仓报告 + 盈亏汇总 | `post_market.log` |
| **每 4 小时** | 💓 心跳检查 | 定期监控 | `heartbeat.log` |

### 周末和节假日

- ❌ 不执行盘中监控
- ✅ 心跳检查继续运行
- ✅ 可手动运行分析

---

## 🚀 快速配置

### 方法 1：一键安装（推荐）

```bash
# 1. 备份现有 crontab
crontab -l > /tmp/old_cron.bak

# 2. 安装新配置
cat /home/admin/openclaw/workspace/notify/buffett_crontab.txt | crontab -

# 3. 验证安装
crontab -l
```

### 方法 2：手动配置

```bash
# 1. 编辑 crontab
crontab -e

# 2. 粘贴以下配置
# (见下方 crontab 配置)

# 3. 保存退出 (:wq)

# 4. 验证
crontab -l
```

---

## 📋 crontab 配置

```bash
# ============================================
# 巴菲特投资系统 - 交易日定时任务
# ============================================

# 环境变量
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# 日志目录
LOG_DIR=/tmp/buffett_system

# ============================================
# 盘前检查 (交易日 09:00)
# ============================================
0 9 * * 1-5 cd /home/admin/openclaw/workspace && \
  python3 notify/cron_config.py --pre-market >> $LOG_DIR/pre_market.log 2>&1

# ============================================
# 盘中监控 (交易日每 30 分钟)
# ============================================
*/30 9-15 * * 1-5 cd /home/admin/openclaw/workspace && \
  python3 notify/price_alert.py --check >> $LOG_DIR/intra_day.log 2>&1

# ============================================
# 盘后分析 (交易日 16:30)
# ============================================
30 16 * * 1-5 cd /home/admin/openclaw/workspace && \
  python3 strategies/buffett_analyzer.py >> $LOG_DIR/post_market.log 2>&1

# ============================================
# 心跳检查 (每 4 小时)
# ============================================
0 */4 * * * cd /home/admin/openclaw/workspace && \
  python3 notify/cron_config.py --monitor >> $LOG_DIR/heartbeat.log 2>&1

# ============================================
# 产品规模检查 (交易日 09:00)
# ============================================
0 9 * * 1-5 cd /home/admin/openclaw/workspace && \
  python3 notify/cron_config.py --check-scale >> $LOG_DIR/scale_check.log 2>&1
```

---

## 📊 任务详细说明

### 1️⃣ 盘前检查 (09:00)

**执行内容:**
- ✅ 产品规模预警检查
- ✅ 持仓价格预警检查
- ✅ 巴菲特买卖信号扫描

**发送通知:**
- 🔴 规模紧急预警（如有）
- 🔔 价格突破预警（如有）
- 🎯 巴菲特买入信号（如有）

**触发条件:**
- 交易日 09:00（周一至周五）

---

### 2️⃣ 盘中监控 (每 30 分钟)

**执行内容:**
- ✅ 实时价格监控
- ✅ 预警条件检查
- ✅ 巴菲特信号计算

**发送通知:**
- 🔔 价格突破预警（实时）
- 🎯 巴菲特买入/卖出信号

**触发条件:**
- 突破预警价
- 安全边际 ≥ 30%
- 溢价 ≥ 30%
- 冷却时间：1 小时

**监控时间:**
- 09:30, 10:00, 10:30, ..., 15:30, 16:00

---

### 3️⃣ 盘后分析 (16:30)

**执行内容:**
- ✅ 持仓盈亏分析
- ✅ 巴菲特评分更新
- ✅ 投资建议生成

**发送通知:**
- 📊 持仓日报
- 📈 个股表现
- 💡 投资建议

**触发条件:**
- 交易日 16:30

---

### 4️⃣ 心跳检查 (每 4 小时)

**执行内容:**
- ✅ 系统状态检查
- ✅ 持仓监控
- ✅ 日志记录

**发送通知:**
- 仅在发现异常时

**执行时间:**
- 00:00, 04:00, 08:00, 12:00, 16:00, 20:00

---

## 🔍 日志管理

### 日志位置

```
/tmp/buffett_system/
├── pre_market.log      # 盘前检查日志
├── intra_day.log       # 盘中监控日志
├── post_market.log     # 盘后分析日志
├── heartbeat.log       # 心跳检查日志
└── scale_check.log     # 规模检查日志
```

### 查看日志

```bash
# 实时查看所有日志
tail -f /tmp/buffett_system/*.log

# 查看最新 50 行
tail -n 50 /tmp/buffett_system/post_market.log

# 搜索错误
grep "ERROR\|❌" /tmp/buffett_system/*.log
```

### 日志轮转

```bash
# 清理 7 天前的日志
find /tmp/buffett_system -name "*.log" -mtime +7 -delete
```

---

## ✅ 验证安装

### 1. 检查 crontab

```bash
crontab -l
```

应该看到所有任务配置。

### 2. 手动测试

```bash
# 测试盘前检查
python3 notify/cron_config.py --pre-market

# 测试盘中监控
python3 notify/price_alert.py --check

# 测试盘后分析
python3 strategies/buffett_analyzer.py
```

### 3. 检查日志

```bash
# 查看最新日志
tail -f /tmp/buffett_system/heartbeat.log
```

---

## ⚠️ 注意事项

### 交易日判断

当前版本使用简化判断：
- ✅ 周一至周五 = 交易日
- ❌ 周六周日 = 休市
- ⚠️ 节假日需要手动调整

### 网络依赖

- 需要稳定的网络连接
- 富途 OpenD 必须运行
- 建议配置网络异常处理

### 系统要求

- Python 3.10+
- 富途 OpenD 已启动
- cron 服务已启用

---

## 🔧 故障排查

### 任务未执行

```bash
# 检查 cron 服务
systemctl status cron

# 查看 cron 日志
grep CRON /var/log/syslog | tail -20
```

### 通知未发送

```bash
# 检查飞书配置
cat notify/feishu_config.json

# 测试通知
python3 notify/send_test.py
```

### 数据获取失败

```bash
# 检查 OpenD 状态
pgrep -f "Futu_OpenD"

# 测试连接
python3 -c "from futu import *; print('OK')"
```

---

## 📞 支持

- 日志位置：`/tmp/buffett_system/`
- 配置文件：`notify/buffett_crontab.txt`
- 调度器：`notify/trading_day_scheduler.py`

---

**配置完成后，系统将自动运行！** 🎉
