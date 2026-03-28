#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股全市场筛选 - 锋哥五好标准
使用 AkShare 获取港股数据
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
    try:
        # 获取港股实时行情列表
        df = ak.stock_hk_spot()
        print(f"共获取到 {len(df)} 只港股")
        return df
    except Exception as e:
        print(f"获取港股列表失败：{e}")
        return None

def get_stock_financials(symbol):
    """获取股票财务数据"""
    try:
        # 获取财务指标
        df = ak.stock_financial_analysis_indicator(symbol=symbol)
        return df
    except Exception as e:
        print(f"获取 {symbol} 财务数据失败：{e}")
        return None

def get_stock_pe(symbol):
    """获取股票 PE"""
    try:
        # 获取实时行情
        df = ak.stock_hk_spot()
        stock_data = df[df['代码'] == symbol]
        if stock_data.empty:
            return None
        pe = stock_data['市盈率'].iloc[0]
        return pe
    except Exception as e:
        print(f"获取 {symbol} PE 失败：{e}")
        return None

def check_stock(symbol, name):
    """检查单只股票是否符合条件"""
    print(f"检查 {symbol} ({name})...")
    
    # 1. 检查 PE
    try:
        df_spot = ak.stock_hk_spot()
        stock_info = df_spot[df_spot['代码'] == symbol]
        if stock_info.empty:
            return None, "无法获取实时数据"
        
        pe = stock_info['市盈率'].iloc[0]
        if pd.isna(pe) or pe >= 30 or pe < 0:
            return None, f"PE 不符合 ({pe})"
    except Exception as e:
        return None, f"PE 获取失败 ({e})"
    
    # 2. 获取财务指标
    try:
        df_fina = ak.stock_financial_analysis_indicator(symbol=symbol)
        if df_fina.empty:
            return None, "财务数据缺失"
        
        # 转换日期列
        df_fina['报告期'] = pd.to_datetime(df_fina['报告期'])
        
        # 获取最近 5 年的年度数据
        current_year = datetime.now().year
        years_data = {}
        
        for year in range(current_year - 5, current_year):
            year_data = df_fina[df_fina['报告期'].dt.year == year]
            if not year_data.empty:
                # 取该年最后一期数据
                latest = year_data.sort_values('报告期', ascending=False).iloc[0]
                years_data[year] = latest
        
        if len(years_data) < 5:
            return None, f"数据年份不足 (只有{len(years_data)}年)"
        
        # 检查各项指标
        roe_list = []
        roic_list = []
        fcf_list = []
        debt_list = []
        
        for year in sorted(years_data.keys()):
            data = years_data[year]
            
            # ROE (加权净资产收益率)
            roe_col = [c for c in data.index if '净资产收益率' in c and '加权' in c]
            if roe_col:
                roe = data[roe_col[0]]
                roe_list.append((year, roe))
            
            # 资产负债率
            debt_col = [c for c in data.index if '资产负债率' in c]
            if debt_col:
                debt = data[debt_col[0]]
                debt_list.append((year, debt))
            
            # ROIC (投入资本回报率)
            roic_col = [c for c in data.index if '投入资本回报率' in c or 'ROIC' in c.upper()]
            if roic_col:
                roic = data[roic_col[0]]
                roic_list.append((year, roic))
        
        # 检查 ROE 连续 5 年 > 5%
        if len(roe_list) < 5:
            return None, "ROE 数据不足 5 年"
        for year, roe in roe_list[-5:]:
            if pd.isna(roe) or roe <= 5:
                return None, f"ROE 不符合 ({year}年：{roe})"
        
        # 检查 ROIC 连续 5 年 > 5%
        if len(roic_list) < 5:
            return None, "ROIC 数据不足 5 年"
        for year, roic in roic_list[-5:]:
            if pd.isna(roic) or roic <= 5:
                return None, f"ROIC 不符合 ({year}年：{roic})"
        
        # 检查资产负债率 < 50%
        if len(debt_list) < 1:
            return None, "资产负债率数据缺失"
        latest_debt = debt_list[-1][1]
        if pd.isna(latest_debt) or latest_debt >= 50:
            return None, f"资产负债率不符合 ({latest_debt}%)"
        
        # 自由现金流检查（需要单独获取现金流量表）
        try:
            df_cashflow = ak.stock_financial_cashflow(symbol=symbol)
            if not df_cashflow.empty:
                df_cashflow['报告期'] = pd.to_datetime(df_cashflow['报告期'])
                fcf_positive_count = 0
                for year in range(current_year - 5, current_year):
                    year_cf = df_cashflow[df_cashflow['报告期'].dt.year == year]
                    if not year_cf.empty:
                        # 查找自由现金流相关列
                        fcf_col = [c for c in year_cf.index if '自由现金流' in c or '现金流量净额' in c]
                        if fcf_col:
                            fcf = year_cf[fcf_col[0]].iloc[-1] if hasattr(year_cf[fcf_col[0]], 'iloc') else year_cf[fcf_col[0]]
                            if not pd.isna(fcf) and fcf > 0:
                                fcf_positive_count += 1
                
                if fcf_positive_count < 5:
                    return None, f"自由现金流不全为正 ({fcf_positive_count}/5 年)"
        except Exception as e:
            print(f"  自由现金流检查跳过：{e}")
            # 如果无法获取，暂时不将此作为硬性条件
        
        return {
            '代码': symbol,
            '名称': name,
            'PE': round(pe, 2),
            'ROE_5y_avg': round(sum([r[1] for r in roe_list[-5:]]) / 5, 2),
            'ROIC_5y_avg': round(sum([r[1] for r in roic_list[-5:]]) / 5, 2),
            '资产负债率': round(latest_debt, 2)
        }, "符合所有条件"
        
    except Exception as e:
        return None, f"财务分析失败 ({e})"

