#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股筛选批次 1/5：筛选股票 000001-000999 开头的所有股票
条件：
- PE < 50
- ROE 连续 5 年 > 5%
- ROIC 连续 5 年 > 5%
- 自由现金流连续 5 年为正
- 资产负债率 < 50%
"""

import tushare as ts
import pandas as pd
from datetime import datetime
import time

# 初始化 Tushare (需要使用 token)
# 注意：实际使用时需要设置正确的 token
# ts.set_token('your_token_here')
pro = ts.pro_api()

def get_stock_list():
    """获取 000 开头的所有 A 股股票列表"""
    print("获取股票列表...")
    stock_list = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,market,list_date')
    # 筛选 000 开头的股票 (深市主板)
    stocks_000 = stock_list[stock_list['ts_code'].str.startswith('000')]
    print(f"找到 {len(stocks_000)} 只 000 开头的股票")
    return stocks_000

def get_financial_indicator(ts_code, year):
    """获取指定年份的财务指标"""
    try:
        # 获取财务指标
        df = pro.fina_indicator(ts_code=ts_code, start_date=f'{year}0101', end_date=f'{year}1231')
        if df.empty:
            return None
        
        # 取最新一期的数据 (通常是年报)
        df = df.sort_values('end_date', ascending=False)
        if len(df) > 0:
            row = df.iloc[0]
            return {
                'year': year,
                'roe': row.get('roe', None),
                'roic': row.get('roic', None),
                'debt_to_asset': row.get('debt_to_asset', None),
                'fcf': row.get('free_cashflow', None)
            }
    except Exception as e:
        print(f"获取 {ts_code} {year}年数据失败：{e}")
    return None

def check_stock_criteria(ts_code, name):
    """检查单只股票是否符合所有条件"""
    print(f"检查 {ts_code} ({name})...", end=" ")
    
    current_year = datetime.now().year
    years_to_check = [current_year - i for i in range(1, 6)]  # 过去 5 年
    
    # 获取当前 PE 和资产负债率
    try:
        # 获取实时行情
        df = pro.daily(ts_code=ts_code, start_date=datetime.now().strftime('%Y%m%d'), 
                      end_date=datetime.now().strftime('%Y%m%d'))
        if df.empty:
            # 尝试获取最近的数据
            end_date = datetime.now()
            for i in range(10):
                check_date = (end_date - pd.Timedelta(days=i)).strftime('%Y%m%d')
                df = pro.daily(ts_code=ts_code, start_date=check_date, end_date=check_date)
                if not df.empty:
                    break
    except Exception as e:
        print(f"获取行情失败：{e}")
        return False, "无法获取行情数据"
    
    # 获取 PE (TTM)
    try:
        df_valuation = pro.daily_basic(ts_code=ts_code, 
                                       start_date=datetime.now().strftime('%Y%m%d'),
                                       end_date=datetime.now().strftime('%Y%m%d'))
        if df_valuation.empty:
            # 尝试获取最近的数据
            for i in range(10):
                check_date = (datetime.now() - pd.Timedelta(days=i)).strftime('%Y%m%d')
                df_valuation = pro.daily_basic(ts_code=ts_code, 
                                              start_date=check_date, end_date=check_date)
                if not df_valuation:
                    break
        
        if not df_valuation.empty:
            pe_ttm = df_valuation.iloc[0].get('pe_ttm', None)
            debt_ratio = df_valuation.iloc[0].get('debt_ratio', None)
        else:
            print("无法获取估值数据")
            return False, "无法获取估值数据"
    except Exception as e:
        print(f"获取估值失败：{e}")
        return False, "获取估值失败"
    
    # 检查 PE < 50
    if pe_ttm is None or pe_ttm <= 0 or pe_ttm >= 50:
        print(f"PE={pe_ttm} 不符合条件")
        return False, f"PE={pe_ttm}"
    
    # 检查资产负债率 < 50%
    if debt_ratio is None or debt_ratio >= 50:
        print(f"资产负债率={debt_ratio} 不符合条件")
        return False, f"资产负债率={debt_ratio}"
    
    # 检查过去 5 年的 ROE, ROIC, 自由现金流
    roe_pass = True
    roic_pass = True
    fcf_pass = True
    
    for year in years_to_check:
        indicator = get_financial_indicator(ts_code, year)
        if indicator is None:
            print(f"无法获取 {year}年财务指标")
            return False, f"无法获取 {year}年数据"
        
        roe = indicator['roe']
        roic = indicator['roic']
        fcf = indicator['fcf']
        
        # ROE > 5%
        if roe is None or roe <= 5:
            roe_pass = False
            print(f"{year}年 ROE={roe} 不符合条件")
            break
        
        # ROIC > 5%
        if roic is None or roic <= 5:
            roic_pass = False
            print(f"{year}年 ROIC={roic} 不符合条件")
            break
        
        # 自由现金流 > 0
        if fcf is None or fcf <= 0:
            fcf_pass = False
            print(f"{year}年自由现金流={fcf} 不符合条件")
            break
        
        time.sleep(0.1)  # 避免请求过快
    
    if not roe_pass:
        return False, "ROE 不连续达标"
    if not roic_pass:
        return False, "ROIC 不连续达标"
    if not fcf_pass:
        return False, "自由现金流不连续为正"
    
    print("✅ 符合条件")
    return True, "通过"

def main():
    print("=" * 60)
    print("A 股筛选批次 1/5: 000001-000999")
    print("筛选条件:")
    print("  - PE < 50")
    print("  - ROE 连续 5 年 > 5%")
    print("  - ROIC 连续 5 年 > 5%")
    print("  - 自由现金流连续 5 年 > 0")
    print("  - 资产负债率 < 50%")
    print("=" * 60)
    
    # 获取股票列表
    stock_list = get_stock_list()
    
    # 筛选结果
    passed_stocks = []
    failed_stocks = []
    
    # 遍历所有股票
    total = len(stock_list)
    for idx, row in stock_list.iterrows():
        ts_code = row['ts_code']
        name = row['name']
        
        try:
            passed, reason = check_stock_criteria(ts_code, name)
            if passed:
                passed_stocks.append({
                    'ts_code': ts_code,
                    'name': name,
                    'reason': reason
                })
            else:
                failed_stocks.append({
                    'ts_code': ts_code,
                    'name': name,
                    'reason': reason
                })
        except Exception as e:
            print(f"处理 {ts_code} 时出错：{e}")
            failed_stocks.append({
                'ts_code': ts_code,
                'name': name,
                'reason': f"错误：{e}"
            })
        
        # 每处理 10 只股票，保存一次进度
        if (idx + 1) % 10 == 0:
            print(f"\n进度：{idx + 1}/{total}, 已通过：{len(passed_stocks)}")
            # 保存中间结果
            pd.DataFrame(passed_stocks).to_csv('/home/admin/openclaw/workspace/screening_batch1_result.csv', index=False)
        
        time.sleep(0.2)  # 控制请求频率
    
    # 保存最终结果
    print("\n" + "=" * 60)
    print("筛选完成!")
    print(f"总检查：{total} 只")
    print(f"符合条件：{len(passed_stocks)} 只")
    print(f"不符合条件：{len(failed_stocks)} 只")
    print("=" * 60)
    
    # 输出符合条件的股票
    if passed_stocks:
        print("\n符合条件的股票:")
        df_passed = pd.DataFrame(passed_stocks)
        print(df_passed.to_string(index=False))
        
        # 保存到 CSV
        df_passed.to_csv('/home/admin/openclaw/workspace/screening_batch1_passed.csv', index=False)
        print(f"\n结果已保存到：/home/admin/openclaw/workspace/screening_batch1_passed.csv")
    else:
        print("\n没有找到符合条件的股票")
    
    return passed_stocks

if __name__ == "__main__":
    main()
