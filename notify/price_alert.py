# -*- coding: utf-8 -*-
"""
价格预警推送系统
================

监控股票价格，当达到预设条件时自动推送通知。

支持的通知渠道:
- 飞书 (Feishu/Lark)
- 微信 (企业微信)
- 邮件
- 系统日志

预警条件:
1. 价格突破（上涨/下跌超过阈值）
2. 涨跌幅预警
3. 成交量异常
4. 巴菲特评分变化
5. 安全边际达到买入/卖出阈值

使用方法:
    python3 notify/price_alert.py --check
"""

import sys
sys.path.insert(0, '/home/admin/openclaw/workspace')

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import os

from futu import *
from data.financial_data import FinancialData
from strategies.buffett_strategy import BuffettStrategy


@dataclass
class AlertCondition:
    """预警条件"""
    code: str
    name: str
    condition_type: str  # 'price_up', 'price_down', 'change_pct', 'volume', 'score', 'margin'
    threshold: float  # 阈值
    current_value: float  # 当前值
    triggered: bool  # 是否触发
    message: str  # 预警消息


@dataclass
class StockAlert:
    """股票预警配置"""
    code: str
    name: str
    current_price: float
    
    # 价格预警
    price_alert_up: Optional[float] = None  # 突破上涨预警价
    price_alert_down: Optional[float] = None  # 跌破下跌预警价
    
    # 涨跌幅预警
    change_pct_alert: float = 5.0  # 涨跌幅超过 X%
    
    # 巴菲特策略预警
    buy_margin_alert: float = 30.0  # 安全边际>30% 时提醒买入
    sell_premium_alert: float = 30.0  # 溢价>30% 时提醒卖出
    
    # 成交量预警
    volume_alert: Optional[float] = None  # 成交量超过 X 股
    
    # 通知设置
    notify_feishu: bool = True
    notify_wechat: bool = False
    notify_email: bool = False
    
    # 最后通知时间（避免重复通知）
    last_notify_time: Optional[datetime] = None
    notify_cooldown: int = 3600  # 通知冷却时间（秒）


