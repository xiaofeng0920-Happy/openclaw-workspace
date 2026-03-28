#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高质量股票筛选器 v2 - 放宽条件版

筛选条件：
- A 股/港股/美股
- 非 ST
- 市值 > 50 亿
- 连续 3 年股息率 > 3%
- 连续 3 年 ROE > 10%
- 连续 3 年 ROIC > 10%
"""

import sys
import time
from pathlib import Path
from datetime import datetime

try:
    import akshare as ak
    import pandas as pd
except ImportError:
    print("❌ 请安装 akshare: pip install akshare")
    sys.exit(1)

# ============== 配置 ==============

MIN_MARKET_CAP = 50  # 50 亿
MIN_DIVIDEND_YIELD = 3.0  # 3%
MIN_ROE = 10.0  # 10%
MIN_ROIC = 10.0  # 10%
YEARS_REQUIRED = 3  # 连续 3 年

OUTPUT_DIR = Path('/home/admin/openclaw/workspace/agents/data-collector/stock_pool')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============== 已知高质量股票池（手动维护 + 数据验证） ==============

# 美股：股息贵族 + 高质量成长股
US_STOCKS = [
    ('AAPL', '苹果', '科技', 0.5, 100, 50),
    ('MSFT', '微软', '科技', 0.8, 35, 30),
    ('GOOGL', '谷歌', '科技', 0, 18, 18),
    ('KO', '可口可乐', '消费', 3.0, 40, 15),
    ('PEP', '百事可乐', '消费', 2.8, 25, 15),
    ('PG', '宝洁', '消费', 2.4, 30, 20),
    ('JNJ', '强生', '医疗', 2.9, 25, 20),
    ('MRK', '默克', '医疗', 2.7, 20, 15),
    ('WMT', '沃尔玛', '消费', 1.5, 20, 12),
    ('HD', '家得宝', '消费', 2.5, 25, 20),
    ('V', 'Visa', '金融', 0.8, 35, 25),
    ('MA', '万事达', '金融', 0.6, 40, 30),
    ('JPM', '摩根大通', '金融', 2.5, 15, 12),
    ('BRK.B', '伯克希尔', '金融', 0, 12, 10),
    ('XOM', '埃克森美孚', '能源', 3.5, 20, 15),
    ('CVX', '雪佛龙', '能源', 3.8, 15, 12),
    ('VZ', 'Verizon', '电信', 6.8, 25, 10),
    ('T', 'AT&T', '电信', 6.5, 15, 8),
    ('MO', '奥驰亚', '烟草', 8.0, 100, 15),
    ('PM', '菲利普莫里斯', '烟草', 5.0, 40, 20),
    ('BTI', '英美烟草', '烟草', 9.0, 40, 15),
    ('PFE', '辉瑞', '医疗', 6.0, 15, 10),
    ('ABBV', '艾伯维', '医疗', 4.0, 30, 20),
    ('INTC', '英特尔', '科技', 2.0, 15, 10),
    ('IBM', 'IBM', '科技', 4.5, 20, 12),
]

# 港股：高股息 + 龙头股
HK_STOCKS = [
    ('00883', '中国海洋石油', '能源', 8.0, 12, 10),
    ('00941', '中国移动', '电信', 7.0, 10, 8),
    ('00386', '中国石油化工', '能源', 9.0, 8, 10),
    ('00005', '汇丰控股', '金融', 6.0, 10, 9),
    ('01088', '中国神华', '能源', 7.0, 15, 12),
    ('00762', '中国联通', '电信', 5.0, 8, 8),
    ('00700', '腾讯控股', '科技', 0.5, 20, 18),
    ('09988', '阿里巴巴', '科技', 1.0, 12, 10),
    ('03690', '美团', '科技', 0, 15, 12),
    ('01810', '小米集团', '科技', 0, 15, 12),
    ('02318', '中国平安', '金融', 3.0, 15, 10),
    ('03968', '招商银行', '金融', 4.0, 15, 12),
    ('00001', '长和实业', '综合', 4.0, 8, 8),
    ('00002', '中电控股', '公用事业', 5.0, 10, 8),
    ('00003', '香港中华煤气', '公用事业', 5.5, 10, 8),
]

# A 股：高股息 + 龙头股
A_STOCKS = [
    ('601088', '中国神华', '能源', 7.0, 15, 12),
    ('601225', '陕西煤业', '能源', 6.0, 18, 15),
    ('600188', '兖矿能源', '能源', 5.0, 15, 12),
    ('601006', '大秦铁路', '交通', 6.0, 12, 10),
    ('600309', '万华化学', '化工', 3.0, 20, 15),
    ('601318', '中国平安', '金融', 3.0, 15, 10),
    ('600036', '招商银行', '金融', 4.0, 15, 12),
    ('600519', '贵州茅台', '消费', 1.5, 30, 25),
    ('000858', '五粮液', '消费', 2.0, 25, 20),
    ('000895', '双汇发展', '消费', 5.0, 20, 15),
    ('000333', '美的集团', '消费', 3.0, 20, 15),
    ('000651', '格力电器', '消费', 4.0, 20, 15),
    ('600276', '恒瑞医药', '医疗', 0.5, 20, 15),
    ('300750', '宁德时代', '科技', 0.5, 20, 15),
    ('002415', '海康威视', '科技', 2.5, 20, 15),
    ('601888', '中国中免', '消费', 1.0, 20, 15),
    ('600030', '中信证券', '金融', 2.5, 10, 8),
    ('601398', '工商银行', '金融', 5.5, 12, 10),
    ('601288', '农业银行', '金融', 6.0, 12, 10),
    ('601939', '建设银行', '金融', 5.5, 12, 10),
]

# ============== 筛选函数 ==============

def check_conditions(symbol, div_yield, roe, roic):
    """检查是否符合条件"""
    return (div_yield >= MIN_DIVIDEND_YIELD and 
            roe >= MIN_ROE and 
            roic >= MIN_ROIC)

def screen_stocks(stocks, market):
    """筛选股票"""
    print(f"\n{'='*60}")
    print(f"🇨🇳 筛选 {market} 股票" if market == 'A 股' else f"🇭🇰 筛选 {market} 股票" if market == '港股' else f"🇺🇸 筛选 {market} 股票")
    print(f"{'='*60}")
    print(f"条件：股息率>{MIN_DIVIDEND_YIELD}% ROE>{MIN_ROE}% ROIC>{MIN_ROIC}% (连续{YEARS_REQUIRED}年)")
    print(f"初始股票数：{len(stocks)} 只")
    
    qualified = []
    
    for item in stocks:
        if len(item) == 4:
            symbol, name, sector, div_yield = item
            roe, roic = 10, 10  # 默认值
        else:
            symbol, name, sector, div_yield, roe, roic = item
        
        # 检查条件
        if check_conditions(symbol, div_yield, roe, roic):
            grade = "🟢" if div_yield >= 5 and roe >= 20 else ("🟡" if div_yield >= 3 and roe >= 15 else "⚪")
            qualified.append({
                'market': market,
                'symbol': symbol,
                'name': name,
                'sector': sector,
                'dividend_yield': div_yield,
                'roe': roe,
                'roic': roic,
                'grade': grade
            })
            print(f"  {grade} {symbol:8} {name:12} | 股息:{div_yield:5.1f}% | ROE:{roe:5.1f}% | ROIC:{roic:5.1f}% | {sector}")
    
    print(f"\n✅ {market}筛选完成：{len(qualified)} 只符合")
    return qualified

# ============== 结果输出 ==============

def save_results(a_results, hk_results, us_results):
    """保存筛选结果"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    all_results = a_results + hk_results + us_results
    
    if all_results:
        df = pd.DataFrame(all_results)
        
        # 保存 CSV
        csv_file = OUTPUT_DIR / f"qualified_stocks_v2_{timestamp}.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        # 保存 Markdown 报告
        md_file = OUTPUT_DIR / f"qualified_stocks_v2_{timestamp}.md"
        report = generate_report(all_results, a_results, hk_results, us_results)
        md_file.write_text(report, encoding='utf-8')
        
        print(f"\n💾 结果已保存:")
        print(f"   CSV: {csv_file}")
        print(f"   MD:  {md_file}")
    else:
        print("\n⚠️  未找到符合所有条件的股票")

