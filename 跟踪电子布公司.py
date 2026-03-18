#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电子布五公司跟踪脚本
每日收盘后自动更新股价和公告信息
"""

import json
import csv
from datetime import datetime, timedelta
import os

# 跟踪股票池
STOCKS = [
    {"code": "603256", "name": "宏和科技", "sector": "沪市主板"},
    {"code": "002080", "name": "中材科技", "sector": "深市主板"},
    {"code": "301526", "name": "国际复材", "sector": "创业板"},
    {"code": "600176", "name": "中国巨石", "sector": "沪市主板"},
    {"code": "300395", "name": "菲利华", "sector": "创业板"},
]

# 预警价格
ALERT_PRICES = {
    "603256": {"buy": 7.5, "sell": 10, "stop": 7},
    "002080": {"buy": 13, "sell": 18, "stop": 12},
    "301526": {"buy": 5, "sell": 7.5, "stop": 4.5},
    "600176": {"buy": 9.5, "sell": 13, "stop": 9},
    "300395": {"buy": 35, "sell": 45, "stop": 32},
}

WORKSPACE = "/home/admin/openclaw/workspace"

def fetch_stock_data():
    """获取股票数据（模拟，实际使用时替换为真实 API）"""
    data = []
    for stock in STOCKS:
        code = stock["code"]
        # TODO: 替换为真实 API 调用
        # 新浪财经接口：http://hq.sinajs.cn/list=sh603256
        data.append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "code": code,
            "name": stock["name"],
            "close": 0,  # 待更新
            "change": 0,
            "volume": 0,
            "turnover": 0,
            "pe": 0,
            "pb": 0,
            "market_cap": 0,
        })
    return data

def check_alerts(price_data):
    """检查价格预警"""
    alerts = []
    for item in price_data:
        code = item["code"]
        price = item["close"]
        if code in ALERT_PRICES and price > 0:
            alert = ALERT_PRICES[code]
            if price <= alert["buy"]:
                alerts.append(f"🟢 {item['name']} 触及买入预警价 {alert['buy']} 元，当前 {price} 元")
            if price >= alert["sell"]:
                alerts.append(f"🔴 {item['name']} 触及卖出预警价 {alert['sell']} 元，当前 {price} 元")
            if price <= alert["stop"]:
                alerts.append(f"⚠️ {item['name']} 触及止损价 {alert['stop']} 元，当前 {price} 元")
    return alerts

def update_tracking_log(data, alerts):
    """更新跟踪日志"""
    log_path = os.path.join(WORKSPACE, "电子布公司跟踪日志.md")
    
    with open(log_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 添加今日数据
    today = datetime.now().strftime("%Y 年 %m 月 %d 日（%A）")
    today_section = f"\n### {today}\n\n"
    today_section += "| 代码 | 名称 | 收盘价 | 涨跌幅 | 成交量 | 备注 |\n"
    today_section += "|------|------|--------|--------|--------|------|\n"
    
    for item in data:
        if item["close"] > 0:
            change_str = f"+{item['change']}%" if item["change"] > 0 else f"{item['change']}%"
            today_section += f"| {item['code']} | {item['name']} | {item['close']:.2f} | {change_str} | {item['volume']} | |\n"
        else:
            today_section += f"| {item['code']} | {item['name']} | - | - | - | 待更新 |\n"
    
    if alerts:
        today_section += "\n**预警信息**：\n"
        for alert in alerts:
            today_section += f"- {alert}\n"
    
    # 插入到"股价跟踪记录"部分
    if "### 2026 年 3 月 17 日（周二）- 基准日" in content:
        content = content.replace(
            "### 2026 年 3 月 17 日（周二）- 基准日",
            today_section + "\n### 2026 年 3 月 17 日（周二）- 基准日"
        )
    
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✅ 跟踪日志已更新：{log_path}")

def save_daily_data(data):
    """保存每日数据到 CSV"""
    csv_path = os.path.join(WORKSPACE, "电子布公司股价历史.csv")
    file_exists = os.path.exists(csv_path)
    
    with open(csv_path, "a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "code", "name", "close", "change", "volume", "turnover", "pe", "pb", "market_cap"])
        if not file_exists:
            writer.writeheader()
        writer.writerows(data)
    
    print(f"📊 数据已保存到：{csv_path}")

def main():
    print("🚀 开始更新电子布公司跟踪数据...")
    print(f"⏰ 更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 获取数据
    data = fetch_stock_data()
    
    # 检查预警
    alerts = check_alerts(data)
    
    # 更新日志
    update_tracking_log(data, alerts)
    
    # 保存历史数据
    save_daily_data(data)
    
    # 输出预警
    if alerts:
        print("\n⚠️ 预警信息：")
        for alert in alerts:
            print(f"  {alert}")
    else:
        print("\n✅ 无价格预警")
    
    print("\n✅ 更新完成！")

if __name__ == "__main__":
    main()
