#!/bin/bash
# 持仓监控系统 - 完整 Cron 安装脚本
# 包含：详细报告 (3 次/天) + 股价更新 (每 30 分钟) + 产品规模检查 (每日)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/tmp/holding-analyzer.log"

echo "============================================================"
echo "📈 锋哥持仓监控系统 - Cron 安装"
echo "============================================================"
echo ""

# 定义 PATH（确保 cron 能找到 openclaw 命令）
CRON_PATH="/home/admin/.nvm/versions/node/v24.14.0/bin:/usr/local/bin:/home/admin/.local/bin:/usr/bin:/bin"

# 创建临时 crontab 文件
TEMP_CRON=$(mktemp)

# 写入 PATH 环境变量
echo "# 持仓监控系统 - 锋哥" > $TEMP_CRON
echo "# 时区：Asia/Shanghai (北京时间)"
echo ""
echo "PATH=$CRON_PATH"
echo ""

# 早盘详细报告 (09:00 北京 = 01:00 UTC)
echo "# === 详细报告 (每日 3 次) ===" >> $TEMP_CRON
echo "0 1 * * * cd $SCRIPT_DIR && python3 run.py --send >> $LOG_FILE 2>&1" >> $TEMP_CRON

# 午间详细报告 (13:00 北京 = 05:00 UTC)
echo "0 5 * * * cd $SCRIPT_DIR && python3 run.py --send >> $LOG_FILE 2>&1" >> $TEMP_CRON

# 晚间详细报告 (19:00 北京 = 11:00 UTC)
echo "0 11 * * * cd $SCRIPT_DIR && python3 run.py --send >> $LOG_FILE 2>&1" >> $TEMP_CRON

# 股价快速更新 (每 30 分钟，静音时段 23:00-07:00 不推送)
echo "" >> $TEMP_CRON
echo "# === 股价快速更新 (每 30 分钟) ===" >> $TEMP_CRON
echo "*/30 * * * * cd $SCRIPT_DIR && python3 price_monitor.py --send >> /tmp/price-monitor.log 2>&1" >> $TEMP_CRON

# 产品规模检查 (09:00 北京 = 01:00 UTC，仅交易日)
echo "" >> $TEMP_CRON
echo "# === 产品规模监控 (每日 09:00) ===" >> $TEMP_CRON
echo "0 1 * * 1-5 cd $SCRIPT_DIR && python3 product_scale_monitor.py >> /tmp/product-scale.log 2>&1" >> $TEMP_CRON

echo ""
echo "📋 即将安装的 Cron 任务:"
echo "------------------------------------------------------------"
cat $TEMP_CRON
echo "------------------------------------------------------------"
echo ""

# 备份现有 crontab
EXISTING=$(crontab -l 2>/dev/null)
if [ -n "$EXISTING" ]; then
    echo "⚠️  检测到现有 crontab，创建备份..."
    crontab -l > /tmp/crontab.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ 备份已保存：/tmp/crontab.backup.*"
    echo ""
fi

# 安装新的 crontab
crontab $TEMP_CRON

if [ $? -eq 0 ]; then
    echo "✅ Cron 任务安装成功！"
    echo ""
    echo "📅 任务时间表（北京时间）:"
    echo "  ┌─────────────────────────────────────────────┐"
    echo "  │ 09:00  早盘详细报告 + 产品规模检查          │"
    echo "  │ 13:00  午间详细报告                         │"
    echo "  │ 19:00  晚间详细报告                         │"
    echo "  │ 每 30 分钟  股价快速更新 (显著变化时推送)    │"
    echo "  └─────────────────────────────────────────────┘"
    echo ""
    echo "📊 日志文件:"
    echo "  - 详细报告：$LOG_FILE"
    echo "  - 股价更新：/tmp/price-monitor.log"
    echo "  - 规模检查：/tmp/product-scale.log"
    echo ""
    echo "🔧 常用命令:"
    echo "  - 查看任务：crontab -l"
    echo "  - 查看日志：tail -f $LOG_FILE"
    echo "  - 手动测试：cd $SCRIPT_DIR && python3 run.py --send"
    echo "  - 编辑任务：crontab -e"
    echo "  - 删除任务：crontab -r"
else
    echo "❌ Cron 任务安装失败！"
    rm -f $TEMP_CRON
    exit 1
fi

# 清理临时文件
rm -f $TEMP_CRON

echo ""
echo "============================================================"
