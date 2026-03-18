#!/usr/bin/env python3
"""
锋哥持仓分析 Agent 团队 - 主执行脚本

运行完整流程：
1. 数据收集 → 2. 持仓分析 → 3. 策略建议 → 4. 报告生成 → 5. 消息推送

用法：
    python scripts/run_portfolio_agent.py [--manual]
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 工作空间根目录
WORKSPACE = Path('/home/admin/openclaw/workspace')
DATA_DIR = WORKSPACE / 'data'
REPORTS_DIR = WORKSPACE / 'reports'
LOGS_DIR = WORKSPACE / 'logs'
CONFIG_FILE = WORKSPACE / 'config' / 'dispatch_config.json'
HOLDINGS_FILE = WORKSPACE / 'memory' / '锋哥持仓_2026-03-16.md'

# 确保目录存在
for d in [DATA_DIR, REPORTS_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def log(message, level='INFO'):
    """日志输出"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [{level}] {message}")


def get_timestamp():
    """获取时间戳字符串"""
    return datetime.now().strftime('%Y-%m-%d_%H-%M')


# ==================== 1. 数据收集员 ====================

def collect_market_data():
    """
    数据收集员：获取市场数据
    
    实际实现需要调用 finance-data 技能或 akshare
    这里用模拟数据演示流程
    """
    log("📡 数据收集员开始工作...")
    
    # TODO: 实际实现需要调用 finance-data 技能查询真实股价
    # 这里用模拟数据
    market_data = {
        "timestamp": datetime.now().isoformat(),
        "dataSource": "simulation",
        "stocks": {
            "US": [
                {"code": "GOOGL", "price": 302.28, "change": -0.03, "changePercent": -0.01},
                {"code": "BRK.B", "price": 490.03, "change": 2.5, "changePercent": 0.51},
                {"code": "KO", "price": 77.34, "change": 0.5, "changePercent": 0.65},
                {"code": "ORCL", "price": 155.11, "change": -1.2, "changePercent": -0.77},
                {"code": "MSFT", "price": 395.55, "change": -8.5, "changePercent": -2.10},
                {"code": "NVDA", "price": 180.25, "change": -2.3, "changePercent": -1.26},
                {"code": "AAPL", "price": 250.12, "change": -3.1, "changePercent": -1.22},
                {"code": "TSLA", "price": 391.20, "change": -5.0, "changePercent": -1.26}
            ],
            "HK": [
                {"code": "00700", "price": 547.50, "change": -5.2, "changePercent": -0.94},
                {"code": "03153", "price": 107.10, "change": -1.3, "changePercent": -1.20},
                {"code": "00883", "price": 29.76, "change": 0.8, "changePercent": 2.76},
                {"code": "09988", "price": 132.50, "change": -1.5, "changePercent": -1.12},
                {"code": "07709", "price": 26.40, "change": 0.3, "changePercent": 1.15}
            ]
        },
        "indices": {
            "SPX": {"value": 5200, "change": 0.5},
            "HSI": {"value": 18500, "change": -1.2},
            "NDX": {"value": 18200, "change": 0.3}
        },
        "news": [
            {"title": "美联储暗示利率政策不变", "source": "彭博", "time": "08:30"},
            {"title": "腾讯发布新 AI 产品", "source": "路透", "time": "09:15"},
            {"title": "油价继续上涨突破$85", "source": "CNBC", "time": "09:30"}
        ],
        "marketStatus": {
            "US": "closed",
            "HK": "open",
            "nextOpen": "2026-03-18T09:30:00-04:00"
        }
    }
    
    # 保存数据
    output_file = DATA_DIR / f"market_data_{get_timestamp()}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(market_data, f, indent=2, ensure_ascii=False)
    
    log(f"✅ 市场数据已保存：{output_file}")
    return str(output_file)


# ==================== 2. 持仓分析师 ====================

