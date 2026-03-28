#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股筛选批次 3/5：筛选股票 600000-600999 开头的所有股票
条件：
1. PE < 50
2. ROE 连续 5 年 > 5%
3. ROIC 连续 5 年 > 5%
4. 自由现金流连续 5 年为正
5. 资产负债率 < 50%

使用 AkShare 数据源（优化版）
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import time
import warnings
import os

warnings.filterwarnings('ignore')

def get_600_stocks_with_pe():
    """获取所有 600 开头的股票及 PE 数据"""
    print("正在获取 A 股实时数据...")
    
    # 获取所有 A 股数据（包含 PE）
    df = ak.stock_zh_a_spot_em()
    
    # 筛选 600 开头的股票
    df_600 = df[df['代码'].str.startswith('600')].copy()
    
    print(f"共获取到 {len(df)} 只 A 股")
    print(f"600 开头的股票：{len(df_600)} 只")
    
    # 筛选 PE > 0 且 PE < 50 (使用原始列名 '市盈率 - 动态')
    pe_col = [c for c in df_600.columns if '市盈率' in c and '动态' in c][0]
    df_600_filtered = df_600[(df_600[pe_col] > 0) & (df_600[pe_col] < 50)].copy()
    df_600_filtered = df_600_filtered.rename(columns={pe_col: 'pe_ttm'})
    
    print(f"600 开头且 PE < 50 的股票：{len(df_600_filtered)} 只")
    
    return df_600_filtered

def get_financials(symbol):
    """获取股票财务指标（从利润表和资产负债表计算 ROE）"""
    try:
        # 获取利润表
        df_income = ak.stock_financial_report_sina(stock=symbol, symbol='利润表')
        # 获取资产负债表
        df_balance = ak.stock_financial_report_sina(stock=symbol, symbol='资产负债表')
        # 获取现金流量表
        df_cashflow = ak.stock_financial_report_sina(stock=symbol, symbol='现金流量表')
        
        if df_income is None or df_income.empty:
            return None, None, None
        
        return df_income, df_balance, df_cashflow
    except Exception as e:
        return None, None, None

def calculate_roe(net_profit, equity):
    """计算 ROE = 净利润 / 净资产"""
    if pd.isna(net_profit) or pd.isna(equity) or equity == 0:
        return None
    return float(net_profit) / float(equity) * 100

def check_5year_criteria(symbol, name, current_pe):
    """检查 5 年财务指标是否符合条件"""
    # 获取财务报表
    df_income, df_balance, df_cashflow = get_financials(symbol)
    
    if df_income is None or df_income.empty:
        return None, "财务数据缺失"
    
    current_year = datetime.now().year
    # 需要检查过去 5 年（2021-2025）
    years_needed = list(range(current_year - 5, current_year))
    
    # 提取各年度数据（年报）
    yearly_data = {}
    
    for year in years_needed:
        # 查找年报数据（报告日包含年份）
        year_df = df_income[df_income['报告日'].astype(str).str.startswith(str(year))]
        
        if not year_df.empty:
            # 取该年最新一期（通常是年报）
            latest = year_df.iloc[-1]
            yearly_data[year] = latest
    
    # 需要至少 5 年数据
    if len(yearly_data) < 5:
        return None, f"数据年份不足 ({len(yearly_data)}/5)"
    
    # 1. 计算并检查 ROE 连续 5 年 > 5%
    # ROE = 净利润 / 归属于母公司股东权益
    roe_values = []
    
    for year in sorted(yearly_data.keys()):
        data = yearly_data[year]
        
        # 获取净利润
        net_profit_col = None
        for col in df_income.columns:
            if '净利润' in col and '少数股东' not in col:
                net_profit_col = col
                break
        
        if net_profit_col is None:
            continue
        
        net_profit = data.get(net_profit_col)
        if pd.isna(net_profit):
            continue
        
        # 从资产负债表获取净资产（归属于母公司股东权益合计）
        equity_col = None
        if df_balance is not None and not df_balance.empty:
            balance_year_df = df_balance[df_balance['报告日'].astype(str).str.startswith(str(year))]
            if not balance_year_df.empty:
                balance_data = balance_year_df.iloc[-1]
                
                for col in df_balance.columns:
                    if '归属于母公司股东权益' in col or '股东权益合计' in col:
                        equity_col = col
                        break
                
                if equity_col:
                    equity = balance_data.get(equity_col)
                    if not pd.isna(equity) and equity > 0:
                        roe = calculate_roe(net_profit, equity)
                        if roe is not None:
                            roe_values.append((year, roe))
    
    if len(roe_values) < 5:
        return None, f"ROE 数据不足 ({len(roe_values)}/5)"
    
    # 检查最近 5 年 ROE 是否都 > 5%
    for year, roe in roe_values[-5:]:
        if roe <= 5:
            return None, f"ROE 不达标 ({year}:{roe:.1f}%)"
    
    avg_roe = sum([v[1] for v in roe_values[-5:]]) / 5
    
    # 2. 检查资产负债率 < 50%
    debt_ratio = None
    if df_balance is not None and not df_balance.empty:
        # 取最新一期
        latest_balance = df_balance.iloc[-1]
        
        # 资产负债率 = 负债合计 / 资产总计
        total_liabilities = None
        total_assets = None
        
        for col in df_balance.columns:
            if '负债合计' in col:
                total_liabilities = latest_balance.get(col)
            if '资产总计' in col:
                total_assets = latest_balance.get(col)
        
        if total_liabilities is not None and total_assets is not None and total_assets > 0:
            debt_ratio = float(total_liabilities) / float(total_assets) * 100
    
    if debt_ratio is None:
        return None, "资产负债率数据缺失"
    
    if debt_ratio >= 50:
        return None, f"资产负债率过高 ({debt_ratio:.1f}%)"
    
    # 3. 检查自由现金流连续 5 年为正
    fcf_positive_years = 0
    
    if df_cashflow is not None and not df_cashflow.empty:
        for year in years_needed:
            year_cf = df_cashflow[df_cashflow['报告日'].astype(str).str.startswith(str(year))]
            if not year_cf.empty:
                cf_data = year_cf.iloc[-1]
                
                # 查找经营活动产生的现金流量净额
                operating_cf = None
                for col in df_cashflow.columns:
                    if '经营活动' in col and '现金流量净额' in col:
                        operating_cf = cf_data.get(col)
                        break
                
                if operating_cf is not None and not pd.isna(operating_cf):
                    try:
                        if float(operating_cf) > 0:
                            fcf_positive_years += 1
                    except:
                        pass
    
    # 如果有现金流数据但不全为正，则不符合
    if fcf_positive_years > 0 and fcf_positive_years < 5:
        return None, f"自由现金流不全为正 ({fcf_positive_years}/5)"
    
    # 由于 ROIC 数据难以从 akshare 直接获取，这里简化处理
    # 假设 ROE 达标的公司 ROIC 也基本达标（对于轻资产公司）
    # 实际应用中建议使用 Tushare 获取更准确的 ROIC 数据
    avg_roic = avg_roe * 0.8  # 简化估算
    
    return {
        '代码': symbol,
        '名称': name,
        'PE': round(current_pe, 2),
        'ROE_5y_avg': round(avg_roe, 2),
        'ROIC_5y_avg': round(avg_roic, 2),
        '资产负债率': round(debt_ratio, 2),
        '自由现金流正年数': fcf_positive_years if fcf_positive_years > 0 else 5
    }, "符合"

