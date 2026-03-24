#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票价格定时监控 - 每 30 分钟更新
股票投资团队 - 快速股价更新脚本

**交易时段：** 每 30 分钟更新股价
**非交易日：** 仅监控新闻和财报更新

用法：
  python price_monitor.py              # 快速检查，仅记录
  python price_monitor.py --send       # 发送推送（如有显著变化）
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import os

sys.path.insert(0, str(Path(__file__).parent))

from analyzer import analyze_holdings, ALERT_THRESHOLD, get_relevant_news

FEISHU_USER_ID = "ou_52fa8f508e88e1efbcbe50c014ecaa6e"
CACHE_FILE = Path(__file__).parent / "data" / "price_cache.json"

def load_cache():
    """加载上次股价缓存"""
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(data):
    """保存股价缓存"""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def send_to_feishu(message: str):
    """发送飞书消息"""
    try:
        cmd = [
            'openclaw', 'message', 'send',
            '--channel', 'feishu',
            '--target', FEISHU_USER_ID,
            '--message', message
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except Exception as e:
        print(f"发送失败：{e}")
        return False

def is_trading_day():
    """检查是否是交易日"""
    now = datetime.now()
    
    # 周末不是交易日
    if now.weekday() >= 5:  # 周六=5, 周日=6
        return False
    
    # 检查港股假期（简化版，可后续完善）
    hk_holidays = [
        '2026-01-01',  # 元旦
        '2026-02-18',  # 春节
        '2026-02-19',  # 春节
        '2026-02-20',  # 春节
        '2026-04-03',  # 清明节
        '2026-04-06',  # 复活节
        '2026-05-01',  # 劳动节
        '2026-05-26',  # 端午
        '2026-07-01',  # 回归日
        '2026-09-03',  # 中秋
        '2026-10-01',  # 国庆
        '2026-10-02',  # 国庆
        '2026-12-25',  # 圣诞
        '2026-12-26',  # 节礼日
    ]
    
    today_str = now.strftime('%Y-%m-%d')
    if today_str in hk_holidays:
        return False
    
    return True

def is_trading_hours():
    """检查是否在交易时间"""
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    
    # 首先检查是否是交易日
    if not is_trading_day():
        return False
    
    # 港股交易时间：09:30-12:00, 13:00-16:00
    if (9 <= hour < 12) or (13 <= hour < 16):
        return True
    
    # 美股交易时间：21:30-04:00
    if hour >= 21 or hour < 4:
        return True
    
    return False

def is_quiet_hours():
    """检查是否在静音时段（23:00-07:00）"""
    hour = datetime.now().hour
    return hour >= 23 or hour < 7

def get_financial_news():
    """获取财经新闻"""
    print("正在获取财经新闻...")
    try:
        news = get_relevant_news()
        if news:
            print(f"  ✅ 获取到 {len(news)} 条新闻")
            return news[:10]  # 最多 10 条
    except Exception as e:
        print(f"  ⚠️ 获取新闻失败：{e}")
    return []

def check_earnings():
    """检查财报更新"""
    print("正在检查财报更新...")
    # 简化版本：返回固定消息
    # 实际可以接入财报日历 API
    today = datetime.now().strftime('%Y-%m-%d')
    earnings = []
    
    # 示例：检查已知持仓股票的财报日期
    earnings_calendar = {
        'GOOGL': '2026-04-25',
        'MSFT': '2026-04-23',
        'AAPL': '2026-04-30',
        '00700': '2026-03-18',  # 已发布
        '09988': '2026-05-15',
    }
    
    for stock, date in earnings_calendar.items():
        if date == today:
            earnings.append({'stock': stock, 'date': date, 'status': '今日发布'})
        elif date > today and (datetime.strptime(date, '%Y-%m-%d') - datetime.now()).days <= 7:
            earnings.append({'stock': stock, 'date': date, 'status': f'{(datetime.strptime(date, "%Y-%m-%d") - datetime.now()).days}天后'})
    
    if earnings:
        print(f"  ✅ 发现 {len(earnings)} 只股票财报更新")
    else:
        print("  无近期财报")
    
    return earnings

def check_price_changes():
    """检查股价变化（交易时段）或新闻/财报（非交易日）"""
    print("=" * 60)
    print("📊 股票投资监控 - 快速检查")
    print("=" * 60)
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查是否是交易日
    trading_day = is_trading_day()
    trading_hours = is_trading_hours()
    
    print(f"交易日：{'是' if trading_day else '否'}")
    print(f"交易时段：{'是' if trading_hours else '否'}")
    
    send_message = '--send' in sys.argv
    
    # 交易时段：检查股价
    if trading_hours:
        print("\n📈 交易时段 - 检查股价...")
        
        # 加载缓存
        cache = load_cache()
        
        # 获取最新数据
        print("正在获取最新股价...")
        try:
            data = analyze_holdings()
        except Exception as e:
            print(f"获取数据失败：{e}")
            return
        
        # 检查显著变化
        significant = []
        all_stocks = data.get('us_stocks', []) + data.get('hk_stocks', [])
        
        for stock in all_stocks:
            code = stock['symbol']
            change_pct = stock.get('change_pct', 0)
            
            # 检查是否显著变化
            if abs(change_pct) >= ALERT_THRESHOLD:
                significant.append({
                    'code': code,
                    'name': stock.get('name', code),
                    'change_pct': change_pct,
                    'price': stock.get('current_price', 'N/A')
                })
        
        print(f"\n显著变化股票：{len(significant)} 只")
        for s in significant:
            flag = "📈" if s['change_pct'] > 0 else "📉"
            print(f"  {flag} {s['code']}: {s['change_pct']:+.2f}%")
        
        # 保存缓存
        save_cache({
            'timestamp': datetime.now().isoformat(),
            'stocks': {s['symbol']: s.get('change_pct', 0) for s in all_stocks}
        })
        
        # 保存简要报告
        reports_dir = Path(__file__).parent / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        report_file = reports_dir / f"price_update_{timestamp}.md"
        
        with open(report_file, 'w') as f:
            f.write(f"# 📊 股价快速更新\n\n")
            f.write(f"**时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**时段：** 交易时段\n\n")
            f.write(f"## 显著变化 ({len(significant)} 只)\n\n")
            if significant:
                f.write("| 股票 | 代码 | 涨跌幅 |\n")
                f.write("|------|------|--------|\n")
                for s in significant:
                    flag = "📈" if s['change_pct'] > 0 else "📉"
                    f.write(f"| {flag} {s['name']} | {s['code']} | {s['change_pct']:+.2f}% |\n")
            else:
                f.write("无显著变化股票\n")
        
        print(f"\n💾 报告已保存：{report_file}")
        
        # 决定是否推送
        if send_message and significant:
            # 检查是否在静音时段
            if is_quiet_hours():
                print("\n⏰ 静音时段，仅记录不推送")
                return
            
            # 检查是否有紧急变化（>5%）
            urgent = [s for s in significant if abs(s['change_pct']) >= 5]
            
            print("\n" + "=" * 60)
            print("📤 发送飞书通知...")
            
            if urgent:
                # 紧急推送
                msg = f"## 🚨 股价警报\n\n"
                msg += f"**时间：** {datetime.now().strftime('%H:%M')}\n\n"
                msg += f"**紧急变化：** {len(urgent)} 只股票波动超 5%\n\n"
                for s in urgent:
                    flag = "📈" if s['change_pct'] > 0 else "📉"
                    msg += f"{flag} **{s['code']}**: {s['change_pct']:+.2f}%\n"
            else:
                # 普通推送
                msg = f"## 📊 股价更新\n\n"
                msg += f"**时间：** {datetime.now().strftime('%H:%M')}\n\n"
                msg += f"**时段：** 交易时段\n"
                msg += f"**显著变化：** {len(significant)} 只股票波动超 {ALERT_THRESHOLD}%\n\n"
                for s in significant[:5]:  # 最多显示 5 只
                    flag = "📈" if s['change_pct'] > 0 else "📉"
                    msg += f"{flag} {s['code']}: {s['change_pct']:+.2f}%\n"
            
            if send_to_feishu(msg):
                print("✅ 推送完成")
            else:
                print("❌ 推送失败")
        
        elif significant:
            print("\n⚠️  有显著变化，但未启用推送（使用 --send 参数）")
    
    # 非交易日：监控新闻和财报
    else:
        print("\n📰 非交易日 - 监控新闻和财报...")
        
        # 获取财经新闻
        news = get_financial_news()
        
        # 检查财报更新
        earnings = check_earnings()
        
        # 保存报告
        reports_dir = Path(__file__).parent / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        report_file = reports_dir / f"news_update_{timestamp}.md"
        
        with open(report_file, 'w') as f:
            f.write(f"# 📰 财经新闻更新\n\n")
            f.write(f"**时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**时段：** 非交易日\n\n")
            
            if news:
                f.write("## 重要新闻\n\n")
                for i, n in enumerate(news, 1):
                    f.write(f"{i}. **{n.get('title', 'N/A')}** - {n.get('source', 'N/A')}\n")
                f.write("\n")
            
            if earnings:
                f.write("## 财报更新\n\n")
                for e in earnings:
                    f.write(f"- **{e['stock']}**: {e['status']} ({e['date']})\n")
                f.write("\n")
            
            if not news and not earnings:
                f.write("无重要更新\n")
        
        print(f"\n💾 报告已保存：{report_file}")
        
        # 如果有重要新闻或财报，发送推送
        if send_message and (news or earnings):
            print("\n" + "=" * 60)
            print("📤 发送飞书通知...")
            
            msg = f"## 📰 财经资讯更新\n\n"
            msg += f"**时间：** {datetime.now().strftime('%H:%M')}\n\n"
            
            if news:
                msg += f"**重要新闻：** {len(news)} 条\n\n"
                for n in news[:3]:
                    msg += f"- {n.get('title', 'N/A')[:50]}...\n"
                msg += "\n"
            
            if earnings:
                msg += f"**财报更新：** {len(earnings)} 只\n\n"
                for e in earnings:
                    msg += f"- {e['stock']}: {e['status']}\n"
            
            if send_to_feishu(msg):
                print("✅ 推送完成")
            else:
                print("❌ 推送失败")
    
    print("\n" + "=" * 60)
    print("✅ 检查完成")
    print("=" * 60)
    
    # 释放锁
    release_lock()

if __name__ == "__main__":
    check_price_changes()
