#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易日定时任务调度器
====================

在每个交易日自动执行：
- 盘前检查 (09:00)
- 盘中监控 (每 30 分钟，09:30-16:00)
- 盘后分析 (16:30)

配置方法:
1. 运行此脚本自动配置 cron
2. 或手动添加到 crontab
"""

import sys
import os
from datetime import datetime, timedelta

# 任务配置
TRADING_TASKS = {
    # 盘前检查 (交易日 09:00)
    'pre_market': {
        'time': '0 9 * * 1-5',  # 周一到周五 9:00
        'command': 'python3 /home/admin/openclaw/workspace/notify/cron_config.py --pre-market',
        'description': '盘前检查：产品规模 + 持仓预警'
    },
    
    # 盘中监控 (交易日每 30 分钟)
    'intra_day': {
        'time': '*/30 9-15 * * 1-5',  # 周一到周五 9:00-16:00 每 30 分钟
        'command': 'python3 /home/admin/openclaw/workspace/notify/price_alert.py --check',
        'description': '盘中监控：价格预警 + 巴菲特信号'
    },
    
    # 盘后分析 (交易日 16:30)
    'post_market': {
        'time': '30 16 * * 1-5',  # 周一到周五 16:30
        'command': 'python3 /home/admin/openclaw/workspace/strategies/buffett_analyzer.py',
        'description': '盘后分析：持仓报告 + 盈亏汇总'
    },
    
    # 每日心跳 (每 4 小时)
    'heartbeat': {
        'time': '0 */4 * * *',  # 每 4 小时
        'command': 'python3 /home/admin/openclaw/workspace/notify/cron_config.py --monitor',
        'description': '心跳检查：持仓监控'
    },
}


def is_trading_day(date=None):
    """
    判断是否为交易日
    
    简化版本：只检查周末，不考虑节假日
    实际应用中应该接入交易日日历
    """
    if date is None:
        date = datetime.now()
    
    # 周一到周五是交易日
    return date.weekday() < 5


def generate_crontab():
    """生成 crontab 配置"""
    crontab_lines = [
        "# ============================================",
        "# 巴菲特投资系统 - 交易日定时任务",
        "# 生成时间：" + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "# ============================================",
        "",
        "# 环境变量",
        "SHELL=/bin/bash",
        "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "",
        "# 日志目录",
        "LOG_DIR=/tmp/buffett_system",
        "",
        "# ============================================",
        "# 盘前检查 (交易日 09:00)",
        "# ============================================",
        "0 9 * * 1-5 cd /home/admin/openclaw/workspace && " +
        "python3 notify/cron_config.py --pre-market >> $LOG_DIR/pre_market.log 2>&1",
        "",
        "# ============================================",
        "# 盘中监控 (交易日每 30 分钟)",
        "# ============================================",
        "*/30 9-15 * * 1-5 cd /home/admin/openclaw/workspace && " +
        "python3 notify/price_alert.py --check >> $LOG_DIR/intra_day.log 2>&1",
        "",
        "# ============================================",
        "# 盘后分析 (交易日 16:30)",
        "# ============================================",
        "30 16 * * 1-5 cd /home/admin/openclaw/workspace && " +
        "python3 strategies/buffett_analyzer.py >> $LOG_DIR/post_market.log 2>&1",
        "",
        "# ============================================",
        "# 心跳检查 (每 4 小时)",
        "# ============================================",
        "0 */4 * * * cd /home/admin/openclaw/workspace && " +
        "python3 notify/cron_config.py --monitor >> $LOG_DIR/heartbeat.log 2>&1",
        "",
        "# ============================================",
        "# 产品规模检查 (交易日 09:00)",
        "# ============================================",
        "0 9 * * 1-5 cd /home/admin/openclaw/workspace && " +
        "python3 notify/cron_config.py --check-scale >> $LOG_DIR/scale_check.log 2>&1",
        "",
    ]
    
    return "\n".join(crontab_lines)


def setup_crontab():
    """设置 crontab"""
    print("=" * 60)
    print("⚙️  配置交易日定时任务")
    print("=" * 60)
    
    # 创建日志目录
    log_dir = "/tmp/buffett_system"
    os.makedirs(log_dir, exist_ok=True)
    print(f"✅ 创建日志目录：{log_dir}")
    
    # 生成 crontab 配置
    crontab_content = generate_crontab()
    
    # 显示配置
    print("\n📋 定时任务配置:")
    print("-" * 60)
    print(crontab_content)
    print("-" * 60)
    
    # 提供两种配置方式
    print("\n💡 配置方法:")
    print()
    print("方法 1: 自动安装 (推荐)")
    print("  运行以下命令:")
    print("  crontab -l > /tmp/old_cron.bak  # 备份现有配置")
    print("  (crontab -l 2>/dev/null; cat -) << 'EOF' >> /tmp/new_cron.txt")
    print(crontab_content)
    print("EOF")
    print("  crontab /tmp/new_cron.txt")
    print()
    print("方法 2: 手动配置")
    print("  1. 运行：crontab -e")
    print("  2. 粘贴上面的配置")
    print("  3. 保存退出 (:wq)")
    print()
    
    # 保存配置到文件
    config_file = "/home/admin/openclaw/workspace/notify/buffett_crontab.txt"
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(crontab_content)
    
    print(f"📁 配置已保存到：{config_file}")
    print()
    
    # 显示任务说明
    print("=" * 60)
    print("📊 任务说明")
    print("=" * 60)
    print()
    print("1️⃣  盘前检查 (09:00)")
    print("   - 检查产品规模预警")
    print("   - 检查持仓价格预警")
    print("   - 发送早间提醒")
    print()
    print("2️⃣  盘中监控 (09:30-16:00, 每 30 分钟)")
    print("   - 实时监控价格")
    print("   - 检查巴菲特买卖信号")
    print("   - 触发预警立即推送")
    print()
    print("3️⃣  盘后分析 (16:30)")
    print("   - 分析持仓盈亏")
    print("   - 生成巴菲特评分报告")
    print("   - 发送盘后总结")
    print()
    print("4️⃣  心跳检查 (每 4 小时)")
    print("   - 定期持仓监控")
    print("   - 系统状态检查")
    print()
    
    print("=" * 60)
    print("✅ 配置完成!")
    print("=" * 60)
    print()
    print("📝 下一步:")
    print("  1. 复制上面的 crontab 配置")
    print("  2. 运行：crontab -e")
    print("  3. 粘贴配置并保存")
    print("  4. 验证：crontab -l")
    print()
    print("🔍 查看日志:")
    print("  tail -f /tmp/buffett_system/*.log")
    print()


if __name__ == "__main__":
    setup_crontab()
