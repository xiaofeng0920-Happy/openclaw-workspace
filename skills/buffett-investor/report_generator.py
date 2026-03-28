# buffett-investor 可视化图表生成模块

"""
生成回测可视化图表
包括净值曲线、回撤曲线、市场状态分布等
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import os


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, output_dir: str = "reports"):
        """
        初始化报告生成器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    
    def generate_all_charts(self, nav_data: pd.DataFrame, 
                           market_state_data: pd.DataFrame,
                           performance_data: Dict) -> List[str]:
        """
        生成所有图表
        
        Args:
            nav_data: 净值数据
            market_state_data: 市场状态数据
            performance_data: 绩效数据
            
        Returns:
            List[str]: 生成的文件路径
        """
        charts = []
        
        # 1. 净值曲线对比图
        chart1 = self.plot_nav_comparison(nav_data)
        if chart1:
            charts.append(chart1)
        
        # 2. 回撤曲线图
        chart2 = self.plot_drawdown(nav_data)
        if chart2:
            charts.append(chart2)
        
        # 3. 市场状态分布图
        chart3 = self.plot_market_state_distribution(market_state_data)
        if chart3:
            charts.append(chart3)
        
        # 4. 年度收益对比图
        chart4 = self.plot_annual_returns(nav_data)
        if chart4:
            charts.append(chart4)
        
        return charts
    
    def plot_nav_comparison(self, nav_data: pd.DataFrame) -> Optional[str]:
        """绘制净值曲线对比图"""
        try:
            if nav_data.empty:
                return None
            
            fig, ax = plt.subplots(figsize=(14, 7))
            
            # 绘制净值曲线
            if '177 支池' in nav_data.columns:
                ax.plot(nav_data.index, nav_data['177 支池'], label='177 支池', linewidth=2, color='#2E86AB')
            if '60 支池' in nav_data.columns:
                ax.plot(nav_data.index, nav_data['60 支池'], label='60 支池', linewidth=2, color='#A23B72')
            if '沪深 300' in nav_data.columns:
                ax.plot(nav_data.index, nav_data['沪深 300'], label='沪深 300', linewidth=2, color='#F18F01', linestyle='--')
            
            ax.set_xlabel('日期', fontsize=12)
            ax.set_ylabel('净值', fontsize=12)
            ax.set_title('巴菲特价值投资策略 - 净值曲线对比 (2021-2026)', fontsize=14, fontweight='bold')
            ax.legend(loc='upper left', fontsize=10)
            ax.grid(True, alpha=0.3)
            
            # 格式化 x 轴日期
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.YearLocator())
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            # 保存图表
            file_path = os.path.join(self.output_dir, '净值曲线对比.png')
            plt.savefig(file_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"✅ 生成净值曲线对比图：{file_path}")
            return file_path
            
        except Exception as e:
            print(f"绘制净值曲线失败：{e}")
            return None
    
    def plot_drawdown(self, nav_data: pd.DataFrame) -> Optional[str]:
        """绘制回撤曲线图"""
        try:
            if nav_data.empty:
                return None
            
            fig, ax = plt.subplots(figsize=(14, 5))
            
            # 计算回撤
            for col in nav_data.columns:
                rolling_max = nav_data[col].expanding().max()
                drawdown = (nav_data[col] - rolling_max) / rolling_max * 100
                
                if col == '177 支池':
                    ax.plot(nav_data.index, drawdown, label='177 支池', linewidth=2, color='#2E86AB')
                elif col == '60 支池':
                    ax.plot(nav_data.index, drawdown, label='60 支池', linewidth=2, color='#A23B72')
                elif col == '沪深 300':
                    ax.plot(nav_data.index, drawdown, label='沪深 300', linewidth=2, color='#F18F01', linestyle='--')
            
            ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            ax.set_xlabel('日期', fontsize=12)
            ax.set_ylabel('回撤 %', fontsize=12)
            ax.set_title('巴菲特价值投资策略 - 回撤对比 (2021-2026)', fontsize=14, fontweight='bold')
            ax.legend(loc='lower left', fontsize=10)
            ax.grid(True, alpha=0.3)
            
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.YearLocator())
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            file_path = os.path.join(self.output_dir, '回撤对比.png')
            plt.savefig(file_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"✅ 生成回撤对比图：{file_path}")
            return file_path
            
        except Exception as e:
            print(f"绘制回撤曲线失败：{e}")
            return None
    
    def plot_market_state_distribution(self, market_state_data: pd.DataFrame) -> Optional[str]:
        """绘制市场状态分布图"""
        try:
            if market_state_data.empty:
                return None
            
            # 统计各状态天数
            state_counts = market_state_data['市场状态'].value_counts()
            
            fig, axes = plt.subplots(1, 2, figsize=(14, 5))
            
            # 饼图
            colors = ['#C62828', '#1565C0', '#2E7D32']
            axes[0].pie(state_counts.values, labels=state_counts.index, autopct='%1.1f%%', 
                       colors=colors, startangle=90)
            axes[0].set_title('市场状态分布（天数占比）', fontsize=12, fontweight='bold')
            
            # 柱状图
            axes[1].bar(state_counts.index, state_counts.values, color=colors)
            axes[1].set_xlabel('市场状态', fontsize=12)
            axes[1].set_ylabel('天数', fontsize=12)
            axes[1].set_title('市场状态分布（天数）', fontsize=12, fontweight='bold')
            
            for i, v in enumerate(state_counts.values):
                axes[1].text(i, v + 5, str(v), ha='center', fontsize=10)
            
            plt.tight_layout()
            
            file_path = os.path.join(self.output_dir, '市场状态分布.png')
            plt.savefig(file_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"✅ 生成市场状态分布图：{file_path}")
            return file_path
            
        except Exception as e:
            print(f"绘制市场状态分布失败：{e}")
            return None
    
    def plot_annual_returns(self, nav_data: pd.DataFrame) -> Optional[str]:
        """绘制年度收益对比图"""
        try:
            if nav_data.empty:
                return None
            
            # 计算年度收益
            nav_data['年份'] = nav_data.index.year
            annual_returns = nav_data.groupby('年份').apply(
                lambda x: (x.iloc[-1] / x.iloc[0] - 1) * 100
            ).drop(columns=['年份'], errors='ignore')
            
            fig, ax = plt.subplots(figsize=(14, 7))
            
            x = np.arange(len(annual_returns.index))
            width = 0.25
            
            for i, col in enumerate(annual_returns.columns):
                ax.bar(x + i*width, annual_returns[col], width, label=col)
            
            ax.set_xlabel('年份', fontsize=12)
            ax.set_ylabel('收益率 %', fontsize=12)
            ax.set_title('巴菲特价值投资策略 - 年度收益对比', fontsize=14, fontweight='bold')
            ax.set_xticks(x + width)
            ax.set_xticklabels(annual_returns.index)
            ax.legend(fontsize=10)
            ax.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            
            file_path = os.path.join(self.output_dir, '年度收益对比.png')
            plt.savefig(file_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"✅ 生成年度收益对比图：{file_path}")
            return file_path
            
        except Exception as e:
            print(f"绘制年度收益失败：{e}")
            return None


if __name__ == "__main__":
    # 测试图表生成
    generator = ReportGenerator(output_dir="reports")
    
    # 创建模拟数据
    dates = pd.date_range('2021-01-01', '2026-03-28', freq='D')
    nav_data = pd.DataFrame({
        '177 支池': (np.random.randn(len(dates)).cumsum() / 100 + 1).cumprod(),
        '60 支池': (np.random.randn(len(dates)).cumsum() / 100 * 0.8 + 1).cumprod(),
        '沪深 300': (np.random.randn(len(dates)).cumsum() / 100 * 0.5 + 1).cumprod()
    }, index=dates)
    
    market_state_data = pd.DataFrame({
        '市场状态': np.random.choice(['牛市', '震荡市', '熊市'], len(dates), p=[0.6, 0.3, 0.1])
    }, index=dates)
    
    charts = generator.generate_all_charts(nav_data, market_state_data, {})
    
    print(f"\n✅ 生成了 {len(charts)} 个图表")
    for chart in charts:
        print(f"  - {chart}")
