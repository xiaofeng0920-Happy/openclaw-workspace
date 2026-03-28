#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票池回测 - 回测最近 5 年涨幅
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

# 股票池（从 manual_stock_pool.md 提取）
STOCK_POOL = {
    'A 股': [
        ('601088', '中国神华'),
        ('601225', '陕西煤业'),
        ('600188', '兖矿能源'),
        ('601006', '大秦铁路'),
        ('000895', '双汇发展'),
        ('600309', '万华化学'),
        ('601318', '中国平安'),
        ('600036', '招商银行'),
    ],
    '港股': [
        ('00883', '中国海洋石油'),
        ('00941', '中国移动'),
        ('00386', '中国石油化工'),
        ('00005', '汇丰控股'),
        ('01088', '中国神华'),
        ('00762', '中国联通'),
    ],
    '美股': [
        ('KO', '可口可乐'),
        ('JNJ', '强生'),
        ('PG', '宝洁'),
        ('T', 'AT&T'),
        ('VZ', 'Verizon'),
        ('XOM', '埃克森美孚'),
        ('CVX', '雪佛龙'),
        ('MO', '奥驰亚'),
        ('BTI', '英美烟草'),
    ]
}

# 回测期间
START_DATE = "20210322"
END_DATE = "20260322"
YEARS = 5

OUTPUT_DIR = Path('/home/admin/openclaw/workspace/agents/data-collector/backtest')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def fetch_with_retry(func, *args, max_retries=3, delay=2, **kwargs):
    """带重试的函数调用"""
    for i in range(max_retries):
        try:
            result = func(*args, **kwargs)
            if result is not None and len(result) > 0:
                return result
        except Exception as e:
            print(f"  请求失败 ({i+1}/{max_retries}): {e}")
            if i < max_retries - 1:
                time.sleep(delay * (i + 1) + random.random())
    return None

def get_a_stock_history(symbol):
    """获取 A 股历史数据"""
    try:
        df = fetch_with_retry(ak.stock_zh_a_hist, symbol=symbol, period="daily", 
                              start_date=START_DATE, end_date=END_DATE)
        if df is not None and len(df) > 0:
            return df
    except:
        pass
    return None

def get_hk_stock_history(symbol):
    """获取港股历史数据"""
    try:
        df = fetch_with_retry(ak.stock_hk_hist, symbol=symbol, period="daily",
                              start_date=START_DATE, end_date=END_DATE)
        if df is not None and len(df) > 0:
            return df
    except:
        pass
    return None

def get_us_stock_history(symbol):
    """获取美股历史数据"""
    try:
        df = fetch_with_retry(ak.stock_us_hist, symbol=symbol, period="daily",
                              start_date=START_DATE, end_date=END_DATE)
        if df is not None and len(df) > 0:
            return df
    except:
        pass
    return None

def calc_returns(df):
    """计算收益率"""
    if df is None or len(df) < 2:
        return None
    
    # 按日期排序
    df = df.sort_values('日期')
    
    start_price = float(df.iloc[0]['收盘'])
    end_price = float(df.iloc[-1]['收盘'])
    
    total_return = ((end_price - start_price) / start_price) * 100
    annual_return = ((end_price / start_price) ** (1/YEARS) - 1) * 100
    
    # 计算最大回撤
    df['cummax'] = df['收盘'].cummax()
    df['drawdown'] = (df['收盘'] - df['cummax']) / df['cummax'] * 100
    max_drawdown = df['drawdown'].min()
    
    # 计算波动率
    daily_returns = df['收盘'].pct_change()
    volatility = daily_returns.std() * (252 ** 0.5) * 100
    
    return {
        'start_price': start_price,
        'end_price': end_price,
        'total_return': total_return,
        'annual_return': annual_return,
        'max_drawdown': max_drawdown,
        'volatility': volatility
    }

def backtest_market(market, stocks, get_history_func):
    """回测单个市场"""
    print(f"\n{'='*60}")
    print(f"回测 {market}")
    print(f"{'='*60}")
    
    results = []
    
    for i, (symbol, name) in enumerate(stocks):
        print(f"\n[{i+1}/{len(stocks)}] {symbol} {name}...", end=" ")
        
        df = get_history_func(symbol)
        if df is None:
            print("❌ 无数据")
            continue
        
        metrics = calc_returns(df)
        if metrics is None:
            print("❌ 计算失败")
            continue
        
        results.append({
            'market': market,
            'symbol': symbol,
            'name': name,
            **metrics
        })
        
        # 显示结果
        flag = "✅" if metrics['total_return'] > 0 else "❌"
        print(f"{flag} 5 年{metrics['total_return']:+.1f}% (年化{metrics['annual_return']:+.1f}%)")
        
        time.sleep(0.3)  # 避免请求过快
    
    return results

def get_benchmark_returns():
    """获取基准指数收益"""
    print(f"\n{'='*60}")
    print("获取基准指数")
    print(f"{'='*60}")
    
    benchmarks = {
        '沪深 300': ('000300', get_a_stock_history),
        '恒生指数': ('HSI', get_hk_stock_history),
        '标普 500': ('^GSPC', get_us_stock_history),
    }
    
    results = []
    for name, (symbol, func) in benchmarks.items():
        df = func(symbol)
        if df is not None:
            metrics = calc_returns(df)
            if metrics:
                results.append({
                    'market': '基准',
                    'symbol': name,
                    'name': name,
                    **metrics
                })
                print(f"{name}: 5 年{metrics['total_return']:+.1f}% (年化{metrics['annual_return']:+.1f}%)")
    
    return results

