#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一投资系统入口脚本

整合巴菲特投资模块和原有投资系统
用法：python3 invest.py [command]

命令：
  screen      - 股票筛选
  market      - 市场状态识别
  allocate    - 动态配置
  trade       - 生成交易指令
  backtest    - 运行回测
  monitor     - 持仓监控（原有系统）
  workflow    - 综合报告（原有系统）
  all         - 运行全部
"""

import sys
import os
from pathlib import Path

# 路径配置
WORKSPACE = Path("/home/admin/openclaw/workspace")
BUFFETT_DIR = WORKSPACE / "skills" / "buffett-investor"
AGENTS_DIR = WORKSPACE / "agents"

def print_banner():
    print("="*80)
    print("统一投资系统 v2.0 - 巴菲特价值投资增强版")
    print("="*80)
    print()

def run_command(cmd, script_path, description):
    """运行命令"""
    print(f"▶ 执行：{description}")
    print(f"📁 路径：{script_path}")
    print("-"*80)
    
    if not script_path.exists():
        print(f"❌ 文件不存在：{script_path}")
        return False
    
    os.chdir(script_path.parent)
    os.system(f"python3 {script_path.name}")
    return True

def cmd_screen():
    """股票筛选"""
    print_banner()
    print("📊 股票筛选 - 186 支高质量股票池")
    print("-"*80)
    run_command("screen", BUFFETT_DIR / "screener.py", "股票筛选")

def cmd_market():
    """市场状态识别"""
    print_banner()
    print("📈 市场状态识别 - 牛/熊/震荡市")
    print("-"*80)
    run_command("market", BUFFETT_DIR / "market_state.py", "市场状态识别")

def cmd_allocate():
    """动态配置"""
    print_banner()
    print("💼 动态资产配置 - 根据市场状态调整仓位")
    print("-"*80)
    run_command("allocate", BUFFETT_DIR / "allocator.py", "动态配置")

def cmd_trade():
    """生成交易指令"""
    print_banner()
    print("💰 生成交易指令 - 带具体建议价格")
    print("-"*80)
    run_command("trade", BUFFETT_DIR / "trader_pro.py", "交易指令生成")

def cmd_backtest():
    """运行回测"""
    print_banner()
    print("📉 回测引擎 - 5 年/8 年/10 年回测")
    print("-"*80)
    run_command("backtest", BUFFETT_DIR / "backtest_engine.py", "回测引擎")

def cmd_monitor():
    """持仓监控（原有系统）"""
    print_banner()
    print("👁️ 持仓监控 - 原有系统")
    print("-"*80)
    run_command("monitor", AGENTS_DIR / "holding-analyzer" / "run.py", "持仓监控")

def cmd_workflow():
    """综合报告（原有系统）"""
    print_banner()
    print("📋 综合报告 - 原有系统")
    print("-"*80)
    run_command("workflow", AGENTS_DIR / "investment-workflow" / "workflow.py", "Workflow")

def cmd_all():
    """运行全部"""
    print_banner()
    print("🚀 运行全部模块")
    print("-"*80)
    
    print("\n1️⃣ 巴菲特核心模块\n")
    cmd_screen()
    print("\n" + "="*80 + "\n")
    cmd_market()
    print("\n" + "="*80 + "\n")
    cmd_allocate()
    print("\n" + "="*80 + "\n")
    cmd_trade()
    print("\n" + "="*80 + "\n")
    cmd_backtest()
    
    print("\n\n2️⃣ 原有系统（兼容）\n")
    cmd_monitor()
    print("\n" + "="*80 + "\n")
    cmd_workflow()

def cmd_help():
    """帮助"""
    print_banner()
    print("用法：python3 invest.py [command]")
    print()
    print("命令:")
    print("  screen      - 股票筛选（186 支高质量）")
    print("  market      - 市场状态识别（牛/熊/震荡市）")
    print("  allocate    - 动态资产配置")
    print("  trade       - 生成交易指令（带具体价格）")
    print("  backtest    - 运行回测（5 年/8 年/10 年）")
    print("  monitor     - 持仓监控（原有系统）")
    print("  workflow    - 综合报告（原有系统）")
    print("  all         - 运行全部")
    print("  help        - 显示帮助")
    print()
    print("示例:")
    print("  python3 invest.py screen    # 股票筛选")
    print("  python3 invest.py trade     # 生成交易指令")
    print("  python3 invest.py all       # 运行全部")
    print()

def main():
    if len(sys.argv) < 2:
        cmd_help()
        return
    
    cmd = sys.argv[1].lower()
    
    commands = {
        'screen': cmd_screen,
        'market': cmd_market,
        'allocate': cmd_allocate,
        'trade': cmd_trade,
        'backtest': cmd_backtest,
        'monitor': cmd_monitor,
        'workflow': cmd_workflow,
        'all': cmd_all,
        'help': cmd_help,
    }
    
    if cmd in commands:
        commands[cmd]()
    else:
        print(f"❌ 未知命令：{cmd}")
        print()
        cmd_help()

if __name__ == '__main__':
    main()
