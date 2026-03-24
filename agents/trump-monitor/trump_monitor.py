#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
川普社交媒体监控
每 30 分钟检查 Truth Social，翻译并推送到飞书
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import hashlib
import requests
import xml.etree.ElementTree as ET

FEISHU_USER_ID = "ou_52fa8f508e88e1efbcbe50c014ecaa6e"
OPENCLAW_PATH = "/home/admin/.nvm/versions/node/v24.14.0/bin/openclaw"
CACHE_FILE = Path(__file__).parent / "data" / "last_post.json"

def get_trump_posts():
    """获取川普最新帖子（通过 Nitter RSS）"""
    print("正在获取川普 Truth Social/Twitter 帖子...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 使用 Nitter RSS（Twitter 镜像）
        response = requests.get(
            'https://nitter.privacy.com.br/realDonaldTrump/rss',
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            channel = root.find('channel')
            
            posts = []
            for item in channel.findall('item')[:5]:
                title = item.find('title').text
                link = item.find('link').text
                pub_date = item.find('pubDate').text
                description = item.find('description').text
                
                # 清理内容
                content = title if title else description
                if description and 'RT' in description:
                    content = description.split('RT ')[-1]
                
                posts.append({
                    'content': content.strip(),
                    'link': link,
                    'time': pub_date
                })
            
            print(f"✅ 获取到 {len(posts)} 条帖子")
            return posts
        
    except Exception as e:
        print(f"⚠️ 获取失败：{e}")
    
    return []

def translate_to_chinese(text):
    """翻译英文到中文（使用简单翻译）"""
    print("正在翻译内容...")
    
    try:
        # 使用 web_fetch 调用翻译服务
        from web_fetch import web_fetch
        
        # 简单翻译：使用 Google Translate URL
        encoded_text = requests.utils.quote(text[:500])
        translate_url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q={encoded_text}"
        
        response = requests.get(translate_url, timeout=10)
        if response.status_code == 200:
            result = response.json()
            translation = ''.join([sentence[0] for sentence in result[0]])
            return translation
        
    except Exception as e:
        print(f"翻译失败：{e}")
    
    return "[翻译暂不可用] " + text

def send_to_feishu(message: str):
    """发送飞书消息"""
    try:
        cmd = [
            OPENCLAW_PATH, 'message', 'send',
            '--channel', 'feishu',
            '--target', FEISHU_USER_ID,
            '--message', message
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except Exception as e:
        print(f"发送失败：{e}")
        return False

def check_cache(post_hash):
    """检查是否已发送"""
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
        if cache.get('hash') == post_hash:
            last_time = datetime.fromisoformat(cache.get('time', '2000-01-01'))
            if datetime.now() - last_time < timedelta(minutes=30):
                return True
    return False

def save_cache(post_hash):
    """保存缓存"""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump({'hash': post_hash, 'time': datetime.now().isoformat()}, f)

def main():
    """主函数"""
    print("=" * 60)
    print("🇺🇸 川普社交媒体监控")
    print("=" * 60)
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    send_message = '--send' in sys.argv
    
    posts = get_trump_posts()
    
    if not posts:
        print("\n⏰ 无新帖子")
        return
    
    latest_post = posts[0]
    post_hash = hashlib.md5(latest_post['content'].encode()).hexdigest()
    
    if check_cache(post_hash):
        print("\n⏰ 30 分钟内已发送过，跳过")
        return
    
    print(f"\n📝 最新帖子:")
    print(f"时间：{latest_post['time']}")
    print(f"内容：{latest_post['content'][:100]}...")
    
    chinese_content = translate_to_chinese(latest_post['content'])
    
    msg = f"## 🇺🇸 川普 Truth Social 更新\n\n"
    msg += f"**时间：** {latest_post['time']}\n\n"
    msg += f"**原文：**\n> {latest_post['content']}\n\n"
    msg += f"**中文翻译：**\n> {chinese_content}\n\n"
    
    if send_message:
        print("\n📤 发送飞书通知...")
        if send_to_feishu(msg):
            print("✅ 推送完成")
            save_cache(post_hash)
        else:
            print("❌ 推送失败")
    
    print("\n" + "=" * 60)
    print("✅ 监控完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
