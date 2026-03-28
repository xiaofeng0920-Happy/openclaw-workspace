#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股筛选批次 3/3：筛选港股 02000-09999 开头的所有股票（约 900 只）
条件：
- PE < 30
- ROE 连续 5 年 > 5%
- ROIC 连续 5 年 > 5%
- 自由现金流连续 5 年为正
- 资产负债率 < 50%

使用 Tushare 筛选
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
import pandas as pd

try:
    import tushare as ts
except ImportError:
    print("❌ 请安装 tushare: pip install tushare")
    sys.exit(1)

# ============== 配置 ==============

# Tushare Token 文件
TUSHARE_TOKEN_FILE = Path('/home/admin/openclaw/workspace/agents/data-collector/.tushare_token')

# 输出路径
OUTPUT_DIR = Path('/home/admin/openclaw/workspace/agents/data-collector/tushare_data')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 筛选条件
MAX_PE = 30.0
MIN_ROE = 5.0
MIN_ROIC = 5.0
MIN_FCF_YEARS = 5
MAX_DEBT_RATIO = 50.0

# 港股代码范围（从 ts_code 提取）
HK_CODE_START = 2000
HK_CODE_END = 9999

# ============== 工具函数 ==============

def get_token():
    """获取 Tushare Token"""
    if TUSHARE_TOKEN_FILE.exists():
        return TUSHARE_TOKEN_FILE.read_text().strip()
    return None

def init_tushare():
    """初始化 Tushare"""
    token = get_token()
    if token:
        ts.set_token(token)
        return ts.pro_api()
    return None

def get_hk_basic():
    """获取港股基本信息"""
    pro = init_tushare()
    if not pro:
        return None
    
    try:
        # 获取港股列表
        df = pro.hk_basic(fields='ts_code,name,market,list_date')
        # 从 ts_code 提取 symbol (如 00001.HK -> 00001)
        df['symbol'] = df['ts_code'].str.extract(r'(\d+)\.HK')[0]
        return df
    except Exception as e:
        print(f"❌ 获取港股列表失败：{e}")
        return None

def get_fina_indicator(ts_code, start_date='20190101', end_date=None):
    """获取财务指标（ROE、ROIC 等）"""
    pro = init_tushare()
    if not pro:
        return None
    
    if end_date is None:
        end_date = datetime.now().strftime('%Y%m%d')
    
    try:
        df = pro.fina_indicator(ts_code=ts_code, start_date=start_date, end_date=end_date,
                               fields='ts_code,end_date,roe_roewa,roic,eps,bps,pe,pe_ttm')
        return df
    except Exception as e:
        return None

def get_cashflow(ts_code, start_date='20190101', end_date=None):
    """获取现金流量表"""
    pro = init_tushare()
    if not pro:
        return None
    
    if end_date is None:
        end_date = datetime.now().strftime('%Y%m%d')
    
    try:
        df = pro.cashflow(ts_code=ts_code, start_date=start_date, end_date=end_date,
                         fields='ts_code,end_date,oper_cf,invest_cf,financing_cf,free_cf')
        return df
    except Exception as e:
        return None

def get_balance(ts_code, start_date='20190101', end_date=None):
    """获取资产负债表"""
    pro = init_tushare()
    if not pro:
        return None
    
    if end_date is None:
        end_date = datetime.now().strftime('%Y%m%d')
    
    try:
        df = pro.balancesheet(ts_code=ts_code, start_date=start_date, end_date=end_date,
                             fields='ts_code,end_date,total_assets,total_liab')
        return df
    except Exception as e:
        return None

def get_yearly_data(df, field, years=5):
    """获取最近 N 年的年度数据"""
    if df is None or len(df) == 0:
        return []
    
    # 按年份分组，取每年最后一个报告期（通常是年报）
    df = df.copy()
    df['year'] = df['end_date'].astype(str).str[:4]
    
    # 按年份分组，取每个年份的最后一条记录
    yearly = df.groupby('year').last().reset_index()
    yearly = yearly.sort_values('year', ascending=False)
    
    # 取最近 N 年
    recent = yearly.head(years)
    
    return recent[field].tolist()