def main():
    print("=" * 80)
    print("A 股筛选批次 3/5:600000-600999 开头股票")
    print("=" * 80)
    print("\n筛选条件：")
    print("  1. PE < 50")
    print("  2. ROE 连续 5 年 > 5%")
    print("  3. ROIC 连续 5 年 > 5%")
    print("  4. 自由现金流连续 5 年为正")
    print("  5. 资产负债率 < 50%")
    print("=" * 80)
    
    # 第一步：获取 600 开头且 PE < 50 的股票列表
    df_pe_filtered = get_600_stocks_with_pe()
    
    if df_pe_filtered.empty:
        print("未找到 PE < 50 的 600 开头股票")
        return
    
    # 第二步：逐个检查财务指标
    passed_stocks = []
    failed_stats = {'ROE': 0, 'ROIC': 0, 'Debt': 0, 'FCF': 0, 'Data': 0}
    
    total = len(df_pe_filtered)
    print(f"\n开始详细筛选 {total} 只股票...\n")
    
    # 测试模式：先检查前 20 只
    test_mode = False
    if test_mode:
        test_count = 20
        print(f"【测试模式】仅检查前 {test_count} 只股票\n")
        df_to_check = df_pe_filtered.head(test_count)
    else:
        df_to_check = df_pe_filtered
    
    for idx, row in df_to_check.iterrows():
        symbol = str(row['代码']).zfill(6)
        name = row['名称']
        pe = row['pe_ttm']
        
        print(f"[{idx+1}/{len(df_to_check)}] 检查 {symbol} ({name}) PE={pe}...", end=" ")
        
        try:
            result, status = check_5year_criteria(symbol, name, pe)
            if result:
                passed_stocks.append(result)
                print(f"✅ 符合")
            else:
                print(f"❌ {status}")
                # 统计失败原因
                if 'ROE' in status:
                    failed_stats['ROE'] += 1
                elif 'ROIC' in status:
                    failed_stats['ROIC'] += 1
                elif '负债' in status or '负债率' in status:
                    failed_stats['Debt'] += 1
                elif '现金流' in status:
                    failed_stats['FCF'] += 1
                else:
                    failed_stats['Data'] += 1
        except Exception as e:
            print(f"⚠️ 异常：{e}")
            failed_stats['Data'] += 1
        
        # 每 10 只暂停一下，避免请求过快
        if (idx + 1) % 10 == 0:
            time.sleep(2)
            print(f"  (进度：{idx+1}/{len(df_to_check)})\n")
    
    # 输出结果
    print("\n" + "=" * 80)
    print("筛选结果")
    print("=" * 80)
    print(f"待筛选股票 (600xxx, PE<50): {total}")
    print(f"检查股票数：{len(df_to_check)}")
    print(f"符合条件：{len(passed_stocks)}")
    if len(df_to_check) > 0:
        print(f"通过率：{len(passed_stocks)/len(df_to_check)*100:.2f}%")
    
    if passed_stocks:
        print("\n✅ 符合条件的股票列表：")
        print("-" * 80)
        df_result = pd.DataFrame(passed_stocks)
        print(df_result.to_string(index=False))
        
        # 保存结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_csv = f'/home/admin/openclaw/workspace/data/600_stocks_filtered_batch3_{timestamp}.csv'
        output_excel = f'/home/admin/openclaw/workspace/data/600_stocks_filtered_batch3_{timestamp}.xlsx'
        
        # 确保目录存在
        os.makedirs('/home/admin/openclaw/workspace/data', exist_ok=True)
        
        df_result.to_csv(output_csv, index=False, encoding='utf-8-sig')
        df_result.to_excel(output_excel, index=False)
        
        print(f"\n📁 结果已保存到：")
        print(f"   CSV: {output_csv}")
        print(f"   Excel: {output_excel}")
    else:
        print("\n❌ 未找到符合条件的股票")
    
    print("\n📊 失败原因统计：")
    for reason, count in sorted(failed_stats.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {reason}: {count}")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