def parse_holdings():
    """解析持仓文件"""
    # TODO: 实际实现需要解析 Markdown 表格
    # 这里用硬编码数据
    holdings = [
        # 美股
        {"code": "GOOGL", "name": "谷歌-A", "quantity": 583, "cost": 302.37, "type": "stock"},
        {"code": "BRK.B", "name": "伯克希尔-B", "quantity": 207, "cost": 440.26, "type": "stock"},
        {"code": "KO", "name": "可口可乐", "quantity": 1589, "cost": 72.77, "type": "stock"},
        {"code": "ORCL", "name": "甲骨文", "quantity": 647, "cost": 168.89, "type": "stock"},
        {"code": "MSFT", "name": "微软", "quantity": 156, "cost": 459.08, "type": "stock"},
        {"code": "NVDA", "name": "英伟达", "quantity": 287, "cost": 187.16, "type": "stock"},
        {"code": "AAPL", "name": "苹果", "quantity": 191, "cost": 264.86, "type": "stock"},
        {"code": "TSLA", "name": "特斯拉", "quantity": 178, "cost": 428.90, "type": "stock"},
        # 港股
        {"code": "00700", "name": "腾讯控股", "quantity": 2500, "cost": 585.78, "type": "stock"},
        {"code": "03153", "name": "南方日经 225", "quantity": 12330, "cost": 119.50, "type": "stock"},
        {"code": "00883", "name": "中国海洋石油", "quantity": 11000, "cost": 20.75, "type": "stock"},
        {"code": "09988", "name": "阿里巴巴-W", "quantity": 5800, "cost": 143.27, "type": "stock"},
        {"code": "07709", "name": "南方两倍做多", "quantity": 27500, "cost": 24.08, "type": "stock"},
    ]
    return holdings


def analyze_portfolio(market_data_file):
    """
    持仓分析师：分析盈亏
    
    实际实现需要：
    1. 读取市场数据
    2. 读取持仓文件
    3. 计算盈亏
    """
    log("📊 持仓分析师开始工作...")
    
    # 读取市场数据
    with open(market_data_file, 'r', encoding='utf-8') as f:
        market_data = json.load(f)
    
    # 解析持仓
    holdings = parse_holdings()
    
    # 计算盈亏
    results = {
        'stocks': [],
        'summary': {
            'totalValue': 0,
            'totalCost': 0,
            'totalGain': 0,
            'dayChange': 0
        }
    }
    
    for holding in holdings:
        code = holding['code']
        cost = holding['cost']
        quantity = holding['quantity']
        
        # 查找当前股价
        current_price = None
        day_change = 0
        for stock in market_data['stocks']['US'] + market_data['stocks']['HK']:
            if stock['code'] == code:
                current_price = stock['price']
                day_change = stock.get('changePercent', 0)
                break
        
        if current_price is None:
            log(f"⚠️ 未找到股价：{code}", 'WARN')
            continue
        
        # 计算盈亏
        market_value = current_price * quantity
        cost_value = cost * quantity
        gain = market_value - cost_value
        gain_percent = (gain / cost_value) * 100 if cost_value > 0 else 0
        
        results['stocks'].append({
            'code': code,
            'name': holding['name'],
            'quantity': quantity,
            'cost': cost,
            'current': current_price,
            'marketValue': market_value,
            'costValue': cost_value,
            'gain': gain,
            'gainPercent': gain_percent,
            'dayChange': day_change
        })
        
        # 累计
        results['summary']['totalValue'] += market_value
        results['summary']['totalCost'] += cost_value
        results['summary']['totalGain'] += gain
        results['summary']['dayChange'] += market_value * day_change / 100
    
    results['summary']['totalGainPercent'] = (
        results['summary']['totalGain'] / results['summary']['totalCost'] * 100
        if results['summary']['totalCost'] > 0 else 0
    )
    results['summary']['dayChangePercent'] = (
        results['summary']['dayChange'] / results['summary']['totalValue'] * 100
        if results['summary']['totalValue'] > 0 else 0
    )
    
    # 识别 TOP3 涨跌
    sorted_stocks = sorted(results['stocks'], key=lambda x: x['gainPercent'], reverse=True)
    results['topGainers'] = sorted_stocks[:3]
    results['topLosers'] = sorted_stocks[-3:]
    
    # 生成警报
    results['alerts'] = []
    for stock in results['stocks']:
        if stock['gainPercent'] < -10:
            results['alerts'].append({
                'level': '🟡',
                'type': '大幅亏损',
                'message': f"{stock['name']} 亏损 {stock['gainPercent']:.1f}%，建议关注"
            })
        elif stock['gainPercent'] > 40:
            results['alerts'].append({
                'level': '🟢',
                'type': '大幅盈利',
                'message': f"{stock['name']} 盈利 {stock['gainPercent']:.1f}%，考虑止盈"
            })
    
    # 保存分析结果
    output_file = DATA_DIR / f"analysis_{get_timestamp()}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    log(f"✅ 分析完成：{output_file}")
    return str(output_file)


