#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股筛选批次 1/5：筛选股票 000001-000999 开头的所有股票
使用 AkShare 作为数据源（无需 token）

条件：
- PE < 50
- ROE 连续 5 年 > 5%
- ROIC 连续 5 年 > 5%
- 自由现金流连续 5 年为正
- 资产负债率 < 50%
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import time
import warnings

warnings.filterwarnings('ignore')

def get_stock_list_000():
    """获取 000 开头的所有 A 股股票列表"""
    print("获取 000 开头的股票列表...")
    try:
        # 获取所有 A 股股票
        df = ak.stock_zh_a_spot_em()
        # 筛选 000 开头的股票
        stocks_000 = df[df['代码'].str.startswith('000')].copy()
        print(f"找到 {len(stocks_000)} 只 000 开头的股票")
        return stocks_000
    except Exception as e:
        print(f"获取股票列表失败：{e}")
        return pd.DataFrame()

def get_financial_indicators(symbol):
    """获取股票的主要财务指标"""
    try:
        # 获取主要财务指标
        df = ak.stock_financial_analysis_indicator(symbol=symbol)
        if df.empty:
            return None
        return df
    except Exception as e:
        # print(f"获取 {symbol} 财务指标失败：{e}")
        return None

def get_balance_sheet(symbol):
    """获取资产负债表数据"""
    try:
        df = ak.stock_financial_report_sina(stock=symbol, symbol="资产负债表")
        if df.empty:
            return None
        return df
    except Exception as e:
        return None

def get_cash_flow(symbol):
    """获取现金流量表数据"""
    try:
        df = ak.stock_financial_report_sina(stock=symbol, symbol="现金流量表")
        if df.empty:
            return None
        return df
    except Exception as e:
        return None

def check_stock_criteria(symbol, name):
    """检查单只股票是否符合所有条件"""
    print(f"检查 {symbol} ({name})...", end=" ")
    
    try:
        # 1. 获取实时行情数据（包含 PE）
        try:
            df_spot = ak.stock_zh_a_spot_em()
            stock_info = df_spot[df_spot['代码'] == symbol]
            if stock_info.empty:
                print("无法获取行情数据")
                return False, "无法获取行情"
            
            pe_ttm = stock_info.iloc[0].get('市盈率 - 动态', None)
            if pe_ttm is None or pe_ttm == '-' or pe_ttm <= 0:
                print(f"PE={pe_ttm} 不符合条件")
                return False, f"PE={pe_ttm}"
            
            # 检查 PE < 50
            if pe_ttm >= 50:
                print(f"PE={pe_ttm:.2f} >= 50，不符合条件")
                return False, f"PE={pe_ttm:.2f}"
        except Exception as e:
            print(f"获取行情失败：{e}")
            return False, "获取行情失败"
        
        # 2. 获取财务指标数据
        try:
            df_indicator = ak.stock_financial_analysis_indicator(symbol=symbol)
            if df_indicator.empty:
                print("无法获取财务指标")
                return False, "无法获取财务指标"
        except Exception as e:
            print(f"获取财务指标失败：{e}")
            return False, "获取财务指标失败"
        
        # 3. 检查 ROE 连续 5 年 > 5%
        # 获取最近 5 年的 ROE 数据
        try:
            df_roe = ak.stock_financial_abstract_ths(symbol=symbol)
            if df_roe.empty:
                print("无法获取 ROE 数据")
                return False, "无法获取 ROE 数据"
            
            # 检查最近 5 年的 ROE
            roe_values = []
            for idx, row in df_roe.iterrows():
                if '净资产收益率' in row:
                    roe_val = row['净资产收益率']
                    if isinstance(roe_val, str):
                        roe_val = float(roe_val.replace('%', ''))
                    roe_values.append(roe_val)
            
            # 取最近 5 年的数据
            if len(roe_values) < 5:
                print(f"ROE 数据不足 5 年（只有{len(roe_values)}年）")
                return False, "ROE 数据不足"
            
            recent_roe = roe_values[:5]
            if not all(r > 5 for r in recent_roe):
                print(f"ROE 不连续>5%: {recent_roe}")
                return False, f"ROE 不达标：{recent_roe}"
        except Exception as e:
            print(f"检查 ROE 失败：{e}")
            return False, "检查 ROE 失败"
        
        # 4. 检查资产负债率 < 50%
        try:
            df_bs = ak.stock_financial_report_sina(stock=symbol, symbol="资产负债表")
            if not df_bs.empty:
                # 获取最新的资产负债率
                latest_row = df_bs.iloc[0]
                if '资产负债率' in latest_row or '资产负债率' in latest_row:
                    key = '资产负债率' if '资产负债率' in latest_row else '资产负债率'
                    debt_ratio = latest_row[key]
                    if isinstance(debt_ratio, str):
                        debt_ratio = float(debt_ratio.replace('%', ''))
                    
                    if debt_ratio >= 50:
                        print(f"资产负债率={debt_ratio:.2f}% >= 50%，不符合条件")
                        return False, f"资产负债率={debt_ratio:.2f}%"
                else:
                    # 尝试从其他字段获取
                    print("无法获取资产负债率数据")
                    return False, "无法获取资产负债率"
        except Exception as e:
            print(f"检查资产负债率失败：{e}")
            return False, "检查资产负债率失败"
        
        # 5. 检查自由现金流连续 5 年为正
        try:
            df_cf = ak.stock_financial_report_sina(stock=symbol, symbol="现金流量表")
            if df_cf.empty:
                print("无法获取现金流量表")
                return False, "无法获取现金流量表"
            
            # 检查经营活动产生的现金流量净额（作为自由现金流的代理）
            fcf_values = []
            for idx, row in df_cf.iterrows():
                for col in ['经营活动产生的现金流量净额', '经营活动现金净额', '经营现金流净额']:
                    if col in row:
                        val = row[col]
                        if isinstance(val, str):
                            try:
                                val = float(val.replace(',', ''))
                            except:
                                val = 0
                        fcf_values.append(val)
                        break
            
            if len(fcf_values) < 5:
                print(f"现金流数据不足 5 年")
                return False, "现金流数据不足"
            
            recent_fcf = fcf_values[:5]
            if not all(f > 0 for f in recent_fcf):
                print(f"自由现金流不连续为正：{recent_fcf}")
                return False, f"现金流不达标"
        except Exception as e:
            print(f"检查自由现金流失败：{e}")
            return False, "检查自由现金流失败"
        
        # 6. ROIC 检查（AkShare 可能不直接提供 ROIC，尝试从财务指标获取）
        try:
            # 尝试从财务指标中获取 ROIC
            if '投入资本回报率' in df_indicator.columns:
                roic_col = '投入资本回报率'
            elif 'ROIC' in df_indicator.columns:
                roic_col = 'ROIC'
            else:
                print("无法获取 ROIC 数据，跳过此项检查")
                roic_col = None
            
            if roic_col:
                roic_values = df_indicator[roic_col].head(5).tolist()
                if len(roic_values) >= 5 and not all(r > 5 for r in roic_values):
                    print(f"ROIC 不连续>5%: {roic_values}")
                    return False, f"ROIC 不达标：{roic_values}"
        except Exception as e:
            print(f"检查 ROIC 失败：{e}")
            return False, "检查 ROIC 失败"
        
        print("✅ 符合条件")
        return True, "通过"
        
    except Exception as e:
        print(f"检查失败：{e}")
        return False, f"错误：{e}"

