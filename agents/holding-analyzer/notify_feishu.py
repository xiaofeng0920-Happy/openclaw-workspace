#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书推送脚本 - 使用飞书开放 API 直接发送消息
"""

import json
import sys
import requests
from pathlib import Path
from datetime import datetime

# 飞书配置
FEISHU_APP_ID = "cli_a92873946239dbd1"
FEISHU_APP_SECRET = "7TyxAnUzgfGyjzi0iIMchgCzHgIbnqju"
FEISHU_USER_ID = "ou_52fa8f508e88e1efbcbe50c014ecaa6e"

def get_tenant_access_token():
    """获取飞书 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }
    
    response = requests.post(url, json=payload, timeout=10)
    result = response.json()
    
    if result.get("code") == 0:
        return result.get("tenant_access_token")
    else:
        raise Exception(f"获取 token 失败：{result}")

def send_to_feishu(message: str):
    """使用飞书开放 API 发送消息"""
    try:
        # 获取 token
        print("正在获取飞书访问令牌...")
        token = get_tenant_access_token()
        
        # 发送消息
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 使用文本消息格式
        params = {"receive_id_type": "open_id"}
        payload = {
            "receive_id": FEISHU_USER_ID,
            "msg_type": "text",
            "content": json.dumps({"text": message})
        }
        
        print(f"发送参数：receive_id={FEISHU_USER_ID}, msg_type=text")
        
        print("正在发送消息...")
        response = requests.post(url, headers=headers, params=params, json=payload, timeout=30)
        result = response.json()
        
        if result.get("code") == 0:
            message_id = result.get("data", {}).get("message_id", "unknown")
            print(f"✅ 消息已发送至飞书 (消息 ID: {message_id})")
            return True
        else:
            print(f"❌ 发送失败：{result}")
            return False
            
    except Exception as e:
        print(f"❌ 发送异常：{e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法：python notify_feishu.py <report_file.md>")
        sys.exit(1)
    
    report_file = Path(sys.argv[1])
    
    if not report_file.exists():
        print(f"❌ 文件不存在：{report_file}")
        sys.exit(1)
    
    # 读取报告
    report_content = report_file.read_text(encoding='utf-8')
    
    # 发送到飞书
    print(f"正在发送报告至飞书...")
    success = send_to_feishu(report_content)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