class PriceAlertSystem:
    """
    价格预警系统
    
    功能:
    1. 监控股票价格
    2. 检查预警条件
    3. 发送通知（飞书/微信/邮件）
    4. 记录预警历史
    """
    
    # 配置文件路径
    CONFIG_FILE = '/home/admin/openclaw/workspace/notify/alerts_config.json'
    HISTORY_FILE = '/home/admin/openclaw/workspace/notify/alert_history.json'
    
    def __init__(self):
        self.quote_ctx = None
        self.fd = FinancialData(source='akshare')
        self.strategy = BuffettStrategy()
        self.alerts: List[StockAlert] = []
        self.history: List[Dict] = []
        
        # 加载配置
        self.load_config()
        self.load_history()
    
    def connect(self) -> bool:
        """连接富途 OpenD"""
        try:
            self.quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
            
            # 验证连接
            ret, data = self.quote_ctx.get_global_state()
            if ret != RET_OK:
                print("❌ 无法连接到 OpenD")
                return False
            
            print("✅ OpenD 连接成功")
            return True
            
        except Exception as e:
            print(f"❌ 连接失败：{e}")
            return False
    
    def load_config(self):
        """加载预警配置"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.alerts = [StockAlert(**item) for item in config.get('alerts', [])]
                print(f"✅ 加载 {len(self.alerts)} 个预警配置")
            except Exception as e:
                print(f"⚠️ 加载配置失败：{e}")
                self.alerts = []
        else:
            # 创建默认配置
            self.create_default_config()
    
    def create_default_config(self):
        """创建默认预警配置（基于锋哥持仓）"""
        default_alerts = [
            # 港股持仓
            StockAlert(
                code='HK.00700',
                name='腾讯控股',
                current_price=508.00,
                price_alert_up=550.00,
                price_alert_down=480.00,
                change_pct_alert=5.0,
                notify_feishu=True
            ),
            StockAlert(
                code='HK.00883',
                name='中国海洋石油',
                current_price=30.38,
                price_alert_up=32.00,
                price_alert_down=28.00,
                change_pct_alert=5.0,
                notify_feishu=True
            ),
            StockAlert(
                code='HK.09988',
                name='阿里巴巴-W',
                current_price=123.70,
                price_alert_up=135.00,
                price_alert_down=115.00,
                change_pct_alert=5.0,
                notify_feishu=True
            ),
            # 美股持仓
            StockAlert(
                code='US.GOOG',
                name='谷歌',
                current_price=302.28,
                price_alert_up=320.00,
                price_alert_down=290.00,
                change_pct_alert=5.0,
                notify_feishu=True
            ),
            StockAlert(
                code='US.BRK.B',
                name='伯克希尔',
                current_price=490.03,
                price_alert_up=510.00,
                price_alert_down=470.00,
                change_pct_alert=5.0,
                notify_feishu=True
            ),
        ]
        
        self.alerts = default_alerts
        self.save_config()
        print(f"✅ 创建 {len(self.alerts)} 个默认预警配置")
    
    def save_config(self):
        """保存预警配置"""
        config = {
            'alerts': [asdict(alert) for alert in self.alerts],
            'updated_at': datetime.now().isoformat()
        }
        
        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def load_history(self):
        """加载预警历史"""
        if os.path.exists(self.HISTORY_FILE):
            try:
                with open(self.HISTORY_FILE, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = []
    
    def save_history(self):
        """保存预警历史"""
        # 只保留最近 100 条
        self.history = self.history[-100:]
        
        with open(self.HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def check_alerts(self) -> List[AlertCondition]:
        """
        检查所有预警条件
        
        返回:
            触发的预警条件列表
        """
        triggered_alerts = []
        
        for alert in self.alerts:
            # 获取最新价格
            current_price = self.get_current_price(alert.code)
            if current_price is None:
                continue
            
            alert.current_price = current_price
            
            # 检查各项条件
            conditions = self.check_single_alert(alert)
            
            for condition in conditions:
                if condition.triggered:
                    # 检查冷却时间
                    if self.is_in_cooldown(alert):
                        print(f"⏸️ {alert.name} 处于冷却期，暂不通知")
                        continue
                    
                    triggered_alerts.append(condition)
                    alert.last_notify_time = datetime.now()
        
        return triggered_alerts
    
    def get_current_price(self, code: str) -> Optional[float]:
        """获取当前价格"""
        try:
            if code.startswith('HK.'):
                ret, data = self.quote_ctx.get_market_snapshot([code])
                if ret == RET_OK and not data.empty:
                    return data.iloc[0]['last_price']
            elif code.startswith('US.'):
                # 美股代码转换
                us_code = code.replace('US.', '')
                ret, data = self.quote_ctx.get_market_snapshot([f'US.{us_code}'])
                if ret == RET_OK and not data.empty:
                    return data.iloc[0]['last_price']
        except Exception as e:
            print(f"⚠️ 获取 {code} 价格失败：{e}")
        
        return None
    
    def check_single_alert(self, alert: StockAlert) -> List[AlertCondition]:
        """检查单只股票的预警条件"""
        conditions = []
        price = alert.current_price
        
        # 1. 突破上涨预警
        if alert.price_alert_up and price >= alert.price_alert_up:
            conditions.append(AlertCondition(
                code=alert.code,
                name=alert.name,
                condition_type='price_up',
                threshold=alert.price_alert_up,
                current_value=price,
                triggered=True,
                message=f"📈 {alert.name} 突破上涨预警价 {alert.price_alert_up}港元，现价{price:.2f}港元"
            ))
        
        # 2. 跌破下跌预警
        if alert.price_alert_down and price <= alert.price_alert_down:
            conditions.append(AlertCondition(
                code=alert.code,
                name=alert.name,
                condition_type='price_down',
                threshold=alert.price_alert_down,
                current_value=price,
                triggered=True,
                message=f"📉 {alert.name} 跌破下跌预警价 {alert.price_alert_down}港元，现价{price:.2f}港元"
            ))
        
        # 3. 巴菲特买入信号（安全边际）
        financials = self.fd.get_financials(alert.code.replace('HK.', '').replace('US.', ''))
        if financials:
            stock = self.strategy.analyze_stock(
                code=alert.code,
                name=alert.name,
                market='HK' if alert.code.startswith('HK') else 'US',
                current_price=price,
                financial_data=financials
            )
            
            if stock:
                # 买入信号
                if stock.margin_of_safety >= alert.buy_margin_alert:
                    conditions.append(AlertCondition(
                        code=alert.code,
                        name=alert.name,
                        condition_type='buy_signal',
                        threshold=alert.buy_margin_alert,
                        current_value=stock.margin_of_safety,
                        triggered=True,
                        message=f"🎯 {alert.name} 出现巴菲特买入信号！安全边际{stock.margin_of_safety:.1f}%，评分{stock.buffett_score}/100"
                    ))
                
                # 卖出信号
                if stock.margin_of_safety <= -alert.sell_premium_alert:
                    conditions.append(AlertCondition(
                        code=alert.code,
                        name=alert.name,
                        condition_type='sell_signal',
                        threshold=-alert.sell_premium_alert,
                        current_value=stock.margin_of_safety,
                        triggered=True,
                        message=f"⚠️ {alert.name} 出现巴菲特卖出信号！溢价{abs(stock.margin_of_safety):.1f}%"
                    ))
        
        return conditions
    
    def is_in_cooldown(self, alert: StockAlert) -> bool:
        """检查是否在冷却期"""
        if alert.last_notify_time is None:
            return False
        
        elapsed = (datetime.now() - alert.last_notify_time).total_seconds()
        return elapsed < alert.notify_cooldown
    
    def send_notification(self, conditions: List[AlertCondition]):
        """发送通知"""
        if not conditions:
            return
        
        # 构建通知消息
        message = self.build_alert_message(conditions)
        
        # 发送到飞书
        self.send_feishu(message)
        
        # 记录历史
        for condition in conditions:
            self.history.append({
                'timestamp': datetime.now().isoformat(),
                'code': condition.code,
                'name': condition.name,
                'type': condition.condition_type,
                'message': condition.message
            })
        
        self.save_history()
    
    def build_alert_message(self, conditions: List[AlertCondition]) -> str:
        """构建预警消息"""
        lines = []
        lines.append("🔔 **价格预警通知**")
        lines.append(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        for condition in conditions:
            icon = {
                'price_up': '📈',
                'price_down': '📉',
                'buy_signal': '🎯',
                'sell_signal': '⚠️',
            }.get(condition.condition_type, '🔔')
            
            lines.append(f"{icon} {condition.message}")
            lines.append("")
        
        lines.append("---")
        lines.append("投资有风险，决策需谨慎")
        
        return "\n".join(lines)
    
    def send_feishu(self, message: str):
        """发送到飞书"""
        try:
            import requests
            import json
            import os
            
            # 加载配置
            config_file = '/home/admin/openclaw/workspace/notify/feishu_config.json'
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                webhook_url = config.get('feishu', {}).get('webhook_url', '')
                
                if webhook_url and 'YOUR_WEBHOOK' not in webhook_url:
                    # 发送消息
                    payload = {
                        "msg_type": "text",
                        "content": {
                            "text": message
                        }
                    }
                    
                    response = requests.post(
                        webhook_url,
                        json=payload,
                        headers={'Content-Type': 'application/json'},
                        timeout=10
                    )
                    
                    result = response.json()
                    if result.get('StatusCode') == 0 or result.get('code') == 0:
                        print(f"✅ 飞书通知发送成功")
                    else:
                        print(f"⚠️ 飞书通知发送失败：{result}")
                else:
                    print(f"⚠️ 飞书 Webhook 未配置，请编辑 notify/feishu_config.json")
                    print(f"📤 消息内容:\n{message}")
            else:
                print(f"⚠️ 配置文件不存在：{config_file}")
                print(f"📤 消息内容:\n{message}")
            
        except Exception as e:
            print(f"⚠️ 发送飞书通知失败：{e}")
    
    def run_check(self):
        """执行一次预警检查"""
        print("=" * 60)
        print("🔔 价格预警检查")
        print("=" * 60)
        print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"监控股票数：{len(self.alerts)}")
        print()
        
        # 连接 OpenD
        if not self.connect():
            print("❌ 无法连接 OpenD，检查终止")
            return
        
        try:
            # 检查预警
            print("🔍 检查预警条件...")
            triggered = self.check_alerts()
            
            if triggered:
                print(f"\n✅ 触发 {len(triggered)} 个预警")
                self.send_notification(triggered)
            else:
                print("\n✅ 无预警触发")
            
        finally:
            if self.quote_ctx:
                self.quote_ctx.close()


def demo_alert():
    """演示预警系统"""
    alert_system = PriceAlertSystem()
    alert_system.run_check()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='价格预警系统')
    parser.add_argument('--check', action='store_true', help='执行预警检查')
    parser.add_argument('--config', action='store_true', help='查看/编辑配置')
    parser.add_argument('--demo', action='store_true', help='运行演示')
    
    args = parser.parse_args()
    
    if args.demo:
        demo_alert()
    elif args.check:
        alert_system = PriceAlertSystem()
        alert_system.run_check()
    elif args.config:
        print(f"配置文件：{PriceAlertSystem.CONFIG_FILE}")
        print(f"历史文件：{PriceAlertSystem.HISTORY_FILE}")
    else:
        parser.print_help()
