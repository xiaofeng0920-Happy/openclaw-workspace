#!/usr/bin/env python3
"""
锋哥持仓分析脚本
每天早中晚自动运行，发送持仓变化分析
"""
import json
import sys
from datetime import datetime

# 持仓数据文件
HOLDINGS_FILE = "/home/admin/openclaw/workspace/memory/锋哥持仓_2026-03-16.md"

def read_holdings():
    """读取持仓数据"""
    try:
        with open(HOLDINGS_FILE, 'r') as f:
            return f.read()
    except Exception as e:
        return f"读取持仓文件失败：{e}"

def generate_analysis():
    """生成持仓分析报告"""
    holdings = read_holdings()
    
    report = f"""
📊 锋哥持仓分析 - {datetime.now().strftime('%Y-%m-%d %H:%M')}

{holdings[:2000]}...

（完整报告请查看持仓文件）
"""
    return report

if __name__ == "__main__":
    print(generate_analysis())
