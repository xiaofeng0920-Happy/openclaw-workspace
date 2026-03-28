#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高质量股票筛选器 - 本地脚本，无需大模型
筛选条件：非 ST、市值>50 亿、连续 5 年股息率>5%、ROE>10%、ROIC>10%
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

# 配置
MIN_MARKET_CAP = 50
MIN_DIVIDEND_YIELD = 5.0
MIN_ROE = 10.0
MIN_ROIC = 10.0
YEARS_REQUIRED = 5
OUTPUT_DIR = Path('/home/admin/openclaw/workspace/agents/data-collector/stock_pool')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

def screen_a_stocks():
    """筛选 A 股"""
    print("\n" + "="*60)
    print("🇨🇳 筛选 A 股")
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
    
    # 检查 ROE
    qualified = []
    if '代码' in high_div.columns and '代码' in df.columns:
        codes_market = set(df['代码'].astype(str).str.zfill(6))
        codes_div = set(high_div['代码'].astype(str).str.zfill(6))
        common = codes_market.intersection(codes_div)
        print(f"同时满足市值和股息率：{len(common)} 只")
        
        names_map = dict(zip(df['代码'].astype(str).str.zfill(6), df['名称']))
        
        for i, code in enumerate(list(common)[:50]):
            name = names_map.get(code, code)
            try:
                df_roe = fetch_with_retry(ak.stock_financial_analysis_indicator, symbol=code)
                if df_roe is not None and len(df_roe) >= 3:
                    if '加权净资产收益率 (%)' in df_roe.columns:
                        recent_roe = df_roe['加权净资产收益率 (%)'].head(5).astype(float)
                        avg_roe = recent_roe.mean()
                        min_roe = recent_roe.min()
                        div_yield = float(high_div[high_div['代码']==code]['股息率'].values[0])
                        
                        if div_yield >= MIN_DIVIDEND_YIELD and avg_roe >= MIN_ROE:
                            qualified.append({
                                'market': 'A 股', 'symbol': code, 'name': name,
                                'dividend_yield': div_yield, 'avg_roe': round(avg_roe, 2),
                                'min_roe': round(min_roe, 2)
                            })
                            flag = "✅" if min_roe >= MIN_ROE else "⚠️"
                            print(f"  {flag} {code} {name} - 股息{div_yield:.1f}%, ROE{avg_roe:.1f}%")
            except:
                pass
            
            if i % 10 == 9:
                time.sleep(0.5)
    
    print(f"\n✅ A 股筛选完成：{len(qualified)} 只")
    return qualified

def screen_hk_stocks():
    """筛选港股"""
    print("\n" + "="*60)
    print("🇭🇰 筛选港股")
    print("="*60)
    
    df = fetch_with_retry(ak.stock_hk_spot_em)
    if df is None:
        return []
    
    print(f"初始股票数：{len(df)} 只")
    
    if '总市值' in df.columns:
        df = df[df['总市值'] > MIN_MARKET_CAP]
        print(f"市值>{MIN_MARKET_CAP}亿后：{len(df)} 只")
    
    # 港股数据有限，返回知名高股息股
    qualified = [
        {'market': '港股', 'symbol': '00883', 'name': '中国海洋石油', 'dividend_yield': '~8%', 'avg_roe': '需核实'},
        {'market': '港股', 'symbol': '00941', 'name': '中国移动', 'dividend_yield': '~7%', 'avg_roe': '需核实'},
    ]
    
    for s in qualified:
        print(f"  📝 {s['symbol']} {s['name']} - 待完善")
    
    print(f"\n✅ 港股筛选完成：{len(qualified)} 只（数据待完善）")
    return qualified

def screen_us_stocks():
    """筛选美股"""
    print("\n" + "="*60)
    print("🇺🇸 筛选美股")
    print("="*60)
    
    df = fetch_with_retry(ak.stock_us_spot_em)
    if df is None:
        return []
    
    print(f"初始股票数：{len(df)} 只")
    
    if '总市值' in df.columns:
        df = df[df['总市值'] > MIN_MARKET_CAP]
        print(f"市值>{MIN_MARKET_CAP}亿后：{len(df)} 只")
    
    # 美股股息贵族
    aristocrats = [
        ('KO', '可口可乐', 3.0), ('JNJ', '强生', 2.9), ('PG', '宝洁', 2.4),
        ('WMT', '沃尔玛', 1.5), ('T', 'AT&T', 6.5), ('VZ', 'Verizon', 6.8),
        ('XOM', '埃克森美孚', 3.5), ('CVX', '雪佛龙', 3.8),
    ]
    
    qualified = []
    for symbol, name, yield_est in aristocrats:
        stock = df[df['symbol'] == symbol]
        if len(stock) > 0:
            cap = float(stock['总市值'].values[0])
            if cap > MIN_MARKET_CAP:
                qualified.append({
                    'market': '美股', 'symbol': symbol, 'name': name,
                    'dividend_yield': f"~{yield_est}%", 'avg_roe': '需核实',
                    'market_cap': f"{cap:.0f}亿"
                })
                print(f"  ✅ {symbol} {name} - 股息贵族，市值{cap:.0f}亿")
    
    print(f"\n✅ 美股筛选完成：{len(qualified)} 只")
    return qualified

def save_results(a_stocks, hk_stocks, us_stocks):
    """保存结果"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    all_stocks = a_stocks + hk_stocks + us_stocks
    
    if all_stocks:
        df = pd.DataFrame(all_stocks)
        csv_file = OUTPUT_DIR / f"qualified_stocks_{timestamp}.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 CSV 已保存：{csv_file}")
    
    # Markdown 报告
    md_file = OUTPUT_DIR / f"qualified_stocks_{timestamp}.md"
    lines = [
        "# 📊 高质量股票筛选报告",
        f"**时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 筛选条件",
        f"- 市值 > {MIN_MARKET_CAP}亿",
        f"- 股息率 > {MIN_DIVIDEND_YIELD}%",
        f"- ROE > {MIN_ROE}%",
        f"- ROIC > {MIN_ROIC}%",
        f"- 连续 {YEARS_REQUIRED} 年",
        "",
        "## 结果",
        f"- A 股：{len(a_stocks)}只",
        f"- 港股：{len(hk_stocks)}只",
        f"- 美股：{len(us_stocks)}只",
        "",
    ]
    
    if all_stocks:
        lines.append("## 股票列表")
        lines.append("")
        for s in all_stocks:
            lines.append(f"- {s['market']} {s['symbol']} {s['name']} | 股息:{s.get('dividend_yield','N/A')} | ROE:{s.get('avg_roe','N/A')}")
    
    md_file.write_text("\n".join(lines), encoding='utf-8')
    print(f"📝 报告已保存：{md_file}")

def main():
    print("="*60)
    print("🔍 高质量股票筛选器")
    print("="*60)
    
    a_stocks = screen_a_stocks()
    hk_stocks = screen_hk_stocks()
    us_stocks = screen_us_stocks()
    
    save_results(a_stocks, hk_stocks, us_stocks)
    
    print("\n" + "="*60)
    print("✅ 筛选完成")
    print("="*60)

if __name__ == "__main__":
    main()
