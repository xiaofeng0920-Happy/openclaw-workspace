#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tushare Pro 数据接口 - 获取完整财务指标（ROIC、ROE 等）

注册：https://tushare.pro
Token: 免费获取（基础积分够用）
"""

import sys
import json
from pathlib import Path
from datetime import datetime

try:
    import tushare as ts
    import pandas as pd
except ImportError:
    print("❌ 请安装 tushare: pip install tushare")
    sys.exit(1)

# ============== 配置 ==============

# Tushare Token（需要用户自行获取）
# 注册 https://tushare.pro 后在个人中心获取
TUSHARE_TOKEN_FILE = Path('/home/admin/openclaw/workspace/agents/data-collector/.tushare_token')

# 输出路径
OUTPUT_DIR = Path('/home/admin/openclaw/workspace/agents/data-collector/tushare_data')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============== 工具函数 ==============

def get_token():
    """获取 Tushare Token"""
    if TUSHARE_TOKEN_FILE.exists():
        return TUSHARE_TOKEN_FILE.read_text().strip()
    else:
        print("⚠️  未找到 Tushare Token")
        print("请注册 https://tushare.pro 并保存 token 到：")
        print(f"   {TUSHARE_TOKEN_FILE}")
        return None

def init_tushare():
    """初始化 Tushare"""
    token = get_token()
    if token:
        ts.set_token(token)
        return ts.pro_api()
    return None

# ============== 数据获取 ==============

def get_stock_basic(market='E'):
    """
    获取股票基本信息
    
    market: E=沪深 A 股，HK=港股，US=美股
    """
    pro = init_tushare()
    if not pro:
        return None
    
    try:
        if market == 'E':
            # A 股
            df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,market,list_date')
        elif market == 'HK':
            # 港股（需要更高积分）
            df = pro.hk_basic(fields='ts_code,symbol,name,area,industry,market,list_date')
        else:
            df = None
        
        return df
    except Exception as e:
        print(f"❌ 获取股票列表失败：{e}")
        return None

def get_income_data(ts_code, start_date='20210101', end_date=None):
    """获取利润表数据（用于计算 ROIC）"""
    pro = init_tushare()
    if not pro:
        return None
    
    if end_date is None:
        end_date = datetime.now().strftime('%Y%m%d')
    
    try:
        df = pro.income(ts_code=ts_code, start_date=start_date, end_date=end_date,
                       fields='ts_code,end_date,revenue,operating_profit,interest_expense')
        return df
    except Exception as e:
        return None

def get_balance_data(ts_code, start_date='20210101', end_date=None):
    """获取资产负债表数据（用于计算 ROIC）"""
    pro = init_tushare()
    if not pro:
        return None
    
    if end_date is None:
        end_date = datetime.now().strftime('%Y%m%d')
    
    try:
        df = pro.balancesheet(ts_code=ts_code, start_date=start_date, end_date=end_date,
                             fields='ts_code,end_date,total_assets,total_liab,monetary_cap')
        return df
    except Exception as e:
        return None

def get_fina_indicator(ts_code, start_date='20210101', end_date=None):
    """获取财务指标（ROE、ROIC 等）"""
    pro = init_tushare()
    if not pro:
        return None
    
    if end_date is None:
        end_date = datetime.now().strftime('%Y%m%d')
    
    try:
        df = pro.fina_indicator(ts_code=ts_code, start_date=start_date, end_date=end_date,
                               fields='ts_code,end_date,roe_roewa,roic,dt_roe_roewa,grossmargin')
        return df
    except Exception as e:
        return None

def get_dividend_data(ts_code):
    """获取分红数据"""
    pro = init_tushare()
    if not pro:
        return None
    
    try:
        df = pro.dividend(ts_code=ts_code,
                         fields='ts_code,ann_date,div_proc,per_share,per_share_tax')
        return df
    except Exception as e:
        return None

def get_daily_hq(ts_code, start_date='20210101', end_date=None):
    """获取日线行情"""
    pro = init_tushare()
    if not pro:
        return None
    
    if end_date is None:
        end_date = datetime.now().strftime('%Y%m%d')
    
    try:
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date,
                      fields='ts_code,trade_date,open,high,low,close,vol,amount')
        return df
    except Exception as e:
        return None

# ============== 指标计算 ==============

def calc_roic(df_income, df_balance):
    """
    计算 ROIC
    
    ROIC = NOPAT / Invested Capital
    NOPAT = 营业利润 × (1 - 税率)
    Invested Capital = 总资产 - 无息流动负债
    """
    if df_income is None or df_balance is None:
        return None
    
    # 简化计算（实际需要更复杂的调整）
    results = []
    
    for idx, row in df_income.iterrows():
        # 找到对应的资产负债表数据
        bal = df_balance[df_balance['end_date'] == row['end_date']]
        if len(bal) == 0:
            continue
        
        bal = bal.iloc[0]
        
        # NOPAT（简化：假设税率 25%）
        nopat = row['operating_profit'] * 0.75
        
        # 投入资本
        invested_capital = bal['total_assets'] - bal['total_liab']
        
        if invested_capital > 0:
            roic = (nopat / invested_capital) * 100
            results.append({
                'date': row['end_date'],
                'roic': roic
            })
    
    return results

def calc_dividend_yield(ts_code, years=5):
    """计算连续 N 年股息率"""
    df_div = get_dividend_data(ts_code)
    if df_div is None or len(df_div) == 0:
        return None
    
    # 获取当前股价
    df_hq = get_daily_hq(ts_code)
    if df_hq is None or len(df_hq) == 0:
        return None
    
    current_price = df_hq.iloc[-1]['close']
    
    # 计算近年股息率
    df_div['dividend'] = df_div['per_share'].fillna(0)
    yearly_div = df_div.groupby(df_div['ann_date'].str[:4])['dividend'].sum()
    
    recent_years = yearly_div.tail(years)
    avg_yield = (recent_years.mean() / current_price) * 100
    
    return {
        'avg_yield': avg_yield,
        'years': len(recent_years),
        'continuous': len(recent_years[recent_years > 0])
    }

# ============== 筛选器 ==============

def screen_high_quality_stocks():
    """筛选高质量股票（使用 Tushare 数据）"""
    print("="*60)
    print("🔍 Tushare 高质量股票筛选")
    print("="*60)
    
    pro = init_tushare()
    if not pro:
        print("❌ Tushare 未初始化")
        return []
    
    # 获取 A 股列表
    print("📥 获取 A 股列表...")
    df_basic = get_stock_basic('E')
    if df_basic is None:
        return []
    
    print(f"   共 {len(df_basic)} 只股票")
    
    # 筛选条件
    MIN_ROE = 10.0
    MIN_ROIC = 10.0
    MIN_DIV_YIELD = 5.0
    MIN_MARKET_CAP = 50  # 亿
    
    qualified = []
    
    # 获取财务指标（批量）
    print("📥 获取财务指标...")
    
    # 遍历股票（示例：前 50 只）
    for idx, row in df_basic.head(50).iterrows():
        ts_code = row['ts_code']
        name = row['name']
        
        print(f"\n[{len(qualified)+1}] {ts_code} {name}...", end=" ")
        
        try:
            # 获取财务指标
            df_fina = get_fina_indicator(ts_code, start_date='20210101')
            
            if df_fina is None or len(df_fina) == 0:
                print("无数据")
                continue
            
            # 检查 ROE 和 ROIC
            recent_roe = df_fina['roe_roewa'].tail(5).mean()
            recent_roic = df_fina['roic'].tail(5).mean() if 'roic' in df_fina.columns else None
            
            # 检查股息率
            div_info = calc_dividend_yield(ts_code)
            avg_yield = div_info['avg_yield'] if div_info else 0
            
            # 判断是否符合
            if recent_roe >= MIN_ROE:
                if recent_roic is None or recent_roic >= MIN_ROIC:
                    if avg_yield >= MIN_DIV_YIELD:
                        qualified.append({
                            'ts_code': ts_code,
                            'name': name,
                            'roe': round(recent_roe, 2),
                            'roic': round(recent_roic, 2) if recent_roic else 'N/A',
                            'dividend_yield': round(avg_yield, 2)
                        })
                        print(f"✅ ROE:{recent_roe:.1f}% ROIC:{recent_roic:.1f if recent_roic else 'N/A'}% 股息:{avg_yield:.1f}%")
                    else:
                        print(f"⚠️ 股息率不足")
                else:
                    print(f"⚠️ ROIC 不足")
            else:
                print(f"⚠️ ROE 不足")
        
        except Exception as e:
            print(f"❌ 错误：{e}")
    
    print(f"\n✅ 筛选完成：{len(qualified)} 只符合")
    return qualified

# ============== 主函数 ==============

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == 'setup':
        # 设置 Token
        token = input("请输入 Tushare Token: ").strip()
        if token:
            TUSHARE_TOKEN_FILE.write_text(token)
            print(f"✅ Token 已保存：{TUSHARE_TOKEN_FILE}")
        return
    
    # 运行筛选
    qualified = screen_high_quality_stocks()
    
    # 保存结果
    if qualified:
        df = pd.DataFrame(qualified)
        csv_file = OUTPUT_DIR / f'tushare_qualified_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 结果已保存：{csv_file}")

if __name__ == "__main__":
    main()
