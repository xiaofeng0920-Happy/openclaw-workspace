#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持仓分析 Agent - 完整运行脚本（含飞书推送）
用法：
  python run.py              # 使用配置持仓（基准日期：2026-03-16）
  python run.py --futu       # 使用富途真实持仓（需要 OpenD）
  python run.py --qveris     # 使用 QVeris 数据源（指数/资金流/新闻）
  python run.py --quick      # 快速模式，只更新股价
  python run.py --send       # 发送飞书通知
  python run.py --send-on-change  # 仅显著变化时发送
  python run.py --futu --send
  python run.py --qveris --send
"""

import json
import sys
import subprocess
import requests
from pathlib import Path
from datetime import datetime
import os

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

# 检查运行模式
USE_FUTU = '--futu' in sys.argv
USE_QVERIS = '--qveris' in sys.argv
QUICK_MODE = '--quick' in sys.argv
SEND_ON_CHANGE = '--send-on-change' in sys.argv

if USE_FUTU:
    from futu_data import (
        get_us_holdings, get_hk_holdings, get_options_holdings,
        get_stock_price, close_contexts
    )
    from analyzer import get_relevant_news, generate_report_futu as generate_report, ALERT_THRESHOLD
elif USE_QVERIS:
    from qveris_data import get_market_daily_report
    from analyzer import generate_market_report, ALERT_THRESHOLD
else:
    from analyzer import analyze_holdings, get_options_status, get_relevant_news, generate_report, ALERT_THRESHOLD

# 飞书用户 ID
FEISHU_USER_ID = "ou_52fa8f508e88e1efbcbe50c014ecaa6e"
FEISHU_APP_ID = "cli_a92873946239dbd1"
FEISHU_APP_SECRET = "7TyxAnUzgfGyjzi0iIMchgCzHgIbnqju"

def get_tenant_access_token():
    """获取飞书 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }
    response = requests.post(url, json=payload, timeout=10)
    result = response.json()
    if result.get("code") == 0:
        return result.get("tenant_access_token")
    else:
        raise Exception(f"获取 token 失败：{result}")

