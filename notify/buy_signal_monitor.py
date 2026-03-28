#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
巴菲特买入信号监控
==================

在交易日实时监控买入信号，触发时发送飞书提醒。

买入条件:
1. 安全边际 ≥ 30% (巴菲特核心指标)
2. 巴菲特评分 ≥ 80 (优秀公司)
3. 股价跌破预警价
4. RSI 超卖 (< 30)
5. 股价低于内在价值 70%

触发时自动发送飞书通知。

使用方法:
    python3 notify/buy_signal_monitor.py --check
"""

import sys
sys.path.insert(0, '/home/admin/openclaw/workspace')

from typing import List, Dict, Optional
from datetime import datetime
import json
import os
import pandas as pd

from futu import *
from data.futu_data import FutuDataAPI
from strategies.buffett_strategy import BuffettStrategy


class BuySignalConfig:
    """买入信号配置"""
    
    # 核心持仓监控列表（基础）
    CORE_WATCHLIST = [
        {
            'code': 'HK.00700',
            'name': '腾讯控股',
            'target_price': 450.00,
            'current_cost': 585.78,
        },
        {
            'code': 'HK.00883',
            'name': '中国海洋石油',
            'target_price': 25.00,
            'current_cost': 20.75,
        },
        {
            'code': 'HK.09988',
            'name': '阿里巴巴-W',
            'target_price': 100.00,
            'current_cost': 143.27,
        },
    ]
    
    # 巴菲特筛选股票池（动态加载）
    BUFFETT_WATCHLIST_FILE = '/home/admin/openclaw/workspace/data/qualified_stocks.csv'
    
    def get_full_watchlist(self) -> List[Dict]:
        """获取完整监控列表"""
        watchlist = list(self.CORE_WATCHLIST)
        
        # 加载筛选结果
        try:
            import pandas as pd
            if os.path.exists(self.BUFFETT_WATCHLIST_FILE):
                df = pd.read_csv(self.BUFFETT_WATCHLIST_FILE)
                
                for _, row in df.head(20).iterrows():  # 最多 20 只
                    code = row['code']
                    # 跳过已在核心列表的股票
                    if not any(c['code'] == code for c in self.CORE_WATCHLIST):
                        watchlist.append({
                            'code': code,
                            'name': row['name'],
                            'target_price': float(row.get('target_price', 0)) or float(row.get('market_cap', 0)) * 0.8,  # 估算
                            'current_cost': 0,
                        })
        except Exception as e:
            pass
        
        return watchlist
    
    # 买入阈值
    BUY_MARGIN_THRESHOLD = 30.0  # 安全边际≥30%
    BUFFETT_SCORE_THRESHOLD = 80  # 巴菲特评分≥80
    RSI_OVERSOLD = 30  # RSI<30 超卖
    INTRINSIC_VALUE_DISCOUNT = 0.7  # 股价<内在价值 70%


class BuySignalMonitor:
    """
    买入信号监控器
    """
    
    def __init__(self):
        self.api = FutuDataAPI()
        self.strategy = BuffettStrategy()
        self.config = BuySignalConfig()
        self.triggered_signals = []
        
    def connect(self) -> bool:
        """连接富途 OpenD"""
        return self.api.connect()
    
    def close(self):
        """关闭连接"""
        self.api.close()
    
    def check_buy_signals(self) -> List[Dict]:
        """
        检查所有持仓股票的买入信号
        
        返回:
            触发的买入信号列表
        """
        self.triggered_signals = []
        
        # 获取完整监控列表
        watchlist = self.config.get_full_watchlist()
        
        print(f"  监控股票：{len(watchlist)} 只")
        
        for stock in watchlist:
            signal = self.analyze_stock(stock)
            if signal and signal['triggered']:
                self.triggered_signals.append(signal)
        
        return self.triggered_signals
    
    def analyze_stock(self, stock: Dict) -> Optional[Dict]:
        """
        分析单只股票的买入信号
        
        参数:
            stock: 股票配置
        
        返回:
            买入信号字典
        """
        code = stock['code']
        name = stock['name']
        target_price = stock['target_price']
        
        # 获取实时价格
        quote = self.api.get_realtime_quote(code)
        if not quote:
            return None
        
        current_price = quote['last_price']
        
        # 获取财务数据
        financials = self.api.get_financials(code)
        
        # 计算巴菲特评分和安全边际
        buffett_stock = self.strategy.analyze_stock(
            code=code,
            name=name,
            market='HK' if code.startswith('HK') else 'US',
            current_price=current_price,
            financial_data=financials
        )
        
        if not buffett_stock:
            return None
        
        # 检查买入条件
        signals = []
        
        # 条件 1: 安全边际 ≥ 30%
        if buffett_stock.margin_of_safety >= self.config.BUY_MARGIN_THRESHOLD:
            signals.append({
                'type': 'safe_margin',
                'name': '安全边际达标',
                'value': f"{buffett_stock.margin_of_safety:.1f}%",
                'threshold': f">= {self.config.BUY_MARGIN_THRESHOLD}%",
                'priority': 1
            })
        
        # 条件 2: 巴菲特评分 ≥ 80
        if buffett_stock.buffett_score >= self.config.BUFFETT_SCORE_THRESHOLD:
            signals.append({
                'type': 'buffett_score',
                'name': '巴菲特评分优秀',
                'value': f"{buffett_stock.buffett_score}/100",
                'threshold': f">= {self.config.BUFFETT_SCORE_THRESHOLD}",
                'priority': 2
            })
        
        # 条件 3: 股价跌破目标价
        if current_price <= target_price:
            discount = ((target_price - current_price) / target_price) * 100
            signals.append({
                'type': 'price_drop',
                'name': '股价跌破目标价',
                'value': f"{current_price:.2f}",
                'threshold': f"<= {target_price:.2f} (-{discount:.1f}%)",
                'priority': 1
            })
        
        # 条件 4: 股价低于内在价值 70%
        if current_price < buffett_stock.fair_value * self.config.INTRINSIC_VALUE_DISCOUNT:
            discount = ((buffett_stock.fair_value - current_price) / buffett_stock.fair_value) * 100
            signals.append({
                'type': 'undervalued',
                'name': '严重低估',
                'value': f"{current_price:.2f}",
                'threshold': f"< {buffett_stock.fair_value * self.config.INTRINSIC_VALUE_DISCOUNT:.2f}",
                'detail': f"内在价值：{buffett_stock.fair_value:.2f}, 折价：{discount:.1f}%",
                'priority': 1
            })
        
        # 条件 5: RSI 超卖（简化版，使用涨跌幅代替）
        if quote.get('change_pct', 0) < -5:
            signals.append({
                'type': 'oversold',
                'name': '超卖信号',
                'value': f"{quote['change_pct']:+.2f}%",
                'threshold': f"< -5%",
                'priority': 3
            })
        
        # 判断是否触发
        triggered = len(signals) > 0
        
        if triggered:
            return {
                'code': code,
                'name': name,
                'current_price': current_price,
                'target_price': target_price,
                'fair_value': buffett_stock.fair_value,
                'margin_of_safety': buffett_stock.margin_of_safety,
                'buffett_score': buffett_stock.buffett_score,
                'triggered': True,
                'signals': signals,
                'recommendation': self._get_recommendation(signals),
                'suggested_position': self._calculate_position(signals, buffett_stock),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
        return None
    
    def _get_recommendation(self, signals: List[Dict]) -> str:
        """获取投资建议"""
        priority_1_count = sum(1 for s in signals if s['priority'] == 1)
        
        if priority_1_count >= 2:
            return "🎯 强力买入"
        elif priority_1_count == 1:
            return "✅ 买入"
        else:
            return "⏸️ 观望"
    
    def _calculate_position(self, signals: List[Dict], stock) -> float:
        """计算建议仓位"""
        base_position = 0.10  # 基础仓位 10%
        
        # 安全边际加分
        if stock.margin_of_safety >= 40:
            base_position += 0.20
        elif stock.margin_of_safety >= 30:
            base_position += 0.15
        
        # 评分加分
        if stock.buffett_score >= 90:
            base_position += 0.10
        elif stock.buffett_score >= 80:
            base_position += 0.05
        
        return min(0.40, base_position)  # 最高 40%
    
    def send_feishu_alert(self, signals: List[Dict]):
        """发送飞书提醒"""
        if not signals:
            return
        
        try:
            from message import message as msg_tool
            
            message = self._build_alert_message(signals)
            
            # 发送到飞书
            msg_tool.send(
                channel='feishu',
                target='ou_52fa8f508e88e1efbcbe50c014ecaa6e',
                message=message
            )
            
            print(f"✅ 飞书提醒已发送 ({len(signals)} 个买入信号)")
            
        except Exception as e:
            print(f"⚠️ 发送飞书失败：{e}")
            # 打印消息内容
            print(self._build_alert_message(signals))
    
    def _build_alert_message(self, signals: List[Dict]) -> str:
        """构建提醒消息"""
        lines = []
        lines.append("🎯 **巴菲特买入信号提醒**")
        lines.append(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"触发信号：{len(signals)} 个")
        lines.append("")
        
        for signal in signals:
            rec_emoji = {
                '🎯 强力买入': '🎯',
                '✅ 买入': '✅',
                '⏸️ 观望': '⏸️'
            }.get(signal['recommendation'], '📊')
            
            lines.append(f"{'='*50}")
            lines.append(f"{rec_emoji} **{signal['name']} ({signal['code']})**")
            lines.append(f"{'='*50}")
            lines.append(f"📈 当前价格：{signal['current_price']:.2f}")
            lines.append(f"💰 内在价值：{signal['fair_value']:.2f}")
            lines.append(f"📊 安全边际：{signal['margin_of_safety']:+.1f}%")
            lines.append(f"⭐ 巴菲特评分：{signal['buffett_score']}/100")
            lines.append(f"💡 投资建议：{signal['recommendation']}")
            lines.append(f"💵 建议仓位：{signal['suggested_position']*100:.0f}%")
            lines.append("")
            
            lines.append("**触发条件:**")
            for s in signal['signals']:
                lines.append(f"✅ {s['name']}: {s['value']} ({s['threshold']})")
            
            lines.append("")
        
        lines.append("="*50)
        lines.append("⚠️ 投资有风险，决策需谨慎")
        lines.append("💡 建议分批建仓，不要一次性买入")
        
        return "\n".join(lines)
    
    def run_check(self):
        """执行一次检查"""
        print("="*60)
        print("🎯 巴菲特买入信号监控")
        print("="*60)
        print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"监控股票：{len(self.config.WATCHLIST)} 只")
        print()
        
        # 连接
        if not self.connect():
            print("❌ 无法连接 OpenD")
            return
        
        try:
            # 检查信号
            print("🔍 检查买入信号...")
            signals = self.check_buy_signals()
            
            if signals:
                print(f"\n✅ 触发 {len(signals)} 个买入信号!")
                for s in signals:
                    print(f"  - {s['name']}: {s['recommendation']}")
                
                # 发送飞书提醒
                self.send_feishu_alert(signals)
            else:
                print("\n✅ 无买入信号触发")
                print("继续观望，等待更好的买入机会")
            
        finally:
            self.close()


def demo_monitor():
    """演示监控"""
    monitor = BuySignalMonitor()
    monitor.run_check()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='巴菲特买入信号监控')
    parser.add_argument('--check', action='store_true', help='执行检查')
    parser.add_argument('--demo', action='store_true', help='运行演示')
    
    args = parser.parse_args()
    
    if args.demo:
        demo_monitor()
    elif args.check:
        monitor = BuySignalMonitor()
        monitor.run_check()
    else:
        parser.print_help()
