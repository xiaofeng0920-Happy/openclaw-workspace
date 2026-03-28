# 富途 OpenD 接入指南

## 1. 安装 OpenD

如果还没安装，使用以下命令：

```bash
# 使用 OpenClaw 技能安装
openclaw skill install-opend
```

或手动安装：
- Windows/Mac/Linux 下载地址：https://www.futunn.com/download/opend
- 安装后启动 OpenD

## 2. 配置 OpenD

### 2.1 创建配置文件

创建 `~/.futu/futu_config.ini`：

```ini
[client]
# OpenD 监听地址
host = 127.0.0.1
port = 11111

# 密码验证（可选，建议设置）
# password = 你的密码
# password_md5 = 密码的 MD5（如果设置了这个，password 会被忽略）

[connection]
# 连接超时（秒）
connect_timeout = 30

# 心跳间隔（秒）
heartbeat_interval = 10
```

### 2.2 启动 OpenD

```bash
# Linux/Mac
~/OpenD/OpenD --config ~/.futu/futu_config.ini

# Windows
# 运行 OpenD.exe，在界面中配置端口和密码
```

### 2.3 登录富途账户

在 OpenD 界面中：
1. 点击"登录"
2. 使用富途牛牛/手机 APP 扫码登录
3. 确保 US 和 HK 市场都连接成功

## 3. 测试连接

```bash
cd /home/admin/openclaw/workspace/agents/holding-analyzer
python futu_data.py
```

预期输出：
```
✅ 报价上下文已连接
✅ 交易上下文已连接
AAPL 价格：{'price': 247.99, 'change_pct': -0.85, ...}
美股持仓：9 只
  AAPL: 191 股，盈亏 +2.34%
  ...
```

## 4. 启用实盘数据

修改 `run.py`，添加 `--futu` 参数：

```bash
# 使用富途真实持仓
python run.py --futu

# 使用富途持仓并发送飞书通知
python run.py --futu --send
```

## 5. 更新定时任务

编辑 `CRON.md`，将定时任务改为使用 `--futu` 参数。

## 常见问题

### Q: 连接失败 "Connection refused"
A: 确保 OpenD 已启动，检查端口 11111 是否监听

### Q: 获取持仓为空
A: 确保已在 OpenD 中登录富途账户，且账户有持仓

### Q: 密码验证失败
A: 检查 `futu_config.py` 中的密码配置，或使用密码的 MD5

## 安全提示

- OpenD 建议设置密码验证
- 不要将配置文件提交到 Git
- 生产环境建议限制 OpenD 只监听本地 (127.0.0.1)