def save_results(all_results, benchmarks):
    """保存回测结果"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if all_results:
        df = pd.DataFrame(all_results)
        
        # 保存 CSV
        csv_file = OUTPUT_DIR / f"backtest_{timestamp}.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        # 保存 Markdown 报告
        md_file = OUTPUT_DIR / f"backtest_{timestamp}.md"
        report = generate_report(all_results, benchmarks)
        md_file.write_text(report, encoding='utf-8')
        
        print(f"\n💾 结果已保存:")
        print(f"   CSV: {csv_file}")
        print(f"   MD:  {md_file}")

def generate_report(all_results, benchmarks):
    """生成 Markdown 报告"""
    lines = []
    lines.append("# 📊 股票池回测报告（5 年）")
    lines.append(f"**回测期间：** {START_DATE} 至 {END_DATE}")
    lines.append(f"**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # 基准对比
    lines.append("## 基准指数表现")
    lines.append("")
    lines.append("| 指数 | 5 年涨幅 | 年化收益 | 最大回撤 |")
    lines.append("|------|---------|---------|---------|")
    for b in benchmarks:
        lines.append(f"| {b['symbol']} | {b['total_return']:+.1f}% | {b['annual_return']:+.1f}% | {b['max_drawdown']:.1f}% |")
    lines.append("")
    
    # 按市场汇总
    for market in ['A 股', '港股', '美股']:
        market_results = [r for r in all_results if r['market'] == market]
        if market_results:
            lines.append(f"## {market}")
            lines.append("")
            lines.append(f"**股票数量：** {len(market_results)} 只")
            
            # 排序
            sorted_results = sorted(market_results, key=lambda x: x['total_return'], reverse=True)
            
            lines.append("")
            lines.append("| 代码 | 名称 | 5 年涨幅 | 年化收益 | 最大回撤 | 波动率 |")
            lines.append("|------|------|---------|---------|---------|--------|")
            
            for r in sorted_results:
                flag = "🚀" if r['total_return'] > 100 else ("✅" if r['total_return'] > 0 else "❌")
                lines.append(f"| {r['symbol']} | {r['name']} | {r['total_return']:+.1f}% | {r['annual_return']:+.1f}% | {r['max_drawdown']:.1f}% | {r['volatility']:.1f}% | {flag}")
            
            # 统计
            avg_return = sum(r['total_return'] for r in market_results) / len(market_results)
            winners = sum(1 for r in market_results if r['total_return'] > 0)
            lines.append("")
            lines.append(f"**平均收益：** {avg_return:+.1f}%")
            lines.append(f"**正收益比例：** {winners}/{len(market_results)} ({winners/len(market_results)*100:.0f}%)")
            lines.append("")
    
    # TOP 10
    lines.append("## 🏆 TOP 10 最佳表现")
    lines.append("")
    top10 = sorted(all_results, key=lambda x: x['total_return'], reverse=True)[:10]
    lines.append("| 排名 | 代码 | 名称 | 市场 | 5 年涨幅 | 年化收益 |")
    lines.append("|------|------|------|------|---------|---------|")
    for i, r in enumerate(top10, 1):
        lines.append(f"| {i} | {r['symbol']} | {r['name']} | {r['market']} | {r['total_return']:+.1f}% | {r['annual_return']:+.1f}% |")
    lines.append("")
    
    # 总结
    lines.append("## 📈 总结")
    lines.append("")
    total_avg = sum(r['total_return'] for r in all_results) / len(all_results)
    lines.append(f"- **股票池平均收益：** {total_avg:+.1f}%")
    lines.append(f"- **年化平均收益：** {(total_avg/YEARS):.1f}%")
    lines.append(f"- **最佳股票：** {top10[0]['name']} ({top10[0]['total_return']:+.1f}%)")
    lines.append(f"- **正收益股票：** {sum(1 for r in all_results if r['total_return']>0)}/{len(all_results)}")
    
    return "\n".join(lines)

def main():
    print("="*60)
    print("📊 股票池回测（5 年）")
    print("="*60)
    print(f"回测期间：{START_DATE} 至 {END_DATE}")
    print(f"股票池：{sum(len(v) for v in STOCK_POOL.values())} 只")
    print("="*60)
    
    all_results = []
    
    # 回测各市场
    a_results = backtest_market('A 股', STOCK_POOL['A 股'], get_a_stock_history)
    hk_results = backtest_market('港股', STOCK_POOL['港股'], get_hk_stock_history)
    us_results = backtest_market('美股', STOCK_POOL['美股'], get_us_stock_history)
    
    all_results = a_results + hk_results + us_results
    
    # 获取基准
    benchmarks = get_benchmark_returns()
    
    # 保存结果
    save_results(all_results, benchmarks)
    
    print("\n" + "="*60)
    print("✅ 回测完成")
    print("="*60)

if __name__ == "__main__":
    main()
