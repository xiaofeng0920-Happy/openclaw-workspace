#!/bin/bash
# 设置股票价格定时更新任务
# 每 30 分钟检查一次股价

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/price_monitor.py"
LOG_FILE="/tmp/price-monitor.log"

echo "正在设置股票价格定时更新任务..."
echo "脚本路径：$SCRIPT_PATH"
echo "日志文件：$LOG_FILE"

# 检查 crontab 是否已存在该任务
EXISTING=$(crontab -l 2>/dev/null | grep -c "price_monitor.py" || echo 0)

if [ "$EXISTING" -gt 0 ]; then
    echo "⚠️  任务已存在，跳过安装"
    crontab -l | grep "price_monitor"
else
    # 添加 cron 任务
    (crontab -l 2>/dev/null; echo "*/30 * * * * cd $SCRIPT_DIR && python3 $SCRIPT_PATH --send >> $LOG_FILE 2>&1") | crontab -
    echo "✅ Cron 任务已添加"
    echo ""
    echo "任务详情:"
    echo "  频率：每 30 分钟"
    echo "  命令：python3 $SCRIPT_PATH --send"
    echo "  日志：$LOG_FILE"
    echo ""
    echo "查看任务：crontab -l | grep price"
    echo "查看日志：tail -f $LOG_FILE"
    echo "删除任务：crontab -e (删除对应行)"
fi

# 显示当前 crontab
echo ""
echo "当前所有 cron 任务:"
crontab -l 2>/dev/null || echo "无 cron 任务"