# ==================== 3. 策略顾问 ====================

def generate_strategy(analysis_file):
    """
    策略顾问：生成操作建议
    """
    log("🧠 策略顾问开始工作...")
    
    # 读取分析数据
    with open(analysis_file, 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    # 生成建议
    recommendations = []
    
    for stock in analysis['stocks']:
        gain_percent = stock['gainPercent']
        
        if gain_percent > 40:
            recommendations.append({
                'priority': '🟢',
                'action': '止盈',
                'target': stock['name'],
                'code': stock['code'],
                'type': 'stock',
                'currentGain': stock['gain'],
                'gainPercent': gain_percent,
                'reason': f"盈利 {gain_percent:.1f}%，建议部分止盈",
                'suggestion': "止盈 30-50%",
                'confidence': 'medium'
            })
        elif gain_percent < -10:
            recommendations.append({
                'priority': '🟡',
                'action': '减仓',
                'target': stock['name'],
                'code': stock['code'],
                'type': 'stock',
                'currentLoss': stock['gain'],
                'lossPercent': gain_percent,
                'reason': f"亏损 {gain_percent:.1f}%，考虑换股",
                'suggestion': "减持 50%，换到强势股",
                'confidence': 'medium'
            })
        else:
            recommendations.append({
                'priority': '🔵',
                'action': '持有',
                'target': stock['name'],
                'code': stock['code'],
                'type': 'stock',
                'currentGain': stock['gain'],
                'gainPercent': gain_percent,
                'reason': "走势正常",
                'suggestion': "继续持有",
                'confidence': 'high'
            })
    
    # 按优先级排序
    priority_order = {'🔴': 0, '🟡': 1, '🟢': 2, '🔵': 3}
    recommendations.sort(key=lambda x: priority_order.get(x['priority'], 4))
    
    # 组合策略
    strategy = {
        'recommendations': recommendations,
        'portfolioStrategy': {
            'assetAllocation': {
                'current': {'US_stocks': 60, 'HK_stocks': 23, 'options': 10, 'cash': 7},
                'recommended': {'US_stocks': 55, 'HK_stocks': 20, 'options': 5, 'cash': 20}
            },
            'riskLevel': 'medium-high',
            'suggestions': [
                '降低期权仓位至 5% 以下',
                '增加现金/债券配置到 20%',
                '考虑增加防御性股票比例'
            ]
        },
        'marketOutlook': {
            'shortTerm': '震荡',
            'mediumTerm': '谨慎乐观',
            'keyRisks': ['美联储利率政策', '地缘政治风险', '科技股估值压力'],
            'keyOpportunities': ['能源股延续涨势', '价值股轮动', '港股估值修复']
        }
    }
    
    # 保存策略
    output_file = DATA_DIR / f"strategy_{get_timestamp()}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(strategy, f, indent=2, ensure_ascii=False)
    
    log(f"✅ 策略完成：{output_file}")
    return str(output_file)


# ==================== 4. 报告撰写员 ====================

def generate_report(analysis_file, strategy_file):
    """
    报告撰写员：生成 Markdown 报告
    """
    log("✍️ 报告撰写员开始工作...")
    
    # 读取数据
    with open(analysis_file, 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    with open(strategy_file, 'r', encoding='utf-8') as f:
        strategy = json.load(f)
    
    summary = analysis['summary']
    
    # 生成报告
    report = f"""# 📊 锋哥持仓日报

**报告时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 📈 总览

| 指标 | 数值 | 变化 |
|------|------|------|
| 总资产 | ${summary['totalValue']:,.0f} | +${summary['dayChange']:,.0f} ({summary['dayChangePercent']:+.2f}%) |
| 总盈亏 | +${summary['totalGain']:,.0f} | {summary['totalGainPercent']:+.1f}% |

---

## 🏆 今日亮点

### 涨得最好的 TOP3
"""
    
    for i, stock in enumerate(analysis['topGainers'][:3], 1):
        report += f"\n{i}. **{stock['name']} ({stock['code']})** {stock['gainPercent']:+.1f}%"
    
    report += "\n\n### 跌得最多的 TOP3\n"
    for i, stock in enumerate(analysis['topLosers'][:3], 1):
        report += f"\n{i}. **{stock['name']} ({stock['code']})** {stock['gainPercent']:+.1f}%"
    
    report += "\n\n---\n\n## ⚠️ 风险提醒\n"
    for alert in analysis.get('alerts', []):
        report += f"\n{alert['level']} **{alert['type']}**: {alert['message']}"
    
    report += "\n\n---\n\n## 💡 操作建议\n"
    for rec in strategy['recommendations'][:7]:
        report += f"\n### {rec['priority']} {rec['action']} - {rec['target']}"
        report += f"\n- 理由：{rec['reason']}"
        report += f"\n- 建议：{rec['suggestion']}"
    
    report += f"""

---

## 🎯 组合策略建议

**当前配置：**
- 美股 {strategy['portfolioStrategy']['assetAllocation']['current']['US_stocks']}%
- 港股 {strategy['portfolioStrategy']['assetAllocation']['current']['HK_stocks']}%
- 期权 {strategy['portfolioStrategy']['assetAllocation']['current']['options']}%
- 现金 {strategy['portfolioStrategy']['assetAllocation']['current']['cash']}%

**建议配置：**
- 美股 {strategy['portfolioStrategy']['assetAllocation']['recommended']['US_stocks']}%
- 港股 {strategy['portfolioStrategy']['assetAllocation']['recommended']['HK_stocks']}%
- 期权 {strategy['portfolioStrategy']['assetAllocation']['recommended']['options']}%
- 现金 {strategy['portfolioStrategy']['assetAllocation']['recommended']['cash']}%

---

> ⚠️ 以上建议仅供参考，不构成投资建议。投资有风险，决策需谨慎。

*报告由 OpenClaw 炒股 Agent 团队自动生成*
"""
    
    # 保存报告
    output_file = REPORTS_DIR / f"持仓日报_{get_timestamp()}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    log(f"✅ 报告完成：{output_file}")
    return str(output_file)


# ==================== 5. 消息推送员 ====================

def dispatch_report(report_file):
    """
    消息推送员：发送报告
    """
    log("📬 消息推送员开始工作...")
    
    # 读取报告
    with open(report_file, 'r', encoding='utf-8') as f:
        report_content = f.read()
    
    # 读取配置
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 模拟发送（实际需要通过 message 工具）
    log(f"📤 准备发送到飞书：{config['channels']['feishu']['target']}")
    log(f"📄 报告长度：{len(report_content)} 字符")
    
    # TODO: 实际实现需要调用 message 工具
    # message(action="send", channel="feishu", target=..., message=report_content)
    
    # 保存发送记录
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'reportFile': str(report_file),
        'channel': 'feishu',
        'target': config['channels']['feishu']['target'],
        'status': 'simulated',  # 实际应为 'success' 或 'error'
        'messageLength': len(report_content)
    }
    
    log_file = LOGS_DIR / f"dispatch_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    log(f"✅ 发送记录已保存：{log_file}")
    
    return log_entry


# ==================== 主流程 ====================

def run_full_pipeline():
    """运行完整流程"""
    log("=" * 50)
    log("🚀 锋哥持仓分析 Agent 团队启动")
    log("=" * 50)
    
    try:
        # 1. 数据收集
        market_data_file = collect_market_data()
        
        # 2. 持仓分析
        analysis_file = analyze_portfolio(market_data_file)
        
        # 3. 策略建议
        strategy_file = generate_strategy(analysis_file)
        
        # 4. 报告生成
        report_file = generate_report(analysis_file, strategy_file)
        
        # 5. 消息推送
        dispatch_result = dispatch_report(report_file)
        
        log("=" * 50)
        log("✅ 全部流程完成！")
        log(f"📄 报告文件：{report_file}")
        log("=" * 50)
        
        return True
        
    except Exception as e:
        log(f"❌ 流程失败：{e}", 'ERROR')
        import traceback
        log(traceback.format_exc(), 'ERROR')
        return False


if __name__ == "__main__":
    success = run_full_pipeline()
    sys.exit(0 if success else 1)
