#!/usr/bin/env python3
"""
产品规模监控脚本

功能：
1. 每日检查规模预警（<500 万紧急，<1000 万关注）
2. 每月提醒更新管理规模数据
3. 生成规模分析报告

用法：
    python scripts/monitor_product_scale.py [--check|--update|--report]
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 工作空间根目录
WORKSPACE = Path('/home/admin/openclaw/workspace')
MEMORY_DIR = WORKSPACE / 'memory'
LOGS_DIR = WORKSPACE / 'logs'
CONFIG_FILE = WORKSPACE / 'config' / 'dispatch_config.json'

# 预警阈值
SCALE_WARNING_THRESHOLD = 1000  # 万元 - 关注线
SCALE_CRITICAL_THRESHOLD = 500  # 万元 - 警戒线

# 确保目录存在
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def log(message, level='INFO'):
    """日志输出"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [{level}] {message}")


def get_latest_scale_file():
    """获取最新的管理规模文件"""
    files = list(MEMORY_DIR.glob('产品管理规模_*.md'))
    if not files:
        return None
    return max(files, key=lambda f: f.stat().st_mtime)


def parse_scale_file(file_path):
    """解析管理规模文件，提取产品数据"""
    products = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 简单解析 Markdown 表格
    lines = content.split('\n')
    in_table = False
    is_product_table = False
    
    for line in lines:
        # 检测产品明细表格
        if '| 产品名称 |' in line or '| 排名 | 产品名称 |' in line:
            in_table = True
            is_product_table = True
            continue
        
        # 检测表格结束
        if in_table and line.startswith('---'):
            continue
        
        if in_table and is_product_table and line.startswith('|'):
            parts = [p.strip() for p in line.split('|') if p.strip()]
            
            # 跳过表头和分隔线
            if '产品名称' in parts[0] or '排名' in parts[0] or '---' in parts[0]:
                continue
            
            # 解析产品数据（根据实际表格格式）
            try:
                # 格式 1: | 排名 | 产品名称 | 规模 | 最新净值 | 日增长 | 今年增长 | 日期 |
                if len(parts) >= 6 and parts[0].isdigit():
                    # 检查是否已存在（去重）
                    name = parts[1]
                    if any(p['name'] == name for p in products):
                        continue
                    
                    product = {
                        'name': name,
                        'scale': float(parts[2].replace(',', '').replace('万元', '')),
                        'nav': parts[3],
                        'daily_change': parts[4],
                        'ytd_change': parts[5],
                        'date': parts[6] if len(parts) > 6 else ''
                    }
                    products.append(product)
                # 格式 2: | 产品名称 | 规模 | 净值 | ...
                elif len(parts) >= 5 and not parts[0].isdigit():
                    name = parts[0]
                    if any(p['name'] == name for p in products):
                        continue
                    
                    product = {
                        'name': name,
                        'scale': float(parts[1].replace(',', '').replace('万元', '')),
                        'nav': parts[2],
                        'daily_change': parts[3],
                        'ytd_change': parts[4],
                        'date': parts[5] if len(parts) > 5 else ''
                    }
                    products.append(product)
            except (ValueError, IndexError) as e:
                continue
    
    return products


def check_scale_alerts(products):
    """检查规模预警"""
    alerts = {
        'critical': [],  # <500 万
        'warning': [],   # <1000 万
        'normal': []     # >=1000 万
    }
    
    for product in products:
        scale = product.get('scale', 0)
        
        if scale < SCALE_CRITICAL_THRESHOLD:
            alerts['critical'].append(product)
        elif scale < SCALE_WARNING_THRESHOLD:
            alerts['warning'].append(product)
        else:
            alerts['normal'].append(product)
    
    return alerts


def generate_alert_message(alerts, file_date):
    """生成预警消息"""
    message = "📊 **产品规模预警**\n\n"
    message += f"**数据日期：** {file_date}\n"
    message += f"**检查时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    
    # 紧急预警
    if alerts['critical']:
        message += "## 🔴 紧急预警（规模<500 万）\n\n"
        message += "| 产品名称 | 规模 (万元) | 状态 |\n"
        message += "|----------|-----------|------|\n"
        for p in alerts['critical']:
            message += f"| {p['name']} | {p['scale']:.2f} | 需立即关注 |\n"
        message += "\n"
    
    # 关注预警
    if alerts['warning']:
        message += "## 🟡 关注提醒（规模<1000 万）\n\n"
        message += "| 产品名称 | 规模 (万元) | 状态 |\n"
        message += "|----------|-----------|------|\n"
        for p in alerts['warning']:
            message += f"| {p['name']} | {p['scale']:.2f} | 持续观察 |\n"
        message += "\n"
    
    # 正常产品
    if alerts['normal']:
        message += "## 🟢 正常产品（规模≥1000 万）\n\n"
        message += f"共 {len(alerts['normal'])} 只产品，规模健康\n\n"
    
    # 总结
    total_critical = len(alerts['critical'])
    total_warning = len(alerts['warning'])
    
    if total_critical > 0:
        message += f"**⚠️ 共有 {total_critical} 只产品需要紧急处理！**\n"
    elif total_warning > 0:
        message += f"**⚠️ 共有 {total_warning} 只产品需要关注**\n"
    else:
        message += "**✅ 所有产品规模健康**\n"
    
    message += "\n> 数据来源：管理规模.xlsx\n"
    message += "*产品规模监控自动预警*"
    
    return message


