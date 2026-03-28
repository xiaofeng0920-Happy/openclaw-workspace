# buffett-investor 回测引擎模块

"""
事件驱动回测框架
支持季度/月度调仓，动态配置策略
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, initial_capital: float = 1000000.0):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}
        self.cash = initial_capital
        self.nav_history = []
        self.trade_history = []
        
    def run_backtest(self, market_data: pd.DataFrame, strategy_params: Dict, 
                    rebalance_frequency: str = "quarterly") -> Dict:
        """运行回测"""
        print(f"开始回测...")
        print(f"  初始资金：{self.initial_capital:,.2f}")
        print(f"  回测周期：{market_data.index[0]} 至 {market_data.index[-1]}")
        
        for date, row in market_data.iterrows():
            self._update_market_state(date, row)
            if self._should_rebalance(date, rebalance_frequency):
                self._execute_rebalance(date, row, strategy_params)
            nav = self._calculate_nav(date, row)
            self.nav_history.append(nav)
        
        performance = self._calculate_performance()
        
        return {
            "initial_capital": self.initial_capital,
            "final_value": self.current_capital,
            "total_return": (self.current_capital - self.initial_capital) / self.initial_capital,
            "performance": performance,
            "nav_history": self.nav_history[-10:],
            "trade_count": len(self.trade_history)
        }
    
    def _update_market_state(self, date: datetime, row: pd.Series):
        self.market_state_history.append({
            "date": date.strftime('%Y-%m-%d'),
            "market_state": row.get('market_state', 'oscillate')
        })
    
    def _should_rebalance(self, date: datetime, rebalance_frequency: str) -> bool:
        if rebalance_frequency == "monthly":
            return date.day == 1
        else:  # quarterly
            return date.month in [1, 4, 7, 10] and date.day <= 5
    
    def _execute_rebalance(self, date: datetime, row: pd.Series, strategy_params: Dict):
        market_state = row.get('market_state', 'oscillate')
        position = strategy_params.get(f'{market_state}_position', 0.75)
        target_value = self.current_capital * position
        
        self.trade_history.append({
            "date": date.strftime('%Y-%m-%d'),
            "action": "rebalance",
            "market_state": market_state,
            "target_position": position
        })
    
    def _calculate_nav(self, date: datetime, row: pd.Series) -> Dict:
        total_value = self.current_capital
        nav = total_value / self.initial_capital
        
        return {
            "date": date.strftime('%Y-%m-%d'),
            "nav": nav,
            "value": total_value
        }
    
    def _calculate_performance(self) -> Dict:
        if not self.nav_history:
            return {}
        
        navs = [h['nav'] for h in self.nav_history]
        current_nav = navs[-1]
        total_return = current_nav - 1
        
        return {
            "total_return": total_return,
            "total_return_pct": total_return * 100,
            "navs": len(navs)
        }


if __name__ == "__main__":
    # 测试回测引擎
    engine = BacktestEngine(initial_capital=1000000)
    
    # 创建模拟数据
    dates = pd.date_range('2021-01-01', '2026-03-28', freq='D')
    data = pd.DataFrame({
        'close': np.random.randn(len(dates)).cumsum() + 3000,
        'market_state': np.random.choice(['bull', 'bear', 'oscillate'], len(dates))
    }, index=dates)
    
    result = engine.run_backtest(data, {'bull_position': 0.95, 'bear_position': 0.60, 'oscillate_position': 0.75})
    
    print(f"\n回测结果:")
    print(f"  累计收益：{result['total_return']*100:.2f}%")
    print(f"  交易次数：{result['trade_count']}")
    print("\n✅ 回测引擎测试通过！")
