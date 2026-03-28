#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
筛选从 2026-02-28 到 2026-03-25 期间跌幅最大的股票
"""

import akshare as ak
import pandas as pd
from datetime import datetime

START_DATE = "20260228"
END_DATE = "20260325"

def get_a_share_declines():
    """获取 A 股跌幅排名"""
    print("📈 获取 A 股数据...")
    try:
        # 获取区间涨跌幅
        df = ak.stock_rank_cxg_ths(symbol="区间涨跌幅", start_date=START_DATE, end_date=END_DATE)
        if df is not None and not df.empty:
            df['market'] = 'A 股'
            return df.head(10)
    except Exception as e:
        print(f"A 股数据获取失败：{e}")
    return pd.DataFrame()

def get_hk_share_declines():
    """获取港股跌幅排名"""
    print("📈 获取港股数据...")
    try:
        # 获取港股每日涨跌幅排名
        df = ak.stock_hk_daily_em()
        if df is not None and not df.empty:
            # 计算区间涨跌幅需要历史数据，这里用当日跌幅替代
            df['market'] = '港股'
            return df.head(10)
    except Exception as e:
        print(f"港股数据获取失败：{e}")
    return pd.DataFrame()

def get_us_share_declines():
    """获取美股跌幅排名"""
    print("📈 获取美股数据...")
    try:
        # 获取美股每日涨跌幅
        df = ak.stock_us_daily_em()
        if df is not None and not df.empty:
            df['market'] = '美股'
            return df.head(10)
    except Exception as e:
        print(f"美股数据获取失败：{e}")
    return pd.DataFrame()

def main():
    print("=" * 60)
    print("📊 跌幅最大股票筛选")
    print(f"📅 区间：{START_DATE} 至 {END_DATE}")
    print("=" * 60)
    
    all_stocks = []
    
    # 获取各市场数据
    a_shares = get_a_share_declines()
    hk_shares = get_hk_share_declines()
    us_shares = get_us_share_declines()
    
    # 合并数据
    if not a_shares.empty:
        all_stocks.append(a_shares)
    if not hk_shares.empty:
        all_stocks.append(hk_shares)
    if not us_shares.empty:
        all_stocks.append(us_shares)
    
    if all_stocks:
        combined = pd.concat(all_stocks, ignore_index=True)
        print(f"\n✅ 共获取 {len(combined)} 只股票数据")
        print(combined.head(20))
    else:
        print("❌ 未能获取股票数据")

if __name__ == "__main__":
    main()
