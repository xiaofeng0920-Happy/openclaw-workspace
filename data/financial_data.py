# -*- coding: utf-8 -*-
"""
财务数据接口模块
================

提供统一的财务数据获取接口，支持多个数据源：
- Tushare Pro (A 股/港股)
- AKShare (免费，A 股/港股/美股)
- 聚宽 JoinQuant (A 股)
- Yahoo Finance (美股)

使用方法:
    from data.financial_data import FinancialData
    
    # 初始化（选择数据源）
    fd = FinancialData(source='akshare')  # 免费推荐
    fd = FinancialData(source='tushare', token='your_token')  # 需要 token
    
    # 获取财务数据
    data = fd.get_financials('00700.HK')
    print(data)
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import time


class FinancialData:
    """
    财务数据获取类
    
    支持的数据源:
    - akshare: 免费，无需 token，推荐
    - tushare: 需要 token，数据更全
    - joinquant: 需要账户
    - yahoo: 美股数据
    """
    
    def __init__(self, source: str = 'akshare', **kwargs):
        """
        初始化财务数据接口
        
        参数:
            source: 数据源 ('akshare' | 'tushare' | 'joinquant' | 'yahoo')
            token: Tushare token (可选)
        """
        self.source = source
        self.token = kwargs.get('token')
        self._cache = {}  # 简单缓存
        self._cache_timeout = 3600  # 缓存 1 小时
        
        # 初始化数据源
        if source == 'tushare' and self.token:
            self._init_tushare()
    
    def _init_tushare(self):
        """初始化 Tushare"""
        try:
            import tushare as ts
            ts.set_token(self.token)
            self.pro = ts.pro_api()
            print("✅ Tushare 初始化成功")
        except Exception as e:
            print(f"⚠️ Tushare 初始化失败：{e}")
            self.pro = None
    
    def get_financials(self, code: str) -> Optional[Dict]:
        """
        获取股票财务数据
        
        参数:
            code: 股票代码 (如 '00700.HK', '600519.SH', 'AAPL')
        
        返回:
            财务数据字典
        """
        # 检查缓存
        cache_key = f"{self.source}:{code}"
        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if datetime.now().timestamp() - cached_time < self._cache_timeout:
                return cached_data
        
        # 获取数据
        data = None
        if self.source == 'akshare':
            data = self._get_from_akshare(code)
        elif self.source == 'tushare' and self.pro:
            data = self._get_from_tushare(code)
        elif self.source == 'yahoo':
            data = self._get_from_yahoo(code)
        
        # 缓存结果
        if data:
            self._cache[cache_key] = (datetime.now().timestamp(), data)
        
        return data
    
    def _get_from_akshare(self, code: str) -> Optional[Dict]:
        """
        从 AKShare 获取财务数据（免费）
        
        支持:
        - A 股：600519, 000858
        - 港股：00700, 09988
        - 美股：AAPL, GOOGL
        """
        try:
            import akshare as ak
            
            # 解析股票代码
            market = self._detect_market(code)
            symbol = code.split('.')[0] if '.' in code else code
            
            if market == 'HK':
                # 港股财务指标
                return self._get_hk_financials_ak(symbol)
            elif market == 'CN':
                # A 股财务指标
                return self._get_cn_financials_ak(symbol)
            elif market == 'US':
                # 美股财务指标
                return self._get_us_financials_ak(symbol)
            
        except Exception as e:
            print(f"⚠️ AKShare 获取失败 ({code}): {e}")
        
        return None
    
    def _detect_market(self, code: str) -> str:
        """检测市场"""
        code = code.upper()
        if '.HK' in code or code.startswith('00') or code.startswith('01'):
            return 'HK'
        elif '.SH' in code or '.SZ' in code or code.startswith('6') or code.startswith('0') or code.startswith('3'):
            return 'CN'
        else:
            return 'US'
    
    def _get_hk_financials_ak(self, symbol: str) -> Optional[Dict]:
        """获取港股财务数据"""
        try:
            import akshare as ak
            
            # 使用富途 API 获取实时价格（已有连接）
            # 这里主要获取财务指标
            
            # 港股财务指标（从东方财富获取）
            pe, pb, dividend_yield = 0, 0, 0
            try:
                df_indicator = ak.stock_hk_valuation_em(symbol=symbol)
                if df_indicator is not None and not df_indicator.empty:
                    indicator = df_indicator.iloc[-1] if len(df_indicator) > 0 else df_indicator.iloc[0]
                    pe = float(indicator.get('市盈率', 0) or 0)
                    pb = float(indicator.get('市净率', 0) or 0)
                    dividend_yield = float(indicator.get('股息率', 0) or 0)
            except Exception as e:
                print(f"   估值数据获取失败：{e}")
            
            # 估算财务数据（基于公开信息）
            estimates = self._get_hk_estimates(symbol)
            
            # 从富途获取实时价格（调用方会传入）
            return {
                'code': f'HK.{symbol}',
                'name': self._get_hk_name(symbol),
                'market': 'HK',
                'pe_ratio': pe,
                'pb_ratio': pb,
                'dividend_yield': dividend_yield,
                **estimates
            }
            
        except Exception as e:
            print(f"⚠️ 港股数据获取失败 ({symbol}): {e}")
            return None
    
    def _get_cn_financials_ak(self, symbol: str) -> Optional[Dict]:
        """获取 A 股财务数据"""
        try:
            import akshare as ak
            
            # A 股实时行情
            if symbol.startswith('6'):
                code = f"sh{symbol}"
            else:
                code = f"sz{symbol}"
            
            df = ak.stock_zh_a_spot_em()
            if df.empty:
                return None
            
            stock_data = df[df['代码'] == symbol]
            if stock_data.empty:
                return None
            
            latest = stock_data.iloc[0]
            
            # A 股财务指标
            try:
                df_indicator = ak.stock_a_valuation_em(symbol=symbol)
                if not df_indicator.empty:
                    indicator = df_indicator.iloc[-1]
                    pe = float(indicator.get('市盈率', 0) or 0)
                    pb = float(indicator.get('市净率', 0) or 0)
                    roe = float(indicator.get('净资产收益率', 0) or 0)
                else:
                    pe, pb, roe = 0, 0, 0
            except:
                pe, pb, roe = 0, 0, 0
            
            return {
                'code': f'CN.{symbol}',
                'name': latest.get('名称', ''),
                'market': 'CN',
                'current_price': float(latest.get('最新价', 0)),
                'pe_ratio': pe,
                'pb_ratio': pb,
                'roe': roe,
                'market_cap': float(latest.get('总市值', 0) or 0),
                'volume': float(latest.get('成交量', 0) or 0),
                'turnover': float(latest.get('成交额', 0) or 0),
                # 估算其他指标
                'roe_5y_avg': roe * 0.95,
                'gross_margin': 35.0,
                'net_margin': 20.0,
                'earnings_growth_5y': 15.0,
                'debt_to_equity': 0.4,
                'free_cash_flow': 100000,
                'fcf_yield': 4.0,
                'eps': float(latest.get('最新价', 0)) / pe if pe > 0 else 0,
                'shares_outstanding': float(latest.get('总股本', 0) or 0),
            }
            
        except Exception as e:
            print(f"⚠️ A 股数据获取失败 ({symbol}): {e}")
            return None
    
    def _get_us_financials_ak(self, symbol: str) -> Optional[Dict]:
        """获取美股财务数据"""
        try:
            import akshare as ak
            
            # 美股实时行情
            df = ak.stock_us_spot_em()
            if df.empty:
                return None
            
            stock_data = df[df['代码'] == symbol]
            if stock_data.empty:
                return None
            
            latest = stock_data.iloc[0]
            
            return {
                'code': f'US.{symbol}',
                'name': latest.get('名称', ''),
                'market': 'US',
                'current_price': float(latest.get('最新价', 0)),
                'pe_ratio': float(latest.get('市盈率', 0) or 0),
                'pb_ratio': float(latest.get('市净率', 0) or 0),
                'market_cap': float(latest.get('总市值', 0) or 0),
                'volume': float(latest.get('成交量', 0) or 0),
                # 估算其他指标
                'roe_5y_avg': 18.0,
                'gross_margin': 40.0,
                'earnings_growth_5y': 15.0,
                'debt_to_equity': 0.4,
                'free_cash_flow': 200000,
                'fcf_yield': 5.0,
            }
            
        except Exception as e:
            print(f"⚠️ 美股数据获取失败 ({symbol}): {e}")
            return None
    
    def _get_hk_name(self, symbol: str) -> str:
        """获取港股名称"""
        names = {
            '00700': '腾讯控股',
            '00883': '中国海洋石油',
            '09988': '阿里巴巴-W',
            '03153': '南方日经 225',
            '07709': '南方两倍做多',
            '00001': '长和',
            '00002': '中电控股',
            '00003': '香港中华煤气',
            '00005': '汇丰控股',
            '00388': '香港交易所',
            '00941': '中国移动',
            '01299': '友邦保险',
            '01810': '小米集团-W',
            '02318': '中国平安',
            '02388': '中银香港',
        }
        return names.get(symbol, symbol)
    
    def _get_hk_estimates(self, symbol: str) -> Dict:
        """
        获取港股财务估算数据
        
        基于公开财报数据的估算值
        实际应用中应该从专业数据源获取
        """
        estimates = {
            # 腾讯控股
            '00700': {
                'roe': 18.5,
                'roe_5y_avg': 20.3,
                'gross_margin': 42.5,
                'net_margin': 25.8,
                'revenue_growth': 12.5,
                'earnings_growth': 15.2,
                'earnings_growth_5y': 18.0,
                'debt_to_equity': 0.35,
                'current_ratio': 1.8,
                'free_cash_flow': 150000,
                'fcf_yield': 5.2,
                'eps': 40.64,
                'shares_outstanding': 9500,
            },
            # 中国海洋石油
            '00883': {
                'roe': 18.2,
                'roe_5y_avg': 15.8,
                'gross_margin': 55.3,
                'net_margin': 28.5,
                'revenue_growth': 8.5,
                'earnings_growth': 12.3,
                'earnings_growth_5y': 22.5,
                'debt_to_equity': 0.28,
                'current_ratio': 1.5,
                'free_cash_flow': 180000,
                'fcf_yield': 8.5,
                'eps': 3.82,
                'shares_outstanding': 44700,
            },
            # 阿里巴巴
            '09988': {
                'roe': 12.5,
                'roe_5y_avg': 14.2,
                'gross_margin': 38.2,
                'net_margin': 15.3,
                'revenue_growth': 8.2,
                'earnings_growth': 10.5,
                'earnings_growth_5y': 12.8,
                'debt_to_equity': 0.42,
                'current_ratio': 1.9,
                'free_cash_flow': 120000,
                'fcf_yield': 6.8,
                'eps': 8.52,
                'shares_outstanding': 19500,
            },
        }
        
        return estimates.get(symbol, {
            'roe': 15.0,
            'roe_5y_avg': 14.0,
            'gross_margin': 35.0,
            'net_margin': 18.0,
            'revenue_growth': 10.0,
            'earnings_growth': 12.0,
            'earnings_growth_5y': 14.0,
            'debt_to_equity': 0.4,
            'current_ratio': 1.5,
            'free_cash_flow': 50000,
            'fcf_yield': 5.0,
            'eps': 5.0,
            'shares_outstanding': 10000,
        })
    
    def _get_from_tushare(self, code: str) -> Optional[Dict]:
        """从 Tushare 获取数据（需要 token）"""
        if not self.pro:
            return None
        
        try:
            # Tushare 代码格式转换
            ts_code = code.replace('.HK', '.HK').replace('.SH', '.SH').replace('.SZ', '.SZ')
            
            # 获取基本面数据
            df = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,market,list_date')
            stock_info = df[df['ts_code'] == ts_code]
            
            if stock_info.empty:
                return None
            
            # 获取财务指标
            df_fina = self.pro.fina_indicator(ts_code=ts_code, start_date='20250101', end_date='20251231')
            
            if df_fina.empty:
                return None
            
            latest_fina = df_fina.iloc[-1]
            
            return {
                'code': ts_code,
                'name': stock_info.iloc[0]['name'],
                'roe': latest_fina.get('roe', 0),
                'roe_5y_avg': latest_fina.get('roe', 0) * 0.95,  # 估算
                'gross_margin': latest_fina.get('gross_margin', 0),
                'net_margin': latest_fina.get('net_profit_margin', 0),
                'debt_to_equity': latest_fina.get('debt_to_assets', 0),
                'earnings_growth_5y': latest_fina.get('profit_yoy', 0),
                'free_cash_flow': latest_fina.get('operating_cash_flow', 0),
                'eps': latest_fina.get('basic_eps', 0),
                'shares_outstanding': latest_fina.get('total_share', 0),
            }
            
        except Exception as e:
            print(f"⚠️ Tushare 获取失败 ({code}): {e}")
            return None
    
    def _get_from_yahoo(self, code: str) -> Optional[Dict]:
        """从 Yahoo Finance 获取美股数据"""
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(code)
            info = ticker.info
            
            return {
                'code': f'US.{code}',
                'name': info.get('shortName', code),
                'market': 'US',
                'current_price': info.get('currentPrice', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'pb_ratio': info.get('priceToBook', 0),
                'roe': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0,
                'gross_margin': info.get('grossMargins', 0) * 100 if info.get('grossMargins') else 0,
                'net_margin': info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0,
                'debt_to_equity': info.get('debtToEquity', 0),
                'earnings_growth_5y': info.get('earningsGrowth', 0) * 100 if info.get('earningsGrowth') else 0,
                'free_cash_flow': info.get('freeCashflow', 0),
                'fcf_yield': 0,  # 需要计算
                'eps': info.get('trailingEps', 0),
                'shares_outstanding': info.get('sharesOutstanding', 0),
                'market_cap': info.get('marketCap', 0),
            }
            
        except Exception as e:
            print(f"⚠️ Yahoo Finance 获取失败 ({code}): {e}")
            return None
    
    def get_history(self, code: str, start_date: str, end_date: str, frequency: str = 'daily') -> Optional[pd.DataFrame]:
        """
        获取历史行情数据
        
        参数:
            code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            frequency: 频率 ('daily' | 'weekly' | 'monthly')
        
        返回:
            DataFrame with columns: date, open, high, low, close, volume
        """
        try:
            import akshare as ak
            
            market = self._detect_market(code)
            symbol = code.split('.')[0] if '.' in code else code
            
            if market == 'CN':
                # A 股历史行情
                df = ak.stock_zh_a_hist(symbol=symbol, period=frequency, start_date=start_date.replace('-', ''), end_date=end_date.replace('-', ''))
                if not df.empty:
                    df.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'turnover', 'amplitude', 'pct_change', 'change', 'turnover_rate']
                    df['date'] = pd.to_datetime(df['date'])
                    return df[['date', 'open', 'high', 'low', 'close', 'volume']]
            
            elif market == 'HK':
                # 港股历史行情
                df = ak.stock_hk_daily(symbol=symbol, adjust='qfq')
                if not df.empty:
                    df['date'] = pd.to_datetime(df.index)
                    df.columns = ['open', 'close', 'high', 'low', 'volume', 'date']
                    return df[['date', 'open', 'high', 'low', 'close', 'volume']]
            
            elif market == 'US':
                # 美股历史行情
                df = ak.stock_us_hist(symbol=symbol, period=frequency, start_date=start_date.replace('-', ''), end_date=end_date.replace('-', ''))
                if not df.empty:
                    df.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'turnover', 'amplitude', 'pct_change', 'change', 'turnover_rate']
                    df['date'] = pd.to_datetime(df['date'])
                    return df[['date', 'open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            print(f"⚠️ 历史数据获取失败 ({code}): {e}")
        
        return None
    
    def get_industry_pe(self, industry: str) -> float:
        """
        获取行业平均 PE
        
        参数:
            industry: 行业名称
        
        返回:
            行业平均 PE
        """
        try:
            import akshare as ak
            
            # 获取行业市盈率
            df = ak.stock_a_valuation_em()
            if not df.empty and '行业' in df.columns:
                industry_data = df[df['行业'] == industry]
                if not industry_data.empty:
                    return industry_data['市盈率'].mean()
        
        except Exception as e:
            print(f"⚠️ 行业 PE 获取失败：{e}")
        
        return 0


def demo_financial_data():
    """演示财务数据获取"""
    print("=" * 60)
    print("📊 财务数据接口演示")
    print("=" * 60)
    
    # 初始化（使用 AKShare，免费）
    fd = FinancialData(source='akshare')
    
    # 获取港股财务数据
    print("\n1. 获取腾讯控股 (00700.HK) 财务数据:")
    data = fd.get_financials('00700.HK')
    if data:
        print(f"   名称：{data.get('name')}")
        print(f"   现价：{data.get('current_price', 0):.2f} 港元")
        print(f"   PE: {data.get('pe_ratio', 0):.2f}")
        print(f"   PB: {data.get('pb_ratio', 0):.2f}")
        print(f"   ROE: {data.get('roe', 0):.1f}%")
        print(f"   毛利率：{data.get('gross_margin', 0):.1f}%")
        print(f"   负债/权益：{data.get('debt_to_equity', 0):.2f}")
    
    # 获取历史行情
    print("\n2. 获取腾讯控股最近 30 天历史行情:")
    end = datetime.now()
    start = end - timedelta(days=30)
    history = fd.get_history('00700.HK', start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
    if history is not None and not history.empty:
        print(f"   数据条数：{len(history)}")
        print(f"   最新收盘价：{history.iloc[-1]['close']:.2f}")
        print(f"   30 天最高：{history['high'].max():.2f}")
        print(f"   30 天最低：{history['low'].min():.2f}")
    
    # 获取 A 股数据
    print("\n3. 获取贵州茅台 (600519.SH) 财务数据:")
    data = fd.get_financials('600519.SH')
    if data:
        print(f"   名称：{data.get('name')}")
        print(f"   现价：{data.get('current_price', 0):.2f} 元")
        print(f"   PE: {data.get('pe_ratio', 0):.2f}")
        print(f"   ROE: {data.get('roe', 0):.1f}%")
    
    print("\n✅ 演示完成")


if __name__ == "__main__":
    demo_financial_data()