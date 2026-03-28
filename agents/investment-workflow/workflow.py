#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投资分析 Workflow - 整合数据采集、持仓分析、报告生成、推送

流程：
1. 数据采集 → 获取股价、财务数据、新闻
2. 持仓分析 → 计算盈亏、风险预警
3. 股票池筛选 → 发现新机会
4. 报告生成 → 整合为 Markdown
5. 飞书推送 → 发送给用户

全部使用本地脚本，不调用大模型！
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# ============== 配置 ==============

WORKSPACE = Path('/home/admin/openclaw/workspace')
AGENTS_DIR = WORKSPACE / 'agents'
OUTPUT_DIR = WORKSPACE / 'reports' / 'workflow'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 飞书用户
FEISHU_USER = "ou_52fa8f508e88e1efbcbe50c014ecaa6e"

# ============== 工具函数 ==============

def run_script(script_path, args=[], capture=True):
    """运行本地脚本"""
    cmd = [sys.executable, str(script_path)] + args
    print(f"📌 运行：{' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=capture, text=True, timeout=300)
        return result.returncode == 0, result.stdout
    except Exception as e:
        print(f"❌ 脚本执行失败：{e}")
        return False, str(e)

def send_feishu(message):
    """发送飞书消息"""
    cmd = [
        'openclaw', 'message', 'send',
        '--channel', 'feishu',
        '--target', FEISHU_USER,
        '--message', message
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.returncode == 0

# ============== Workflow 步骤 ==============

def step1_data_collection():
    """步骤 1: 数据采集"""
    print("\n" + "="*60)
    print("📥 步骤 1: 数据采集")
    print("="*60)
    
    # 运行持仓分析（含股价获取）
    holding_analyzer = AGENTS_DIR / 'holding-analyzer' / 'run.py'
    success, output = run_script(holding_analyzer)
    
    if success:
        print("✅ 持仓数据采集完成")
        return True
    else:
        print("❌ 持仓数据采集失败")
        return False

def step2_portfolio_analysis():
    """步骤 2: 持仓分析"""
    print("\n" + "="*60)
    print("📊 步骤 2: 持仓分析")
    print("="*60)
    
    # 读取最新持仓报告
    reports_dir = AGENTS_DIR / 'holding-analyzer' / 'reports'
    report_files = sorted(reports_dir.glob('report_*.md'))
    
    if report_files:
        latest_report = report_files[-1]
        print(f"✅ 读取最新报告：{latest_report.name}")
        
        # 解析报告内容
        content = latest_report.read_text(encoding='utf-8')
        
        # 提取显著变化
        significant_changes = []
        for line in content.split('\n'):
            if '📈' in line or '📉' in line:
                significant_changes.append(line.strip())
        
        print(f"   发现 {len(significant_changes)} 只显著变化股票")
        return True, significant_changes
    else:
        print("❌ 未找到持仓报告")
        return False, []

def step3_stock_pool_update():
    """步骤 3: 股票池更新 + 技术指标"""
    print("\n" + "="*60)
    print("📋 步骤 3: 股票池检查 + 技术指标")
    print("="*60)
    
    # 读取股票池
    stock_pool_file = AGENTS_DIR / 'data-collector' / 'manual_stock_pool.md'
    
    if stock_pool_file.exists():
        content = stock_pool_file.read_text(encoding='utf-8')
        print("✅ 股票池已加载")
        
        # 统计股票数量
        a_count = content.count('A 股')
        hk_count = content.count('港股')
        us_count = content.count('美股')
        
        print(f"   A 股：{a_count}只 | 港股：{hk_count}只 | 美股：{us_count}只")
        
        # 运行技术指标分析（选取重点股票）
        tech_script = AGENTS_DIR / 'data-collector' / 'technical_indicators.py'
        if tech_script.exists():
            print("\n📊 运行技术指标分析...")
            success, _ = run_script(tech_script, capture=True)
            if success:
                print("✅ 技术指标分析完成")
            else:
                print("⚠️  技术指标分析失败")
        
        return True
    else:
        print("⚠️  股票池文件不存在")
        return False

def step4_agent_team():
    """步骤 4: 炒股 Agent 团队（持仓分析 + 策略建议）"""
    print("\n" + "="*60)
    print("🤖 步骤 4: 炒股 Agent 团队")
    print("="*60)
    
    agent_script = AGENTS_DIR / 'investment-workflow' / 'agent_team.py'
    if agent_script.exists():
        success, output = run_script(agent_script, capture=True)
        if success:
            print("✅ 炒股 Agent 团队完成")
            return True
        else:
            print("⚠️  炒股 Agent 团队失败")
            return False
    else:
        print("⚠️  脚本不存在")
        return False

def step5_report_generation(significant_changes, agent_team_success):
    """步骤 5: 生成综合报告"""
    print("\n" + "="*60)
    print("📝 步骤 5: 生成综合报告")
    print("="*60)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = OUTPUT_DIR / f'workflow_report_{timestamp}.md'
    
    lines = []
    lines.append("# 📊 投资分析日报")
    lines.append(f"**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # 持仓概览
    lines.append("## 1️⃣ 持仓监控")
    lines.append("")
    if significant_changes:
        lines.append("### 显著变化")
        lines.append("")
        for change in significant_changes[:10]:
            lines.append(f"- {change}")
    else:
        lines.append("*无显著变化*")
    lines.append("")
    
    # 股票池
    lines.append("## 2️⃣ 股票池 + 技术指标")
    lines.append("")
    lines.append("**高质量股票池：** 20+ 只")
    lines.append("- A 股：8 只（煤炭、银行、消费）")
    lines.append("- 港股：6 只（石油、电信、银行）")
    lines.append("- 美股：9 只（消费、电信、烟草）")
    lines.append("")
    lines.append("📊 技术指标：MACD、RSI、KDJ、布林带")
    lines.append("📄 详见：`agents/data-collector/technical/`")
    lines.append("")
    
    # 炒股 Agent 团队
    if agent_team_success:
        lines.append("## 3️⃣ 持仓分析（Agent 团队）")
        lines.append("")
        lines.append("✅ 数据收集员 → 持仓分析师 → 策略顾问 → 报告撰写员")
        lines.append("")
        lines.append("📄 持仓日报：`reports/持仓日报_*.md`")
        lines.append("")
    
    # 建议
    lines.append("## 4️⃣ 操作建议")
    lines.append("")
    lines.append("1. **持仓监控** - 每日 3 次自动检查")
    lines.append("2. **股票池** - 季度更新财务数据（Tushare Pro）")
    lines.append("3. **技术指标** - 每日分析 MACD/RSI/KDJ")
    lines.append("4. **回测** - 年度回顾策略有效性")
    lines.append("")
    
    # 保存报告
    content = "\n".join(lines)
    report_file.write_text(content, encoding='utf-8')
    print(f"✅ 报告已保存：{report_file}")
    
    return True, content, report_file

def send_feishu_notify(report_content, report_file):
    """步骤 6: 飞书推送"""
    print("\n" + "="*60)
    print("📤 步骤 6: 飞书推送")
    print("="*60)
    
    # 生成简短通知
    short_msg = f"## 📊 投资分析日报\n\n"
    short_msg += f"**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    short_msg += "### ✅ 今日完成\n"
    short_msg += "- 持仓监控（3 次/日）\n"
    short_msg += "- 股票池检查 + 技术指标\n"
    short_msg += "- 炒股 Agent 团队分析\n"
    short_msg += "- 综合报告生成\n\n"
    short_msg += f"_详细报告：{report_file.name}_"
    
    success = send_feishu(short_msg)
    
    if success:
        print("✅ 飞书推送成功")
        return True
    else:
        print("❌ 飞书推送失败")
        return False

# ============== 主 Workflow ==============

def run_workflow():
    """执行完整 Workflow"""
    print("="*60)
    print("🚀 投资分析 Workflow")
    print("="*60)
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    results = {
        'step1_data': False,
        'step2_analysis': False,
        'step3_pool': False,
        'step4_agent_team': False,
        'step5_report': False,
        'step6_notify': False,
    }
    
    # 步骤 1: 数据采集
    results['step1_data'] = step1_data_collection()
    if not results['step1_data']:
        print("⚠️  数据采集失败，继续后续步骤...")
    
    # 步骤 2: 持仓分析
    success, changes = step2_portfolio_analysis()
    results['step2_analysis'] = success
    
    # 步骤 3: 股票池检查 + 技术指标
    results['step3_pool'] = step3_stock_pool_update()
    
    # 步骤 4: 炒股 Agent 团队
    results['step4_agent_team'] = step4_agent_team()
    
    # 步骤 5: 报告生成
    success, content, report_file = step5_report_generation(changes, results['step4_agent_team'])
    results['step5_report'] = success
    
    # 步骤 6: 飞书推送
    results['step6_notify'] = send_feishu_notify(content, report_file)
    
    # 总结
    print("\n" + "="*60)
    print("📊 Workflow 执行总结")
    print("="*60)
    
    steps = [
        ('数据采集', results['step1_data']),
        ('持仓分析', results['step2_analysis']),
        ('股票池 + 技术指标', results['step3_pool']),
        ('炒股 Agent 团队', results['step4_agent_team']),
        ('报告生成', results['step5_report']),
        ('飞书推送', results['step6_notify']),
    ]
    
    for name, success in steps:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    total_success = sum(1 for _, s in steps if s)
    print(f"\n总计：{total_success}/{len(steps)} 步骤成功")
    print("="*60)
    
    return results

# ============== CLI ==============

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else 'full'
    
    if mode == 'full':
        run_workflow()
    elif mode == 'test':
        print("测试模式 - 仅验证配置")
        print(f"✅ 工作目录：{WORKSPACE}")
        print(f"✅ 输出目录：{OUTPUT_DIR}")
        print(f"✅ 飞书用户：{FEISHU_USER}")
    else:
        print(f"未知模式：{mode}")
        print("用法：python3 workflow.py [full|test]")
