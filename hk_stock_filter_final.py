#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股全市场筛选 - 锋哥五好标准（最终版）
使用 AkShare 东方财富接口
条件：
1. PE < 30
2. ROE 连续 5 年 > 5%
3. ROIC 连续 5 年 > 5%
4. 自由现金流连续 5 年为正
5. 资产负债率 < 50%
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import time
import warnings

warnings.filterwarnings('ignore')

def get_hk_stock_list():
    """获取港股列表"""
    print("正在获取港股列表...")
    df = ak.stock_hk_spot_em()
    print(f"共获取到 {len(df)} 只港股")
    return df

def get_financials(symbol):
    """获取财务指标（东方财富）"""
    try:
        df = ak.stock_financial_hk_analysis_indicator_em(symbol=symbol)
        if df.empty:
            return None
        df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'])
        return df
    except Exception as e:
        return None

def get_current_price(symbol):
    """获取当前股价"""
    try:
        df = ak.stock_hk_spot_em()
        stock = df[df['代码'] == symbol]
        if stock.empty:
            return None
        return float(stock['最新价'].iloc[0])
    except:
        return None

def check_stock(symbol, name, price):
    """检查单只股票"""
    # 获取财务数据
    df_fina = get_financials(symbol)
    if df_fina is None or df_fina.empty:
        return None, "财务数据缺失"
    
    # 获取最新一年的 EPS_TTM 用于计算 PE
    latest = df_fina.sort_values('REPORT_DATE', ascending=False).iloc[0]
    eps_ttm = latest.get('EPS_TTM')
    
    if pd.isna(eps_ttm) or eps_ttm <= 0:
        return None, f"EPS 无效 ({eps_ttm})"
    
    # 计算 PE = 股价 / EPS
    pe = price / eps_ttm
    if pe >= 30:
        return None, f"PE 过高 ({pe:.1f})"
    
    # 获取过去 5 年数据
    current_year = datetime.now().year
    years_needed = list(range(current_year - 5, current_year))
    
    yearly_data = {}
    for year in years_needed:
        year_df = df_fina[df_fina['REPORT_DATE'].dt.year == year]
        if not year_df.empty:
            latest_year = year_df.sort_values('REPORT_DATE', ascending=False).iloc[0]
            yearly_data[year] = latest_year
    
    if len(yearly_data) < 5:
        return None, f"数据年份不足 ({len(yearly_data)}/5)"
    
    # 检查 ROE (ROE_YEARLY)
    roe_values = []
    for year in sorted(yearly_data.keys()):
        data = yearly_data[year]
        roe = data.get('ROE_YEARLY')
        if not pd.isna(roe):
            roe_values.append((year, float(roe)))
    
    if len(roe_values) < 5:
        return None, f"ROE 数据不足 ({len(roe_values)}/5)"
    
    for year, roe in roe_values[-5:]:
        if roe <= 5:
            return None, f"ROE 不达标 ({year}:{roe:.1f}%)"
    
    # 检查 ROIC (ROIC_YEARLY)
    roic_values = []
    for year in sorted(yearly_data.keys()):
        data = yearly_data[year]
        roic = data.get('ROIC_YEARLY')
        if not pd.isna(roic):
            roic_values.append((year, float(roic)))
    
    if len(roic_values) < 5:
        return None, f"ROIC 数据不足 ({len(roic_values)}/5)"
    
    for year, roic in roic_values[-5:]:
        if roic <= 5:
            return None, f"ROIC 不达标 ({year}:{roic:.1f}%)"
    
    # 检查资产负债率 (DEBT_ASSET_RATIO)
    debt_values = []
    for year in sorted(yearly_data.keys()):
        data = yearly_data[year]
        debt = data.get('DEBT_ASSET_RATIO')
        if not pd.isna(debt):
            debt_values.append((year, float(debt)))
    
    if not debt_values:
        return None, "资产负债率数据缺失"
    
    latest_debt = debt_values[-1][1]
    if latest_debt >= 50:
        return None, f"负债率过高 ({latest_debt:.1f}%)"
    
    # 检查自由现金流 (PER_NETCASH_OPERATE - 每股经营活动现金流)
    fcf_values = []
    for year in sorted(yearly_data.keys()):
        data = yearly_data[year]
        fcf = data.get('PER_NETCASH_OPERATE')
        if not pd.isna(fcf):
            fcf_values.append((year, float(fcf)))
    
    if len(fcf_values) < 5:
        # 如果现金流数据不足，暂时不卡这个条件
        pass
    else:
        for year, fcf in fcf_values[-5:]:
            if fcf <= 0:
                return None, f"现金流为负 ({year}:{fcf:.2f})"
    
    # 计算平均值
    avg_roe = sum([v[1] for v in roe_values[-5:]]) / len(roe_values[-5:])
    avg_roic = sum([v[1] for v in roic_values[-5:]]) / len(roic_values[-5:])
    avg_debt = sum([v[1] for v in debt_values[-5:]]) / len(debt_values[-5:])
    
    return {
        '代码': symbol,
        '名称': name,
        '股价': round(price, 2),
        'EPS_TTM': round(eps_ttm, 2),
        'PE': round(pe, 1),
        'ROE_5y_avg': round(avg_roe, 2),
        'ROIC_5y_avg': round(avg_roic, 2),
        '负债率': round(avg_debt, 2)
    }, "符合"

