#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一投资系统入口脚本 v2.1

整合巴菲特投资模块和原有系统
支持 Profile 多账户、模型回退链、SQLite 状态存储

用法：
  python3 invest.py [command] [--profile 产品名] [--model 模型名]

命令:
  screen      - 股票筛选
  market      - 市场状态识别
  allocate    - 动态配置
  trade       - 生成交易指令
  backtest    - 运行回测
  monitor     - 持仓监控
  workflow    - 综合报告
  all         - 运行全部
  help        - 显示帮助

示例:
  python3 invest.py monitor                  # 默认 Profile
  python3 invest.py monitor --profile 前锋 1 号   # 指定产品
  python3 invest.py market --model qwen-max  # 指定模型
"""

import sys
import os
import argparse
import yaml
from pathlib import Path

# 路径配置
WORKSPACE = Path("/home/admin/openclaw/workspace")
BUFFETT_DIR = WORKSPACE / "skills" / "buffett-investor"
AGENTS_DIR = WORKSPACE / "agents"
PROFILES_DIR = WORKSPACE / "profiles"
CONFIG_FILE = WORKSPACE / "invest.yaml"

# 全局配置
args = None
profile_config = None


def load_config():
    """加载配置文件"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


def load_profile(profile_name: str = None):
    """加载 Profile 配置"""
    if not profile_name:
        return None
    
    profile_file = PROFILES_DIR / f"{profile_name}.yaml"
    if profile_file.exists():
        with open(profile_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    print(f"⚠️  Profile 未找到：{profile_name}")
    return None


def print_banner():
    version = "v2.1"
    profile_info = f" | Profile: {profile_config['profile']['name']}" if profile_config else ""
    print("="*80)
    print(f"统一投资系统 {version} - 巴菲特价值投资增强版{profile_info}")
    print("="*80)
    print()


def run_command(cmd, script_path, description, env=None):
    """运行命令"""
    print(f"▶ 执行：{description}")
    print(f"📁 路径：{script_path}")
    if env:
        print(f"🔧 环境：{env}")
    print("-"*80)
    
    if not script_path.exists():
        print(f"❌ 文件不存在：{script_path}")
        return False
    
    os.chdir(script_path.parent)
    
    # 设置环境变量
    if env:
        for key, value in env.items():
            os.environ[key] = str(value)
    
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
    
    env = {}
    if profile_config:
        env['INVEST_PROFILE'] = profile_config['profile']['name']
        if 'data' in profile_config:
            env['HOLDINGS_FILE'] = profile_config['data'].get('holdings_file', '')
            env['PRODUCTS_FILE'] = profile_config['data'].get('products_file', '')
    
    run_command("monitor", AGENTS_DIR / "holding-analyzer" / "run.py", "持仓监控", env)


def cmd_workflow():
    """综合报告（原有系统）"""
    print_banner()
    print("📋 综合报告 - 原有系统")
    print("-"*80)
    
    env = {}
    if profile_config:
        env['INVEST_PROFILE'] = profile_config['profile']['name']
    
    run_command("workflow", AGENTS_DIR / "investment-workflow" / "workflow.py", "Workflow", env)


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
    print("用法：python3 invest.py [command] [options]")
    print()
    print("命令:")
    print("  screen      - 股票筛选（186 支高质量）")
    print("  market      - 市场状态识别（牛/熊/震荡市）")
    print("  allocate    - 动态资产配置")
    print("  trade       - 生成交易指令（带具体价格）")
    print("  backtest    - 运行回测（5 年/8 年/10 年）")
    print("  monitor     - 持仓监控")
    print("  workflow    - 综合报告")
    print("  all         - 运行全部")
    print("  help        - 显示帮助")
    print()
    print("选项:")
    print("  --profile <产品名>   指定产品账户 (前锋 1 号，前锋 3 号，...)")
    print("  --model <模型名>     指定模型 (qwen3.5-plus, qwen2.5-72b, ...)")
    print("  --list-profiles      列出所有可用 Profile")
    print()
    print("示例:")
    print("  python3 invest.py monitor")
    print("  python3 invest.py monitor --profile 前锋 1 号")
    print("  python3 invest.py market --model qwen-max")
    print("  python3 invest.py --list-profiles")
    print()
    
    # 列出可用 Profile
    if PROFILES_DIR.exists():
        print("可用 Profile:")
        for profile_file in sorted(PROFILES_DIR.glob("*.yaml")):
            print(f"  - {profile_file.stem}")
        print()


def cmd_list_profiles():
    """列出所有 Profile"""
    print_banner()
    print("📋 可用 Profile:")
    print("-"*80)
    
    if not PROFILES_DIR.exists():
        print("  (无)")
        return
    
    config = load_config()
    default_profile = config.get('profiles', {}).get('default', {}).get('name', '默认')
    print(f"默认 Profile: {default_profile}")
    print()
    
    for profile_file in sorted(PROFILES_DIR.glob("*.yaml")):
        with open(profile_file, 'r', encoding='utf-8') as f:
            profile_data = yaml.safe_load(f)
        
        name = profile_data.get('profile', {}).get('name', profile_file.stem)
        enabled = profile_data.get('profile', {}).get('enabled', True)
        ptype = profile_data.get('profile', {}).get('type', 'unknown')
        threshold = profile_data.get('alert', {}).get('scale_threshold_wan', 'N/A')
        
        status = "✅" if enabled else "❌"
        print(f"  {status} {name:15} | 类型：{ptype:10} | 预警阈值：{threshold}万")
    
    print()


def main():
    global args, profile_config
    
    parser = argparse.ArgumentParser(description='统一投资系统 v2.1')
    parser.add_argument('command', nargs='?', default='help', help='命令')
    parser.add_argument('--profile', type=str, help='指定产品账户')
    parser.add_argument('--model', type=str, help='指定模型')
    parser.add_argument('--list-profiles', action='store_true', help='列出所有 Profile')
    
    args = parser.parse_args()
    
    # 处理 --list-profiles
    if args.list_profiles:
        cmd_list_profiles()
        return
    
    # 加载 Profile 配置
    if args.profile:
        profile_config = load_profile(args.profile)
        if not profile_config:
            print(f"❌ Profile 未找到：{args.profile}")
            print()
            print("使用 --list-profiles 查看可用 Profile")
            return
    
    # 设置模型（通过环境变量）
    if args.model:
        os.environ['INVEST_MODEL'] = args.model
    
    # 执行命令
    cmd = args.command.lower()
    
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
        'list-profiles': cmd_list_profiles,
    }
    
    if cmd in commands:
        commands[cmd]()
    else:
        print(f"❌ 未知命令：{cmd}")
        print()
        cmd_help()


if __name__ == '__main__':
    main()
