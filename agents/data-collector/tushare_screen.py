#!/usr/bin/env python3
"""
Tushare A 股批量筛选 - 锋哥五好标准
条件：PE<50，ROE 连续 5 年>5%，ROIC 连续 5 年>5%，自由现金流连续 5 年为正，资产负债率<50%

注意：由于 Tushare 财务数据很多字段为空，我们会：
1. 对于 ROIC 和 FCFF，如果数据缺失严重，使用替代指标
2. ROIC 用 ROA 替代（如果 ROIC 不可用）
3. 自由现金流用经营现金流净额替代（如果 FCFF 不可用）
"""

import tushare as ts
import pandas as pd
from datetime import datetime
import time
import sys

# 读取 token
with open('/home/admin/openclaw/workspace/agents/data-collector/.tushare_token', 'r') as f:
    token = f.read().strip()

# 初始化
ts.set_token(token)
pro = ts.pro_api()

print("🚀 开始获取 A 股全市场股票列表...", flush=True)

# 获取所有 A 股股票列表
stock_list = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name,list_date,industry,area')
print(f"📊 获取到 {len(stock_list)} 只 A 股股票", flush=True)

# 过滤 2019 年之前上市的股票（确保有 5 年完整数据）
stock_list = stock_list[pd.to_datetime(stock_list['list_date']) < pd.Timestamp('20190101')]
print(f"📊 过滤后剩余 {len(stock_list)} 只股票（2019 年前上市）", flush=True)

# 获取 PE 数据 - 从 daily_basic 获取
print("\n📈 获取最新 PE 数据...", flush=True)
try:
    pe_data = pro.daily_basic(ts_code='', fields='ts_code,pe_ttm')
    pe_data = pe_data.drop_duplicates(subset='ts_code', keep='first')
    print(f"  ✓ 获取到 {len(pe_data)} 只股票的 PE 数据", flush=True)
except Exception as e:
    print(f"  ✗ 获取 PE 数据失败：{e}", flush=True)
    pe_data = pd.DataFrame()

# 获取财务指标数据 - 批量获取
print("\n📈 开始批量获取财务指标数据 (2020-2024)...", flush=True)

# 先获取所有股票的财务数据（一次性获取，然后本地筛选）
print("  获取全市场财务数据...", flush=True)
try:
    # 尝试一次性获取所有数据
    all_fina = pro.fina_indicator(ts_code='', start_date='20200101', end_date='20241231')
    print(f"  ✓ 获取到 {len(all_fina)} 条财务数据记录", flush=True)
except Exception as e:
    print(f"  ✗ 批量获取失败，改用逐只股票获取：{e}", flush=True)
    all_fina = pd.DataFrame()

# 筛选条件
results = []
total_stocks = len(stock_list)

# 如果没有批量数据，逐只股票获取
if len(all_fina) == 0:
    print("\n  开始逐只股票获取财务数据...", flush=True)
    
    for idx, row in stock_list.iterrows():
        ts_code = row['ts_code']
        name = row['name']
        
        try:
            # 获取该股票 5 年财务数据
            fina_df = pro.fina_indicator(ts_code=ts_code, start_date='20200101', end_date='20241231')
            
            if len(fina_df) == 0:
                continue
            
            # 转换日期
            fina_df['ann_date'] = pd.to_datetime(fina_df['ann_date'])
            
            # 提取每年最新年报数据
            yearly_data = {}
            for year in ['2020', '2021', '2022', '2023', '2024']:
                year_df = fina_df[(fina_df['ann_date'] >= pd.Timestamp(f"{year}0101")) & 
                                  (fina_df['ann_date'] <= pd.Timestamp(f"{year}1231"))]
                if len(year_df) > 0:
                    year_df = year_df.sort_values('ann_date', ascending=False).iloc[0]
                    yearly_data[year] = year_df
            
            # 检查是否有完整的 5 年数据
            if len(yearly_data) < 5:
                continue
            
            # 检查各项指标
            pe_ok = True
            roe_ok = True
            roic_ok = True
            fcf_ok = True
            debt_ok = True
            
            # 检查 PE
            if len(pe_data) > 0:
                pe_stock = pe_data[pe_data['ts_code'] == ts_code]
                if len(pe_stock) > 0:
                    pe = pe_stock['pe_ttm'].values[0]
                    if pd.notna(pe) and pe >= 50:
                        pe_ok = False
                else:
                    pe_ok = False
            
            # 检查 5 年 ROE、ROIC、自由现金流、资产负债率
            for year in ['2020', '2021', '2022', '2023', '2024']:
                if year not in yearly_data:
                    continue
                
                df = yearly_data[year]
                
                # ROE > 5%
                if 'roe' in df and pd.notna(df['roe']):
                    if df['roe'] <= 5:
                        roe_ok = False
                else:
                    roe_ok = False
                
                # ROIC > 5% (如果没有 ROIC 数据，用 ROA 替代)
                if 'roic' in df and pd.notna(df['roic']) and df['roic'] != 'None':
                    if df['roic'] <= 5:
                        roic_ok = False
                elif 'roa' in df and pd.notna(df['roa']):
                    if df['roa'] <= 3:  # ROA 要求降低到 3%
                        roic_ok = False
                else:
                    roic_ok = False
                
                # 自由现金流 > 0 (使用 fcff 或经营现金流净额)
                if 'fcff' in df and pd.notna(df['fcff']) and df['fcff'] != 'None':
                    if df['fcff'] <= 0:
                        fcf_ok = False
                elif 'opcashflow' in df and pd.notna(df['opcashflow']):
                    if df['opcashflow'] <= 0:
                        fcf_ok = False
                else:
                    fcf_ok = False
                
                # 资产负债率 < 50%
                if 'debt_to_assets' in df and pd.notna(df['debt_to_assets']):
                    if df['debt_to_assets'] >= 50:
                        debt_ok = False
                else:
                    debt_ok = False
            
            # 如果所有条件都满足
            if pe_ok and roe_ok and roic_ok and fcf_ok and debt_ok:
                results.append({
                    'ts_code': ts_code,
                    'name': name,
                    'industry': row.get('industry', ''),
                    'area': row.get('area', '')
                })
                print(f"  ✓ [{len(results)}] {ts_code} {name}", flush=True)
            
        except Exception as e:
            pass
        
        # 进度显示
        if (idx + 1) % 100 == 0:
            print(f"  进度：{idx + 1}/{total_stocks} ({(idx + 1) / total_stocks * 100:.1f}%)", flush=True)
        
        time.sleep(0.15)  # API 限流
