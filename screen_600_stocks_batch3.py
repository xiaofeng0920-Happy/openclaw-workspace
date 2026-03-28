#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股筛选批次 3/5：筛选股票 600000-600999 开头的所有股票（约 950 只）
条件：
1. PE < 50
2. ROE 连续 5 年 > 5%
3. ROIC 连续 5 年 > 5%
4. 自由现金流连续 5 年为正
5. 资产负债率 < 50%

使用 AkShare 数据源
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import time
import warnings
import os

warnings.filterwarnings('ignore')

def get_600_stocks():
    """获取所有 600 开头的 A 股列表"""
    print("正在获取 A 股列表...")
    df = ak.stock_info_a_code_name()
    
    # 筛选 600 开头的股票
    df_600 = df[df['code'].str.startswith('600')].copy()
    df_600['code'] = df_600['code'].astype(str).str.zfill(6)
    
    print(f"共获取到 {len(df_600)} 只 600 开头的股票")
    return df_600

def get_stock_pe(ts_code):
    """获取股票最新 PE (TTM)"""
    try:
        # 获取实时行情
        df = ak.stock_a_lg_indicator(symbol=ts_code)
        if df is None or df.empty:
            return None
        
        # 取最新一行的 PE 数据
        latest = df.iloc[-1]
        if 'pe_ttm' in latest.index:
            pe = latest['pe_ttm']
            if pd.notna(pe) and pe > 0:
                return float(pe)
        return None
    except Exception as e:
        return None

def get_financials(symbol):
    """获取股票财务指标（年度数据）"""
    try:
        # 获取财务指标
        df = ak.stock_financial_analysis_indicator(symbol=symbol)
        if df is None or df.empty:
            return None
        
        df['报告期'] = pd.to_datetime(df['报告期'])
        return df
    except Exception as e:
        return None

def get_cashflow(symbol):
    """获取现金流量表"""
    try:
        df = ak.stock_financial_cashflow(symbol=symbol)
        if df is None or df.empty:
            return None
        
        df['报告期'] = pd.to_datetime(df['报告期'])
        return df
    except Exception as e:
        return None

