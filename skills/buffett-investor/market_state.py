# buffett-investor 市场状态识别模块

"""
基于沪深 300 指数技术指标和市场广度识别市场状态
牛市、熊市、震荡市判断
"""

import pandas as pd
import akshare as ak
from datetime import datetime, timedelta
from typing import Dict, Optional
import numpy as np

try:
    from .config import (
        BULL_PRICE_VS_MA250, BULL_MA250_SLOPE_MIN, BULL_RSI14_MIN, BULL_MARKET_BREADTH_MIN,
        BEAR_PRICE_VS_MA250, BEAR_MA250_SLOPE_MAX, BEAR_RSI14_MAX, BEAR_MARKET_BREADTH_MAX
    )
except ImportError:
    from config import (
        BULL_PRICE_VS_MA250, BULL_MA250_SLOPE_MIN, BULL_RSI14_MIN, BULL_MARKET_BREADTH_MIN,
        BEAR_PRICE_VS_MA250, BEAR_MA250_SLOPE_MAX, BEAR_RSI14_MAX, BEAR_MARKET_BREADTH_MAX
    )


class MarketStateIdentifier:
    """市场状态识别器"""
    
    def __init__(self, index_code: str = "000300.SH"):
        """
        初始化识别器
        
        Args:
            index_code: 指数代码（默认沪深 300）
        """
        self.index_code = index_code
        
    def identify_market_state(self, lookback_days: int = 250) -> Dict:
        """
        识别当前市场状态
        
        Args:
            lookback_days: 回看天数
            
        Returns:
            Dict: 市场状态判断结果
        """
        # 1. 获取指数数据
        index_data = self._get_index_data(lookback_days)
        
        if index_data.empty:
            return {"error": "获取指数数据失败"}
        
        # 2. 计算技术指标
        indicators = self._calculate_indicators(index_data)
        
        # 3. 判断市场状态
        market_state = self._judge_market_state(indicators)
        
        # 4. 计算置信度
        confidence = self._calculate_confidence(indicators, market_state)
        
        # 5. 构建返回结果
        result = {
            "market_state": market_state,
            "market_state_cn": self._state_to_chinese(market_state),
            "confidence": confidence,
            "indicators": indicators,
            "timestamp": datetime.now().isoformat(),
            "index_code": self.index_code
        }
        
        return result
    
    def _get_index_data(self, lookback_days: int) -> pd.DataFrame:
        """
        获取指数历史数据
        
        Args:
            lookback_days: 回看天数
            
        Returns:
            DataFrame: 指数行情数据
        """
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=lookback_days)).strftime('%Y%m%d')
        
        try:
            # 获取沪深 300 指数历史行情
            df = ak.index_zh_a_hist(
                symbol=self.index_code,
                period="daily",
                start_date=start_date,
                end_date=end_date
            )
            
            if not df.empty:
                # 重命名列
                df = df.rename(columns={
                    '日期': 'date',
                    '开盘': 'open',
                    '收盘': 'close',
                    '最高': 'high',
                    '最低': 'low',
                    '成交量': 'volume',
                    '成交额': 'amount'
                })
                
                # 设置日期索引
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date').sort_index()
                
            return df
            
        except Exception as e:
            print(f"获取指数数据失败：{e}")
            return pd.DataFrame()
    
    def _calculate_indicators(self, df: pd.DataFrame) -> Dict:
        """
        计算技术指标
        
        Args:
            df: 指数行情数据
            
        Returns:
            Dict: 技术指标
        """
        indicators = {}
        
        if df.empty:
            return indicators
        
        latest_close = df['close'].iloc[-1]
        
        # 1. MA250（年线）
        df['ma250'] = df['close'].rolling(window=250).mean()
        ma250 = df['ma250'].iloc[-1]
        indicators['ma250'] = ma250
        
        # 2. MA250 斜率（20 日变化率）
        if len(df) > 20:
            ma250_20days_ago = df['ma250'].iloc[-21]
            ma250_slope = (ma250 - ma250_20days_ago) / ma250_20days_ago * 100
        else:
            ma250_slope = 0
        indicators['ma250_slope'] = ma250_slope
        
        # 3. 收盘价 vs MA250
        price_vs_ma250 = (latest_close - ma250) / ma250 * 100
        indicators['price_vs_ma250'] = price_vs_ma250
        indicators['price_vs_ma250_position'] = "above" if price_vs_ma250 > 0 else "below"
        
        # 4. RSI(14)
        indicators['rsi14'] = self._calculate_rsi(df['close'], period=14)
        
        # 5. 市场广度（涨跌家数比）- 需要额外数据源
        # 这里简化处理，实际需要从全市场涨跌家数计算
        indicators['market_breadth'] = self._get_market_breadth()
        
        # 6. 其他辅助指标
        # 20 日动量
        if len(df) > 20:
            momentum_20d = (latest_close - df['close'].iloc[-21]) / df['close'].iloc[-21] * 100
        else:
            momentum_20d = 0
        indicators['momentum_20d'] = momentum_20d
        
        # 60 日动量
        if len(df) > 60:
            momentum_60d = (latest_close - df['close'].iloc[-61]) / df['close'].iloc[-61] * 100
        else:
            momentum_60d = 0
        indicators['momentum_60d'] = momentum_60d
        
        # 波动率（20 日年化）
        returns = df['close'].pct_change()
        volatility_20d = returns.tail(20).std() * np.sqrt(252) * 100
        indicators['volatility_20d'] = volatility_20d
        
        return indicators
    
    def _calculate_rsi(self, series: pd.Series, period: int = 14) -> float:
        """
        计算 RSI 指标
        
        Args:
            series: 价格序列
            period: RSI 周期
            
        Returns:
            float: RSI 值
        """
        delta = series.diff()
        
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not rsi.empty else 50
    
    def _get_market_breadth(self) -> float:
        """
        获取市场广度（涨跌家数比）
        
        Returns:
            float: 市场广度值（0-1）
        """
        # 简化实现：获取上证指数涨跌家数
        try:
            # 获取市场涨跌家数
            df = ak.stock_market_pe_lg(symbol="sh")
            
            if not df.empty and '上涨家数' in df.columns:
                up_count = df['上涨家数'].iloc[-1]
                down_count = df['下跌家数'].iloc[-1]
                
                total = up_count + down_count
                if total > 0:
                    breadth = up_count / total
                    return breadth
                    
        except Exception as e:
            print(f"获取市场广度失败：{e}")
        
        # 默认值
        return 0.50
    
    def _judge_market_state(self, indicators: Dict) -> str:
        """
        判断市场状态
        
        Args:
            indicators: 技术指标
            
        Returns:
            str: 市场状态 (bull/bear/oscillate)
        """
        if not indicators:
            return "oscillate"
        
        # 牛市条件（需同时满足）
        bull_conditions = [
            indicators.get('price_vs_ma250_position') == BULL_PRICE_VS_MA250,
            indicators.get('ma250_slope', 0) > BULL_MA250_SLOPE_MIN,
            indicators.get('rsi14', 50) > BULL_RSI14_MIN,
            indicators.get('market_breadth', 0.5) > BULL_MARKET_BREADTH_MIN
        ]
        
        if all(bull_conditions):
            return "bull"
        
        # 熊市条件（满足 2 个及以上）
        bear_conditions = [
            indicators.get('price_vs_ma250_position') == BEAR_PRICE_VS_MA250,
            indicators.get('ma250_slope', 0) < BEAR_MA250_SLOPE_MAX,
            indicators.get('rsi14', 50) < BEAR_RSI14_MAX,
            indicators.get('market_breadth', 0.5) < BEAR_MARKET_BREADTH_MAX
        ]
        
        if sum(bear_conditions) >= 2:
            return "bear"
        
        # 默认震荡市
        return "oscillate"
    
    def _calculate_confidence(self, indicators: Dict, market_state: str) -> float:
        """
        计算判断置信度
        
        Args:
            indicators: 技术指标
            market_state: 市场状态
            
        Returns:
            float: 置信度（0-1）
        """
        if not indicators or market_state == "oscillate":
            return 0.50
        
        if market_state == "bull":
            # 牛市置信度：基于指标超出阈值的程度
            confidence = 0.0
            
            # RSI 超出程度
            rsi_excess = (indicators.get('rsi14', 50) - BULL_RSI14_MIN) / 50
            confidence += min(rsi_excess, 0.25)
            
            # 价格超出 MA250 程度
            price_excess = indicators.get('price_vs_ma250', 0) / 100
            confidence += min(max(price_excess, 0), 0.25)
            
            # 市场广度超出程度
            breadth_excess = (indicators.get('market_breadth', 0.5) - BULL_MARKET_BREADTH_MIN)
            confidence += min(max(breadth_excess, 0), 0.25)
            
            # MA250 斜率
            slope_excess = indicators.get('ma250_slope', 0) / 100
            confidence += min(max(slope_excess, 0), 0.25)
            
            return min(max(0.5 + confidence, 0), 1)
        
        elif market_state == "bear":
            # 熊市置信度：基于指标低于阈值的程度
            confidence = 0.0
            
            # RSI 低于程度
            rsi_deficit = (BEAR_RSI14_MAX - indicators.get('rsi14', 50)) / 40
            confidence += min(max(rsi_deficit, 0), 0.25)
            
            # 价格低于 MA250 程度
            price_deficit = abs(indicators.get('price_vs_ma250', 0)) / 100
            confidence += min(max(price_deficit, 0), 0.25)
            
            # 市场广度低于程度
            breadth_deficit = BEAR_MARKET_BREADTH_MAX - indicators.get('market_breadth', 0.5)
            confidence += min(max(breadth_deficit, 0), 0.25)
            
            # MA250 斜率
            slope_deficit = abs(indicators.get('ma250_slope', 0)) / 100
            confidence += min(max(slope_deficit, 0), 0.25)
            
            return min(max(0.5 + confidence, 0), 1)
        
        return 0.50
    
    def _state_to_chinese(self, state: str) -> str:
        """
        市场状态转中文
        
        Args:
            state: 市场状态代码
            
        Returns:
            str: 中文描述
        """
        state_map = {
            "bull": "🐂 牛市",
            "bear": "🐻 熊市",
            "oscillate": "📊 震荡市"
        }
        return state_map.get(state, "未知")
    
    def get_allocation_suggestion(self, market_state: str) -> Dict:
        """
        根据市场状态获取配置建议
        
        Args:
            market_state: 市场状态
            
        Returns:
            Dict: 配置建议
        """
        from .config import (
            BULL_POSITION_MIN, BULL_POSITION_MAX,
            BEAR_POSITION_MIN, BEAR_POSITION_MAX,
            OSCILLATE_POSITION_MIN, OSCILLATE_POSITION_MAX
        )
        
        suggestions = {
            "bull": {
                "position_min": BULL_POSITION_MIN,
                "position_max": BULL_POSITION_MAX,
                "stock_pool": "177 支全行业股票池",
                "strategy": "积极进攻，超配周期和成长行业",
                "pe_max": 35,
                "focus": "高 Beta 股票，动量因子"
            },
            "bear": {
                "position_min": BEAR_POSITION_MIN,
                "position_max": BEAR_POSITION_MAX,
                "stock_pool": "60 支严格财务筛选股票池",
                "strategy": "防御为主，超配防御行业和高股息",
                "debt_ratio_max": 40,
                "focus": "低波动，高股息率>3%"
            },
            "oscillate": {
                "position_min": OSCILLATE_POSITION_MIN,
                "position_max": OSCILLATE_POSITION_MAX,
                "stock_pool": "120 支中等筛选股票池",
                "strategy": "均衡配置，适度超配消费医药",
                "pe_max": 25,
                "focus": "ROE 稳定性，低波动"
            }
        }
        
        return suggestions.get(market_state, suggestions["oscillate"])


# ========== 使用示例 ==========
if __name__ == "__main__":
    # 初始化识别器
    identifier = MarketStateIdentifier()
    
    # 识别市场状态
    result = identifier.identify_market_state()
    
    print(f"\n市场状态：{result.get('market_state_cn', '未知')}")
    print(f"置信度：{result.get('confidence', 0):.2%}")
    
    if result.get('indicators'):
        indicators = result['indicators']
        print(f"\n技术指标:")
        print(f"  收盘价 vs MA250: {indicators.get('price_vs_ma250', 0):.2f}%")
        print(f"  MA250 斜率：{indicators.get('ma250_slope', 0):.2f}%")
        print(f"  RSI(14): {indicators.get('rsi14', 50):.2f}")
        print(f"  市场广度：{indicators.get('market_breadth', 0.5):.2%}")
    
    # 获取配置建议
    if result.get('market_state'):
        suggestion = identifier.get_allocation_suggestion(result['market_state'])
        print(f"\n配置建议:")
        print(f"  股票池：{suggestion['stock_pool']}")
        print(f"  仓位：{suggestion['position_min']:.0%}-{suggestion['position_max']:.0%}")
        print(f"  策略：{suggestion['strategy']}")
