#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时任务配置
============

使用系统 cron 或 Python 调度器执行定期任务。

任务列表:
1. 价格预警检查（每 5 分钟）
2. 持仓监控（每 4 小时）
3. 产品规模检查（每日 09:00）
4. 巴菲特策略分析（每日收盘后）

配置方法:
1. 使用系统 cron（推荐）
2. 使用 Python APScheduler
3. 使用 OpenClaw 心跳机制
"""

import sys
sys.path.insert(0, '/home/admin/openclaw/workspace')

from notify.price_alert import PriceAlertSystem
from strategies.buffett_analyzer import analyze_portfolio
from datetime import datetime
import subprocess


def check_price_alerts():
    """价格预警检查（每 5 分钟）"""
    print(f"\n{'='*60}")
    print(f"🔔 价格预警检查 - {datetime.now()}")
    print(f"{'='*60}")
    
    alert_system = PriceAlertSystem()
    alert_system.run_check()


def monitor_portfolio():
    """持仓监控（每 4 小时）"""
    print(f"\n{'='*60}")
    print(f"📊 持仓监控 - {datetime.now()}")
    print(f"{'='*60}")
    
    analyze_portfolio()


def pre_market_check():
    """盘前检查（交易日 09:00）"""
    print(f"\n{'='*60}")
    print(f"🌅 盘前检查 - {datetime.now()}")
    print(f"{'='*60}")
    
    # 1. 产品规模检查
    check_product_scale()
    
    # 2. 价格预警检查
    from notify.price_alert import PriceAlertSystem
    alert_system = PriceAlertSystem()
    alert_system.run_check()
    
    print("\n✅ 盘前检查完成")


def check_product_scale():
    """产品规模检查（每日 09:00）"""
    print(f"\n{'='*60}")
    print(f"📈 产品规模检查 - {datetime.now()}")
    print(f"{'='*60}")
    
    # 读取产品规模文件
    try:
        with open('/home/admin/openclaw/workspace/memory/产品管理规模_2026-03-18.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查预警
        if '🔴 紧急' in content:
            print("⚠️ 发现紧急规模预警！")
            # 发送通知
            send_scale_alert()
        
        print("✅ 产品规模检查完成")
        
    except Exception as e:
        print(f"❌ 检查失败：{e}")


def send_scale_alert():
    """发送规模预警通知"""
    try:
        from message import message as msg_tool
        
        alert_msg = """🔴 **产品规模紧急预警**

前锋 8 号：224.64 万元 (< 500 万，已 11 天)
前锋 6 号：191.18 万元 (< 500 万，已 9 天)

⚠️ 停止申购预警日:
- 前锋 8 号：2026-05-29
- 前锋 6 号：2026-06-02

💡 建议：尽快联系渠道，启动持续营销或补充规模"""
        
        msg_tool.send(
            channel='feishu',
            target='ou_52fa8f508e88e1efbcbe50c014ecaa6e',
            message=alert_msg
        )
        print("✅ 规模预警已发送")
        
    except Exception as e:
        print(f"⚠️ 发送预警失败：{e}")


def daily_analysis():
    """每日收盘后分析（每个交易日 16:30）"""
    print(f"\n{'='*60}")
    print(f"📊 每日收盘分析 - {datetime.now()}")
    print(f"{'='*60}")
    
    analyze_portfolio()


# Cron 配置示例
CRON_EXAMPLES = """
# ============================================
# 巴菲特投资系统 - Cron 任务配置
# ============================================

# 价格预警检查（每 5 分钟）
*/5 * * * * cd /home/admin/openclaw/workspace && python3 notify/price_alert.py --check >> /tmp/price_alert.log 2>&1

# 持仓监控（每 4 小时）
0 */4 * * * cd /home/admin/openclaw/workspace && python3 -c "from notify.cron_config import monitor_portfolio; monitor_portfolio()" >> /tmp/portfolio_monitor.log 2>&1

# 产品规模检查（每个交易日 09:00）
0 9 * * 1-5 cd /home/admin/openclaw/workspace && python3 -c "from notify.cron_config import check_product_scale; check_product_scale()" >> /tmp/scale_check.log 2>&1

# 每日收盘分析（每个交易日 16:30）
30 16 * * 1-5 cd /home/admin/openclaw/workspace && python3 -c "from notify.cron_config import daily_analysis; daily_analysis()" >> /tmp/daily_analysis.log 2>&1

# ============================================
# 配置方法:
# 1. crontab -e
# 2. 粘贴上述配置
# 3. 保存退出
# ============================================
"""


def setup_cron():
    """设置 cron 任务"""
    print(CRON_EXAMPLES)
    print("\n💡 配置方法:")
    print("1. 运行：crontab -e")
    print("2. 粘贴上述配置")
    print("3. 保存退出 (:wq)")
    print("\n⚠️ 或者手动添加到 crontab 文件")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='定时任务配置')
    parser.add_argument('--setup', action='store_true', help='显示 cron 配置')
    parser.add_argument('--pre-market', action='store_true', help='执行盘前检查')
    parser.add_argument('--check-alerts', action='store_true', help='执行价格预警检查')
    parser.add_argument('--monitor', action='store_true', help='执行持仓监控')
    parser.add_argument('--check-scale', action='store_true', help='执行产品规模检查')
    parser.add_argument('--daily', action='store_true', help='执行每日分析')
    
    args = parser.parse_args()
    
    if args.setup:
        setup_cron()
    elif args.pre_market:
        pre_market_check()
    elif args.check_alerts:
        check_price_alerts()
    elif args.monitor:
        monitor_portfolio()
    elif args.check_scale:
        check_product_scale()
    elif args.daily:
        daily_analysis()
    else:
        parser.print_help()
