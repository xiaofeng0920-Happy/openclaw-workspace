#!/bin/bash
# 设置早晨叫醒服务 Cron 任务
# 每天早上 7:00 运行

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/wakeup_call.py"
LOG_FILE="/tmp/wakeup-call.log"

echo "正在设置早晨叫醒服务..."
echo "脚本路径：$SCRIPT_PATH"
echo "日志文件：$LOG_FILE"

# 检查 crontab 是否已存在该任务
EXISTING=$(crontab -l 2>/dev/null | grep -c "wakeup_call.py" || echo 0)

if [ "$EXISTING" -gt 0 ]; then
    echo "⚠️  任务已存在，跳过安装"
    crontab -l | grep "wakeup"
else
    # 添加 cron 任务
    (crontab -l 2>/dev/null; echo "0 7 * * * cd $SCRIPT_DIR && python3 $SCRIPT_PATH --send >> $LOG_FILE 2>&1") | crontab -
    echo "✅ Cron 任务已添加"
    echo ""
    echo "任务详情:"
    echo "  时间：每天早上 7:00"
    echo "  内容：叫醒提醒 + 天气预报 + 市场简报 + 今日日程"
    echo "  日志：$LOG_FILE"
    echo ""
    echo "查看任务：crontab -l | grep wakeup"
    echo "查看日志：tail -f $LOG_FILE"
    echo "删除任务：crontab -e (删除对应行)"
fi

# 显示当前 crontab
echo ""
echo "当前所有 cron 任务:"
crontab -l 2>/dev/null || echo "无 cron 任务"