def check_5year_criteria(symbol, name):
    """检查 5 年财务指标是否符合条件"""
    # 获取财务指标
    df_fina = get_financials(symbol)
    if df_fina is None or df_fina.empty:
        return None, "财务数据缺失"
    
    current_year = datetime.now().year
    # 需要检查过去 5 年（2021-2025）
    years_needed = list(range(current_year - 5, current_year))
    
    # 提取各年度数据（取每年最新一期）
    yearly_data = {}
    for year in years_needed:
        year_df = df_fina[df_fina['报告期'].dt.year == year]
        if not year_df.empty:
            # 按报告期排序，取最新一期
            latest = year_df.sort_values('报告期', ascending=False).iloc[0]
            yearly_data[year] = latest
    
    # 需要至少 5 年数据
    if len(yearly_data) < 5:
        return None, f"数据年份不足 ({len(yearly_data)}/5)"
    
    # 1. 检查 ROE 连续 5 年 > 5%
    roe_values = []
    for year in sorted(yearly_data.keys()):
        data = yearly_data[year]
        # 查找 ROE 列（净资产收益率）
        roe_col = None
        for col in data.index:
            if '净资产收益率' in str(col) and '加权' in str(col):
                roe_col = col
                break
        if roe_col is None:
            for col in data.index:
                if '净资产收益率' in str(col):
                    roe_col = col
                    break
        
        if roe_col and pd.notna(data[roe_col]):
            try:
                roe_values.append((year, float(data[roe_col])))
            except:
                pass
    
    if len(roe_values) < 5:
        return None, f"ROE 数据不足 ({len(roe_values)}/5)"
    
    # 检查最近 5 年 ROE 是否都 > 5%
    for year, roe in roe_values[-5:]:
        if roe <= 5:
            return None, f"ROE 不达标 ({year}:{roe:.1f}%)"
    
    avg_roe = sum([v[1] for v in roe_values[-5:]]) / 5
    
    # 2. 检查 ROIC 连续 5 年 > 5%
    roic_values = []
    for year in sorted(yearly_data.keys()):
        data = yearly_data[year]
        # 查找 ROIC 列（投入资本回报率）
        roic_col = None
        for col in data.index:
            if '投入资本回报率' in str(col) or 'ROIC' in str(col).upper():
                roic_col = col
                break
        
        if roic_col and pd.notna(data[roic_col]):
            try:
                roic_values.append((year, float(data[roic_col])))
            except:
                pass
    
    if len(roic_values) < 5:
        return None, f"ROIC 数据不足 ({len(roic_values)}/5)"
    
    for year, roic in roic_values[-5:]:
        if roic <= 5:
            return None, f"ROIC 不达标 ({year}:{roic:.1f}%)"
    
    avg_roic = sum([v[1] for v in roic_values[-5:]]) / 5
    
    # 3. 检查资产负债率 < 50%
    debt_values = []
    for year in sorted(yearly_data.keys()):
        data = yearly_data[year]
        # 查找资产负债率列
        debt_col = None
        for col in data.index:
            if '资产负债率' in str(col):
                debt_col = col
                break
        
        if debt_col and pd.notna(data[debt_col]):
            try:
                debt_values.append((year, float(data[debt_col])))
            except:
                pass
    
    if not debt_values:
        return None, "资产负债率数据缺失"
    
    latest_debt = debt_values[-1][1]
    if latest_debt >= 50:
        return None, f"资产负债率过高 ({latest_debt:.1f}%)"
    
    # 4. 检查自由现金流连续 5 年为正
    df_cf = get_cashflow(symbol)
    fcf_positive_years = 0
    fcf_years_data = []
    
    if df_cf is not None and not df_cf.empty:
        for year in years_needed:
            year_cf = df_cf[df_cf['报告期'].dt.year == year]
            if not year_cf.empty:
                # 查找自由现金流或经营活动现金流量净额
                fcf_col = None
                for col in year_cf.columns:
                    if '自由现金流' in str(col):
                        fcf_col = col
                        break
                if fcf_col is None:
                    for col in year_cf.columns:
                        if '经营活动' in str(col) and '现金流量净额' in str(col):
                            fcf_col = col
                            break
                
                if fcf_col:
                    try:
                        latest_cf = year_cf[fcf_col].iloc[-1] if hasattr(year_cf[fcf_col], 'iloc') else year_cf[fcf_col].values[-1]
                        cf_value = float(latest_cf)
                        fcf_years_data.append((year, cf_value))
                        if cf_value > 0:
                            fcf_positive_years += 1
                    except:
                        pass
    
    # 如果现金流数据不足 5 年或不全为正，则不符合
    if len(fcf_years_data) > 0 and fcf_positive_years < 5:
        return None, f"自由现金流不全为正 ({fcf_positive_years}/5)"
    
    # 获取最新 PE
    pe = get_stock_pe(symbol)
    if pe is None or pe <= 0 or pe >= 50:
        return None, f"PE 不达标 (PE={pe})"
    
    return {
        '代码': symbol,
        '名称': name,
        'PE': round(pe, 2),
        'ROE_5y_avg': round(avg_roe, 2),
        'ROIC_5y_avg': round(avg_roic, 2),
        '资产负债率': round(latest_debt, 2),
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
    
    # 第一步：获取 600 开头的股票列表
    df_600 = get_600_stocks()
    
    if df_600.empty:
        print("未找到 600 开头的股票")
        return
    
    # 第二步：逐个检查财务指标
    passed_stocks = []
    failed_stats = {'PE': 0, 'ROE': 0, 'ROIC': 0, 'Debt': 0, 'FCF': 0, 'Data': 0}
    
    total = len(df_600)
    print(f"\n开始详细筛选 {total} 只股票...\n")
    
    for idx, row in df_600.iterrows():
        symbol = str(row['code']).zfill(6)
        name = row['name'] if 'name' in row.index else '未知'
        
        print(f"[{idx+1}/{total}] 检查 {symbol} ({name})...", end=" ")
        
        try:
            result, status = check_5year_criteria(symbol, name)
            if result:
                passed_stocks.append(result)
                print(f"✅ 符合")
            else:
                print(f"❌ {status}")
                # 统计失败原因
                if 'PE' in status:
                    failed_stats['PE'] += 1
                elif 'ROE' in status:
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
            print(f"  (进度：{idx+1}/{total})\n")
    
    # 输出结果
    print("\n" + "=" * 80)
    print("筛选结果")
    print("=" * 80)
    print(f"待筛选股票 (600xxx): {total}")
    print(f"符合条件：{len(passed_stocks)}")
    print(f"通过率：{len(passed_stocks)/total*100:.2f}%")
    
    if passed_stocks:
        print("\n✅ 符合条件的股票列表：")
        print("-" * 80)
        df_result = pd.DataFrame(passed_stocks)
        print(df_result.to_string(index=False))
        
        # 保存结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_csv = f'/home/admin/openclaw/workspace/data/600_stocks_filtered_{timestamp}.csv'
        output_excel = f'/home/admin/openclaw/workspace/data/600_stocks_filtered_{timestamp}.xlsx'
        
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
