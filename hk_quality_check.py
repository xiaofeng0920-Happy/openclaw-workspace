#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股筛选 - 锋哥五好标准
直接检查已知优质港股
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 已知优质港股列表（锋哥持仓 + 常见价值股）
STOCKS_TO_CHECK = [
    '00700',  # 腾讯控股
    '00883',  # 中国海洋石油
    '02318',  # 中国平安
    '00941',  # 中国移动
    '00005',  # 汇丰控股
    '00388',  # 香港交易所
    '00001',  # 长和
    '00002',  # 中电控股
    '00003',  # 香港中华煤气
    '00006',  # 电能实业
    '00011',  # 恒生银行
    '00012',  # 恒基地产
    '00016',  # 新鸿基地产
    '00017',  # 新世界发展
    '00027',  # 银河娱乐
    '00066',  # 港铁公司
    '00101',  # 恒隆地产
    '00144',  # 招商局港口
    '00267',  # 中信股份
    '00288',  # 万洲国际
    '00386',  # 中国石油化工
    '00489',  # 东风集团
    '00688',  # 中国海外发展
    '00728',  # 中国电信
    '00762',  # 中国联通
    '00823',  # 领展房产
    '00857',  # 中国石油
    '00883',  # 中海油
    '00914',  # 海螺水泥
    '00939',  # 建设银行
    '00941',  # 中国移动
    '00992',  # 联想集团
    '01038',  # 长江基建
    '01044',  # 恒安国际
    '01088',  # 中国神华
    '01109',  # 华润置地
    '01113',  # 长实集团
    '01177',  # 中国生物制药
    '01211',  # 比亚迪股份
    '01299',  # 友邦保险
    '01398',  # 工商银行
    '01928',  # 金沙中国
    '01997',  # 九龙仓置业
    '02007',  # 碧桂园
    '02020',  # 安踏体育
    '02319',  # 蒙牛乳业
    '02328',  # 中国财险
    '02382',  # 舜宇光学
    '02628',  # 中国人寿
    '02688',  # 新奥能源
    '03328',  # 交通银行
    '03968',  # 招商银行
    '03988',  # 中国银行
]

def get_financials(symbol):
    """获取财务数据"""
    try:
        df = ak.stock_financial_hk_analysis_indicator_em(symbol=symbol)
        if df is not None and not df.empty:
            df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'])
            return df
    except:
        pass
    return None

def get_price(symbol):
    """获取股价"""
    try:
        df = ak.stock_hk_spot_em()
        stock = df[df['代码'] == symbol]
        if not stock.empty:
            return float(stock['最新价'].iloc[0])
    except:
        pass
    return None

def check_stock(symbol):
    """检查股票"""
    df = get_financials(symbol)
    if df is None or df.empty:
        return None, "无数据"
    
    price = get_price(symbol)
    if price is None:
        return None, "无股价"
    
    # 获取最新 EPS
    latest = df.sort_values('REPORT_DATE', ascending=False).iloc[0]
    eps = latest.get('EPS_TTM')
    if pd.isna(eps) or eps <= 0:
        return None, f"EPS={eps}"
    
    # 计算 PE
    pe = price / eps
    if pe >= 30:
        return None, f"PE={pe:.0f}"
    
    # 获取 5 年数据
    current_year = datetime.now().year
    years_data = {}
    for year in range(current_year - 5, current_year):
        ydf = df[df['REPORT_DATE'].dt.year == year]
        if not ydf.empty:
            years_data[year] = ydf.sort_values('REPORT_DATE', ascending=False).iloc[0]
    
    if len(years_data) < 5:
        return None, f"数据{len(years_data)}/5"
    
    # 检查 ROE
    roe_vals = []
    for y in sorted(years_data.keys()):
        roe = years_data[y].get('ROE_YEARLY')
        if not pd.isna(roe):
            roe_vals.append(roe)
            if roe <= 5:
                return None, f"ROE={roe:.0f}%"
    if len(roe_vals) < 5:
        return None, "ROE 不足"
    
    # 检查 ROIC
    roic_vals = []
    for y in sorted(years_data.keys()):
        roic = years_data[y].get('ROIC_YEARLY')
        if not pd.isna(roic):
            roic_vals.append(roic)
            if roic <= 5:
                return None, f"ROIC={roic:.0f}%"
    if len(roic_vals) < 5:
        return None, "ROIC 不足"
    
    # 检查负债率
    debt = years_data[sorted(years_data.keys())[-1]].get('DEBT_ASSET_RATIO')
    if pd.isna(debt) or debt >= 50:
        return None, f"负债={debt:.0f}%"
    
    # 检查现金流
    fcf_ok = True
    for y in sorted(years_data.keys()):
        fcf = years_data[y].get('PER_NETCASH_OPERATE')
        if not pd.isna(fcf) and fcf <= 0:
            fcf_ok = False
            break
    
    if not fcf_ok:
        return None, "现金流负"
    
    return {
        '代码': symbol,
        '名称': latest.get('SECURITY_NAME_ABBR', ''),
        '股价': round(price, 2),
        'EPS': round(eps, 2),
        'PE': round(pe, 1),
        'ROE_5y': round(sum(roe_vals)/5, 1),
        'ROIC_5y': round(sum(roic_vals)/5, 1),
        '负债率': round(debt, 1)
    }, "✅"

def main():
    print("=" * 70)
    print("港股筛选 - 锋哥五好标准")
    print("=" * 70)
    
    passed = []
    failed = {}
    
    for i, sym in enumerate(STOCKS_TO_CHECK):
        print(f"[{i+1}/{len(STOCKS_TO_CHECK)}] {sym}...", end=" ")
        try:
            result, status = check_stock(sym)
            if result:
                passed.append(result)
                print(f"{status}")
            else:
                print(f"❌ {status}")
                failed[status] = failed.get(status, 0) + 1
        except Exception as e:
            print(f"⚠️ {e}")
            failed['异常'] = failed.get('异常', 0) + 1
    
    print("\n" + "=" * 70)
    print(f"检查{len(STOCKS_TO_CHECK)}只 | 符合{len(passed)}只")
    
    if passed:
        print("\n✅ 符合锋哥五好标准的港股：")
        print("-" * 70)
        df_r = pd.DataFrame(passed)
        print(df_r.to_string(index=False))
        df_r.to_csv('/home/admin/openclaw/workspace/hk_quality_stocks.csv', index=False)
        print("\n已保存到 hk_quality_stocks.csv")
    else:
        print("\n❌ 无符合股票")
    
    if failed:
        print("\n失败原因：")
        for k, v in sorted(failed.items(), key=lambda x: -x[1])[:5]:
            print(f"  {k}: {v}")
    print("=" * 70)

if __name__ == '__main__':
    main()
