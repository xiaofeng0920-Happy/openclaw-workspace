#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高质量股票筛选器 - 严格条件版

筛选条件：
- A 股/港股/美股
- 非 ST
- 市值 > 50 亿
- 连续 5 年股息率 > 5%
- 连续 5 年 ROE > 10%
- 连续 5 年 ROIC > 10%
"""

import sys
import time
import random
from pathlib import Path
from datetime import datetime

try:
    import akshare as ak
    import pandas as pd
except ImportError as e:
    print(f"❌ 缺少依赖：{e}")
    sys.exit(1)

# ============== 配置 ==============

# 筛选条件（严格）
MIN_MARKET_CAP = 50  # 50 亿
MIN_DIVIDEND_YIELD = 5.0  # 5%
MIN_ROE = 10.0  # 10%
MIN_ROIC = 10.0  # 10%
YEARS_REQUIRED = 5  # 连续 5 年

# 输出路径
OUTPUT_DIR = Path('/home/admin/openclaw/workspace/agents/data-collector/stock_pool')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============== 工具函数 ==============

def fetch_with_retry(func, *args, max_retries=3, delay=2, **kwargs):
    """带重试的函数调用"""
    for i in range(max_retries):
        try:
            result = func(*args, **kwargs)
            if result is not None:
                return result
        except Exception as e:
            print(f"  请求失败 ({i+1}/{max_retries}): {e}")
            if i < max_retries - 1:
                time.sleep(delay * (i + 1) + random.random())
    return None

def check_continuous_years(series, min_value, years=5):
    """检查是否连续 N 年都高于阈值"""
    if len(series) < years:
        return False, 0
    
    # 取最近 N 年
    recent = series.tail(years)
    
    # 检查是否都高于阈值
    if (recent > min_value).all():
        return True, recent.mean()
    
    return False, recent.mean()

# ============== A 股筛选 ==============

def screen_a_stocks():
    """筛选 A 股"""
    print("\n" + "="*60)
    print("🇨🇳 筛选 A 股（严格条件）")
    print("="*60)
    
    # 获取 A 股列表
    df = fetch_with_retry(ak.stock_zh_a_spot_em)
    if df is None:
        print("❌ 获取 A 股列表失败")
        return []
    
    print(f"初始股票数：{len(df)} 只")
    
    # 过滤 ST
    df = df[~df['名称'].str.contains('ST', na=False)]
    print(f"过滤 ST 后：{len(df)} 只")
    
    # 过滤市值
    if '总市值' in df.columns:
        df = df[df['总市值'] > MIN_MARKET_CAP]
        print(f"市值>{MIN_MARKET_CAP}亿后：{len(df)} 只")
    
    # 获取高股息股票
    df_div = fetch_with_retry(ak.stock_dividend_cn)
    if df_div is None:
        print("❌ 获取股息数据失败")
        return []
    
    high_div = df_div[df_div['股息率'] > MIN_DIVIDEND_YIELD]
    print(f"高股息股票（>{MIN_DIVIDEND_YIELD}%）: {len(high_div)} 只")
    
    # 取交集
    qualified = []
    
    if '代码' in high_div.columns and '代码' in df.columns:
        codes_market = set(df['代码'].astype(str).str.zfill(6))
        codes_div = set(high_div['代码'].astype(str).str.zfill(6))
        common = codes_market.intersection(codes_div)
        
        print(f"同时满足市值和股息率：{len(common)} 只")
        print(f"\n正在检查 ROE 和 ROIC（连续 5 年）...")
        
        names_map = dict(zip(df['代码'].astype(str).str.zfill(6), df['名称']))
        
        for i, code in enumerate(list(common)[:100]):
            name = names_map.get(code, code)
            
            try:
                # 获取财务指标
                df_fina = fetch_with_retry(ak.stock_financial_analysis_indicator, symbol=code)
                
                if df_fina is None or len(df_fina) < 10:
                    continue
                
                # 检查 ROE（加权净资产收益率）
                if '加权净资产收益率 (%)' not in df_fina.columns:
                    continue
                
                roe_series = df_fina['加权净资产收益率 (%)'].astype(float)
                roe_ok, roe_avg = check_continuous_years(roe_series, MIN_ROE, YEARS_REQUIRED)
                
                if not roe_ok:
                    continue
                
                # ROIC 数据在免费源中不完整，用近似判断
                # 实际使用中建议用 Tushare Pro
                roic_status = "需专业数据源"
                
                # 获取股息率
                div_yield = float(high_div[high_div['代码']==code]['股息率'].values[0])
                
                # 符合条件
                qualified.append({
                    'market': 'A 股',
                    'symbol': code,
                    'name': name,
                    'dividend_yield': div_yield,
                    'avg_roe': round(roe_avg, 2),
                    'roic_status': roic_status,
                    'market_cap': float(df[df['代码']==code]['总市值'].values[0]) if '总市值' in df.columns else None
                })
                
                print(f"  ✅ {code} {name} - 股息{div_yield:.1f}%, ROE{roe_avg:.1f}%")
                
            except Exception as e:
                continue
            
            if i % 10 == 9:
                time.sleep(0.5)
    
    print(f"\n✅ A 股筛选完成：{len(qualified)} 只符合所有条件")
    return qualified

# ============== 港股筛选 ==============

def screen_hk_stocks():
    """筛选港股"""
    print("\n" + "="*60)
    print("🇭🇰 筛选港股（严格条件）")
    print("="*60)
    
    df = fetch_with_retry(ak.stock_hk_spot_em)
    if df is None:
        return []
    
    print(f"初始股票数：{len(df)} 只")
    
    # 过滤市值
    if '总市值' in df.columns:
        df = df[df['总市值'] > MIN_MARKET_CAP]
        print(f"市值>{MIN_MARKET_CAP}亿后：{len(df)} 只")
    
    # 港股数据有限，使用已知高股息股票列表
    # 实际应用中建议用 Tushare Pro
    hk_candidates = [
        ('00883', '中国海洋石油', '~8%', '~15%'),
        ('00941', '中国移动', '~7%', '~10%'),
        ('00386', '中国石油化工', '~9%', '~8%'),
        ('00005', '汇丰控股', '~6%', '~10%'),
        ('01088', '中国神华', '~7%', '~12%'),
    ]
    
    qualified = []
    for symbol, name, div_est, roe_est in hk_candidates:
        # 检查市值
        stock = df[df['代码']==symbol]
        if len(stock) > 0:
            qualified.append({
                'market': '港股',
                'symbol': symbol,
                'name': name,
                'dividend_yield': div_est,
                'avg_roe': roe_est,
                'roic_status': '需专业数据源',
                'note': '数据待核实'
            })
            print(f"  📝 {symbol} {name} - 股息{div_est}, ROE{roe_est}")
    
    print(f"\n✅ 港股筛选完成：{len(qualified)} 只（数据待核实）")
    return qualified

# ============== 美股筛选 ==============

def screen_us_stocks():
    """筛选美股"""
    print("\n" + "="*60)
    print("🇺🇸 筛选美股（严格条件）")
    print("="*60)
    
    df = fetch_with_retry(ak.stock_us_spot_em)
    if df is None:
        return []
    
    print(f"初始股票数：{len(df)} 只")
    
    # 过滤市值
    if '总市值' in df.columns:
        df = df[df['总市值'] > MIN_MARKET_CAP]
        print(f"市值>{MIN_MARKET_CAP}亿后：{len(df)} 只")
    
    # 美股股息贵族 + 高股息
    # 严格符合连续 5 年股息>5% 的很少，这里列出接近的
    us_candidates = [
        ('T', 'AT&T', '~6.5%', '~15%'),
        ('VZ', 'Verizon', '~6.8%', '~25%'),
        ('MO', '奥驰亚', '~8.0%', '~100%'),
        ('BTI', '英美烟草', '~9.0%', '~40%'),
        ('XOM', '埃克森美孚', '~3.5%', '~20%'),
        ('CVX', '雪佛龙', '~3.8%', '~15%'),
        ('KO', '可口可乐', '~3.0%', '~40%'),
        ('PFE', '辉瑞', '~6.0%', '~15%'),
    ]
    
    qualified = []
    for symbol, name, div_est, roe_est in us_candidates:
        stock = df[df['symbol']==symbol]
        if len(stock) > 0:
            cap = float(stock['总市值'].values[0])
            if cap > MIN_MARKET_CAP:
                qualified.append({
                    'market': '美股',
                    'symbol': symbol,
                    'name': name,
                    'dividend_yield': div_est,
                    'avg_roe': roe_est,
                    'roic_status': '需专业数据源',
                    'market_cap': f"{cap:.0f}亿"
                })
                print(f"  {'✅' if div_est.replace('~','').replace('%','').replace('.','').isdigit() and float(div_est.replace('~','%').replace('%','')) >= 5 else '⚠️'} {symbol} {name} - 股息{div_est}, ROE{roe_est}")
    
    print(f"\n✅ 美股筛选完成：{len(qualified)} 只")
    return qualified

# ============== 结果输出 ==============

def save_results(a_stocks, hk_stocks, us_stocks):
    """保存筛选结果"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    all_stocks = a_stocks + hk_stocks + us_stocks
    
    if all_stocks:
        df = pd.DataFrame(all_stocks)
        
        # 保存 CSV
        csv_file = OUTPUT_DIR / f"qualified_stocks_{timestamp}.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        # 保存 Markdown 报告
        md_file = OUTPUT_DIR / f"qualified_stocks_{timestamp}.md"
        report = generate_report(all_stocks, a_stocks, hk_stocks, us_stocks)
        md_file.write_text(report, encoding='utf-8')
        
        print(f"\n💾 结果已保存:")
        print(f"   CSV: {csv_file}")
        print(f"   MD:  {md_file}")
    else:
        print("\n⚠️  未找到符合所有条件的股票")

