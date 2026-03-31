# 富途 OpenD 快速安装指南

**检查时间：** 2026-03-31 10:07  
**当前状态：** OpenD 未安装

---

## 📥 方法 1：Linux 命令行安装（推荐）

### 1. 下载安装脚本

```bash
cd ~
mkdir -p OpenD
cd OpenD

# 下载 Linux 版 OpenD
wget https://www.futunn.com/download/opend-linux -O OpenD.tar.gz

# 或备用下载地址
# wget https://static.futunn.com/futu/opend/linux/OpenD.tar.gz
```

### 2. 解压

```bash
tar -xzf OpenD.tar.gz
```

### 3. 配置

```bash
# 创建配置目录
mkdir -p ~/.futu

# 创建配置文件
cat > ~/.futu/futu_config.ini << 'EOF'
[client]
host = 127.0.0.1
port = 11111
# password = 你的密码（可选）
# password_md5 = 密码的 MD5（可选）

[connection]
connect_timeout = 30
heartbeat_interval = 10
EOF
```

### 4. 启动

```bash
cd ~/OpenD
./OpenD --config ~/.futu/futu_config.ini
```

### 5. 登录

在终端中会显示二维码，使用富途牛牛 APP 扫码登录。

---

## 📥 方法 2：使用 OpenClaw 技能

```bash
# 查看可用技能
openclaw skills

# 查找 install-opend 技能
openclaw skills | grep -i opend
```

---

## 📥 方法 3：手动下载

访问官网下载页面：
https://www.futunn.com/download/opend

选择对应操作系统版本下载。

---

## ✅ 验证安装

```bash
cd /home/admin/openclaw/workspace/agents/holding-analyzer
python3 check_opend.py
```

预期输出：
```
✅ OpenD 正在运行
✅ 端口已监听：11111
✅ 配置文件存在
✅ futu 已安装
```

---

## 🔌 测试连接

```bash
python3 test_futu.py
```

预期输出：
```
✅ 报价上下文已连接
✅ 交易上下文已连接
AAPL 价格：$xxx.xx
美股持仓：x 只
```

---

## 🚀 使用真实持仓数据

```bash
# 使用富途真实持仓执行监控
python3 run.py --futu

# 使用富途持仓并发送飞书通知
python3 run.py --futu --send
```

---

## ⚠️ 常见问题

### Q: 下载失败
A: 尝试备用下载地址或使用方法 3 手动下载

### Q: 启动失败 "Permission denied"
A: 添加执行权限：`chmod +x OpenD`

### Q: 连接失败 "Connection refused"
A: 检查 OpenD 是否启动，端口是否正确

### Q: 登录失败
A: 确保富途账户已开通港股/美股交易权限

---

## 📞 技术支持

- 富途官方文档：https://www.futunn.com/download/opend
- OpenD 用户群：富途牛牛 APP 内搜索"OpenD"

---

**创建时间：** 2026-03-31 10:07  
**最后更新：** 2026-03-31 10:07
