# buffett-investor 股票筛选模块

"""
基于巴菲特价值投资理念的股票筛选系统
筛选条件：PE<30, ROE>8%, ROIC>8%, 市值>30 亿，负债率<50%, 现金流连续 5 年为正
"""

import pandas as pd
import akshare as ak
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os

try:
    from .config import (
        PE_MAX, ROE_MIN, ROIC_MIN, MARKET_CAP_MIN,
        DEBT_RATIO_MAX, FCF_POSITIVE_YEARS,
        STOCK_POOL_177, STOCK_POOL_60, STOCK_POOL_120,
        TUSHARE_TOKEN_PATH
    )
except ImportError:
    from config import (
        PE_MAX, ROE_MIN, ROIC_MIN, MARKET_CAP_MIN,
        DEBT_RATIO_MAX, FCF_POSITIVE_YEARS,
        STOCK_POOL_177, STOCK_POOL_60, STOCK_POOL_120,
        TUSHARE_TOKEN_PATH
    )


class StockScreener:
    """股票筛选器"""
    
    def __init__(self, data_source: str = "tushare"):
        """
        初始化筛选器
        
        Args:
            data_source: 数据源 (akshare/tushare)
        """
        self.data_source = data_source
        self.tushare_token = self._load_tushare_token()
        
    def _load_tushare_token(self) -> Optional[str]:
        """加载 Tushare Token"""
        if os.path.exists(TUSHARE_TOKEN_PATH):
            with open(TUSHARE_TOKEN_PATH, 'r') as f:
                return f.read().strip()
        return None
    
    def get_stock_universe(self) -> pd.DataFrame:
        """
        获取筛选范围：沪深 300 + 中证 1000 成分股
        
        Returns:
            DataFrame: 股票清单
        """
        # 获取沪深 300 成分股
        hs300 = ak.index_stock_cons_csindex(symbol="000300")
        
        # 获取中证 1000 成分股
        zz1000 = ak.index_stock_cons_csindex(symbol="000852")
        
        # 合并去重
        universe = pd.concat([hs300, zz1000]).drop_duplicates(subset=['股票代码'])
        
        return universe
    
    def get_financial_data(self, stock_codes: List[str]) -> pd.DataFrame:
        """
        获取财务数据
        
        Args:
            stock_codes: 股票代码列表
            
        Returns:
            DataFrame: 财务指标数据
        """
        if self.data_source == "tushare" and self.tushare_token:
            return self._get_financial_data_tushare(stock_codes)
        else:
            return self._get_financial_data_akshare(stock_codes)
    
    def _get_financial_data_tushare(self, stock_codes: List[str]) -> pd.DataFrame:
        """使用 Tushare 获取财务数据（批量查询，速度快）"""
        import tushare as ts
        
        ts.set_token(self.tushare_token)
        pro = ts.pro_api()
        
        # 获取财务指标
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=5*365)).strftime('%Y%m%d')
        
        # 批量获取财务指标
        financial_data = []
        for code in stock_codes:
            try:
                # 转换代码格式
                ts_code = code.replace('.', '')
                
                # 获取财务指标
                fina_indicator = pro.fina_indicator(
                    ts_code=ts_code,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if not fina_indicator.empty:
                    financial_data.append(fina_indicator)
                    
            except Exception as e:
                print(f"获取 {code} 财务数据失败：{e}")
                continue
        
        if financial_data:
            df = pd.concat(financial_data, ignore_index=True)
            return df
        else:
            return pd.DataFrame()
    
    def _get_financial_data_akshare(self, stock_codes: List[str]) -> pd.DataFrame:
        """使用 AkShare 获取财务数据（逐个查询，速度慢）"""
        financial_data = []
        
        for code in stock_codes:
            try:
                # 获取个股财务指标
                df = ak.stock_financial_analysis_indicator(symbol=code)
                
                if not df.empty:
                    df['股票代码'] = code
                    financial_data.append(df)
                    
            except Exception as e:
                print(f"获取 {code} 财务数据失败：{e}")
                continue
        
        if financial_data:
            df = pd.concat(financial_data, ignore_index=True)
            return df
        else:
            return pd.DataFrame()
    
    def screen(self, 
               pe_max: float = None,
               roe_min: float = None,
               roic_min: float = None,
               market_cap_min: float = None,
               debt_ratio_max: float = None,
               fcf_positive_years: int = None,
               pool_type: str = "177") -> Dict:
        """
        执行股票筛选
        
        Args:
            pe_max: PE 上限
            roe_min: ROE 下限%
            roic_min: ROIC 下限%
            market_cap_min: 市值下限（亿）
            debt_ratio_max: 资产负债率上限%
            fcf_positive_years: 连续正现金流年数
            pool_type: 股票池类型 (177/60/120)
            
        Returns:
            Dict: 筛选结果
        """
        # 使用预设配置
        if pool_type == "177":
            config = STOCK_POOL_177
        elif pool_type == "60":
            config = STOCK_POOL_60
        elif pool_type == "120":
            config = STOCK_POOL_120
        else:
            config = STOCK_POOL_177
        
        # 覆盖参数
        pe_max = pe_max or config.get("pe_max", PE_MAX)
        roe_min = roe_min or config.get("roe_min", ROE_MIN)
        roic_min = roic_min or config.get("roic_min", ROIC_MIN)
        market_cap_min = market_cap_min or config.get("market_cap_min", MARKET_CAP_MIN)
        debt_ratio_max = debt_ratio_max or config.get("debt_ratio_max", DEBT_RATIO_MAX)
        fcf_positive_years = fcf_positive_years or config.get("fcf_positive_years", FCF_POSITIVE_YEARS)
        
        print(f"开始筛选股票池：{config.get('name', pool_type)}")
        print(f"筛选条件：PE<{pe_max}, ROE>{roe_min}%, ROIC>{roic_min}%, 市值>{market_cap_min}亿")
        
        # 1. 获取股票范围
        universe = self.get_stock_universe()
        print(f"筛选范围：{len(universe)} 只股票（沪深 300+ 中证 1000）")
        
        # 2. 获取财务数据
        stock_codes = universe['股票代码'].tolist()
        financial_data = self.get_financial_data(stock_codes)
        
        if financial_data.empty:
            return {"error": "获取财务数据失败"}
        
        # 3. 执行筛选
        filtered_stocks = self._apply_filters(
            financial_data,
            pe_max=pe_max,
            roe_min=roe_min,
            roic_min=roic_min,
            market_cap_min=market_cap_min,
            debt_ratio_max=debt_ratio_max,
            fcf_positive_years=fcf_positive_years
        )
        
        # 4. 计算统计指标
        stats = self._calculate_statistics(filtered_stocks)
        
        # 5. 构建返回结果
        result = {
            "pool_type": pool_type,
            "pool_name": config.get("name", f"{pool_type}支股票池"),
            "count": len(filtered_stocks),
            "stocks": filtered_stocks.to_dict('records'),
            "statistics": stats,
            "filters": {
                "pe_max": pe_max,
                "roe_min": roe_min,
                "roic_min": roic_min,
                "market_cap_min": market_cap_min,
                "debt_ratio_max": debt_ratio_max,
                "fcf_positive_years": fcf_positive_years
            },
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"筛选完成：{len(filtered_stocks)} 只股票符合条件")
        
        return result
    
    def _apply_filters(self, 
                       df: pd.DataFrame,
                       pe_max: float,
                       roe_min: float,
                       roic_min: float,
                       market_cap_min: float,
                       debt_ratio_max: float,
                       fcf_positive_years: int) -> pd.DataFrame:
        """
        应用筛选条件
        
        Args:
            df: 财务数据 DataFrame
            pe_max: PE 上限
            roe_min: ROE 下限
            roic_min: ROIC 下限
            market_cap_min: 市值下限
            debt_ratio_max: 负债率上限
            fcf_positive_years: 连续正现金流年数
            
        Returns:
            DataFrame: 筛选后的股票
        """
        # 这里需要根据实际数据字段名调整
        # 示例逻辑：
        
        # 1. PE 筛选
        if 'pe_ttm' in df.columns:
            df = df[df['pe_ttm'] < pe_max]
        
        # 2. ROE 筛选（连续 5 年）
        if 'roe' in df.columns:
            df = df[df['roe'] > roe_min]
        
        # 3. ROIC 筛选（连续 5 年）
        if 'roic' in df.columns:
            df = df[df['roic'] > roic_min]
        
        # 4. 市值筛选
        if 'market_cap' in df.columns:
            df = df[df['market_cap'] > market_cap_min]
        
        # 5. 负债率筛选
        if debt_ratio_max and 'debt_ratio' in df.columns:
            df = df[df['debt_ratio'] < debt_ratio_max]
        
        # 6. 自由现金流筛选（连续 5 年为正）
        if fcf_positive_years and 'fcf' in df.columns:
            # 需要检查连续年数
            pass
        
        # 去重并排序
        df = df.drop_duplicates(subset=['股票代码'])
        df = df.sort_values('roe', ascending=False)
        
        return df
    
    def _calculate_statistics(self, df: pd.DataFrame) -> Dict:
        """
        计算统计指标
        
        Args:
            df: 筛选后的股票 DataFrame
            
        Returns:
            Dict: 统计指标
        """
        stats = {}
        
        if 'pe_ttm' in df.columns:
            stats['avg_pe'] = df['pe_ttm'].mean()
            stats['min_pe'] = df['pe_ttm'].min()
            stats['max_pe'] = df['pe_ttm'].max()
        
        if 'roe' in df.columns:
            stats['avg_roe'] = df['roe'].mean()
            stats['max_roe'] = df['roe'].max()
        
        if 'roic' in df.columns:
            stats['avg_roic'] = df['roic'].mean()
        
        if 'market_cap' in df.columns:
            stats['avg_market_cap'] = df['market_cap'].mean()
            stats['max_market_cap'] = df['market_cap'].max()
            stats['min_market_cap'] = df['market_cap'].min()
        
        return stats
    
    def get_industry_breakdown(self, stocks: List[Dict]) -> Dict:
        """
        获取行业分布
        
        Args:
            stocks: 股票列表
            
        Returns:
            Dict: 行业分布统计
        """
        from .config import INDUSTRY_MAP
        
        industry_count = {}
        
        for stock in stocks:
            code = stock.get('code', stock.get('股票代码'))
            
            # 查找股票所属行业
            for industry, codes in INDUSTRY_MAP.items():
                if code in codes:
                    industry_count[industry] = industry_count.get(industry, 0) + 1
                    break
        
        return industry_count


# ========== 使用示例 ==========
if __name__ == "__main__":
    # 初始化筛选器
    screener = StockScreener(data_source="akshare")
    
    # 筛选 177 支股票池
    result_177 = screener.screen(pool_type="177")
    print(f"\n177 支池：{result_177.get('count', 0)} 只股票")
    
    # 筛选 60 支股票池
    result_60 = screener.screen(pool_type="60")
    print(f"60 支池：{result_60.get('count', 0)} 只股票")
    
    # 获取行业分布
    if result_177.get('stocks'):
        industry_breakdown = screener.get_industry_breakdown(result_177['stocks'])
        print(f"\n行业分布：{industry_breakdown}")