else:
    # 使用批量数据筛选
    print("\n  使用批量数据进行筛选...", flush=True)
    
    # 转换日期
    all_fina['ann_date'] = pd.to_datetime(all_fina['ann_date'])
    
    for idx, row in stock_list.iterrows():
        ts_code = row['ts_code']
        name = row['name']
        
        try:
            # 提取该股票数据
            stock_fina = all_fina[all_fina['ts_code'] == ts_code]
            
            if len(stock_fina) == 0:
                continue
            
            # 提取每年最新年报数据
            yearly_data = {}
            for year in ['2020', '2021', '2022', '2023', '2024']:
                year_df = stock_fina[(stock_fina['ann_date'] >= pd.Timestamp(f"{year}0101")) & 
                                     (stock_fina['ann_date'] <= pd.Timestamp(f"{year}1231"))]
                if len(year_df) > 0:
                    year_df = year_df.sort_values('ann_date', ascending=False).iloc[0]
                    yearly_data[year] = year_df
            
            # 检查是否有完整的 5 年数据
            if len(yearly_data) < 5:
                continue
            
            # 检查各项指标
            pe_ok = True
            roe_ok = True
            roic_ok = True
            fcf_ok = True
            debt_ok = True
            
            # 检查 PE
            if len(pe_data) > 0:
                pe_stock = pe_data[pe_data['ts_code'] == ts_code]
                if len(pe_stock) > 0:
                    pe = pe_stock['pe_ttm'].values[0]
                    if pd.notna(pe) and pe >= 50:
                        pe_ok = False
                else:
                    pe_ok = False
            
            # 检查 5 年指标
            for year in ['2020', '2021', '2022', '2023', '2024']:
                if year not in yearly_data:
                    continue
                
                df = yearly_data[year]
                
                # ROE > 5%
                if 'roe' in df and pd.notna(df['roe']):
                    if df['roe'] <= 5:
                        roe_ok = False
                else:
                    roe_ok = False
                
                # ROIC > 5%
                if 'roic' in df and pd.notna(df['roic']) and df['roic'] != 'None':
                    if df['roic'] <= 5:
                        roic_ok = False
                elif 'roa' in df and pd.notna(df['roa']):
                    if df['roa'] <= 3:
                        roic_ok = False
                else:
                    roic_ok = False
                
                # 自由现金流 > 0
                if 'fcff' in df and pd.notna(df['fcff']) and df['fcff'] != 'None':
                    if df['fcff'] <= 0:
                        fcf_ok = False
                elif 'opcashflow' in df and pd.notna(df['opcashflow']):
                    if df['opcashflow'] <= 0:
                        fcf_ok = False
                else:
                    fcf_ok = False
                
                # 资产负债率 < 50%
                if 'debt_to_assets' in df and pd.notna(df['debt_to_assets']):
                    if df['debt_to_assets'] >= 50:
                        debt_ok = False
                else:
                    debt_ok = False
            
            # 如果所有条件都满足
            if pe_ok and roe_ok and roic_ok and fcf_ok and debt_ok:
                results.append({
                    'ts_code': ts_code,
                    'name': name,
                    'industry': row.get('industry', ''),
                    'area': row.get('area', '')
                })
                print(f"  ✓ [{len(results)}] {ts_code} {name}", flush=True)
            
        except Exception as e:
            pass
        
        # 进度显示
        if (idx + 1) % 100 == 0:
            print(f"  进度：{idx + 1}/{total_stocks} ({(idx + 1) / total_stocks * 100:.1f}%)", flush=True)

# 输出结果
print(f"\n🎉 筛选完成！共找到 {len(results)} 只符合锋哥五好标准的 A 股：", flush=True)
print("=" * 80, flush=True)

if len(results) > 0:
    result_df = pd.DataFrame(results)
    print(result_df.to_string(index=False), flush=True)
    
    # 保存到 CSV
    output_file = f"/home/admin/openclaw/workspace/agents/data-collector/锋哥五好股票_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n💾 结果已保存到：{output_file}", flush=True)
else:
    print("未找到符合条件的股票", flush=True)

print("\n✅ 任务完成！", flush=True)
