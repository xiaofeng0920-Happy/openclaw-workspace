# buffett-investor 配置参数

"""
巴菲特价值投资技能配置参数
可根据实际投资偏好调整
"""

# ========== 筛选条件 ==========
# 基础筛选（177 支池）
PE_MAX = 30  # PE_TTM 上限
ROE_MIN = 8  # ROE 下限%
ROIC_MIN = 8  # ROIC 下限%
MARKET_CAP_MIN = 30  # 近 5 年市值下限（亿）

# 严格筛选（60 支池）额外条件
DEBT_RATIO_MAX = 50  # 资产负债率上限%
FCF_POSITIVE_YEARS = 5  # 连续正自由现金流年数

# ========== 市场状态识别 ==========
# 牛市条件（需同时满足）
BULL_PRICE_VS_MA250 = "above"  # 收盘价 vs MA250
BULL_MA250_SLOPE_MIN = 0  # MA250 斜率最小值
BULL_RSI14_MIN = 50  # RSI(14) 最小值
BULL_MARKET_BREADTH_MIN = 0.60  # 市场广度最小值

# 熊市条件（满足 2 个及以上）
BEAR_PRICE_VS_MA250 = "below"  # 收盘价 vs MA250
BEAR_MA250_SLOPE_MAX = 0  # MA250 斜率最大值
BEAR_RSI14_MAX = 40  # RSI(14) 最大值
BEAR_MARKET_BREADTH_MAX = 0.40  # 市场广度最大值

# ========== 动态配置 ==========
# 仓位配置
BULL_POSITION_MIN = 0.90  # 牛市最低仓位
BULL_POSITION_MAX = 1.00  # 牛市最高仓位

BEAR_POSITION_MIN = 0.50  # 熊市最低仓位
BEAR_POSITION_MAX = 0.70  # 熊市最高仓位

OSCILLATE_POSITION_MIN = 0.70  # 震荡市最低仓位
OSCILLATE_POSITION_MAX = 0.85  # 震荡市最高仓位

# 行业权重调整（相对基准）
BULL_CYCLICAL_OVERWEIGHT = 0.20  # 牛市超配周期行业
BULL_GROWTH_OVERWEIGHT = 0.15  # 牛市超配成长行业
BULL_DEFENSIVE_UNDERWEIGHT = -0.10  # 牛市低配防御行业

BEAR_DEFENSIVE_OVERWEIGHT = 0.25  # 熊市超配防御行业
BEAR_HIGH_DIVIDEND_OVERWEIGHT = 0.15  # 熊市超配高股息
BEAR_CYCLICAL_UNDERWEIGHT = -0.20  # 熊市低配周期行业

OSCILLATE_CONSUMER_OVERWEIGHT = 0.05  # 震荡市超配消费
OSCILLATE_PHARMA_OVERWEIGHT = 0.05  # 震荡市超配医药
OSCILLATE_UTILITY_OVERWEIGHT = 0.05  # 震荡市超配公用事业

# ========== 个股筛选规则 ==========
# 牛市
BULL_BETA_MIN = 1.2  # 高 Beta 股票
BULL_PE_MAX = 35  # 适度放宽估值

# 熊市
BEAR_DEBT_RATIO_MAX = 40  # 强化财务安全
BEAR_DIVIDEND_YIELD_MIN = 0.03  # 股息率>3%
BEAR_VOLATILITY_MAX = 0.20  # 低波动股票

# 震荡市
OSCILLATE_ROE_STABILITY_MIN = 0.70  # ROE 稳定性
OSCILLATE_PE_MAX = 25  # 估值限制
OSCILLATE_VOLATILITY_MAX = 0.25  # 低波动

# ========== 调仓机制 ==========
REBALANCE_FREQUENCY = "monthly"  # monthly/quarterly
REBALANCE_DAY = 1  # 每月第 1 个交易日
QUARTERLY_REBALANCE_MONTHS = [1, 4, 7, 10]  # 季度调仓月份

MAX_TURNOVER = 0.30  # 最大换手率%
MAX_SINGLE_TRADE_RATIO = 0.05  # 单笔交易最大占比%

# 调仓触发条件
REBALANCE_THRESHOLD = 0.05  # 权重偏离>5% 触发调仓

