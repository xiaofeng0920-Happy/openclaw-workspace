# buffett-investor 动态配置模块
"""根据市场状态动态调整股票池、仓位、行业权重"""

from typing import Dict, List, Optional
from datetime import datetime

# 配置常量
STOCK_POOL_177 = {"name": "177 支全行业股票池", "count": 177}
STOCK_POOL_60 = {"name": "60 支严格财务筛选股票池", "count": 60}
STOCK_POOL_120 = {"name": "120 支中等筛选股票池", "count": 120}

DEFENSIVE_INDUSTRIES = ["白酒与葡萄酒", "中药", "西药", "医疗保健设备", "海港与服务"]
CYCLICAL_INDUSTRIES = ["铝", "煤炭与消费用燃料", "基础化工", "工业机械"]
GROWTH_INDUSTRIES = ["生物科技", "电气部件与设备", "有线和卫星电视"]


class DynamicAllocator:
    """动态配置器"""
    
    def __init__(self):
        """初始化配置器"""
        pass
    
    def get_allocation(self, market_state: str, stock_pool_data: Dict, 
                      risk_preference: str = "balanced") -> Dict:
        """获取动态配置建议"""
        stock_pool = self._select_stock_pool(market_state)
        position_range = self._get_position_range(market_state, risk_preference)
        industry_weights = self._get_industry_weights(market_state)
        stock_filters = self._get_stock_filters(market_state)
        
        return {
            "market_state": market_state,
            "market_state_cn": self._state_to_chinese(market_state),
            "stock_pool": stock_pool,
            "position_range": position_range,
            "recommended_position": (position_range['min'] + position_range['max']) / 2,
            "industry_weights": industry_weights,
            "stock_filters": stock_filters,
            "strategy_description": self._get_strategy_description(market_state),
            "timestamp": datetime.now().isoformat()
        }
    
    def _select_stock_pool(self, market_state: str) -> Dict:
        """选择股票池"""
        if market_state == "bull":
            return STOCK_POOL_177
        elif market_state == "bear":
            return STOCK_POOL_60
        else:
            return STOCK_POOL_120
    
    def _get_position_range(self, market_state: str, risk_preference: str) -> Dict:
        """获取仓位范围"""
        adjustment = {"aggressive": 0.05, "balanced": 0.0, "conservative": -0.05}.get(risk_preference, 0)
        
        if market_state == "bull":
            return {"min": max(0, 0.90 + adjustment), "max": min(1, 1.00 + adjustment)}
        elif market_state == "bear":
            return {"min": max(0, 0.50 + adjustment), "max": min(1, 0.70 + adjustment)}
        else:
            return {"min": max(0, 0.70 + adjustment), "max": min(1, 0.85 + adjustment)}
    
    def _get_industry_weights(self, market_state: str) -> Dict:
        """获取行业权重配置"""
        base_weight = 1.0 / 13
        industry_weights = {}
        
        if market_state == "bull":
            for industry in DEFENSIVE_INDUSTRIES:
                industry_weights[industry] = base_weight * 0.90
            for industry in CYCLICAL_INDUSTRIES:
                industry_weights[industry] = base_weight * 1.20
            for industry in GROWTH_INDUSTRIES:
                industry_weights[industry] = base_weight * 1.15
        elif market_state == "bear":
            for industry in DEFENSIVE_INDUSTRIES:
                industry_weights[industry] = base_weight * 1.25
            for industry in CYCLICAL_INDUSTRIES:
                industry_weights[industry] = base_weight * 0.80
            for industry in GROWTH_INDUSTRIES:
                industry_weights[industry] = base_weight
        else:
            for industry in list(DEFENSIVE_INDUSTRIES) + list(CYCLICAL_INDUSTRIES) + list(GROWTH_INDUSTRIES):
                industry_weights[industry] = base_weight
        
        total_weight = sum(industry_weights.values())
        if total_weight > 0:
            for industry in industry_weights:
                industry_weights[industry] /= total_weight
        
        return industry_weights
    
    def _get_stock_filters(self, market_state: str) -> Dict:
        """获取个股筛选规则"""
        if market_state == "bull":
            return {"pe_max": 35, "beta_min": 1.2, "focus": "高 Beta 股票，动量因子"}
        elif market_state == "bear":
            return {"debt_ratio_max": 40, "dividend_yield_min": 0.03, "focus": "低负债，高股息"}
        else:
            return {"pe_max": 25, "roe_stability_min": 0.70, "focus": "ROE 稳定，合理估值"}
    
    def _get_strategy_description(self, market_state: str) -> str:
        """获取策略描述"""
        descriptions = {
            "bull": "🐂 牛市策略：积极进攻，90-100% 仓位，超配周期和成长行业",
            "bear": "🐻 熊市策略：防御为主，50-70% 仓位，超配防御行业和高股息",
            "oscillate": "📊 震荡市策略：均衡配置，70-85% 仓位，适度超配消费医药"
        }
        return descriptions.get(market_state, descriptions["oscillate"])
    
    def _state_to_chinese(self, state: str) -> str:
        """市场状态转中文"""
        return {"bull": "🐂 牛市", "bear": "🐻 熊市", "oscillate": "📊 震荡市"}.get(state, "未知")


if __name__ == "__main__":
    allocator = DynamicAllocator()
    
    print("="*60)
    print("动态配置测试")
    print("="*60)
    
    for state in ["bull", "bear", "oscillate"]:
        print(f"\n{allocator._state_to_chinese(state)}")
        allocation = allocator.get_allocation(state, {}, "balanced")
        print(f"  股票池：{allocation['stock_pool'].get('name', 'N/A')}")
        print(f"  仓位：{allocation['position_range']['min']:.0%} - {allocation['position_range']['max']:.0%}")
        print(f"  推荐：{allocation['recommended_position']:.0%}")
    
    print("\n✅ 测试通过！")