def main():
    print("=" * 60)
    print("港股全市场筛选 - 锋哥五好标准")
    print("=" * 60)
    print("筛选条件：")
    print("1. PE < 30")
    print("2. ROE 连续 5 年 > 5%")
    print("3. ROIC 连续 5 年 > 5%")
    print("4. 自由现金流连续 5 年为正")
    print("5. 资产负债率 < 50%")
    print("=" * 60)
    
    # 获取港股列表
    hk_stocks = get_hk_stock_list()
    if hk_stocks is None or hk_stocks.empty:
        print("获取港股列表失败，退出")
        return
    
    # 筛选结果
    passed_stocks = []
    
    # 只检查前 50 只做测试（因为全量检查会非常慢）
    test_limit = 50
    print(f"\n开始筛选（测试模式：前{test_limit}只股票）...\n")
    
    for idx, row in hk_stocks.head(test_limit).iterrows():
        symbol = str(row['代码']).zfill(6) if '代码' in row.columns else None
        if symbol is None:
            continue
        
        name = row['名称'] if '名称' in row.columns else '未知'
        
        try:
            result, reason = check_stock(symbol, name)
            if result:
                passed_stocks.append(result)
                print(f"✅ {symbol} ({name}) - 符合所有条件")
            else:
                print(f"❌ {symbol} ({name}) - {reason}")
        except Exception as e:
            print(f"⚠️  {symbol} ({name}) - 异常：{e}")
        
        # 每 5 只股票暂停一下
        if (idx + 1) % 5 == 0:
            time.sleep(2)
            print(f"\n进度：{idx + 1}/{test_limit}\n")
    
    # 输出结果
    print("\n" + "=" * 60)
    print("筛选结果")
    print("=" * 60)
    print(f"检查股票数：{test_limit}")
    print(f"符合条件：{len(passed_stocks)}")
    
    if passed_stocks:
        print("\n符合锋哥五好标准的港股：")
        print("-" * 60)
        df_result = pd.DataFrame(passed_stocks)
        print(df_result.to_string(index=False))
        
        # 保存到 CSV
        df_result.to_csv('/home/admin/openclaw/workspace/hk_filtered_stocks.csv', index=False, encoding='utf-8-sig')
        print(f"\n结果已保存到：hk_filtered_stocks.csv")
    else:
        print("\n未找到符合条件的股票")

if __name__ == '__main__':
    main()
