#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
富途 OpenAPI 数据获取模块
获取真实持仓、实时行情、期权持仓等
"""

import sys
from pathlib import Path
from datetime import datetime

try:
    from futu import *
except ImportError:
    print("请安装 futu-api: pip install futu-api")
    sys.exit(1)

from futu_config import FUTU_CONFIG

# 全局报价上下文
QUOTE_CTX = None
TRADE_CTX = None

def init_quote_context():
    """初始化报价上下文"""
    global QUOTE_CTX
    if QUOTE_CTX is None:
        QUOTE_CTX = OpenQuoteContext(
            host=FUTU_CONFIG['host'],
            port=FUTU_CONFIG['port']
        )
        print("✅ 报价上下文已连接")
    return QUOTE_CTX

def init_trade_context():
    """初始化交易上下文（需要登录）"""
    global TRADE_CTX
    if TRADE_CTX is None:
        TRADE_CTX = OpenTradeContext(
            host=FUTU_CONFIG['host'],
            port=FUTU_CONFIG['port'],
            password=FUTU_CONFIG.get('password'),
            password_md5=FUTU_CONFIG.get('password_md5')
        )
        print("✅ 交易上下文已连接")
    return TRADE_CTX

def close_contexts():
    """关闭所有上下文"""
    global QUOTE_CTX, TRADE_CTX
    if QUOTE_CTX:
        QUOTE_CTX.close()
        QUOTE_CTX = None
    if TRADE_CTX:
        TRADE_CTX.close()
        TRADE_CTX = None

def get_stock_price(symbol, market='US'):
    """获取股票实时价格"""
    ctx = init_quote_context()
    try:
        if market == 'US':
            code = f"US.{symbol}"
        else:
            code = f"HK.{symbol}"
        
        ret, data = ctx.get_stock_quote([code])
        if ret == RET_OK and len(data) > 0:
            return {
                'price': float(data['last_price'][0]),
                'change_pct': float(data['change_rate'][0]) * 100,
                'volume': int(data['volume'][0]) if 'volume' in data else 0
            }
    except Exception as e:
        print(f"获取 {code} 价格失败：{e}")
    return None

def get_us_holdings():
    """获取美股真实持仓"""
    ctx = init_trade_context()
    try:
        # 需要先获取账户列表
        ret_acc, acc_list = ctx.get_acc_list()
        if ret_acc != RET_OK:
            print(f"获取账户列表失败：{acc_list}")
            return []
        
        holdings = []
        for acc in acc_list.to_dict():
            if acc['trd_env'] == 0:  # 真实账户
                ret, data = ctx.get_position_list(
                    trd_acc=acc['trd_acc'],
                    position_filter=0,  # 全部持仓
                    code='',
                    market=Market.US
                )
                if ret == RET_OK:
                    for _, row in data.iterrows():
                        holdings.append({
                            'symbol': row['code'].replace('US.', ''),
                            'name': row.get('name', ''),
                            'shares': float(row['qty']),
                            'cost_price': float(row.get('cost_price', 0)),
                            'market_value': float(row.get('market_val', 0)),
                            'pl': float(row.get('pl_val', 0)),
                            'pl_pct': float(row.get('pl_ratio', 0)) * 100
                        })
        return holdings
    except Exception as e:
        print(f"获取美股持仓失败：{e}")
        return []

def get_hk_holdings():
    """获取港股真实持仓"""
    ctx = init_trade_context()
    try:
        ret_acc, acc_list = ctx.get_acc_list()
        if ret_acc != RET_OK:
            print(f"获取账户列表失败：{acc_list}")
            return []
        
        holdings = []
        for acc in acc_list.to_dict():
            if acc['trd_env'] == 0:
                ret, data = ctx.get_position_list(
                    trd_acc=acc['trd_acc'],
                    position_filter=0,
                    code='',
                    market=Market.HK
                )
                if ret == RET_OK:
                    for _, row in data.iterrows():
                        holdings.append({
                            'symbol': row['code'].replace('HK.', ''),
                            'name': row.get('name', ''),
                            'shares': float(row['qty']),
                            'cost_price': float(row.get('cost_price', 0)),
                            'market_value': float(row.get('market_val', 0)),
                            'pl': float(row.get('pl_val', 0)),
                            'pl_pct': float(row.get('pl_ratio', 0)) * 100
                        })
        return holdings
    except Exception as e:
        print(f"获取港股持仓失败：{e}")
        return []

def get_options_holdings():
    """获取期权持仓"""
    ctx = init_trade_context()
    try:
        ret_acc, acc_list = ctx.get_acc_list()
        if ret_acc != RET_OK:
            return []
        
        options = []
        for acc in acc_list.to_dict():
            if acc['trd_env'] == 0:
                # 获取港股期权持仓
                ret, data = ctx.get_position_list(
                    trd_acc=acc['trd_acc'],
                    position_filter=0,
                    code='',
                    market=Market.HK
                )
                if ret == RET_OK:
                    for _, row in data.iterrows():
                        code = row['code']
                        # 期权代码格式：HK.HKX2603C00700 (港股期权)
                        if 'HKX' in code or 'OPT' in code:
                            options.append({
                                'code': code,
                                'name': row.get('name', ''),
                                'shares': float(row['qty']),
                                'cost_price': float(row.get('cost_price', 0)),
                                'market_value': float(row.get('market_val', 0)),
                                'pl': float(row.get('pl_val', 0))
                            })
        return options
    except Exception as e:
        print(f"获取期权持仓失败：{e}")
        return []

def get_account_info():
    """获取账户信息（资金、购买力等）"""
    ctx = init_trade_context()
    try:
        ret_acc, acc_list = ctx.get_acc_list()
        if ret_acc != RET_OK:
            return None
        
        accounts = []
        for acc in acc_list.to_dict():
            if acc['trd_env'] == 0:
                ret, data = ctx.get_accinfo(trd_acc=acc['trd_acc'])
                if ret == RET_OK:
                    accounts.append({
                        'trd_acc': acc['trd_acc'],
                        'channel': acc['channel'],
                        'total_assets': float(data.get('total_assets', 0)),
                        'cash': float(data.get('cash', 0)),
                        'buying_power': float(data.get('buying_power', 0))
                    })
        return accounts
    except Exception as e:
        print(f"获取账户信息失败：{e}")
        return None

if __name__ == "__main__":
    # 测试
    print("测试富途 OpenAPI 连接...")
    
    # 测试报价
    quote = get_stock_price('AAPL', 'US')
    print(f"AAPL 价格：{quote}")
    
    # 测试持仓
    us_holdings = get_us_holdings()
    print(f"美股持仓：{len(us_holdings)} 只")
    for h in us_holdings[:5]:
        print(f"  {h['symbol']}: {h['shares']} 股，盈亏 {h['pl_pct']:+.2f}%")
    
    hk_holdings = get_hk_holdings()
    print(f"港股持仓：{len(hk_holdings)} 只")
    
    close_contexts()
    print("✅ 测试完成")