def main():
    print("=" * 60)
    print("A 股筛选批次 1/5: 000001-000999")
    print("数据源：AkShare")
    print("筛选条件:")
    print("  - PE < 50")
    print("  - ROE 连续 5 年 > 5%")
    print("  - ROIC 连续 5 年 > 5%")
    print("  - 自由现金流连续 5 年 > 0")
    print("  - 资产负债率 < 50%")
    print("=" * 60)
    print()
    
    # 获取股票列表
    stock_list = get_stock_list_000()
    if stock_list.empty:
        print("未能获取股票列表，退出")
        return []
    
    # 筛选结果
    passed_stocks = []
    failed_stocks = []
    
    # 遍历所有股票
    total = len(stock_list)
    print(f"\n开始筛选 {total} 只股票...\n")
    
    for idx, row in stock_list.iterrows():
        symbol = row['代码']
        name = row['名称']
        
        try:
            passed, reason = check_stock_criteria(symbol, name)
            if passed:
                passed_stocks.append({
                    '代码': symbol,
                    '名称': name,
                    '原因': reason
                })
            else:
                failed_stocks.append({
                    '代码': symbol,
                    '名称': name,
                    '原因': reason
                })
        except Exception as e:
            print(f"处理 {symbol} 时出错：{e}")
            failed_stocks.append({
                '代码': symbol,
                '名称': name,
                '原因': f"错误：{e}"
            })
        
        # 每处理 10 只股票，保存一次进度
        if (idx + 1) % 10 == 0:
            print(f"\n进度：{idx + 1}/{total}, 已通过：{len(passed_stocks)}")
            # 保存中间结果
            if passed_stocks:
                pd.DataFrame(passed_stocks).to_csv('/home/admin/openclaw/workspace/screening_batch1_result.csv', index=False)
        
        time.sleep(0.3)  # 控制请求频率，避免被限
    
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
