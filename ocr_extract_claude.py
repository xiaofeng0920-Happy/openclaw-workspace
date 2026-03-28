#!/usr/bin/env python3
"""OCR extraction using Claude Vision API for better accuracy."""

import anthropic
import base64
from pathlib import Path

def extract_with_claude(image_path: str) -> str:
    """Use Claude to extract text from an image with high accuracy."""
    client = anthropic.Anthropic()
    
    image_data = base64.standard_b64encode(Path(image_path).read_bytes()).decode()
    ext = Path(image_path).suffix.lower()
    media_type = "image/png" if ext == ".png" else "image/jpeg"
    
    prompt = """请提取这张图片中的所有文字内容，包括：
- 标题和副标题
- 所有数字和数据
- 表格内容
- 底部导航栏文字
- 评论区和互动数据

请保持原文的格式和结构，按从上到下的顺序完整输出。
如果某些文字模糊不清，请标注 [模糊]。
只输出提取的文字，不要添加其他解释。"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )
    
    return message.content[0].text

if __name__ == "__main__":
    images = [
        "/home/admin/.openclaw/media/inbound/13b152a4-eb52-4028-8e22-238eea2f5648.png",
        "/home/admin/.openclaw/media/inbound/05438ca6-5c1a-4659-9395-27e3940a49dc.png"
    ]

    for i, img_path in enumerate(images, 1):
        print(f"\n{'='*60}")
        print(f"图片 {i} OCR 结果:")
        print(f"{'='*60}")
        try:
            text = extract_with_claude(img_path)
            print(text)
        except Exception as e:
            print(f"[错误：{e}]")
