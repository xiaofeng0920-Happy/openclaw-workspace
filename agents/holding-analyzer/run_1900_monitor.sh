#!/bin/bash
# 19:00 持仓监控任务 - 综合执行脚本
# 执行：持仓分析 + 产品规模监控 + 飞书推送

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/tmp/holding-analyzer-1900.log"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

echo "========================================" | tee -a "$LOG_FILE"
echo "📊 19:00 持仓监控任务启动" | tee -a "$LOG_FILE"
echo "时间：$TIMESTAMP" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 1. 执行持仓分析
echo "" | tee -a "$LOG_FILE"
echo "=== 任务 1: 持仓分析 ===" | tee -a "$LOG_FILE"
cd "$SCRIPT_DIR"
python3 run.py --send >> "$LOG_FILE" 2>&1
HOLDING_STATUS=$?

if [ $HOLDING_STATUS -eq 0 ]; then
    echo "✅ 持仓分析完成" | tee -a "$LOG_FILE"
else
    echo "❌ 持仓分析失败 (状态码：$HOLDING_STATUS)" | tee -a "$LOG_FILE"
fi

# 2. 执行产品规模监控
echo "" | tee -a "$LOG_FILE"
echo "=== 任务 2: 产品规模监控 ===" | tee -a "$LOG_FILE"
cd "$SCRIPT_DIR"
python3 product_scale_monitor.py --send >> "$LOG_FILE" 2>&1
SCALE_STATUS=$?

if [ $SCALE_STATUS -eq 0 ]; then
    echo "✅ 产品规模监控完成" | tee -a "$LOG_FILE"
else
    echo "❌ 产品规模监控失败 (状态码：$SCALE_STATUS)" | tee -a "$LOG_FILE"
fi

# 3. 总结
echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "📋 任务执行总结" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "持仓分析：$([ $HOLDING_STATUS -eq 0 ] && echo '✅ 成功' || echo '❌ 失败')" | tee -a "$LOG_FILE"
echo "产品规模：$([ $SCALE_STATUS -eq 0 ] && echo '✅ 成功' || echo '❌ 失败')" | tee -a "$LOG_FILE"
echo "完成时间：$(date "+%Y-%m-%d %H:%M:%S")" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 返回总体状态
if [ $HOLDING_STATUS -eq 0 ] && [ $SCALE_STATUS -eq 0 ]; then
    exit 0
else
    exit 1
fi