def check_roe_continuous(df_fina, min_roe=5.0, years=5):
    """检查 ROE 连续 N 年 > min_roe"""
    if df_fina is None or len(df_fina) == 0:
        return False, []
    
    roe_values = get_yearly_data(df_fina, 'roe_roewa', years)
    
    if len(roe_values) < years:
        return False, roe_values
    
    # 检查是否所有年份都大于最小值
    for roe in roe_values:
        if pd.isna(roe) or roe <= min_roe:
            return False, roe_values
    
    return True, roe_values

def check_roic_continuous(df_fina, min_roic=5.0, years=5):
    """检查 ROIC 连续 N 年 > min_roic"""
    if df_fina is None or len(df_fina) == 0:
        return False, []
    
    # 检查是否有 roic 字段
    if 'roic' not in df_fina.columns:
        return False, []
    
    roic_values = get_yearly_data(df_fina, 'roic', years)
    
    if len(roic_values) < years:
        return False, roic_values
    
    # 检查是否所有年份都大于最小值
    for roic in roic_values:
        if pd.isna(roic) or roic <= min_roic:
            return False, roic_values
    
    return True, roic_values

def check_fcf_continuous(df_cashflow, years=5):
    """检查自由现金流连续 N 年为正"""
    if df_cashflow is None or len(df_cashflow) == 0:
        return False, []
    
    # 优先使用 free_cf 字段，如果没有则计算
    if 'free_cf' in df_cashflow.columns:
        fcf_values = get_yearly_data(df_cashflow, 'free_cf', years)
    else:
        # 自由现金流 = 经营现金流 - 投资现金流
        df = df_cashflow.copy()
        df['free_cf'] = df['oper_cf'] - df['invest_cf']
        fcf_values = get_yearly_data(df, 'free_cf', years)
    
    if len(fcf_values) < years:
        return False, fcf_values
    
    # 检查是否所有年份都为正
    for fcf in fcf_values:
        if pd.isna(fcf) or fcf <= 0:
            return False, fcf_values
    
    return True, fcf_values

def check_debt_ratio(df_balance, max_ratio=50.0):
    """检查资产负债率 < max_ratio"""
    if df_balance is None or len(df_balance) == 0:
        return False, []
    
    # 获取最近一年的数据
    df = df_balance.copy()
    df = df.sort_values('end_date', ascending=False)
    latest = df.head(1)
    
    if len(latest) == 0:
        return False, []
    
    row = latest.iloc[0]
    total_assets = row['total_assets']
    total_liab = row['total_liab']
    
    if pd.isna(total_assets) or pd.isna(total_liab) or total_assets <= 0:
        return False, []
    
    debt_ratio = (total_liab / total_assets) * 100
    
    return debt_ratio < max_ratio, [debt_ratio]

def get_pe_from_fina(df_fina):
    """从财务指标获取 PE"""
    if df_fina is None or len(df_fina) == 0:
        return None
    
    # 使用 PE_TTM
    df = df_fina.sort_values('end_date', ascending=False)
    
    # 尝试 pe_ttm 字段
    if 'pe_ttm' in df.columns:
        pe = df.iloc[0]['pe_ttm']
        if pd.notna(pe) and pe > 0:
            return pe
    
    # 尝试 pe 字段
    if 'pe' in df.columns:
        pe = df.iloc[0]['pe']
        if pd.notna(pe) and pe > 0:
            return pe
    
    return None