def send_to_feishu(message: str):
    """使用飞书开放 API 发送消息"""
    import requests
    try:
        # 获取 token
        print("正在获取飞书访问令牌...")
        token = get_tenant_access_token()
        
        # 发送消息
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        params = {"receive_id_type": "open_id"}
        payload = {
            "receive_id": FEISHU_USER_ID,
            "msg_type": "text",
            "content": json.dumps({"text": message})
        }
        
        print("正在发送消息...")
        response = requests.post(url, headers=headers, params=params, json=payload, timeout=30)
        result = response.json()
        
        if result.get("code") == 0:
            message_id = result.get("data", {}).get("message_id", "unknown")
            print(f"✅ 消息已发送至飞书 (消息 ID: {message_id})")
            return True
        else:
            print(f"❌ 发送失败：{result}")
            return False
            
    except Exception as e:
        print(f"❌ 发送异常：{e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    send_message = '--send' in sys.argv
    
    print("=" * 60)
    print("🤖 持仓分析 Agent - 启动")
    print("=" * 60)
    
    if USE_FUTU:
        print("数据源：富途 OpenD (实盘)")
        print("⚠️  确保 OpenD 已启动并登录")
    elif USE_QVERIS:
        print("数据源：QVeris API")
        print("📊 支持：指数/资金流/新闻/创新高")
    else:
        print("基准日期：2026-03-16 (配置持仓)")
    
    print(f"预警阈值：±{ALERT_THRESHOLD}%")
    print(f"飞书推送：{'启用' if send_message else '禁用'}")
    print("=" * 60)
    
    try:
        if USE_QVERIS:
            # 使用 QVeris 获取市场数据
            print("\n📊 正在获取市场日报数据...")
            market_data = get_market_daily_report()
            
            # 生成市场日报
            print("\n📝 正在生成市场日报...")
            report = generate_market_report(market_data)
            
            # 保存报告
            output_path = Path(__file__).parent / "reports"
            output_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d')
            report_file = output_path / f"market_daily_{timestamp}.md"
            report_file.write_text(report, encoding='utf-8')
            print(f"\n💾 报告已保存：{report_file}")
            
            # 发送到飞书
            if send_message:
                print("\n" + "=" * 60)
                print("📤 正在发送飞书通知...")
                print("=" * 60)
                
                # 生成简短通知
                indices = market_data.get('indices', [])
                short_msg = f"## 📊 A 股市场日报\n\n"
                short_msg += f"**日期：** {datetime.now().strftime('%Y-%m-%d')}\n\n"
                
                short_msg += "| 指数 | 收盘价 | 涨跌幅 |\n"
                short_msg += "|------|--------|--------|\n"
                
                for idx in indices[:5]:
                    flag = "📈" if idx['change_pct'] > 0 else "📉"
                    short_msg += f"| {flag} {idx['code']} | {idx['price']:.2f} | {idx['change_pct']:+.2f}% |\n"
                
                short_msg += f"\n_详细报告已生成，可在 workspace 查看_"
                
                success = send_to_feishu(short_msg)
                
                if success:
                    print("✅ 推送完成")
                else:
                    print("❌ 推送失败")
            
            print("\n" + "=" * 60)
            print("✅ 市场日报完成")
            print("=" * 60)
            
        elif USE_FUTU:
            # 使用富途真实持仓
            print("\n📈 正在获取美股持仓...")
            us_holdings = get_us_holdings()
            print(f"   获取到 {len(us_holdings)} 只美股")
            
            print("\n📈 正在获取港股持仓...")
            hk_holdings = get_hk_holdings()
            print(f"   获取到 {len(hk_holdings)} 只港股")
            
            # 转换为 analyzer 兼容格式
            results = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'us_stocks': us_holdings,
                'hk_stocks': hk_holdings,
                'significant_changes': [],
                'market': 'futu'
            }
            
            # 计算显著变化
            for stock in us_holdings + hk_holdings:
                if abs(stock.get('pl_pct', 0)) >= ALERT_THRESHOLD:
                    results['significant_changes'].append(stock)
            
            # 获取期权持仓
            print("\n📋 正在获取期权持仓...")
            options_raw = get_options_holdings()
            options_status = []
            for opt in options_raw:
                options_status.append({
                    'name': opt.get('name', opt['code']),
                    'symbol': opt['code'],
                    'type': 'OPT',
                    'expiry': '-',
                    'strike': 0,
                    'shares': opt['shares'],
                    'cost': opt['cost_price'],
                    'stock_price': 0,
                    'intrinsic_value': 0,
                    'status': 'active',
                    'pl': opt.get('pl', 0)
                })
            
            # 获取新闻
            print("\n📰 正在获取相关新闻...")
            news = get_relevant_news()
            
            # 生成报告
            print("\n📝 正在生成报告...")
            report = generate_report(results, options_status, news)
            
            # 保存报告
            output_path = Path(__file__).parent / "reports"
            output_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = output_path / f"report_{timestamp}.md"
            report_file.write_text(report, encoding='utf-8')
            print(f"\n💾 报告已保存：{report_file}")
            
            # 统计显著变化
            significant_count = len(results['significant_changes'])
            print(f"\n⚠️  显著变化股票：{significant_count} 只")
            
            for stock in results['significant_changes']:
                flag = "📈" if stock.get('pl_pct', stock.get('change_pct', 0)) > 0 else "📉"
                currency = "HK$" if stock.get('market') == 'HK' else "$"
                pct = stock.get('pl_pct', stock.get('change_pct', 0))
                print(f"   {flag} {stock['symbol']} {stock.get('name', '')}: {pct:+.2f}%")
            
            # 发送到飞书
            if send_message and significant_count > 0:
                print("\n" + "=" * 60)
                print("📤 正在发送飞书通知...")
                print("=" * 60)
                
                short_msg = f"## 📊 持仓监控预警\n\n"
                short_msg += f"**检查时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                short_msg += f"**数据源：** 富途 OpenD (实盘)\n"
                short_msg += f"**显著变化：** {significant_count} 只股票波动超 {ALERT_THRESHOLD}%\n\n"
                
                short_msg += "| 股票 | 代码 | 变化 | 影响 |\n"
                short_msg += "|------|------|------|------|\n"
                
                for stock in sorted(results['significant_changes'], key=lambda x: abs(x.get('pl_pct', x.get('change_pct', 0))), reverse=True)[:10]:
                    flag = "📈" if stock.get('pl_pct', stock.get('change_pct', 0)) > 0 else "📉"
                    currency = "HK$" if stock.get('market') == 'HK' else "$"
                    pct = stock.get('pl_pct', stock.get('change_pct', 0))
                    impact = stock.get('pl', stock.get('change_value', 0))
                    short_msg += f"| {flag} {stock.get('name', stock['symbol'])} | {stock['symbol']} | {pct:+.2f}% | {currency}{impact:,.0f} |\n"
                
                short_msg += f"\n_详细报告已生成，可在 workspace 查看_"
                
                success = send_to_feishu(short_msg)
                if success:
                    print("✅ 推送完成")
                else:
                    print("❌ 推送失败")
            
            print("\n" + "=" * 60)
            print("✅ 持仓分析完成")
            print("=" * 60)
            
        else:
            # 使用配置持仓
            print("\n📈 正在分析持仓...")
            results = analyze_holdings()
            
            print("\n📋 正在分析期权持仓...")
            options_status = get_options_status()
            
            # 获取新闻
            print("\n📰 正在获取相关新闻...")
            news = get_relevant_news()
            
            # 生成报告
            print("\n📝 正在生成报告...")
            report = generate_report(results, options_status, news)
            
            # 保存报告
            output_path = Path(__file__).parent / "reports"
            output_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = output_path / f"report_{timestamp}.md"
            report_file.write_text(report, encoding='utf-8')
            print(f"\n💾 报告已保存：{report_file}")
            
            # 统计显著变化
            significant_count = len(results['significant_changes'])
            print(f"\n⚠️  显著变化股票：{significant_count} 只")
            
            for stock in results['significant_changes']:
                flag = "📈" if stock.get('pl_pct', stock.get('change_pct', 0)) > 0 else "📉"
                currency = "HK$" if stock.get('market') == 'HK' else "$"
                pct = stock.get('pl_pct', stock.get('change_pct', 0))
                print(f"   {flag} {stock['symbol']} {stock.get('name', '')}: {pct:+.2f}%")
            
            # 发送到飞书
            if send_message and significant_count > 0:
                print("\n" + "=" * 60)
                print("📤 正在发送飞书通知...")
                print("=" * 60)
                
                short_msg = f"## 📊 持仓监控预警\n\n"
                short_msg += f"**检查时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                short_msg += f"**数据源：** 配置持仓\n"
                short_msg += f"**显著变化：** {significant_count} 只股票波动超 {ALERT_THRESHOLD}%\n\n"
                
                short_msg += "| 股票 | 代码 | 变化 | 影响 |\n"
                short_msg += "|------|------|------|------|\n"
                
                for stock in sorted(results['significant_changes'], key=lambda x: abs(x.get('pl_pct', x.get('change_pct', 0))), reverse=True)[:10]:
                    flag = "📈" if stock.get('pl_pct', stock.get('change_pct', 0)) > 0 else "📉"
                    currency = "HK$" if stock.get('market') == 'HK' else "$"
                    pct = stock.get('pl_pct', stock.get('change_pct', 0))
                    impact = stock.get('pl', stock.get('change_value', 0))
                    short_msg += f"| {flag} {stock.get('name', stock['symbol'])} | {stock['symbol']} | {pct:+.2f}% | {currency}{impact:,.0f} |\n"
                
                short_msg += f"\n_详细报告已生成，可在 workspace 查看_"
                
                success = send_to_feishu(short_msg)
                if success:
                    print("✅ 推送完成")
                else:
                    print("❌ 推送失败")
            
            print("\n" + "=" * 60)
            print("✅ 持仓分析完成")
            print("=" * 60)
        
        return 0
        
    finally:
        if USE_FUTU:
            close_contexts()

if __name__ == "__main__":
    sys.exit(main())