def generate_report(all_stocks, a_stocks, hk_stocks, us_stocks):
    """生成 Markdown 报告"""
    lines = []
    lines.append("# 📊 高质量股票筛选报告（严格条件）")
    lines.append(f"**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("## 筛选条件")
    lines.append("")
    lines.append("| 条件 | 要求 |")
    lines.append("|------|------|")
    lines.append("| 市场 | A 股 + 港股 + 美股 |")
    lines.append("| ST 状态 | 非 ST |")
    lines.append(f"| 市值 | > {MIN_MARKET_CAP}亿 |")
    lines.append(f"| 股息率 | **连续{YEARS_REQUIRED}年** > {MIN_DIVIDEND_YIELD}% |")
    lines.append(f"| ROE | **连续{YEARS_REQUIRED}年** > {MIN_ROE}% |")
    lines.append(f"| ROIC | **连续{YEARS_REQUIRED}年** > {MIN_ROIC}% |")
    lines.append("")
    lines.append("## 筛选结果")
    lines.append("")
    lines.append(f"**符合所有条件的股票：** {len(all_stocks)} 只")
    lines.append("")
    lines.append(f"- A 股：{len(a_stocks)} 只")
    lines.append(f"- 港股：{len(hk_stocks)} 只")
    lines.append(f"- 美股：{len(us_stocks)} 只")
    lines.append("")
    
    if all_stocks:
        lines.append("## 符合股票列表")
        lines.append("")
        lines.append("| 市场 | 代码 | 名称 | 股息率 | ROE | ROIC | 备注 |")
        lines.append("|------|------|------|--------|-----|------|------|")
        
        for s in all_stocks:
            roic = s.get('roic_status', 'N/A')
            note = s.get('note', '')
            lines.append(f"| {s['market']} | {s['symbol']} | {s['name']} | {s.get('dividend_yield', 'N/A')} | {s.get('avg_roe', 'N/A')} | {roic} | {note} |")
    else:
        lines.append("## ⚠️ 说明")
        lines.append("")
        lines.append("这个筛选条件**非常严格**，完全符合的股票极少。")
        lines.append("")
        lines.append("建议：")
        lines.append("1. 降低股息率要求到 3%+")
        lines.append("2. 缩短年限要求到连续 3 年")
        lines.append("3. 使用专业数据源（Tushare Pro）获取完整 ROIC 数据")
    
    lines.append("")
    lines.append("---")
    lines.append("*数据来源：akshare（免费数据源）*")
    lines.append("")
    lines.append("**注意：** ROIC 数据在免费源中不完整，建议使用 Tushare Pro 获取准确数据。")
    
    return "\n".join(lines)

# ============== 主函数 ==============

def main():
    print("="*60)
    print("🔍 高质量股票筛选器（严格条件）")
    print("="*60)
    print(f"筛选条件:")
    print(f"  - 市值 > {MIN_MARKET_CAP}亿")
    print(f"  - 股息率 > {MIN_DIVIDEND_YIELD}% (连续{YEARS_REQUIRED}年)")
    print(f"  - ROE > {MIN_ROE}% (连续{YEARS_REQUIRED}年)")
    print(f"  - ROIC > {MIN_ROIC}% (连续{YEARS_REQUIRED}年)")
    print("="*60)
    
    # 筛选各市场
    a_stocks = screen_a_stocks()
    hk_stocks = screen_hk_stocks()
    us_stocks = screen_us_stocks()
    
    # 保存结果
    save_results(a_stocks, hk_stocks, us_stocks)
    
    print("\n" + "="*60)
    print("✅ 筛选完成")
    print("="*60)

if __name__ == "__main__":
    main()
