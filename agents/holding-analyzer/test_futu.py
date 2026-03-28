#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试富途 OpenD 连接
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from futu_data import (
    get_stock_price, get_us_holdings, get_hk_holdings,
    get_options_holdings, get_account_info, close_contexts
)

def main():
    print("=" * 60)
    print("🔌 富途 OpenD 连接测试")
    print("=" * 60)
    
    # 测试 1: 报价连接
    print("\n1️⃣  测试报价连接...")
    quote = get_stock_price('AAPL', 'US')
    if quote:
        print(f"   ✅ AAPL 价格：${quote['price']:.2f} ({quote['change_pct']:+.2f}%)")
    else:
        print("   ❌ 报价连接失败 - 请确保 OpenD 已启动")
        close_contexts()
        return 1
    
    # 测试 2: 交易连接（需要登录）
    print("\n2️⃣  测试交易连接...")
    try:
        us_holdings = get_us_holdings()
        if us_holdings is not None:
            print(f"   ✅ 交易连接成功")
            print(f"   📊 美股持仓：{len(us_holdings)} 只")
            for h in us_holdings[:5]:
                pl_flag = "📈" if h['pl'] > 0 else "📉" if h['pl'] < 0 else "➖"
                print(f"      {pl_flag} {h['symbol']}: {h['shares']:.0f} 股，盈亏 {h['pl_pct']:+.2f}% (${h['pl']:,.0f})")
        else:
            print("   ⚠️  获取持仓失败 - 可能未登录或无持仓")
    except Exception as e:
        print(f"   ❌ 交易连接失败：{e}")
        print("   请确保在 OpenD 中已登录富途账户")
    
    # 测试 3: 港股持仓
    print("\n3️⃣  获取港股持仓...")
    try:
        hk_holdings = get_hk_holdings()
        if hk_holdings is not None:
            print(f"   ✅ 港股持仓：{len(hk_holdings)} 只")
            for h in hk_holdings[:5]:
                pl_flag = "📈" if h['pl'] > 0 else "📉" if h['pl'] < 0 else "➖"
                print(f"      {pl_flag} {h['symbol']}: {h['shares']:.0f} 股，盈亏 {h['pl_pct']:+.2f}% (HK${h['pl']:,.0f})")
        else:
            print("   ⚠️  无港股持仓或未连接")
    except Exception as e:
        print(f"   ❌ 获取港股持仓失败：{e}")
    
    # 测试 4: 期权持仓
    print("\n4️⃣  获取期权持仓...")
    try:
        options = get_options_holdings()
        if options:
            print(f"   ✅ 期权持仓：{len(options)} 个")
            for opt in options[:5]:
                print(f"      {opt['name']}: {opt['shares']:.0f} 份")
        else:
            print("   ⚠️  无期权持仓")
    except Exception as e:
        print(f"   ⚠️  获取期权持仓失败：{e}")
    
    # 测试 5: 账户信息
    print("\n5️⃣  获取账户信息...")
    try:
        accounts = get_account_info()
        if accounts:
            for acc in accounts:
                print(f"   ✅ 账户 {acc['trd_acc']} ({acc['channel']})")
                print(f"      总资产：${acc['total_assets']:,.0f}")
                print(f"      现金：${acc['cash']:,.0f}")
                print(f"      购买力：${acc['buying_power']:,.0f}")
        else:
            print("   ⚠️  无法获取账户信息")
    except Exception as e:
        print(f"   ⚠️  获取账户信息失败：{e}")
    
    close_contexts()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
    print("\n💡 下一步:")
    print("   运行：python run.py --futu --send")
    print("   使用真实持仓数据进行监控")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
