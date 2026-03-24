#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
富途 OpenD 数据收集器
股票投资团队 - data-collector 的富途 OpenD 数据源实现

**主数据源：** 富途 OpenD（实盘持仓 + 实时行情）
**备用数据源：** akshare（网络故障时）

用法：
  python futu_collector.py --send    # 收集数据并发送
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/home/admin/openclaw/workspace/agents/holding-analyzer')

FEISHU_USER_ID = "ou_52fa8f508e88e1efbcbe50c014ecaa6e"
OPENCLAW_PATH = "/home/admin/.nvm/versions/node/v24.14.0/bin/openclaw"

def check_opend_status():
    """检查 OpenD 是否运行"""
    try:
        result = subprocess.run(['pgrep', '-f', 'OpenD'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def get_futu_holdings():
    """从富途 OpenD 获取真实持仓"""
    print("正在从富途 OpenD 获取持仓...")
    
    try:
        from futu_data import get_us_holdings, get_hk_holdings, get_account_info
        
        us_holdings = get_us_holdings()
        hk_holdings = get_hk_holdings()
        accounts = get_account_info()
        
        result = {
            'dataSource': '富途 OpenD',
            'timestamp': datetime.now().isoformat(),
            'us_holdings': us_holdings,
            'hk_holdings': hk_holdings,
            'accounts': accounts,
            'total_us_count': len(us_holdings),
            'total_hk_count': len(hk_holdings),
        }
        
        print(f"  ✅ 美股持仓：{len(us_holdings)} 只")
        print(f"  ✅ 港股持仓：{len(hk_holdings)} 只")
        
        if accounts:
            for acc in accounts:
                print(f"  💰 账户 {acc['trd_acc']}: ${acc['total_assets']:,.0f}")
        
        return result
        
    except Exception as e:
        print(f"  ⚠️ 富途 OpenD 获取失败：{e}")
        print("  切换到备用数据源 akshare...")
        return None

def get_akshare_holdings():
    """从 akshare 获取持仓（备用）"""
    print("正在从 akshare 获取持仓数据...")
    
    try:
        from analyzer import analyze_holdings
        data = analyze_holdings()
        
        result = {
            'dataSource': 'akshare',
            'timestamp': datetime.now().isoformat(),
            'us_holdings': data.get('us_stocks', []),
            'hk_holdings': data.get('hk_stocks', []),
            'total_us_count': len(data.get('us_stocks', [])),
            'total_hk_count': len(data.get('hk_stocks', [])),
        }
        
        print(f"  ✅ 美股：{result['total_us_count']} 只")
        print(f"  ✅ 港股：{result['total_hk_count']} 只")
        
        return result
        
    except Exception as e:
        print(f"  ⚠️ akshare 获取失败：{e}")
        return None

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

def generate_report(data):
    """生成持仓报告"""
    lines = []
    lines.append("# 📊 富途持仓日报")
    lines.append(f"**数据源：** {data.get('dataSource', 'Unknown')}")
    lines.append(f"**时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    
    # 美股持仓
    us_holdings = data.get('us_holdings', [])
    if us_holdings:
        lines.append("## 🇺🇸 美股持仓")
        lines.append("")
        lines.append("| 股票 | 持仓 | 市价 | 盈亏% |")
        lines.append("|------|------|------|------|")
        
        for stock in us_holdings[:10]:  # 最多显示 10 只
            flag = "📈" if stock.get('pl', stock.get('change', 0)) > 0 else "📉"
            lines.append(f"| {flag} {stock['symbol']} | {stock.get('shares', 0):.0f} | ${stock.get('market_value', stock.get('current_price', 0)):,.2f} | {stock.get('pl_pct', stock.get('change_pct', 0)):+.2f}% |")
        
        lines.append("")
    
    # 港股持仓
    hk_holdings = data.get('hk_holdings', [])
    if hk_holdings:
        lines.append("## 🇭🇰 港股持仓")
        lines.append("")
        lines.append("| 股票 | 持仓 | 市价 | 盈亏% |")
        lines.append("|------|------|------|------|")
        
        for stock in hk_holdings[:10]:  # 最多显示 10 只
            flag = "📈" if stock.get('pl', stock.get('change', 0)) > 0 else "📉"
            lines.append(f"| {flag} {stock['symbol']} | {stock.get('shares', 0):.0f} | HK${stock.get('market_value', stock.get('current_price', 0)):,.2f} | {stock.get('pl_pct', stock.get('change_pct', 0)):+.2f}% |")
        
        lines.append("")
    
    # 账户总览
    accounts = data.get('accounts', [])
    if accounts:
        lines.append("## 💰 账户总览")
        lines.append("")
        lines.append("| 账户 | 总资产 | 现金 | 购买力 |")
        lines.append("|------|--------|------|--------|")
        
        for acc in accounts:
            lines.append(f"| {acc['trd_acc']} | ${acc['total_assets']:,.0f} | ${acc['cash']:,.0f} | ${acc['buying_power']:,.0f} |")
        
        lines.append("")
    
    return "\n".join(lines)

def main():
    """主函数"""
    print("=" * 60)
    print("📊 富途 OpenD 数据收集器")
    print("=" * 60)
    
    # 检查 OpenD 状态
    print("\n🔌 检查 OpenD 状态...")
    if check_opend_status():
        print("  ✅ OpenD 运行中")
    else:
        print("  ⚠️ OpenD 未运行，将使用备用数据源")
    
    # 获取数据（优先富途）
    print("\n📈 获取持仓数据...")
    data = get_futu_holdings()
    
    if not data:
        data = get_akshare_holdings()
    
    if not data:
        print("\n❌ 所有数据源失败")
        return 1
    
    # 保存数据
    output_dir = Path('/home/admin/openclaw/workspace/data')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    output_file = output_dir / f'futu_holdings_{timestamp}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 数据已保存：{output_file}")
    
    # 生成报告
    print("\n📝 生成报告...")
    report = generate_report(data)
    
    report_file = output_dir / f'futu_report_{timestamp}.md'
    report_file.write_text(report, encoding='utf-8')
    print(f"📄 报告已保存：{report_file}")
    
    # 发送飞书
    send_message = '--send' in sys.argv
    if send_message:
        print("\n📤 发送飞书通知...")
        
        short_msg = f"## 📊 富途持仓更新\n\n"
        short_msg += f"**数据源：** {data.get('dataSource', 'Unknown')}\n"
        short_msg += f"**美股：** {data.get('total_us_count', 0)} 只\n"
        short_msg += f"**港股：** {data.get('total_hk_count', 0)} 只\n\n"
        
        # 添加显著变化
        all_stocks = data.get('us_holdings', []) + data.get('hk_holdings', [])
        significant = [s for s in all_stocks if abs(s.get('pl_pct', s.get('change_pct', 0))) >= 3]
        
        if significant:
            short_msg += f"**显著变化：** {len(significant)} 只\n\n"
            for s in significant[:5]:
                flag = "📈" if s.get('pl_pct', s.get('change_pct', 0)) > 0 else "📉"
                pct = s.get('pl_pct', s.get('change_pct', 0))
                short_msg += f"{flag} {s['symbol']}: {pct:+.2f}%\n"
        
        if send_to_feishu(short_msg):
            print("✅ 推送完成")
        else:
            print("❌ 推送失败")
    
    print("\n" + "=" * 60)
    print("✅ 数据收集完成")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
