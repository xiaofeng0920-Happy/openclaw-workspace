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
OPENCLAW_PATH = "/home/admin/.nvm/versions/node/v24.14.0/bin/openclaw"
CACHE_FILE = Path(__file__).parent / "data" / "price_cache.json"

# 防止重复推送的标志文件
LOCK_FILE = Path(__file__).parent / "data" / "price_monitor.lock"

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

def check_lock():
    """检查是否有锁（防止重复运行）"""
    if LOCK_FILE.exists():
        import time
        if time.time() - LOCK_FILE.stat().st_mtime > 300:
            LOCK_FILE.unlink()
            return False
        return True
    return False

def set_lock():
    """设置锁"""
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOCK_FILE.touch()

def release_lock():
    """释放锁"""
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()

def send_to_feishu(message: str):
    """发送飞书消息（带锁机制防止重复）"""
    try:
        cache_file = Path(__file__).parent / "data" / "last_sent.json"
        if cache_file.exists():
            import time
            with open(cache_file, 'r') as f:
                last_sent = json.load(f)
            if time.time() - last_sent.get('time', 0) < 300:
                if last_sent.get('hash') == hash(message):
                    print("⏰ 5 分钟内已发送相同内容，跳过")
                    return True
        
        cmd = [
            OPENCLAW_PATH, 'message', 'send',
            '--channel', 'feishu',
            '--target', FEISHU_USER_ID,
            '--message', message
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            import time
            with open(cache_file, 'w') as f:
                json.dump({'time': time.time(), 'hash': hash(message)}, f)
            return True
        return False
    except Exception as e:
        print(f"发送失败：{e}")
        return False

def is_trading_day():
    """检查是否是交易日"""
    now = datetime.now()
    if now.weekday() >= 5:
        return False
    
    hk_holidays = [
        '2026-01-01', '2026-02-18', '2026-02-19', '2026-02-20',
        '2026-04-03', '2026-04-06', '2026-05-01', '2026-05-26',
        '2026-07-01', '2026-09-03', '2026-10-01', '2026-10-02',
        '2026-12-25', '2026-12-26',
    ]
    
    today_str = now.strftime('%Y-%m-%d')
    if today_str in hk_holidays:
        return False
    
    return True

def is_trading_hours():
    """检查是否在交易时间"""
    now = datetime.now()
    hour = now.hour
    
    if not is_trading_day():
        return False
    
    if (9 <= hour < 12) or (13 <= hour < 16):
        return True
    
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
            return news[:10]
    except Exception as e:
        print(f"  ⚠️ 获取新闻失败：{e}")
    return []

def check_earnings():
    """检查财报更新"""
    print("正在检查财报更新...")
    today = datetime.now().strftime('%Y-%m-%d')
    earnings = []
    
    earnings_calendar = {
        'GOOGL': '2026-04-25',
        'MSFT': '2026-04-23',
        'AAPL': '2026-04-30',
        '00700': '2026-03-18',
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
    
    trading_day = is_trading_day()
    trading_hours = is_trading_hours()
    
    print(f"交易日：{'是' if trading_day else '否'}")
    print(f"交易时段：{'是' if trading_hours else '否'}")
    
    send_message = '--send' in sys.argv
    
    if trading_hours:
        print("\n📈 交易时段 - 检查股价...")
        
        cache = load_cache()
        
        print("正在获取最新股价...")
        try:
            data = analyze_holdings()
        except Exception as e:
            print(f"获取数据失败：{e}")
            return
        
        significant = []
        all_stocks = data.get('us_stocks', []) + data.get('hk_stocks', [])
        
        for stock in all_stocks:
            code = stock['symbol']
            change_pct = stock.get('change_pct', 0)
            
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
        
        save_cache({
            'timestamp': datetime.now().isoformat(),
            'stocks': {s['symbol']: s.get('change_pct', 0) for s in all_stocks}
        })
        
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
        
        if send_message and significant:
            if is_quiet_hours():
                print("\n⏰ 静音时段，仅记录不推送")
                return
            
            urgent = [s for s in significant if abs(s['change_pct']) >= 5]
            
            print("\n" + "=" * 60)
            print("📤 发送飞书通知...")
            
            if urgent:
                msg = f"## 🚨 股价警报\n\n"
                msg += f"**时间：** {datetime.now().strftime('%H:%M')}\n\n"
                msg += f"**紧急变化：** {len(urgent)} 只股票波动超 5%\n\n"
                for s in urgent:
                    flag = "📈" if s['change_pct'] > 0 else "📉"
                    msg += f"{flag} **{s['code']}**: {s['change_pct']:+.2f}%\n"
            else:
                msg = f"## 📊 股价更新\n\n"
                msg += f"**时间：** {datetime.now().strftime('%H:%M')}\n\n"
                msg += f"**时段：** 交易时段\n"
                msg += f"**显著变化：** {len(significant)} 只股票波动超 {ALERT_THRESHOLD}%\n\n"
                for s in significant[:5]:
                    flag = "📈" if s['change_pct'] > 0 else "📉"
                    msg += f"{flag} {s['code']}: {s['change_pct']:+.2f}%\n"
            
            if send_to_feishu(msg):
                print("✅ 推送完成")
            else:
                print("❌ 推送失败")
        
        elif significant:
            print("\n⚠️  有显著变化，但未启用推送（使用 --send 参数）")
    
    else:
        print("\n📰 非交易日/非交易时段 - 监控新闻和财报...")
        
        news = get_financial_news()
        earnings = check_earnings()
        
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

if __name__ == "__main__":
    try:
        check_price_changes()
    finally:
        release_lock()