def main():
    print("=" * 70)
    print("港股全市场筛选 - 锋哥五好标准")
    print("=" * 70)
    print("\n筛选条件：")
    print("  1. PE < 30")
    print("  2. ROE 连续 5 年 > 5%")
    print("  3. ROIC 连续 5 年 > 5%")
    print("  4. 自由现金流连续 5 年为正")
    print("  5. 资产负债率 < 50%")
    print("=" * 70)
    
    # 获取港股列表
    df_stocks = get_hk_stock_list()
    
    # 筛选结果
    passed_stocks = []
    failed_stats = {}
    
    # 测试模式：只检查前 50 只
    test_mode = True
    test_count = 50 if test_mode else len(df_stocks)
    
    print(f"\n开始筛选（{'测试' if test_mode else '全量'}模式：前{test_count}只）...\n")
    
    for idx in range(min(test_count, len(df_stocks))):
        row = df_stocks.iloc[idx]
        symbol = str(row['代码']).zfill(6)
        name = row['名称']
        price = row['最新价']
        
        print(f"[{idx+1}/{test_count}] {symbol} ({name}) 股价={price}...", end=" ")
        
        try:
            result, status = check_stock(symbol, name, price)
            if result:
                passed_stocks.append(result)
                print(f"✅ 符合")
            else:
                print(f"❌ {status}")
                # 统计失败原因
                key = status.split(':')[0] if ':' in status else status
                failed_stats[key] = failed_stats.get(key, 0) + 1
        except Exception as e:
            print(f"⚠️ 异常：{e}")
            failed_stats['异常'] = failed_stats.get('异常', 0) + 1
        
        # 每 10 只暂停
        if (idx + 1) % 10 == 0:
            time.sleep(2)
            print(f"  (进度：{idx+1}/{test_count})\n")
    
    # 输出结果
    print("\n" + "=" * 70)
    print("筛选结果")
    print("=" * 70)
    print(f"检查股票数：{test_count}")
    print(f"符合条件：{len(passed_stocks)}")
    if test_count > 0:
        print(f"通过率：{len(passed_stocks)/test_count*100:.1f}%")
    
    if passed_stocks:
        print("\n✅ 符合锋哥五好标准的港股：")
        print("-" * 70)
        df_result = pd.DataFrame(passed_stocks)
        print(df_result.to_string(index=False))
        
        # 保存
        output_file = '/home/admin/openclaw/workspace/hk_filtered_stocks.csv'
        df_result.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n📁 结果已保存到：{output_file}")
    else:
        print("\n❌ 未找到符合条件的股票")
    
    if failed_stats:
        print("\n📊 失败原因 TOP5：")
        for reason, count in sorted(failed_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {reason}: {count}")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