def send_alert(message):
    """发送预警消息（模拟）"""
    log(f"📤 准备发送预警消息")
    log(f"📄 消息长度：{len(message)} 字符")
    
    # TODO: 实际实现需要调用 message 工具
    # message(action="send", channel="feishu", target=..., message=message)
    
    # 保存发送记录
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'type': 'scale_alert',
        'messageLength': len(message),
        'status': 'simulated'
    }
    
    log_file = LOGS_DIR / f"scale_alert_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    log(f"✅ 预警记录已保存：{log_file}")
    print("\n" + message)


def check_monthly_update():
    """检查是否需要更新管理规模数据"""
    latest_file = get_latest_scale_file()
    
    if not latest_file:
        return True, "从未更新"
    
    # 检查文件日期
    file_date_str = latest_file.stem.split('_')[-1]  # 提取 YYYY-MM-DD
    try:
        file_date = datetime.strptime(file_date_str, '%Y-%m-%d')
        days_since_update = (datetime.now() - file_date).days
        
        if days_since_update > 30:
            return True, f"已{days_since_update}天未更新"
        else:
            return False, f"上次更新：{days_since_update}天前"
    
    except ValueError:
        return True, "无法解析日期"


def generate_monthly_reminder():
    """生成月度更新提醒"""
    message = "📊 **管理规模数据更新提醒**\n\n"
    message += f"**检查时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    
    needs_update, reason = check_monthly_update()
    
    if needs_update:
        message += f"⚠️ **需要更新** - {reason}\n\n"
        message += "**请上传最新的管理规模 Excel 文件，包含：**\n"
        message += "- 产品名称\n"
        message += "- 产品规模（万元）\n"
        message += "- 最新净值\n"
        message += "- 日净值增长率\n"
        message += "- 今年净值增长率\n"
        message += "- 日期\n"
        message += "- 备注（如有预警）\n\n"
        message += "**上传后我会自动：**\n"
        message += "1. 解析 Excel 数据\n"
        message += "2. 生成管理规模报告\n"
        message += "3. 检查规模预警\n"
        message += "4. 保存到 memory 目录\n\n"
    else:
        message += f"✅ **数据最新** - {reason}\n\n"
        message += "下次更新提醒：约 30 天后\n"
    
    message += "\n*产品规模监控自动提醒*"
    
    return message, needs_update


def daily_check():
    """执行每日检查"""
    log("=" * 50)
    log("🔍 产品规模每日检查")
    log("=" * 50)
    
    # 获取最新文件
    latest_file = get_latest_scale_file()
    
    if not latest_file:
        log("❌ 未找到管理规模文件", 'ERROR')
        log("请先上传管理规模 Excel 文件")
        return False
    
    log(f"📄 使用文件：{latest_file.name}")
    
    # 解析数据
    products = parse_scale_file(latest_file)
    
    if not products:
        log("❌ 无法解析产品数据", 'ERROR')
        return False
    
    log(f"✅ 解析 {len(products)} 只产品")
    
    # 检查预警
    alerts = check_scale_alerts(products)
    
    log(f"🔴 紧急预警：{len(alerts['critical'])} 只")
    log(f"🟡 关注提醒：{len(alerts['warning'])} 只")
    log(f"🟢 正常产品：{len(alerts['normal'])} 只")
    
    # 提取文件日期
    file_date_str = latest_file.stem.split('_')[-1]
    
    # 生成并发送预警消息
    if alerts['critical'] or alerts['warning']:
        message = generate_alert_message(alerts, file_date_str)
        send_alert(message)
    else:
        log("✅ 无预警，无需发送消息")
    
    log("=" * 50)
    log("✅ 每日检查完成")
    log("=" * 50)
    
    return True


def monthly_update():
    """执行月度更新检查"""
    log("=" * 50)
    log("📅 管理规模月度更新检查")
    log("=" * 50)
    
    message, needs_update = generate_monthly_reminder()
    
    if needs_update:
        log("⚠️ 需要更新管理规模数据")
        print("\n" + message)
        # TODO: 发送提醒消息
    else:
        log("✅ 数据最新，无需更新")
    
    log("=" * 50)
    
    return True


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='产品规模监控')
    parser.add_argument('--check', action='store_true', help='每日检查（规模预警）')
    parser.add_argument('--update', action='store_true', help='月度更新检查')
    parser.add_argument('--report', action='store_true', help='生成报告')
    
    args = parser.parse_args()
    
    if args.check:
        return daily_check()
    elif args.update:
        return monthly_update()
    elif args.report:
        # TODO: 生成详细报告
        log("报告功能开发中...")
        return True
    else:
        # 默认执行每日检查
        return daily_check()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
