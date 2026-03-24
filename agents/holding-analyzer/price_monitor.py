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
    """检查是否在交易时间（港股或美股）"""
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    
    if not is_trading_day():
        return False
    
    # 港股交易时间：09:30-12:00, 13:00-16:00
    if (hour == 9 and minute >= 30) or (10 <= hour < 12) or (13 <= hour < 16):
        return True
    
    # 美股交易时间：21:30-04:00
    if (hour == 21 and minute >= 30) or (22 <= hour < 24) or (0 <= hour < 4):
        return True
    
    return False

def is_hk_after_hours():
    """检查是否是港股盘后（16:00-18:00）"""
    now = datetime.now()
    hour = now.hour
    
    if not is_trading_day():
        return False
    
    # 港股盘后：16:00-18:00
    if 16 <= hour < 18:
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

def generate_daily_summary():
    """生成盘后总结报告"""
    print("\n📊 生成盘后总结报告...")
    
    try:
        data = analyze_holdings()
    except Exception as e:
        print(f"获取数据失败：{e}")
        return
    
    all_stocks = data.get('us_stocks', []) + data.get('hk_stocks', [])
    significant = [s for s in all_stocks if abs(s.get('change_pct', 0)) >= 3]
    
    # 生成总结报告
    msg = f"## 📊 盘后总结\n\n"
    msg += f"**日期：** {datetime.now().strftime('%Y-%m-%d')}\n"
    msg += f"**时间：** {datetime.now().strftime('%H:%M')}\n\n"
    
    msg += f"**显著变化：** {len(significant)} 只股票波动超 3%\n\n"
    
    if significant:
        msg += "| 股票 | 代码 | 涨跌幅 |\n"
        msg += "|------|------|--------|\n"
        for s in sorted(significant, key=lambda x: abs(x['change_pct']), reverse=True):
            flag = "📈" if s['change_pct'] > 0 else "📉"
            msg += f"| {flag} {s['name']} | {s['code']} | {s['change_pct']:+.2f}% |\n"
    
    msg += f"\n_明日 09:30 继续监控_"
    
    if send_to_feishu(msg):
        print("✅ 盘后总结已发送")
    else:
        print("❌ 盘后总结发送失败")

def check_price_changes():
    """检查股价变化（交易时段）或新闻/财报（非交易日）"""
    print("=" * 60)
    print("📊 股票投资监控 - 快速检查")
    print("=" * 60)
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    trading_day = is_trading_day()
    trading_hours = is_trading_hours()
    hk_after_hours = is_hk_after_hours()
    
    print(f"交易日：{'是' if trading_day else '否'}")
    print(f"交易时段：{'是' if trading_hours else '否'}")
    print(f"港股盘后：{'是' if hk_after_hours else '否'}")
    
    send_message = '--send' in sys.argv
    
    # 港股盘后总结（17:00 发送一次）
    if hk_after_hours:
        now = datetime.now()
        if now.hour == 17 and now.minute <= 5:  # 17:00-17:05 发送
            print("\n📊 港股盘后 - 发送总结报告...")
            generate_daily_summary()
            return
        else:
            print("\n⏰ 港股盘后，已发送过总结，跳过本次检查")
            return
    
    if trading_hours:
        print("\n📈 交易时段 - 检查股价...")
        
        cache = load_cache()
        
        print("正在获取最新股价...")
        try:
            data = analyze_holdings()
        except Exception as e:
            print(f"获取数据失败：{e}")
            return
        
        # 判断当前是哪个市场的交易时段
        hour = datetime.now().hour
        is_hk_session = (9 <= hour < 12) or (13 <= hour < 16)
        is_us_session = (hour >= 21) or (hour < 4)
        
        # 根据交易时段选择股票
        if is_hk_session:
            print("  港股交易时段 - 仅监控港股")
            all_stocks = data.get('hk_stocks', [])
        elif is_us_session:
            print("  美股交易时段 - 仅监控美股")
            all_stocks = data.get('us_stocks', [])
        else:
            all_stocks = data.get('us_stocks', []) + data.get('hk_stocks', [])
        
        significant = []
        
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
        # 非交易时段：不监控股价，仅记录日志
        print("\n⏰ 非交易时段，不监控股价")
        print("   盘后总结：17:00 发送")
        print("   下次检查：下一个交易时段")
    
    print("\n" + "=" * 60)
    print("✅ 检查完成")
    print("=" * 60)

if __name__ == "__main__":
    try:
        check_price_changes()
    finally:
        release_lock()
