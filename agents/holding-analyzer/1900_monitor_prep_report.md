# 📊 19:00 持仓监控任务 - 准备报告

**准备时间：** 2026-03-28 18:20  
**执行时间：** 2026-03-28 19:00 (约 40 分钟后)  
**准备状态：** ✅ 已完成

---

## ✅ 准备工作清单

### 1. 脚本状态检查

| 脚本 | 状态 | 位置 |
|------|------|------|
| `run.py` | ✅ 正常 | `/home/admin/openclaw/workspace/agents/holding-analyzer/run.py` |
| `product_scale_monitor.py` | ✅ 正常 | `/home/admin/openclaw/workspace/agents/holding-analyzer/product_scale_monitor.py` |
| `notify_feishu.py` | ✅ 正常 | `/home/admin/openclaw/workspace/agents/holding-analyzer/notify_feishu.py` |
| `run_1900_monitor.sh` | ✅ 已创建 | `/home/admin/openclaw/workspace/agents/holding-analyzer/run_1900_monitor.sh` |

### 2. 飞书推送配置

| 配置项 | 值 | 状态 |
|--------|-----|------|
| App ID | `cli_a92873946239dbd1` | ✅ |
| User ID | `ou_52fa8f508e88e1efbcbe50c014ecaa6e` | ✅ |
| API 连接 | Token 获取成功 | ✅ |

### 3. 定时任务设置

| 任务 | 时间 | 状态 |
|------|------|------|
| at job #1 | 2026-03-28 19:00:00 | ✅ 已设置 |

**查看任务：** `atq`  
**查看任务内容：** `at -c 1`  
**删除任务：** `atrm 1`

### 4. 执行内容

19:00 将执行以下任务：

1. **持仓分析** (`run.py --send`)
   - 分析配置持仓（基准日期：2026-03-16）
   - 检测显著变化（阈值：±3.0%）
   - 生成 Markdown 报告
   - 推送飞书通知（如有显著变化）

2. **产品规模监控** (`product_scale_monitor.py --send`)
   - 读取最新产品规模数据
   - 检查规模预警（<500 万紧急，<1000 万关注）
   - 生成规模报告
   - 推送飞书预警（如有预警产品）

3. **日志记录**
   - 日志文件：`/tmp/holding-analyzer-1900.log`
   - 实时查看：`tail -f /tmp/holding-analyzer-1900.log`

---

## 📋 当前持仓概况

### 显著变化股票（参考 13:29 数据）

| 股票 | 代码 | 变化 | 状态 |
|------|------|------|------|
| 腾讯控股 | 00700 | -15.63% | 📉 大幅下跌 |
| 南方日经 225 | 03153 | -10.42% | 📉 大幅下跌 |
| 谷歌-A | GOOGL | -8.51% | 📉 下跌 |
| 甲骨文 | ORCL | -8.51% | 📉 下跌 |
| 特斯拉 | TSLA | -7.51% | 📉 下跌 |
| 英伟达 | NVDA | -7.06% | 📉 下跌 |
| 微软 | MSFT | -6.54% | 📉 下跌 |
| 可口可乐 | KO | +3.89% | 📈 上涨 |

### 产品规模预警

| 产品 | 规模 (万元) | 状态 |
|------|-----------|------|
| 前锋 8 号 | 224.64 | 🔴 紧急 (<500 万) |
| 前锋 6 号 | 191.18 | 🔴 紧急 (<500 万) |
| 乾享 1 号 | 712.88 | 🟡 关注 (<1000 万) |
| 前沿 1 号 | 995.35 | 🟡 关注 (<1000 万) |
| 领航 FOF 1 号 | 986.69 | 🟡 关注 (<1000 万) |

---

## 🔧 应急操作

### 手动执行（如需提前测试）
```bash
cd /home/admin/openclaw/workspace/agents/holding-analyzer
./run_1900_monitor.sh
```

### 取消定时任务
```bash
atrm 1
```

### 查看日志
```bash
tail -f /tmp/holding-analyzer-1900.log
```

### 单独测试飞书推送
```bash
cd /home/admin/openclaw/workspace/agents/holding-analyzer
python3 notify_feishu.py reports/report_20260328_132957.md
```

---

## 📞 推送接收人

- **飞书用户 ID:** `ou_52fa8f508e88e1efbcbe50c014ecaa6e` (锋哥)
- **推送条件:** 
  - 持仓变化超过 ±3.0%
  - 产品规模低于 1000 万（关注）或 500 万（紧急）

---

*准备完成，等待 19:00 自动执行*
