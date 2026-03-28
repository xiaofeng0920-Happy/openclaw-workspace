#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品规模监控 - 本地脚本，无需大模型
检查产品管理规模，预警低于 500 万的产品
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# 飞书用户 ID
FEISHU_USER_ID = "ou_52fa8f508e88e1efbcbe50c014ecaa6e"

# 预警阈值
SCALE_WARNING = 500  # 500 万
SCALE_ATTENTION = 1000  # 1000 万

def send_to_feishu(message: str):
    """使用 OpenClaw message 工具发送飞书消息"""
    try:
        cmd = [
            'openclaw', 'message', 'send',
            '--channel', 'feishu',
            '--target', FEISHU_USER_ID,
            '--message', message
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ 消息已发送至飞书")
            return True
        else:
            print(f"❌ 发送失败：{result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 发送异常：{e}")
        return False

def parse_scale_file(file_path: Path):
    """解析产品规模 Markdown 文件"""
    if not file_path.exists():
        return None
    
    content = file_path.read_text(encoding='utf-8')
    
    products = []
    lines = content.split('\n')
    
    in_table = False
    for line in lines:
        # 检测表格开始
        if '| 排名 | 产品名称 | 规模 (万元) |' in line:
            in_table = True
            continue
        
        if in_table:
            # 跳过表头分隔线
            if line.startswith('|---'):
                continue
            
            # 解析数据行
            if line.startswith('|') and '|' in line[1:]:
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) >= 3:
                    try:
                        rank = int(parts[0])
                        name = parts[1]
                        scale_str = parts[2].replace(',', '')
                        scale = float(scale_str)
                        
                        products.append({
                            'rank': rank,
                            'name': name,
                            'scale': scale  # 单位：万元
                        })
                    except (ValueError, IndexError):
                        continue
            
            # 检测表格结束
            if line.strip() == '' or not line.startswith('|'):
                in_table = False
    
    return products

def check_scale():
    """检查产品规模"""
    # 查找最新的产品规模文件
    memory_dir = Path('/home/admin/openclaw/workspace/memory')
    scale_files = list(memory_dir.glob('产品管理规模_*.md'))
    
    if not scale_files:
        print("❌ 未找到产品规模文件")
        return None
    
    # 按日期排序，取最新的
    latest_file = sorted(scale_files)[-1]
    print(f"📄 读取文件：{latest_file.name}")
    
    products = parse_scale_file(latest_file)
    
    if not products:
        print("❌ 解析失败")
        return None
    
    # 分析规模
    warnings = []
    total_scale = 0
    
    for p in products:
        total_scale += p['scale']
        
        if p['scale'] < SCALE_WARNING:
            warnings.append({
                **p,
                'level': '🔴 紧急',
                'message': f"规模仅{p['scale']:.0f}万，已低于{SCALE_WARNING}万"
            })
        elif p['scale'] < SCALE_ATTENTION:
            warnings.append({
                **p,
                'level': '🟡 关注',
                'message': f"规模{p['scale']:.0f}万，低于{SCALE_ATTENTION}万"
            })
    
    return {
        'file': latest_file.name,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'products': products,
        'warnings': warnings,
        'total_scale': total_scale,
        'product_count': len(products)
    }

def generate_report(result: dict):
    """生成规模报告"""
    lines = []
    lines.append("## 📊 产品规模监控")
    lines.append(f"**检查时间：** {result['timestamp']}")
    lines.append(f"**数据源：** {result['file']}")
    lines.append("")
    
    # 总览
    lines.append("### 总览")
    lines.append(f"- 产品数量：{result['product_count']} 只")
    lines.append(f"- 总规模：**{result['total_scale']:,.0f} 万元** ({result['total_scale']/10000:.2f} 亿元)")
    lines.append("")
    
    # 预警
    if result['warnings']:
        lines.append("### ⚠️ 规模预警")
        lines.append("")
        lines.append("| 产品 | 规模 (万元) | 状态 |")
        lines.append("|------|-----------|------|")
        
        for w in sorted(result['warnings'], key=lambda x: x['scale']):
            lines.append(f"| {w['name']} | {w['scale']:,.0f} | {w['level']} |")
        
        lines.append("")
    else:
        lines.append("### ✅ 无预警")
        lines.append("所有产品规模均高于 500 万")
        lines.append("")
    
    # 规模分布
    lines.append("### 规模分布")
    lines.append("")
    
    ranges = [
        ('>1 亿元', lambda s: s > 10000),
        ('5000 万 -1 亿', lambda s: 5000 < s <= 10000),
        ('1000 万 -5000 万', lambda s: 1000 < s <= 5000),
        ('500 万 -1000 万', lambda s: 500 < s <= 1000),
        ('<500 万', lambda s: s <= 500),
    ]
    
    for range_name, check in ranges:
        count = sum(1 for p in result['products'] if check(p['scale']))
        if count > 0:
            names = [p['name'] for p in result['products'] if check(p['scale'])]
            lines.append(f"- **{range_name}**: {count} 只 ({', '.join(names)})")
    
    return "\n".join(lines)

def main():
    """主函数"""
    send_message = '--send' in sys.argv
    
    print("=" * 50)
    print("📊 产品规模监控")
    print("=" * 50)
    
    # 检查规模
    result = check_scale()
    
    if not result:
        print("❌ 检查失败")
        return 1
    
    # 生成报告
    report = generate_report(result)
    print("\n" + report)
    
    # 发送预警
    if send_message and result['warnings']:
        print("\n" + "=" * 50)
        print("📤 发送预警通知...")
        
        # 生成简短预警消息
        urgent = [w for w in result['warnings'] if '🔴' in w['level']]
        attention = [w for w in result['warnings'] if '🟡' in w['level']]
        
        short_msg = "## 🔴 产品规模预警\n\n" if urgent else "## 📊 产品规模监控\n\n"
        short_msg += f"**检查时间：** {result['timestamp']}\n"
        short_msg += f"**预警产品：** {len(result['warnings'])} 只\n\n"
        
        if urgent:
            short_msg += "### 紧急\n"
            for w in urgent:
                short_msg += f"- {w['name']}: {w['scale']:,.0f} 万\n"
            short_msg += "\n"
        
        if attention:
            short_msg += "### 关注\n"
            for w in attention:
                short_msg += f"- {w['name']}: {w['scale']:,.0f} 万\n"
        
        short_msg += f"\n_总规模：{result['total_scale']:,.0f} 万元_"
        
        success = send_to_feishu(short_msg)
        
        if success:
            print("✅ 预警已发送")
        else:
            print("❌ 发送失败")
    
    print("\n" + "=" * 50)
    print("✅ 检查完成")
    print("=" * 50)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