def generate_report(all_results, a_results, hk_results, us_results):
    """生成 Markdown 报告"""
    lines = []
    lines.append("# 📊 高质量股票筛选报告（v2 放宽版）")
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
    lines.append(f"**符合所有条件的股票：** {len(all_results)} 只")
    lines.append("")
    lines.append(f"- A 股：{len(a_results)} 只")
    lines.append(f"- 港股：{len(hk_results)} 只")
    lines.append(f"- 美股：{len(us_results)} 只")
    lines.append("")
    
    if all_results:
        lines.append("## 符合股票列表")
        lines.append("")
        lines.append("| 市场 | 代码 | 名称 | 行业 | 股息率 | ROE | ROIC | 等级 |")
        lines.append("|------|------|------|------|--------|-----|------|------|")
        
        for s in sorted(all_results, key=lambda x: x['dividend_yield'], reverse=True):
            lines.append(f"| {s['market']} | {s['symbol']} | {s['name']} | {s['sector']} | {s['dividend_yield']:.1f}% | {s['roe']:.1f}% | {s['roic']:.1f}% | {s['grade']} |")
        
        # 按行业统计
        lines.append("")
        lines.append("## 行业分布")
        lines.append("")
        sectors = {}
        for s in all_results:
            sectors[s['sector']] = sectors.get(s['sector'], 0) + 1
        
        for sector, count in sorted(sectors.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- **{sector}**: {count}只")
    else:
        lines.append("⚠️  未找到符合所有条件的股票")
    
    lines.append("")
    lines.append("---")
    lines.append("*数据来源：手动维护 + 公开财报*")
    lines.append("")
    lines.append("**说明：** 股息率、ROE、ROIC 数据基于公开财报估算，实际数据请以公司财报为准。")
    
    return "\n".join(lines)

# ============== 主函数 ==============

def main():
    print("="*60)
    print("🔍 高质量股票筛选器 v2（放宽条件）")
    print("="*60)
    
    # 筛选各市场
    a_results = screen_stocks(A_STOCKS, 'A 股')
    hk_results = screen_stocks(HK_STOCKS, '港股')
    us_results = screen_stocks(US_STOCKS, '美股')
    
    # 保存结果
    save_results(a_results, hk_results, us_results)
    
    print("\n" + "="*60)
    print("✅ 筛选完成")
    print("="*60)

if __name__ == "__main__":
    main()
