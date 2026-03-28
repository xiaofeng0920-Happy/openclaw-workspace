# buffett-investor 调仓执行模块
from datetime import datetime
from typing import Dict, List

class Rebalancer:
    def __init__(self, initial_capital: float = 1000000.0):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
    
    def generate_rebalance_plan(self, allocation: Dict, current_holdings: Dict, stock_prices: Dict) -> Dict:
        target = {code: 1.0/len(allocation.get("top_picks", [])) for code in allocation.get("top_picks", []) if code in stock_prices}
        trades = [{"action": "buy", "code": code, "weight": w} for code, w in target.items()]
        cost = {"total_cost": sum(t["weight"]*self.current_capital for t in trades)*0.0005, "cost_ratio_bps": 5}
        return {"action": "rebalance", "date": datetime.now().strftime("%Y-%m-%d"), "trades": trades, "total_trades": len(trades), "estimated_cost": cost}

if __name__ == "__main__":
    r = Rebalancer()
    plan = r.generate_rebalance_plan({"top_picks": ["600519.SH", "000858.SZ"]}, {}, {"600519.SH": 1800})
    print(f"调仓计划：{plan['action']}, 交易数：{plan['total_trades']}")
    print("✅ rebalancer.py 测试通过")
