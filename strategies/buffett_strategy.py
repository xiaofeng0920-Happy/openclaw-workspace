# -*- coding: utf-8 -*-
"""
巴菲特价值投资选股策略
========================

基于沃伦·巴菲特的投资哲学，量化选股和交易逻辑。

核心原则：
1. 护城河 (Economic Moat) - 持续的竞争优势
2. 高 ROE - 通常 > 15%
3. 低负债 - 负债/权益 < 0.5
4. 稳定的盈利增长
5. 充沛的自由现金流
6. 估值合理 - PE < 15 或低于内在价值
7. 安全边际 - 价格低于内在价值 30% 以上
8. 长期持有 - 至少 3-5 年
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


@dataclass
class BuffettStock:
    """巴菲特选股标准的数据结构"""
    code: str
    name: str
    market: str  # HK/US/CN
    
    # 价格数据
    current_price: float
    fair_value: float  # 内在价值
    margin_of_safety: float  # 安全边际 (%)
    
    # 盈利能力
    roe: float  # 净资产收益率 (%)
    roe_5y_avg: float  # 5 年平均 ROE
    gross_margin: float  # 毛利率 (%)
    net_margin: float  # 净利率 (%)
    
    # 增长能力
    revenue_growth: float  # 营收增长率 (%)
    earnings_growth: float  # 盈利增长率 (%)
    earnings_growth_5y: float  # 5 年平均盈利增长
    
    # 财务健康
    debt_to_equity: float  # 负债/权益
    current_ratio: float  # 流动比率
    free_cash_flow: float  # 自由现金流 (百万)
    fcf_yield: float  # 自由现金流收益率 (%)
    
    # 估值指标
    pe_ratio: float  # 市盈率
    pb_ratio: float  # 市净率
    peg_ratio: float  # PEG 比率
    
    # 护城河评分 (1-10)
    moat_score: int
    
    # 综合评分 (1-100) - 可选，后续计算
    buffett_score: int = 0
    
    # 投资建议 - 可选，后续计算
    recommendation: str = "HOLD"  # STRONG_BUY / BUY / HOLD / SELL
    
    # 置信度 (0-1) - 可选，后续计算
    confidence: float = 0.5
    
    # 持仓信息（可选）
    shares: int = 0
    cost_basis: float = 0.0
    market_value: float = 0.0
    cost_value: float = 0.0
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0


class BuffettStrategy:
    """
    巴菲特价值投资策略实现
    
    选股流程：
    1. 初步筛选 - 排除不符合基本标准的股票
    2. 财务分析 - 深度分析财务指标
    3. 护城河评估 - 量化竞争优势
    4. 估值计算 - DCF 或简化模型
    5. 安全边际计算 - 确定买入价格
    6. 综合评分 - 给出投资建议
    """
    
    # 巴菲特选股阈值
    MIN_ROE = 15.0  # 最低 ROE (%)
    MIN_ROE_5Y_AVG = 15.0  # 5 年平均 ROE 最低值
    MAX_DEBT_TO_EQUITY = 0.5  # 最高负债/权益比
    MIN_GROSS_MARGIN = 30.0  # 最低毛利率 (%)
    MIN_EARNINGS_GROWTH = 10.0  # 最低盈利增长率 (%)
    MAX_PE = 15.0  # 最高 PE
    MIN_FCF_YIELD = 4.0  # 最低自由现金流收益率 (%)
    MIN_MARGIN_OF_SAFETY = 30.0  # 最低安全边际 (%)
    
    def __init__(self):
        self.stock_pool: List[BuffettStock] = []
    
    def calculate_fair_value_dcf(
        self,
        free_cash_flow: float,
        growth_rate: float,
        discount_rate: float,
        terminal_growth: float,
        shares_outstanding: float,
        forecast_years: int = 5
    ) -> float:
        """
        使用 DCF 模型计算内在价值
        
        参数:
            free_cash_flow: 当前自由现金流 (百万)
            growth_rate: 预期增长率 (%)
            discount_rate: 折现率 (%) - 巴菲特通常用 10%
            terminal_growth: 永续增长率 (%) - 通常用 GDP 增速 2-3%
            shares_outstanding: 总股本 (百万股)
            forecast_years: 预测年数
        
        返回:
            每股内在价值
        """
        # 预测未来现金流
        future_cf = []
        for year in range(1, forecast_years + 1):
            cf = free_cash_flow * (1 + growth_rate) ** year
            discounted_cf = cf / (1 + discount_rate) ** year
            future_cf.append(discounted_cf)
        
        # 计算终值 (Terminal Value)
        final_year_cf = free_cash_flow * (1 + growth_rate) ** forecast_years
        terminal_value = final_year_cf * (1 + terminal_growth) / (discount_rate - terminal_growth)
        discounted_terminal_value = terminal_value / (1 + discount_rate) ** forecast_years
        
        # 计算企业价值
        enterprise_value = sum(future_cf) + discounted_terminal_value
        
        # 计算每股价值
        fair_value_per_share = enterprise_value / shares_outstanding
        
        return fair_value_per_share
    
    def calculate_fair_value_pe(self, earnings_per_share: float, fair_pe: float = 15.0) -> float:
        """
        使用合理 PE 法计算内在价值
        
        巴菲特认为 15 倍 PE 是合理估值
        """
        return earnings_per_share * fair_pe
    
    def calculate_margin_of_safety(self, current_price: float, fair_value: float) -> float:
        """
        计算安全边际
        
        安全边际 = (内在价值 - 当前价格) / 内在价值 * 100%
        
        巴菲特建议至少 30% 的安全边际
        """
        if fair_value <= 0:
            return 0.0
        return ((fair_value - current_price) / fair_value) * 100
    
    def calculate_moat_score(
        self,
        roe_5y_avg: float,
        gross_margin: float,
        market_share: float = 0.0,
        brand_strength: int = 5,
        switching_cost: int = 5
    ) -> int:
        """
        计算护城河评分 (1-10)
        
        考虑因素:
        - ROE 稳定性
        - 毛利率水平
        - 市场份额
        - 品牌优势
        - 转换成本
        """
        score = 0
        
        # ROE 评分 (0-3 分)
        if roe_5y_avg >= 20:
            score += 3
        elif roe_5y_avg >= 15:
            score += 2
        elif roe_5y_avg >= 10:
            score += 1
        
        # 毛利率评分 (0-3 分)
        if gross_margin >= 50:
            score += 3
        elif gross_margin >= 40:
            score += 2
        elif gross_margin >= 30:
            score += 1
        
        # 品牌优势 (0-2 分)
        score += (brand_strength - 3) / 2
        
        # 转换成本 (0-2 分)
        score += (switching_cost - 3) / 2
        
        return min(10, max(1, int(score)))
    
    def calculate_buffett_score(self, stock: BuffettStock) -> int:
        """
        计算巴菲特综合评分 (1-100)
        
        权重分配:
        - ROE: 25 分
        - 盈利增长: 20 分
        - 财务健康: 15 分
        - 护城河: 20 分
        - 估值: 20 分
        """
        score = 0
        
        # ROE 评分 (25 分)
        if stock.roe_5y_avg >= 20:
            score += 25
        elif stock.roe_5y_avg >= 15:
            score += 20
        elif stock.roe_5y_avg >= 12:
            score += 15
        elif stock.roe_5y_avg >= 10:
            score += 10
        elif stock.roe_5y_avg >= 8:
            score += 5
        
        # 盈利增长评分 (20 分)
        if stock.earnings_growth_5y >= 20:
            score += 20
        elif stock.earnings_growth_5y >= 15:
            score += 15
        elif stock.earnings_growth_5y >= 10:
            score += 10
        elif stock.earnings_growth_5y >= 5:
            score += 5
        
        # 财务健康评分 (15 分)
        if stock.debt_to_equity <= 0.3:
            score += 15
        elif stock.debt_to_equity <= 0.5:
            score += 12
        elif stock.debt_to_equity <= 0.7:
            score += 8
        elif stock.debt_to_equity <= 1.0:
            score += 4
        
        # 护城河评分 (20 分)
        score += stock.moat_score * 2
        
        # 估值评分 (20 分)
        if stock.pe_ratio <= 10:
            score += 20
        elif stock.pe_ratio <= 15:
            score += 15
        elif stock.pe_ratio <= 20:
            score += 10
        elif stock.pe_ratio <= 25:
            score += 5
        
        # 安全边际加分
        if stock.margin_of_safety >= 40:
            score += 10
        elif stock.margin_of_safety >= 30:
            score += 5
        
        return min(100, max(1, score))
    
    def get_recommendation(self, score: int, margin_of_safety: float) -> Tuple[str, float]:
        """
        根据评分和安全边际给出投资建议
        
        返回:
            (建议类型，置信度)
        """
        if score >= 80 and margin_of_safety >= 30:
            return "STRONG_BUY", 0.9
        elif score >= 70 and margin_of_safety >= 20:
            return "BUY", 0.75
        elif score >= 60:
            return "HOLD", 0.6
        elif score >= 50:
            return "HOLD", 0.5
        else:
            return "SELL", 0.7
    
    def analyze_stock(
        self,
        code: str,
        name: str,
        market: str,
        current_price: float,
        financial_data: Dict
    ) -> Optional[BuffettStock]:
        """
        分析单只股票
        
        参数:
            code: 股票代码
            name: 股票名称
            market: 市场 (HK/US/CN)
            current_price: 当前价格
            financial_data: 财务数据字典
        
        返回:
            BuffettStock 对象，如果不符合基本标准则返回 None
        """
        # 提取财务数据
        roe = financial_data.get('roe', 0)
        roe_5y_avg = financial_data.get('roe_5y_avg', roe)
        gross_margin = financial_data.get('gross_margin', 0)
        net_margin = financial_data.get('net_margin', 0)
        
        revenue_growth = financial_data.get('revenue_growth', 0)
        earnings_growth = financial_data.get('earnings_growth', 0)
        earnings_growth_5y = financial_data.get('earnings_growth_5y', earnings_growth)
        
        debt_to_equity = financial_data.get('debt_to_equity', 1)
        current_ratio = financial_data.get('current_ratio', 1)
        free_cash_flow = financial_data.get('free_cash_flow', 0)
        fcf_yield = financial_data.get('fcf_yield', 0)
        
        pe_ratio = financial_data.get('pe_ratio', 0)
        pb_ratio = financial_data.get('pb_ratio', 0)
        eps = financial_data.get('eps', 0)
        shares_outstanding = financial_data.get('shares_outstanding', 1)
        
        # 初步筛选 - 排除明显不符合标准的股票
        if roe_5y_avg < self.MIN_ROE_5Y_AVG * 0.5:  # 至少达到标准的一半
            return None
        
        if debt_to_equity > self.MAX_DEBT_TO_EQUITY * 3:  # 负债过高
            return None
        
        # 计算内在价值 (DCF 模型)
        fair_value_dcf = self.calculate_fair_value_dcf(
            free_cash_flow=free_cash_flow,
            growth_rate=earnings_growth_5y / 100,
            discount_rate=0.10,  # 10% 折现率
            terminal_growth=0.03,  # 3% 永续增长
            shares_outstanding=shares_outstanding
        )
        
        # 计算内在价值 (PE 法)
        fair_value_pe = self.calculate_fair_value_pe(eps, fair_pe=15)
        
        # 取两种方法的平均值
        fair_value = (fair_value_dcf + fair_value_pe) / 2
        
        # 计算安全边际
        margin_of_safety = self.calculate_margin_of_safety(current_price, fair_value)
        
        # 计算 PEG
        peg_ratio = pe_ratio / earnings_growth_5y if earnings_growth_5y > 0 else 999
        
        # 计算护城河评分
        moat_score = self.calculate_moat_score(
            roe_5y_avg=roe_5y_avg,
            gross_margin=gross_margin
        )
        
        # 创建股票对象
        stock = BuffettStock(
            code=code,
            name=name,
            market=market,
            current_price=current_price,
            fair_value=fair_value,
            margin_of_safety=margin_of_safety,
            roe=roe,
            roe_5y_avg=roe_5y_avg,
            gross_margin=gross_margin,
            net_margin=net_margin,
            revenue_growth=revenue_growth,
            earnings_growth=earnings_growth,
            earnings_growth_5y=earnings_growth_5y,
            debt_to_equity=debt_to_equity,
            current_ratio=current_ratio,
            free_cash_flow=free_cash_flow,
            fcf_yield=fcf_yield,
            pe_ratio=pe_ratio,
            pb_ratio=pb_ratio,
            peg_ratio=peg_ratio,
            moat_score=moat_score
        )
        
        # 计算综合评分
        stock.buffett_score = self.calculate_buffett_score(stock)
        
        # 获取投资建议
        stock.recommendation, stock.confidence = self.get_recommendation(
            stock.buffett_score,
            stock.margin_of_safety
        )
        
        return stock
    
    def screen_stocks(self, stock_list: List[BuffettStock], min_score: int = 60) -> List[BuffettStock]:
        """
        筛选股票
        
        参数:
            stock_list: 待筛选的股票列表
            min_score: 最低评分要求
        
        返回:
            符合标准的股票列表
        """
        return [
            stock for stock in stock_list
            if stock.buffett_score >= min_score
        ]
    
    def generate_report(self, stocks: List[BuffettStock]) -> str:
        """
        生成投资分析报告
        """
        if not stocks:
            return "没有符合巴菲特选股标准的股票。"
        
        # 按评分排序
        stocks_sorted = sorted(stocks, key=lambda x: x.buffett_score, reverse=True)
        
        report = []
        report.append("# 📊 巴菲特价值投资选股报告")
        report.append(f"\n**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**筛选股票数量:** {len(stocks_sorted)}")
        report.append("")
        
        # 强力推荐
        strong_buy = [s for s in stocks_sorted if s.recommendation == "STRONG_BUY"]
        if strong_buy:
            report.append("## 🎯 强力推荐 (STRONG BUY)")
            report.append("")
            for stock in strong_buy[:5]:
                report.append(self._format_stock_summary(stock))
        
        # 推荐买入
        buy = [s for s in stocks_sorted if s.recommendation == "BUY"]
        if buy:
            report.append("\n## ✅ 推荐买入 (BUY)")
            report.append("")
            for stock in buy[:5]:
                report.append(self._format_stock_summary(stock))
        
        # 详细表格
        report.append("\n## 📋 完整股票列表")
        report.append("")
        report.append("| 排名 | 代码 | 名称 | 评分 | 建议 | 现价 | 内在价值 | 安全边际 | ROE | PE |")
        report.append("|------|------|------|------|------|------|---------|---------|------|-----|")
        
        for i, stock in enumerate(stocks_sorted[:20], 1):
            report.append(
                f"| {i} | {stock.code} | {stock.name} | {stock.buffett_score} | "
                f"{self._format_recommendation(stock.recommendation)} | "
                f"{stock.current_price:.2f} | {stock.fair_value:.2f} | "
                f"{stock.margin_of_safety:+.1f}% | {stock.roe_5y_avg:.1f}% | {stock.pe_ratio:.1f} |"
            )
        
        return "\n".join(report)
    
    def _format_stock_summary(self, stock: BuffettStock) -> str:
        """格式化股票摘要"""
        return (
            f"### {stock.name} ({stock.code})\n"
            f"- **综合评分:** {stock.buffett_score}/100\n"
            f"- **投资建议:** {self._format_recommendation(stock.recommendation)} (置信度：{stock.confidence:.0%})\n"
            f"- **当前价格:** {stock.current_price:.2f} 港元\n"
            f"- **内在价值:** {stock.fair_value:.2f} 港元\n"
            f"- **安全边际:** {stock.margin_of_safety:+.1f}%\n"
            f"- **ROE (5 年平均):** {stock.roe_5y_avg:.1f}%\n"
            f"- **市盈率:** {stock.pe_ratio:.1f}\n"
            f"- **护城河评分:** {stock.moat_score}/10\n"
            f"- **自由现金流收益率:** {stock.fcf_yield:.1f}%\n"
            f"- **负债/权益:** {stock.debt_to_equity:.2f}\n"
            ""
        )
    
    def _format_recommendation(self, rec: str) -> str:
        """格式化投资建议"""
        mapping = {
            "STRONG_BUY": "🎯 强力买入",
            "BUY": "✅ 买入",
            "HOLD": "⏸️ 持有",
            "SELL": "❌ 卖出"
        }
        return mapping.get(rec, rec)


# 巴菲特名言
BUFFETT_QUOTES = [
    "价格是你付出的，价值是你得到的。",
    "以合理的价格买入优秀的公司，远胜于以优惠的价格买入平庸的公司。",
    "如果你不愿意持有一只股票 10 年，那就不要持有它 10 分钟。",
    "别人贪婪时我恐惧，别人恐惧时我贪婪。",
    "我们的 favorite holding period is forever.",
    "投资的第一条规则是不要亏钱，第二条规则是记住第一条。",
    "只有当潮水退去，你才知道谁在裸泳。",
    "我们喜欢的持有期是永远。",
]


if __name__ == "__main__":
    # 示例：分析腾讯控股
    strategy = BuffettStrategy()
    
    # 模拟财务数据（实际应从 API 或数据库获取）
    tencent_data = {
        'roe': 18.5,
        'roe_5y_avg': 20.3,
        'gross_margin': 42.5,
        'net_margin': 25.8,
        'revenue_growth': 12.5,
        'earnings_growth': 15.2,
        'earnings_growth_5y': 18.0,
        'debt_to_equity': 0.35,
        'current_ratio': 1.8,
        'free_cash_flow': 150000,  # 1500 亿
        'fcf_yield': 5.2,
        'pe_ratio': 12.5,
        'pb_ratio': 2.8,
        'eps': 40.64,
        'shares_outstanding': 9500  # 95 亿股
    }
    
    # 分析腾讯
    tencent_stock = strategy.analyze_stock(
        code='HK.00700',
        name='腾讯控股',
        market='HK',
        current_price=508.00,
        financial_data=tencent_data
    )
    
    if tencent_stock:
        print(strategy.generate_report([tencent_stock]))
    else:
        print("腾讯不符合基本筛选标准")
