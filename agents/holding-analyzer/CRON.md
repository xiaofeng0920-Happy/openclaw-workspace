# 持仓分析 Agent - Cron 定时任务配置

## 安装 Cron 任务

```bash
# 编辑 crontab
crontab -e

# 添加以下任务（北京时间 UTC+8）
```

## 定时任务

### 早盘监控 (09:00)
```cron
0 1 * * * cd /home/admin/openclaw/workspace/agents/holding-analyzer && python3 run.py --send >> /tmp/holding-analyzer.log 2>&1
```

### 午间监控 (13:00)
```cron
0 5 * * * cd /home/admin/openclaw/workspace/agents/holding-analyzer && python3 run.py --send >> /tmp/holding-analyzer.log 2>&1
```

### 晚间监控 (19:00)
```cron
0 11 * * * cd /home/admin/openclaw/workspace/agents/holding-analyzer && python3 run.py --send >> /tmp/holding-analyzer.log 2>&1
```

## 说明

- Cron 使用 UTC 时间，北京时间 = UTC+8
- 09:00 北京 = 01:00 UTC
- 13:00 北京 = 05:00 UTC
- 19:00 北京 = 11:00 UTC

## 查看日志

```bash
# 查看最新日志
tail -f /tmp/holding-analyzer.log

# 查看今日日志
grep "$(date +%Y-%m-%d)" /tmp/holding-analyzer.log
```

## 手动测试

```bash
cd /home/admin/openclaw/workspace/agents/holding-analyzer
python3 run.py --send
```

## 暂停/恢复任务

```bash
# 暂停（注释掉所有任务）
crontab -e
# 在每行前加 #

# 恢复（移除 #）
crontab -e
```

## 查看已安装任务

```bash
crontab -l
```
