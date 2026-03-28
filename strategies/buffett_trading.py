# -*- coding: utf-8 -*-
"""
巴菲特交易策略执行模块
======================

基于巴菲特投资哲学的买入/卖出决策和仓位管理。

核心交易原则：
1. 只在价格大幅低于内在价值时买入（安全边际 > 30%）
2. 分批建仓，避免一次性买入
3. 长期持有，不频繁交易
4. 只在基本面恶化或价格远高于价值时卖出
5. 集中投资，重仓最有信心的股票
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
from datetime import datetime
from enum import Enum
import math

from .buffett_strategy import BuffettStock


class Action(Enum):
    """交易动作"""
    STRONG_BUY = "强力买入"
    BUY = "买入"
    HOLD = "持有"
    REDUCE = "减持"
    SELL = "卖出"
    STRONG_SELL = "强力卖出"


@dataclass
class TradeSignal:
    """交易信号"""
    code: str
    name: str
    action: Action
    current_price: float
    fair_value: float
    target_price: Optional[float]  # 目标买入/卖出价
    position_ratio: float  # 建议仓位比例 (0-1)
    reason: str
    confidence: float  # 置信度 0-1
    priority: int  # 优先级 1-5


class BuffettTradingStrategy:
    """
    巴菲特交易策略
    
    买入规则:
    1. 安全边际 > 30% → 强力买入
    2. 安全边际 20-30% → 买入
    3. 安全边际 10-20% → 观望
    4. 安全边际 < 10% → 不买入
    
    卖出规则:
    1. 价格 > 内在价值 50% → 强力卖出
    2. 价格 > 内在价值 30% → 卖出
    3. 基本面恶化（ROE 大幅下降、负债激增）→ 减持/卖出
    4. 发现更好的投资机会 → 调仓
    
    仓位管理:
    - 单只股票最高仓位：40%
    - 强力买入股票：20-40%
    - 买入股票：10-20%
    - 持有股票：维持现有仓位
    """
    
    # 买入阈值
    STRONG_BUY_MARGIN = 30.0  # 强力买入安全边际
    BUY_MARGIN = 20.0  # 买入安全边际
    WATCH_MARGIN = 10.0  # 观望安全边际
    
    # 卖出阈值
    STRONG_SELL_PREMIUM = 50.0  # 强力卖出溢价
    SELL_PREMIUM = 30.0  # 卖出溢价
    
    # 仓位限制
    MAX_POSITION = 0.40  # 单只股票最高 40%
    MIN_POSITION = 0.05  # 单只股票最低 5%
    
    def calculate_target_buy_price(self, fair_value: float, margin: float = 30.0) -> float:
        """
        计算目标买入价
        
        目标价 = 内在价值 / (1 + 安全边际)
        """
        return fair_value / (1 + margin / 100)
    
    def calculate_target_sell_price(self, fair_value: float, premium: float = 30.0) -> float:
        """
        计算目标卖出价
        
        目标价 = 内在价值 * (1 + 溢价)
        """
        return fair_value * (1 + premium / 100)
    
    def calculate_position_ratio(self, score: int, margin_of_safety: float) -> float:
        """
        根据评分和安全边际计算建议仓位比例
        
        巴菲特原则：集中投资，重仓最有信心的股票
        """
        # 基础仓位 (根据评分)
        if score >= 90:
            base_ratio = 0.35
        elif score >= 80:
            base_ratio = 0.25
        elif score >= 70:
            base_ratio = 0.15
        elif score >= 60:
            base_ratio = 0.10
        else:
            base_ratio = 0.05
        
        # 安全边际调整
        if margin_of_safety >= 40:
            adjustment = 1.2
        elif margin_of_safety >= 30:
            adjustment = 1.1
        elif margin_of_safety >= 20:
            adjustment = 1.0
        else:
            adjustment = 0.8
        
        position = base_ratio * adjustment
        
        # 限制在合理范围内
        return min(self.MAX_POSITION, max(self.MIN_POSITION, position))
    
    def generate_signal(self, stock: BuffettStock, current_position: float = 0.0) -> TradeSignal:
        """
        生成交易信号
        
        参数:
            stock: 股票分析对象
            current_position: 当前仓位比例 (0-1)
        
        返回:
            TradeSignal 交易信号
        """
        margin = stock.margin_of_safety
        score = stock.buffett_score
        fair_value = stock.fair_value
        current_price = stock.current_price
        
        # 计算目标价格
        target_buy = self.calculate_target_buy_price(fair_value, self.STRONG_BUY_MARGIN)
        target_sell = self.calculate_target_sell_price(fair_value, self.SELL_PREMIUM)
        target_strong_sell = self.calculate_target_sell_price(fair_value, self.STRONG_SELL_PREMIUM)
        
        # 计算建议仓位
        target_position = self.calculate_position_ratio(score, margin)
        
        # 判断交易动作
        if margin >= self.STRONG_BUY_MARGIN and score >= 80:
            action = Action.STRONG_BUY
            reason = f"安全边际{margin:.1f}% > {self.STRONG_BUY_MARGIN}%, 评分{score}/100"
            confidence = 0.9
            priority = 1
        elif margin >= self.BUY_MARGIN and score >= 70:
            action = Action.BUY
            reason = f"安全边际{margin:.1f}% > {self.BUY_MARGIN}%, 评分{score}/100"
            confidence = 0.75
            priority = 2
        elif margin <= -self.STRONG_SELL_PREMIUM:
            action = Action.STRONG_SELL
            reason = f"价格高于内在价值{abs(margin):.1f}%, 严重高估"
            confidence = 0.85
            priority = 1
        elif margin <= -self.SELL_PREMIUM:
            action = Action.SELL
            reason = f"价格高于内在价值{abs(margin):.1f}%, 高估"
            confidence = 0.7
            priority = 2
        elif margin > 0 and score >= 60:
            action = Action.HOLD
            reason = f"合理估值，继续持有"
            confidence = 0.6
            priority = 3
        elif margin < 0 and margin > -self.SELL_PREMIUM:
            action = Action.HOLD
            reason = f"小幅高估，但可继续持有"
            confidence = 0.5
            priority = 3
        else:
            action = Action.REDUCE
            reason = f"估值偏高或基本面不确定"
            confidence = 0.6
            priority = 4
        
        # 如果有现有仓位，调整建议
        if current_position > 0:
            if action == Action.STRONG_BUY and current_position < target_position:
                # 加仓建议
                additional = target_position - current_position
                reason += f" | 建议加仓{additional*100:.1f}%"
            elif action == Action.SELL and current_position > 0:
                reason += f" | 当前仓位{current_position*100:.1f}%"
        
        return TradeSignal(
            code=stock.code,
            name=stock.name,
            action=action,
            current_price=current_price,
            fair_value=fair_value,
            target_price=target_buy if action in [Action.STRONG_BUY, Action.BUY] else target_sell,
            position_ratio=target_position if action in [Action.STRONG_BUY, Action.BUY] else current_position,
            reason=reason,
            confidence=confidence,
            priority=priority
        )
    
    def generate_portfolio_signals(
        self,
        stocks: List[BuffettStock],
        current_positions: Dict[str, float],
        total_capital: float
    ) -> List[TradeSignal]:
        """
        生成投资组合的交易信号
        
        参数:
            stocks: 股票分析列表
            current_positions: 当前各股票仓位比例 {code: ratio}
            total_capital: 总资金
        
        返回:
            按优先级排序的交易信号列表
        """
        signals = []
        
        for stock in stocks:
            current_pos = current_positions.get(stock.code, 0.0)
            signal = self.generate_signal(stock, current_pos)
            signals.append(signal)
        
        # 按优先级排序
        signals.sort(key=lambda x: (x.priority, -x.confidence))
        
        return signals
    
    def generate_trade_plan(
        self,
        signals: List[TradeSignal],
        available_capital: float,
        current_holdings: Dict[str, int]
    ) -> str:
        """
        生成交易计划
        
        参数:
            signals: 交易信号列表
            available_capital: 可用资金
            current_holdings: 当前持仓数量 {code: shares}
        
        返回:
            交易计划文本
        """
        lines = []
        lines.append("# 📋 巴菲特交易计划")
        lines.append(f"\n**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**可用资金:** {available_capital:,.0f} 港元\n")
        
        # 买入建议
        buy_signals = [s for s in signals if s.action in [Action.STRONG_BUY, Action.BUY]]
        if buy_signals:
            lines.append("## 🛒 买入建议\n")
            for signal in buy_signals:
                target_shares = int((available_capital * signal.position_ratio) / signal.current_price)
                estimated_cost = target_shares * signal.current_price
                
                if target_shares > 0:
                    lines.append(f"### {signal.name} ({signal.code})")
                    lines.append(f"- **动作:** {signal.action.value}")
                    lines.append(f"- **现价:** {signal.current_price:.2f} 港元")
                    lines.append(f"- **内在价值:** {signal.fair_value:.2f} 港元")
                    lines.append(f"- **安全边际:** {((signal.fair_value - signal.current_price) / signal.fair_value * 100):.1f}%")
                    lines.append(f"- **建议仓位:** {signal.position_ratio*100:.1f}%")
                    lines.append(f"- **建议买入:** {target_shares:,} 股")
                    lines.append(f"- **预计金额:** {estimated_cost:,.0f} 港元")
                    lines.append(f"- **理由:** {signal.reason}")
                    lines.append(f"- **置信度:** {signal.confidence*100:.0f}%")
                    lines.append("")
        
        # 卖出建议
        sell_signals = [s for s in signals if s.action in [Action.SELL, Action.STRONG_SELL, Action.REDUCE]]
        if sell_signals:
            lines.append("## 💰 卖出/减持建议\n")
            for signal in sell_signals:
                current_shares = current_holdings.get(signal.code, 0)
                if current_shares > 0:
                    if signal.action == Action.STRONG_SELL:
                        sell_ratio = 1.0  # 全部卖出
                    elif signal.action == Action.SELL:
                        sell_ratio = 0.5  # 卖出一半
                    else:
                        sell_ratio = 0.25  # 减持 25%
                    
                    sell_shares = int(current_shares * sell_ratio)
                    estimated_proceeds = sell_shares * signal.current_price
                    
                    lines.append(f"### {signal.name} ({signal.code})")
                    lines.append(f"- **动作:** {signal.action.value}")
                    lines.append(f"- **现价:** {signal.current_price:.2f} 港元")
                    lines.append(f"- **内在价值:** {signal.fair_value:.2f} 港元")
                    lines.append(f"- **溢价:** {((signal.current_price - signal.fair_value) / signal.fair_value * 100):.1f}%")
                    lines.append(f"- **当前持仓:** {current_shares:,} 股")
                    lines.append(f"- **建议卖出:** {sell_shares:,} 股 ({sell_ratio*100:.0f}%)")
                    lines.append(f"- **预计金额:** {estimated_proceeds:,.0f} 港元")
                    lines.append(f"- **理由:** {signal.reason}")
                    lines.append("")
        
        # 持有建议
        hold_signals = [s for s in signals if s.action == Action.HOLD]
        if hold_signals:
            lines.append("## ⏸️ 继续持有\n")
            for signal in hold_signals:
                lines.append(f"- **{signal.name} ({signal.code})**: {signal.reason}")
            lines.append("")
        
        # 风险提示
        lines.append("## ⚠️ 风险提示\n")
        lines.append("1. **分散风险**: 单只股票不超过总仓位的 40%")
        lines.append("2. **分批建仓**: 大额买入建议分 2-3 次完成")
        lines.append("3. **长期持有**: 买入后至少持有 3-5 年")
        lines.append("4. **定期复盘**: 每季度检查基本面变化")
        lines.append("5. **安全边际**: 永远不要支付超过内在价值的价格")
        
        # 巴菲特名言
        from .buffett_strategy import BUFFETT_QUOTES
        import random
        lines.append(f"\n📖 **巴菲特名言**: \"{random.choice(BUFFETT_QUOTES)}\"")
        
        return "\n".join(lines)


def demo_trading_strategy():
    """演示交易策略"""
    from .buffett_strategy import BuffettStrategy
    
    # 创建策略实例
    buffett_strategy = BuffettStrategy()
    trading_strategy = BuffettTradingStrategy()
    
    # 模拟持仓股票
    tencent = buffett_strategy.analyze_stock(
        code='HK.00700',
        name='腾讯控股',
        market='HK',
        current_price=508.00,
        financial_data={
            'roe': 18.5, 'roe_5y_avg': 20.3, 'gross_margin': 42.5,
            'net_margin': 25.8, 'revenue_growth': 12.5, 'earnings_growth': 15.2,
            'earnings_growth_5y': 18.0, 'debt_to_equity': 0.35, 'current_ratio': 1.8,
            'free_cash_flow': 150000, 'fcf_yield': 5.2, 'pe_ratio': 12.5,
            'pb_ratio': 2.8, 'eps': 40.64, 'shares_outstanding': 9500,
        }
    )
    
    cnooc = buffett_strategy.analyze_stock(
        code='HK.00883',
        name='中国海洋石油',
        market='HK',
        current_price=30.38,
        financial_data={
            'roe': 18.2, 'roe_5y_avg': 15.8, 'gross_margin': 55.3,
            'net_margin': 28.5, 'revenue_growth': 8.5, 'earnings_growth': 12.3,
            'earnings_growth_5y': 22.5, 'debt_to_equity': 0.28, 'current_ratio': 1.5,
            'free_cash_flow': 180000, 'fcf_yield': 8.5, 'pe_ratio': 8.5,
            'pb_ratio': 1.2, 'eps': 3.82, 'shares_outstanding': 44700,
        }
    )
    
    alibaba = buffett_strategy.analyze_stock(
        code='HK.09988',
        name='阿里巴巴-W',
        market='HK',
        current_price=123.70,
        financial_data={
            'roe': 12.5, 'roe_5y_avg': 14.2, 'gross_margin': 38.2,
            'net_margin': 15.3, 'revenue_growth': 8.2, 'earnings_growth': 10.5,
            'earnings_growth_5y': 12.8, 'debt_to_equity': 0.42, 'current_ratio': 1.9,
            'free_cash_flow': 120000, 'fcf_yield': 6.8, 'pe_ratio': 10.5,
            'pb_ratio': 1.5, 'eps': 8.52, 'shares_outstanding': 19500,
        }
    )
    
    stocks = [tencent, cnooc, alibaba]
    
    # 当前仓位（模拟）
    current_positions = {
        'HK.00700': 0.30,  # 腾讯 30%
        'HK.00883': 0.25,  # 中海油 25%
        'HK.09988': 0.20,  # 阿里 20%
    }
    
    # 生成交易信号
    signals = trading_strategy.generate_portfolio_signals(
        stocks=stocks,
        current_positions=current_positions,
        total_capital=1000000
    )
    
    # 生成交易计划
    trade_plan = trading_strategy.generate_trade_plan(
        signals=signals,
        available_capital=250000,  # 可用资金 25 万
        current_holdings={
            'HK.00700': 2500,
            'HK.00883': 11000,
            'HK.09988': 5800,
        }
    )
    
    print(trade_plan)


if __name__ == "__main__":
    demo_trading_strategy()
