# -*- coding: utf-8 -*-
"""
飞书通知集成
============

通过飞书开放平台发送通知消息。

支持的消息类型:
- 文本消息
- 富文本消息
- 卡片消息
- 交互式卡片

使用方法:
    from notify.feishu_notifier import FeishuNotifier
    
    notifier = FeishuNotifier()
    notifier.send_text("测试消息", user_id="ou_xxx")
"""

import json
import requests
from typing import List, Optional, Dict
from datetime import datetime
import hashlib
import hmac
import base64
import time


class FeishuNotifier:
    """
    飞书通知发送器
    
    支持两种发送方式:
    1. 机器人 Webhook（群聊）
    2. 开放平台 API（私聊/群聊）
    """
    
    def __init__(self, webhook_url: str = None, app_id: str = None, app_secret: str = None):
        """
        初始化飞书通知器
        
        参数:
            webhook_url: 机器人 Webhook URL（群聊用）
            app_id: 飞书应用 App ID
            app_secret: 飞书应用 App Secret
        """
        self.webhook_url = webhook_url
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.token_expire_time = 0
        
        # 默认配置
        self.default_user_id = "ou_52fa8f508e88e1efbcbe50c014ecaa6e"  # 锋哥
    
    def get_access_token(self) -> Optional[str]:
        """获取访问令牌"""
        if not self.app_id or not self.app_secret:
            return None
        
        # 检查 token 是否过期
        if self.access_token and time.time() < self.token_expire_time:
            return self.access_token
        
        try:
            url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
            payload = {
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }
            
            response = requests.post(url, json=payload, timeout=10)
            data = response.json()
            
            if data.get('code') == 0:
                self.access_token = data['tenant_access_token']
                self.token_expire_time = time.time() + 7000  # 提前 1000 秒过期
                return self.access_token
            else:
                print(f"❌ 获取 token 失败：{data}")
                return None
                
        except Exception as e:
            print(f"❌ 获取 token 异常：{e}")
            return None
    
    def send_text(self, text: str, user_id: str = None, open_id: str = None, 
                  chat_id: str = None, msg_type: str = 'text') -> bool:
        """
        发送文本消息
        
        参数:
            text: 消息内容
            user_id: 用户 ID
            open_id: 用户 Open ID
            chat_id: 群聊 ID
            msg_type: 消息类型 ('text' | 'post' | 'interactive')
        
        返回:
            是否发送成功
        """
        # 确定接收者
        receive_id = user_id or open_id or chat_id
        if not receive_id:
            receive_id = self.default_user_id
        
        # 确定 ID 类型
        if user_id:
            id_type = 'user_id'
        elif open_id:
            id_type = 'open_id'
        elif chat_id:
            id_type = 'chat_id'
        else:
            id_type = 'open_id'  # 默认
        
        # 使用 Webhook 发送（群聊）
        if self.webhook_url and chat_id:
            return self._send_via_webhook(text)
        
        # 使用 API 发送（私聊/群聊）
        if self.app_id and self.app_secret:
            return self._send_via_api(text, receive_id, id_type, msg_type)
        
        print("⚠️ 未配置飞书通知凭证")
        return False
    
    def _send_via_webhook(self, text: str) -> bool:
        """通过 Webhook 发送（群聊机器人）"""
        try:
            payload = {
                "msg_type": "text",
                "content": {
                    "text": text
                }
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            data = response.json()
            if data.get('StatusCode') == 0 or data.get('code') == 0:
                print(f"✅ 飞书 Webhook 发送成功")
                return True
            else:
                print(f"❌ 飞书 Webhook 发送失败：{data}")
                return False
                
        except Exception as e:
            print(f"❌ 飞书 Webhook 发送异常：{e}")
            return False
    
    def _send_via_api(self, text: str, receive_id: str, id_type: str, msg_type: str) -> bool:
        """通过 API 发送"""
        token = self.get_access_token()
        if not token:
            return False
        
        try:
            url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={id_type}"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "receive_id": receive_id,
                "msg_type": msg_type,
                "content": json.dumps({
                    "text": text
                }, ensure_ascii=False)
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            data = response.json()
            
            if data.get('code') == 0:
                print(f"✅ 飞书 API 发送成功到 {id_type}={receive_id}")
                return True
            else:
                print(f"❌ 飞书 API 发送失败：{data}")
                return False
                
        except Exception as e:
            print(f"❌ 飞书 API 发送异常：{e}")
            return False
    
    def send_rich_text(self, content: List[List[Dict]]) -> bool:
        """
        发送富文本消息
        
        参数:
            content: 富文本内容，格式如:
            [
                [{"tag": "text", "text": "你好 "}, {"tag": "a", "text": "点击这里", "href": "https://..."}],
                [{"tag": "text", "text": "第二行"}]
            ]
        """
        receive_id = self.default_user_id
        
        token = self.get_access_token()
        if not token:
            return False
        
        try:
            url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "receive_id": receive_id,
                "msg_type": "post",
                "content": json.dumps({
                    "zh_cn": {
                        "title": "📊 投资提醒",
                        "content": content
                    }
                }, ensure_ascii=False)
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            data = response.json()
            
            if data.get('code') == 0:
                print(f"✅ 飞书富文本发送成功")
                return True
            else:
                print(f"❌ 飞书富文本发送失败：{data}")
                return False
                
        except Exception as e:
            print(f"❌ 飞书富文本发送异常：{e}")
            return False
    
    def send_card(self, card_json: Dict) -> bool:
        """
        发送交互式卡片消息
        
        参数:
            card_json: 卡片配置 JSON
        """
        receive_id = self.default_user_id
        
        token = self.get_access_token()
        if not token:
            return False
        
        try:
            url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "receive_id": receive_id,
                "msg_type": "interactive",
                "content": json.dumps(card_json, ensure_ascii=False)
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            data = response.json()
            
            if data.get('code') == 0:
                print(f"✅ 飞书卡片发送成功")
                return True
            else:
                print(f"❌ 飞书卡片发送失败：{data}")
                return False
                
        except Exception as e:
            print(f"❌ 飞书卡片发送异常：{e}")
            return False


def create_alert_card(alerts: List[Dict]) -> Dict:
    """
    创建预警卡片
    
    参数:
        alerts: 预警列表
    
    返回:
        卡片配置 JSON
    """
    elements = []
    
    for alert in alerts:
        color = 'red' if '下跌' in alert.get('message', '') or '卖出' in alert.get('message', '') else 'green'
        
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**{alert.get('name')}**\n{alert.get('message')}"
            }
        })
    
    card = {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "template": "red",
            "title": {
                "tag": "plain_text",
                "content": "🔔 价格预警通知"
            }
        },
        "elements": elements
    }
    
    return card


def demo_notifier():
    """演示通知发送"""
    print("=" * 60)
    print("📤 飞书通知演示")
    print("=" * 60)
    
    # 创建通知器（需要配置凭证）
    notifier = FeishuNotifier(
        # webhook_url="https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
        # app_id="cli_xxx",
        # app_secret="xxx"
    )
    
    # 测试文本消息
    text = """🔔 **价格预警通知**

📈 腾讯控股 (00700)
突破上涨预警价 550.00 港元，现价 555.00 港元

🎯 中国海洋石油 (00883)
出现巴菲特买入信号！安全边际 35.2%，评分 85/100

---
投资有风险，决策需谨慎"""
    
    print("\n准备发送消息:")
    print(text)
    print("\n⚠️ 实际发送需要配置飞书凭证")
    
    # 实际发送（需要配置）
    # notifier.send_text(text)


if __name__ == "__main__":
    demo_notifier()
