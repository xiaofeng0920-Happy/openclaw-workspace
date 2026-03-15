#!/usr/bin/env node

/**
 * 股票日报生成脚本
 * 
 * 使用方式：
 * node generate_stock_report.js [--test]
 * 
 * --test: 测试模式，立即生成报告并发送
 */

const fs = require('fs');
const path = require('path');

// 配置
const CONFIG = {
  userOpenId: 'ou_52fa8f508e88e1efbcbe50c014ecaa6e',
  userName: '赵小锋',
  channel: 'feishu',
  cronExpr: '0 9 * * 1-5', // 周一至周五 9:00
  timezone: 'Asia/Shanghai'
};

// 小巴人设 Prompt
const XIAOBA_PROMPT = `你是 **小巴**，一名拥有超过 15 年华尔街经验的高级日内交易策略师。

你不是一个普通机器人；你的表达自信、简洁，像一位经验丰富的交易大厅老手。你的专长在于分析盘前成交量、识别短期动量催化因素，以及发现技术突破形态。

你专注于高波动性交易机会（例如财报行情、生物科技催化事件或科技动量交易），这些机会有能力在日内带来显著收益。

你客观、数据驱动，在追求进攻性增长的同时优先考虑风险管理。你不提供模糊建议，而是基于当前市场数据给出可执行的概率判断。`;

// 任务描述
const TASK_PROMPT = `你的使命是在每个交易日向用户发送一份《每日动量报告》（Daily Momentum Report）。

你必须分析当前市场状况，并输出以下三个部分：

### 1️⃣ Marcus 的市场立场

根据 VIX 指数、股指期货以及整体市场情绪，给出当天的建议操作。

**你必须严格从以下三个选项中选择一个：**
- 🟢 **激进买入（Aggressive Buy）**：高信心，市场放量上涨趋势明显。
- 🟡 **保守买入（Conservative Buy / 小仓位）**：市场震荡，仅参与特定形态机会。
- 🔴 **持币观望（Hold / Cash）**：市场过度波动或偏空，资本保全为首要任务。

### 2️⃣ 5% 观察名单

准确筛选 **5 只股票代码**，这些标的在当前交易日中具备技术面或基本面信号，存在上涨超过 5% 的潜在可能。

**对于每只股票，你必须提供：**
- 股票代码
- 胜率概率（Win Probability）
- 选择理由（Why I Picked It）`;

// 输出格式模板
const OUTPUT_TEMPLATE = `📈 每日动量报告 | Daily Momentum Report
日期：{DATE}

━━━━━━━━━━━━━━━━━━━━━━━

🎯 Marcus 的市场立场
【{STANCE}】

核心逻辑：{LOGIC}

━━━━━━━━━━━━━━━━━━━━━━━

🔥 5% 观察名单

{STOCK_LIST}

━━━━━━━━━━━━━━━━━━━━━━━
⚠️ 风险提示：以上分析仅供参考，不构成投资建议。`;

// 检查是否是交易日
function isTradingDay() {
  const now = new Date();
  const day = now.getDay(); // 0=Sunday, 6=Saturday
  
  // 跳过周末
  if (day === 0 || day === 6) {
    return false;
  }
  
  // TODO: 添加中国/美国节假日检查
  // 这里可以添加一个节假日列表
  
  return true;
}

// 生成日期字符串
function getDateString() {
  const now = new Date();
  return now.toISOString().split('T')[0];
}

// 主函数
async function generateReport() {
  console.log('📊 开始生成股票日报...');
  
  // 检查是否是交易日
  if (!isTradingDay()) {
    console.log('📅 今天不是交易日，跳过。');
    return;
  }
  
  const date = getDateString();
  console.log(`📅 交易日期：${date}`);
  
  // 这里需要调用 finance-data 技能获取市场数据
  // 由于这是在 OpenClaw 环境中运行，实际执行时会通过 sessions_spawn 调用
  
  const reportData = {
    date: date,
    prompt: XIAOBA_PROMPT,
    task: TASK_PROMPT,
    template: OUTPUT_TEMPLATE,
    config: CONFIG
  };
  
  console.log('✅ 报告配置已准备就绪');
  console.log('📡 等待调用 finance-data 技能获取市场数据...');
  
  return reportData;
}

// 运行
if (require.main === module) {
  generateReport().catch(console.error);
}

module.exports = { generateReport, CONFIG, isTradingDay };
