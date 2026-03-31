#!/usr/bin/env python3
"""
持仓截图 OCR 识别脚本
使用 Tesseract 识别股票持仓截图中的股票名称、数量、盈亏等信息
"""

import sys
import subprocess
import json
import re
from pathlib import Path

def run_ocr(image_path):
    """使用 Tesseract 进行 OCR 识别"""
    result = subprocess.run(
        ['tesseract', image_path, 'stdout', '-l', 'chi_sim+eng'],
        capture_output=True,
        text=True
    )
    return result.stdout

def parse_holdings(ocr_text):
    """解析 OCR 文本，提取持仓信息"""
    holdings = []
    
    # 匹配股票行模式
    # 例如：GOOGL 谷歌-A  1,283 股  $188.56  -8.79%
    patterns = [
        # 美股模式：代码 + 名称 + 数量 + 价格 + 盈亏
        r'([A-Z]{2,6})\s+([\u4e00-\u9fa5A-Z\-]+)\s+([\d,]+)\s*股\s+\$?([\d.]+)\s+([+-]?[\d.]+)%',
        # 港股模式：代码 + 名称 + 数量 + 价格 + 盈亏
        r'(\d{5,6})\s+([\u4e00-\u9fa5A-Z\-]+)\s+([\d,]+)\s+([\d.]+)\s+([+-]?[\d.]+)%',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, ocr_text)
        for match in matches:
            try:
                if len(match.groups()) == 5:
                    code, name, quantity, price, change = match.groups()
                    holdings.append({
                        'code': code,
                        'name': name.strip(),
                        'quantity': quantity.replace(',', ''),
                        'price': price,
                        'change': change
                    })
            except Exception as e:
                print(f"解析失败：{e}")
    
    return holdings

def main():
    if len(sys.argv) < 2:
        print("用法：python3 ocr_holdings.py <图片路径>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not Path(image_path).exists():
        print(f"错误：文件不存在 {image_path}")
        sys.exit(1)
    
    print(f"📷 开始 OCR 识别：{image_path}")
    
    # 执行 OCR
    ocr_text = run_ocr(image_path)
    
    print("\n=== OCR 识别结果 ===")
    print(ocr_text[:2000] if len(ocr_text) > 2000 else ocr_text)
    print("\n=== 解析持仓 ===")
    
    # 解析持仓
    holdings = parse_holdings(ocr_text)
    
    if holdings:
        print(f"\n✅ 识别到 {len(holdings)} 只股票：\n")
        for h in holdings:
            print(f"  {h['code']} {h['name']}: {h['quantity']}股 @ ${h['price']} ({h['change']}%)")
    else:
        print("\n⚠️  未识别到标准格式的持仓，可能需要手动调整")
    
    # 输出 JSON
    print("\n=== JSON 输出 ===")
    print(json.dumps(holdings, ensure_ascii=False, indent=2))
    
    return holdings

if __name__ == '__main__':
    main()