# ========== 风险控制 ==========
MAX_DRAWDOWN_THRESHOLD = 0.15  # 回撤>15% 触发减仓
DRAWDOWN_REDUCE_POSITION = 0.20  # 触发减仓 20%

MAX_POSITION_SINGLE_STOCK = 0.05  # 单只股票最大仓位 5%
MAX_POSITION_SINGLE_INDUSTRY = 0.20  # 单行业最大仓位 20%

STOP_LOSS_RATIO = 0.10  # 单只股票止损线 10%
TAKE_PROFIT_RATIO = 0.40  # 单只股票止盈线 40%

# ========== 股票池定义 ==========
# 177 支池：基础筛选
STOCK_POOL_177 = {
    "name": "177 支全行业股票池",
    "pe_max": 30,
    "roe_min": 8,
    "roic_min": 8,
    "market_cap_min": 30,
    "count": 177
}

# 60 支池：严格筛选
STOCK_POOL_60 = {
    "name": "60 支严格财务筛选股票池",
    "pe_max": 30,
    "roe_min": 8,
    "roic_min": 8,
    "market_cap_min": 30,
    "debt_ratio_max": 50,
    "fcf_positive_years": 5,
    "count": 60
}

# 120 支池：中等筛选
STOCK_POOL_120 = {
    "name": "120 支中等筛选股票池",
    "pe_max": 30,
    "roe_min": 8,
    "roic_min": 8,
    "market_cap_min": 30,
    "debt_ratio_max": 60,
    "count": 120
}

# ========== 行业分类 ==========
INDUSTRY_MAP = {
    "白酒与葡萄酒": ["600519.SH", "000858.SZ", "000568.SZ", "603369.SH", "000596.SZ", "603198.SH"],
    "中药": ["600285.SH", "300181.SZ", "600085.SH", "600993.SH", "002275.SZ"],
    "工业机械": ["002611.SZ", "002158.SZ", "002690.SZ", "603025.SH"],
    "西药": ["002001.SZ", "002020.SZ", "601089.SH"],
    "电气部件与设备": ["603195.SH", "600406.SH", "603013.SH"],
    "铝": ["000807.SZ", "601702.SH"],
    "医疗保健设备": ["300760.SZ", "300832.SZ"],
    "有线和卫星电视": ["301262.SZ", "300770.SZ"],
    "海港与服务": ["600018.SH", "601298.SH"],
    "煤炭与消费用燃料": ["601088.SH", "601225.SH"],
    "基础化工": ["600273.SH", "605099.SH"],
    "生物科技": ["300896.SZ", "300685.SZ"],
    "服装、服饰与奢侈品": ["002867.SZ", "002832.SZ"]
}

# 行业分类（按防御/周期/成长）
DEFENSIVE_INDUSTRIES = ["白酒与葡萄酒", "中药", "西药", "医疗保健设备", "海港与服务"]
CYCLICAL_INDUSTRIES = ["铝", "煤炭与消费用燃料", "基础化工", "工业机械"]
GROWTH_INDUSTRIES = ["生物科技", "电气部件与设备", "有线和卫星电视"]
CONSUMER_INDUSTRIES = ["服装、服饰与奢侈品"]

# ========== 绩效基准 ==========
BENCHMARK_INDEX = "000300.SH"  # 沪深 300
BENCHMARK_NAME = "沪深 300 指数"

# ========== 数据源配置 ==========
DATA_SOURCE = {
    "price": "tushare",  # 行情数据：tushare/akshare/futu_openD【Tushare 优先】
    "financial": "tushare",  # 财务数据：tushare/akshare【Tushare 优先】
    "index": "tushare"  # 指数数据：tushare/akshare【Tushare 优先】
}

# Tushare Token（需配置）
TUSHARE_TOKEN_PATH = "/home/admin/openclaw/workspace/agents/data-collector/.tushare_token"

# ========== 日志与报告 ==========
LOG_LEVEL = "INFO"
LOG_PATH = "/home/admin/openclaw/workspace/skills/buffett-investor/logs"
REPORT_PATH = "/home/admin/openclaw/workspace/skills/buffett-investor/reports"

# ========== 版本 ==========
VERSION = "1.0.0"
LAST_UPDATED = "2026-03-28"
