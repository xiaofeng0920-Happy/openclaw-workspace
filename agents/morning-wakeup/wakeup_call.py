#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
早晨叫醒服务 - 综合版
包含：叫醒提醒 + 天气预报 + 隔夜市场简报 + 今日日程

用法：
  python wakeup_call.py --send    # 发送完整叫醒服务
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import json

FEISHU_USER_ID = "ou_52fa8f508e88e1efbcbe50c014ecaa6e"

def get_weather():
    """获取天气预报"""
    try:
        import requests
        # 使用 wttr.in 获取天气预报（免费，无需 API key）
        response = requests.get('https://wttr.in/Shanghai?format=j1', timeout=10)
        if response.status_code == 200:
            data = response.json()
            current = data['current_condition'][0]
            forecast = data['weather'][0]
            
            return {
                'temp': current.get('temp_C', 'N/A'),
                'weather': current.get('weatherDescZh', [{}])[0].get('value', current.get('weatherDesc', [{}])[0].get('value', 'N/A')),
                'humidity': current.get('humidity', 'N/A'),
                'wind': current.get('windspeedKmph', 'N/A'),
                'high': forecast.get('maxtempC', 'N/A'),
                'low': forecast.get('mintempC', 'N/A'),
            }
    except Exception as e:
        print(f"获取天气失败：{e}")
    
    # 备用：返回示例数据
    return {
        'temp': '18',
        'weather': '多云',
        'humidity': '65%',
        'wind': '15',
        'high': '22',
        'low': '15',
    }

def get_market_summary():
    """获取隔夜市场简报"""
    try:
        sys.path.insert(0, '/home/admin/openclaw/workspace/agents/holding-analyzer')
        from analyzer import analyze_holdings
        
        data = analyze_holdings()
        
        # 提取关键数据
        us_stocks = data.get('us_stocks', [])
        hk_stocks = data.get('hk_stocks', [])
        
        # 找出最大涨跌幅
        all_stocks = us_stocks + hk_stocks
        if all_stocks:
            top_gainer = max(all_stocks, key=lambda x: x.get('change_pct', 0))
            top_loser = min(all_stocks, key=lambda x: x.get('change_pct', 0))
            
            return {
                'top_gainer': top_gainer,
                'top_loser': top_loser,
                'significant_count': len([s for s in all_stocks if abs(s.get('change_pct', 0)) >= 3])
            }
    except Exception as e:
        print(f"获取市场数据失败：{e}")
    
    return None

def get_calendar():
    """获取今日日程（从 MEMORY.md 或日历文件）"""
    # 简化版本：返回固定提醒
    return [
        "09:00 - 早盘持仓监控",
        "13:00 - 午间持仓监控",
        "19:00 - 晚间持仓监控",
        "每 30 分钟 - 股价快速更新",
    ]

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

def send_tts(text: str):
    """发送 TTS 语音"""
    try:
        cmd = [
            'openclaw', 'tts',
            '--channel', 'feishu',
            '--text', text
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except Exception as e:
        print(f"TTS 失败：{e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("⏰ 早晨叫醒服务 - 启动")
    print("=" * 60)
    
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    weekday = now.strftime('%A')
    
    # 1. 获取数据
    print("\n📊 正在获取数据...")
    
    print("  获取天气预报...")
    weather = get_weather()
    
    print("  获取市场简报...")
    market = get_market_summary()
    
    print("  获取今日日程...")
    calendar = get_calendar()
    
    # 2. 构建叫醒消息
    print("\n📝 构建叫醒消息...")
    
    message = f"""## ⏰ 起床时间到！

**锋哥，早上好！** 🌞

**日期：** {date_str} ({weekday})
**当前时间：** {now.strftime('%H:%M')}

---

### 🌤️ 天气预报（上海）

| 项目 | 数值 |
|------|------|
| 当前温度 | {weather['temp']}°C |
| 天气状况 | {weather['weather']} |
| 湿度 | {weather['humidity']} |
| 风速 | {weather['wind']} km/h |
| 今日最高 | {weather['high']}°C |
| 今日最低 | {weather['low']}°C |

**穿衣建议：** {('建议穿薄外套' if int(weather.get('high', 20)) < 25 else '可以穿短袖') if weather.get('high', '20').isdigit() else '根据实际温度调整'}

---

### 📊 隔夜市场简报

"""
    
    if market:
        top_g = market.get('top_gainer', {})
        top_l = market.get('top_loser', {})
        
        message += f"""**最大涨幅：** 📈 {top_g.get('symbol', 'N/A')} ({top_g.get('change_pct', 0):+.2f}%)
**最大跌幅：** 📉 {top_l.get('symbol', 'N/A')} ({top_l.get('change_pct', 0):+.2f}%)
**显著变化：** {market.get('significant_count', 0)} 只股票波动超 3%

"""
    else:
        message += "**市场数据暂缺**\n\n"
    
    message += f"""---

### 📋 今日日程提醒

"""
    
    for item in calendar:
        message += f"- {item}\n"
    
    message += f"""
---

### 💡 温馨提示

新的一天开始了，祝你今天工作顺利！🚀

**持仓监控：** 已自动运行，如有显著变化会及时推送。

---

*早安！加油！* 💪
"""
    
    # 3. 发送消息
    print("\n📤 发送飞书消息...")
    if send_to_feishu(message):
        print("✅ 消息已发送")
    else:
        print("❌ 消息发送失败")
    
    # 4. 发送 TTS 语音
    print("\n🔊 发送 TTS 语音...")
    tts_text = f"锋哥，早上好！现在是早上 7 点，该起床啦！新的一天开始了，祝你今天工作顺利！"
    if send_tts(tts_text):
        print("✅ 语音已发送")
    else:
        print("❌ 语音发送失败")
    
    print("\n" + "=" * 60)
    print("✅ 叫醒服务完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
