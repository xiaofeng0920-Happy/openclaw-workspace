# buffett-investor 市场状态识别模块（增强版）

"""
基于沪深 300 指数技术指标和市场广度识别市场状态
支持 4 个牛市条件 +4 个熊市条件的详细判断
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import akshare as ak


class MarketStateIdentifier:
    """市场状态识别器（增强版）"""
    
    def __init__(self, index_code: str = "000300.SH"):
        """
        初始化识别器
        
        Args:
            index_code: 指数代码（默认沪深 300）
        """
        self.index_code = index_code
        self.last_data = None
        self.history = []
    
    def identify_market_state(self, lookback_days: int = 250) -> Dict:
        """
        识别当前市场状态（增强版）
        
        Args:
            lookback_days: 回看天数
            
        Returns:
            Dict: 市场状态判断结果（包含详细条件）
        """
        # 1. 获取指数数据
        index_data = self._get_index_data(lookback_days)
        
        if index_data.empty:
            return {"error": "获取指数数据失败"}
        
        self.last_data = index_data
        
        # 2. 计算技术指标
        indicators = self._calculate_indicators(index_data)
        
        # 3. 判断市场状态（4+4 条件）
        market_state, bull_conditions, bear_conditions = self._judge_market_state_detailed(indicators)
        
        # 4. 计算置信度
        confidence = self._calculate_confidence(bull_conditions, bear_conditions, market_state)
        
        # 5. 记录历史
        self.history.append({
            "date": datetime.now().strftime('%Y-%m-%d'),
            "market_state": market_state,
            "confidence": confidence
        })
        
        # 6. 构建返回结果
        result = {
            "market_state": market_state,
            "market_state_cn": self._state_to_chinese(market_state),
            "confidence": confidence,
            "indicators": indicators,
            "bull_conditions": bull_conditions,
            "bull_conditions_met": sum(bull_conditions.values()),
            "bull_conditions_required": 4,
            "bear_conditions": bear_conditions,
            "bear_conditions_met": sum(bear_conditions.values()),
            "bear_conditions_required": 2,
            "timestamp": datetime.now().isoformat(),
            "index_code": self.index_code
        }
        
        return result
    
    def _get_index_data(self, lookback_days: int) -> pd.DataFrame:
        """获取指数历史数据"""
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=lookback_days)).strftime('%Y%m%d')
        
        try:
            df = ak.index_zh_a_hist(
                symbol=self.index_code,
                period="daily",
                start_date=start_date,
                end_date=end_date
            )
            
            if not df.empty:
                df = df.rename(columns={
                    '日期': 'date',
                    '收盘': 'close',
                    '开盘': 'open',
                    '最高': 'high',
                    '最低': 'low',
                    '成交量': 'volume',
                    '成交额': 'amount'
                })
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date').sort_index()
            
            return df
            
        except Exception as e:
            print(f"获取指数数据失败：{e}")
            return pd.DataFrame()
    
    def _calculate_indicators(self, df: pd.DataFrame) -> Dict:
        """计算技术指标"""
        indicators = {}
        
        if df.empty:
            return indicators
        
        latest_close = df['close'].iloc[-1]
        
        # 1. MA250（年线）
        df['ma250'] = df['close'].rolling(window=250).mean()
        ma250 = df['ma250'].iloc[-1]
        indicators['ma250'] = ma250
        
        # 2. MA250 斜率（5 日变化率）
        if len(df) > 5:
            ma250_5days_ago = df['ma250'].iloc[-6]
            ma250_slope = (ma250 - ma250_5days_ago) / ma250_5days_ago
        else:
            ma250_slope = 0
        indicators['ma250_slope'] = ma250_slope
        
        # 3. 收盘价 vs MA250
        price_vs_ma250 = (latest_close - ma250) / ma250
        indicators['price_vs_ma250'] = price_vs_ma250
        indicators['price_vs_ma250_position'] = "above" if price_vs_ma250 > 0 else "below"
        
        # 4. RSI(14)
        indicators['rsi14'] = self._calculate_rsi(df['close'], period=14)
        
        # 5. 市场广度（涨跌家数比）
        indicators['market_breadth'] = self._get_market_breadth()
        
        return indicators
    
    def _calculate_rsi(self, series: pd.Series, period: int = 14) -> float:
        """计算 RSI 指标"""
        delta = series.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not rsi.empty else 50
    
    def _get_market_breadth(self) -> float:
        """获取市场广度（简化实现）"""
        try:
            df = ak.stock_market_pe_lg(symbol="sh")
            if not df.empty and '上涨家数' in df.columns:
                up_count = df['上涨家数'].iloc[-1]
                down_count = df['下跌家数'].iloc[-1]
                total = up_count + down_count
                if total > 0:
                    return up_count / total
        except:
            pass
        return 0.50
    
    def _judge_market_state_detailed(self, indicators: Dict) -> Tuple[str, Dict, Dict]:
        """
        判断市场状态（4+4 条件详细判断）
        
        Returns:
            Tuple: (市场状态，牛市条件 dict, 熊市条件 dict)
        """
        if not indicators:
            return "oscillate", {}, {}
        
        # 牛市条件（4 个，需同时满足）
        bull_conditions = {
            "bull_cond1_price_above_ma250": indicators.get('price_vs_ma250_position') == "above",
            "bull_cond2_ma250_slope_positive": indicators.get('ma250_slope', 0) > 0,
            "bull_cond3_rsi_above_50": indicators.get('rsi14', 50) > 50,
            "bull_cond4_market_breadth_above_60": indicators.get('market_breadth', 0.5) > 0.60
        }
        
        # 熊市条件（4 个，需满足 2 个及以上）
        bear_conditions = {
            "bear_cond1_price_below_ma250": indicators.get('price_vs_ma250_position') == "below",
            "bear_cond2_ma250_slope_negative": indicators.get('ma250_slope', 0) < 0,
            "bear_cond3_rsi_below_40": indicators.get('rsi14', 50) < 40,
            "bear_cond4_market_breadth_below_40": indicators.get('market_breadth', 0.5) < 0.40
        }
        
        # 判断
        if all(bull_conditions.values()):
            return "bull", bull_conditions, bear_conditions
        
        if sum(bear_conditions.values()) >= 2:
            return "bear", bull_conditions, bear_conditions
        
        return "oscillate", bull_conditions, bear_conditions
    
    def _calculate_confidence(self, bull_conditions: Dict, bear_conditions: Dict, market_state: str) -> float:
        """计算判断置信度"""
        if not bull_conditions or market_state == "oscillate":
            return 0.50
        
        if market_state == "bull":
            # 牛市置信度：基于超出阈值的程度
            base_confidence = 0.50
            # 4 个条件全部满足，基础置信度 +0.25
            base_confidence += 0.25
            return min(base_confidence, 1.0)
        
        elif market_state == "bear":
            # 熊市置信度：基于满足条件的数量
            bear_met = sum(bear_conditions.values())
            base_confidence = 0.50 + (bear_met - 2) * 0.125  # 2 个条件 0.5, 3 个 0.625, 4 个 0.75
            return min(base_confidence, 1.0)
        
        return 0.50
    
    def _state_to_chinese(self, state: str) -> str:
        """市场状态转中文"""
        state_map = {
            "bull": "🐂 牛市",
            "bear": "🐻 熊市",
            "oscillate": "📊 震荡市"
        }
        return state_map.get(state, "未知")
    
    def get_allocation_suggestion(self, market_state: str) -> Dict:
        """根据市场状态获取配置建议"""
        suggestions = {
            "bull": {
                "position_min": 0.90,
                "position_max": 1.00,
                "stock_pool": "177 支全行业股票池",
                "strategy": "积极进攻，超配周期和成长行业",
                "pe_max": 35,
                "focus": "高 Beta 股票，动量因子"
            },
            "bear": {
                "position_min": 0.50,
                "position_max": 0.70,
                "stock_pool": "60 支严格财务筛选股票池",
                "strategy": "防御为主，超配防御行业和高股息",
                "debt_ratio_max": 40,
                "focus": "低波动，高股息率>3%"
            },
            "oscillate": {
                "position_min": 0.70,
                "position_max": 0.85,
                "stock_pool": "120 支中等筛选股票池",
                "strategy": "均衡配置，适度超配消费医药",
                "pe_max": 25,
                "focus": "ROE 稳定性，低波动"
            }
        }
        
        return suggestions.get(market_state, suggestions["oscillate"])


# ========== 使用示例 ==========
if __name__ == "__main__":
    identifier = MarketStateIdentifier()
    result = identifier.identify_market_state()
    
    print("="*80)
    print("市场状态识别结果")
    print("="*80)
    print(f"\n市场状态：{result.get('market_state_cn', '未知')}")
    print(f"置信度：{result.get('confidence', 0):.0%}")
    
    print(f"\n牛市条件（需同时满足 4 个）:")
    print(f"  满足数量：{result.get('bull_conditions_met', 0)}/4")
    for cond, met in result.get('bull_conditions', {}).items():
        status = "✅" if met else "❌"
        print(f"  {status} {cond}: {met}")
    
    print(f"\n熊市条件（需满足 2 个及以上）:")
    print(f"  满足数量：{result.get('bear_conditions_met', 0)}/4")
    for cond, met in result.get('bear_conditions', {}).items():
        status = "✅" if met else "❌"
        print(f"  {status} {cond}: {met}")
    
    if result.get('indicators'):
        indicators = result['indicators']
        print(f"\n技术指标:")
        print(f"  收盘价 vs MA250: {indicators.get('price_vs_ma250', 0)*100:.2f}%")
        print(f"  MA250 斜率：{indicators.get('ma250_slope', 0)*100:.2f}%")
        print(f"  RSI(14): {indicators.get('rsi14', 50):.2f}")
        print(f"  市场广度：{indicators.get('market_breadth', 0.5)*100:.1f}%")
    
    # 获取配置建议
    if result.get('market_state'):
        suggestion = identifier.get_allocation_suggestion(result['market_state'])
        print(f"\n配置建议:")
        print(f"  股票池：{suggestion['stock_pool']}")
        print(f"  仓位：{suggestion['position_min']:.0%}-{suggestion['position_max']:.0%}")
        print(f"  策略：{suggestion['strategy']}")