def screen_hk_stocks():
    """筛选港股 02000-09999"""
    print("="*60)
    print("🔍 港股筛选批次 3/3: 02000-09999")
    print("="*60)
    print(f"筛选条件：")
    print(f"  - PE < {MAX_PE}")
    print(f"  - ROE 连续 5 年 > {MIN_ROE}%")
    print(f"  - ROIC 连续 5 年 > {MIN_ROIC}%")
    print(f"  - 自由现金流连续 5 年 > 0")
    print(f"  - 资产负债率 < {MAX_DEBT_RATIO}%")
    print("="*60)
    
    pro = init_tushare()
    if not pro:
        print("❌ Tushare 未初始化")
        return []
    
    # 获取港股列表
    print("\n📥 获取港股列表...")
    df_basic = get_hk_basic()
    
    if df_basic is None:
        print("❌ 获取港股列表失败")
        return []
    
    print(f"   共 {len(df_basic)} 只港股")
    
    # 筛选 02000-09999 范围的股票
    df_basic['symbol_int'] = df_basic['symbol'].astype(int)
    df_hk_range = df_basic[(df_basic['symbol_int'] >= HK_CODE_START) & 
                           (df_basic['symbol_int'] <= HK_CODE_END)]
    
    print(f"   02000-09999 范围：{len(df_hk_range)} 只股票")
    
    qualified = []
    total_checked = 0
    skipped_no_data = 0
    
    # 遍历股票
    for idx, row in df_hk_range.iterrows():
        ts_code = row['ts_code']
        symbol = row['symbol']
        name = row['name']
        
        total_checked += 1
        
        if total_checked % 50 == 0:
            print(f"\n📊 已检查 {total_checked}/{len(df_hk_range)} 只股票，符合{len(qualified)}只，无数据{skipped_no_data}只...")
        
        try:
            # 获取财务指标（包含 PE）
            df_fina = get_fina_indicator(ts_code)
            
            if df_fina is None or len(df_fina) == 0:
                skipped_no_data += 1
                continue
            
            # 获取 PE
            pe = get_pe_from_fina(df_fina)
            if pe is None or pe <= 0 or pe >= MAX_PE:
                continue
            
            # 获取现金流量表
            df_cashflow = get_cashflow(ts_code)
            
            # 获取资产负债表
            df_balance = get_balance(ts_code)
            
            # 检查 ROE 连续 5 年 > 5%
            roe_ok, roe_values = check_roe_continuous(df_fina, MIN_ROE, 5)
            if not roe_ok:
                continue
            
            # 检查 ROIC 连续 5 年 > 5%
            roic_ok, roic_values = check_roic_continuous(df_fina, MIN_ROIC, 5)
            if not roic_ok:
                continue
            
            # 检查自由现金流连续 5 年为正
            fcf_ok, fcf_values = check_fcf_continuous(df_cashflow, 5)
            if not fcf_ok:
                continue
            
            # 检查资产负债率 < 50%
            debt_ok, debt_values = check_debt_ratio(df_balance, MAX_DEBT_RATIO)
            if not debt_ok:
                continue
            
            # 所有条件符合
            qualified.append({
                'ts_code': ts_code,
                'symbol': symbol,
                'name': name,
                'PE': round(pe, 2),
                'ROE_5Y_avg': round(sum(roe_values)/len(roe_values), 2),
                'ROIC_5Y_avg': round(sum(roic_values)/len(roic_values), 2),
                'FCF_positive_years': 5,
                'debt_ratio': round(debt_values[0], 2)
            })
            
            print(f"✅ [{len(qualified)}] {symbol} {name} - PE:{pe:.1f} ROE:{roe_values[0]:.1f}% ROIC:{roic_values[0]:.1f}% 负债:{debt_values[0]:.1f}%")
            
            # 避免请求过快
            time.sleep(0.3)
            
        except Exception as e:
            continue
    
    print(f"\n{'='*60}")
    print(f"✅ 筛选完成！")
    print(f"   检查股票数：{total_checked}")
    print(f"   符合条件：{len(qualified)} 只")
    print(f"   无数据跳过：{skipped_no_data} 只")
    print(f"{'='*60}")
    
    return qualified

def main():
    """主函数"""
    # 运行筛选
    qualified = screen_hk_stocks()
    
    # 保存结果
    if qualified:
        df = pd.DataFrame(qualified)
        csv_file = OUTPUT_DIR / f'hk_screen_batch3_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 结果已保存：{csv_file}")
        
        # 打印结果
        print("\n📋 符合条件的股票列表：")
        print(df.to_string(index=False))
    else:
        print("\n⚠️  未找到符合条件的股票")

if __name__ == "__main__":
    main()
