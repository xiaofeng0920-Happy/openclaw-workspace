# buffett-investor - 巴菲特价值投资技能

"""
基于巴菲特价值投资理念的自动化投资技能
支持股票筛选、市场状态识别、动态配置、调仓 rebalance、绩效监控
"""

from .screener import StockScreener
from .market_state import MarketStateIdentifier
from .allocator import DynamicAllocator

__version__ = "1.0.0"
__author__ = "OpenClaw AgentSkill"

__all__ = [
    "StockScreener",
    "MarketStateIdentifier",
    "DynamicAllocator"
]


def create_screener(data_source: str = "tushare") -> StockScreener:
    """创建股票筛选器"""
    return StockScreener(data_source=data_source)


def create_market_identifier(index_code: str = "000300.SH") -> MarketStateIdentifier:
    """创建市场状态识别器"""
    return MarketStateIdentifier(index_code=index_code)


def create_allocator() -> DynamicAllocator:
    """创建动态配置器"""
    return DynamicAllocator()
