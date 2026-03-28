#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试飞书通知发送
"""

import sys
sys.path.insert(0, '/home/admin/openclaw/workspace')

from datetime import datetime

# 测试消息
test_message = f"""🔔 **巴菲特投资系统 - 测试通知**

时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ 系统配置完成！

📊 已启用功能:
• 真实财务数据 API
• 巴菲特选股策略
• 历史回测系统
• 价格预警监控
• 飞书通知推送

🎯 当前持仓分析:
• 中国海洋石油：99/100 强力买入
• 腾讯控股：86/100 持有
• 阿里巴巴：65/100 持有

---
投资有风险，决策需谨慎"""

print(test_message)

# 使用 OpenClaw message 工具发送
try:
    import subprocess
    
    # 通过 OpenClaw message 命令发送
    cmd = [
        'openclaw',
        'message',
        'send',
        '--channel', 'feishu',
        '--target', 'ou_52fa8f508e88e1efbcbe50c014ecaa6e',
        '--message', test_message
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    
    if result.returncode == 0:
        print("\n✅ 飞书通知发送成功！")
    else:
        print(f"\n⚠️ 发送失败：{result.stderr}")
        
except Exception as e:
    print(f"\n⚠️ 发送异常：{e}")
    print("\n💡 请手动创建飞书机器人:")
    print("1. 打开飞书，创建群聊")
    print("2. 添加机器人 → 自定义机器人")
    print("3. 复制 Webhook 地址")
    print("4. 编辑 notify/feishu_config.json")
