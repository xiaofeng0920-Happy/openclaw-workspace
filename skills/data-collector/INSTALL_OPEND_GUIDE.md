# 富途 OpenD 安装指南（Linux/Ubuntu）

**更新日期：** 2026-03-24  
**系统：** Ubuntu 22.04.5 LTS (x86_64)

---

## ⚠️ 当前状态

- OpenD 未安装
- 需要手动下载安装

---

## 📥 安装步骤

### 方法 1：从富途官网下载（推荐）

#### 1. 访问富途 OpenD 下载页面

打开浏览器访问：
```
https://www.futunn.com/download/opend
```

#### 2. 选择 Linux 版本

- 点击下载 **Linux 版 OpenD**
- 下载文件格式：`.tar.gz` 或 `.deb`

#### 3. 解压安装

```bash
# 创建目录
mkdir -p ~/OpenD
cd ~/OpenD

# 解压（假设下载的是 .tar.gz）
tar -xzf ~/Downloads/OpenD_*.tar.gz

# 或者如果是 .deb 文件
sudo dpkg -i ~/Downloads/OpenD_*.deb
```

#### 4. 启动 OpenD

```bash
# 直接运行
~/OpenD/OpenD

# 或使用配置文件
~/OpenD/OpenD --config ~/.futu/futu_config.ini
```

---

### 方法 2：使用 Wine 运行 Windows 版（备选）

如果官方没有 Linux 版，可以使用 Wine 运行 Windows 版：

#### 1. 安装 Wine

```bash
sudo apt update
sudo apt install wine64 -y
```

#### 2. 下载 Windows 版 OpenD

从富途官网下载 Windows 版：
```
https://www.futunn.com/download/opend
```

#### 3. 使用 Wine 运行

```bash
wine ~/Downloads/OpenD_Setup.exe
```

---

### 方法 3：使用 Docker（高级用户）

如果有 Docker，可以运行容器化 OpenD：

```bash
docker run -d \
  --name futu-opend \
  -p 11111:11111 \
  -v ~/.futu:/root/.futu \
  futunn/opend:latest
```

---

## ⚙️ 配置 OpenD

### 创建配置文件

```bash
mkdir -p ~/.futu
cat > ~/.futu/futu_config.ini << EOF
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

### 登录富途账户

1. 启动 OpenD
2. 使用富途牛牛 APP 或手机扫描二维码登录
3. 确保 US 和 HK 市场都连接成功

---

## ✅ 验证安装

### 检查 OpenD 是否运行

```bash
# 检查进程
pgrep -f OpenD

# 检查端口
netstat -tlnp | grep 11111
```

### 测试连接

```bash
cd /home/admin/openclaw/workspace/skills/data-collector
python3 futu_collector.py
```

预期输出：
```
🔌 检查 OpenD 状态...
  ✅ OpenD 运行中

📈 获取持仓数据...
正在从富途 OpenD 获取持仓...
  ✅ 美股持仓：8 只
  ✅ 港股持仓：5 只
```

---

## 🔧 常见问题

### Q1: 下载链接失效？

**解决：** 联系富途客服获取最新下载链接，或访问富途牛牛官网。

### Q2: 无法启动 OpenD？

**解决：**
- 检查依赖库：`ldd ~/OpenD/OpenD`
- 安装缺失的库：`sudo apt install <missing-lib>`

### Q3: 连接失败？

**解决：**
- 检查防火墙：`sudo ufw allow 11111`
- 检查配置文件路径：`~/.futu/futu_config.ini`
- 确保已登录富途账户

---

## 📞 富途客服

- **官网：** https://www.futunn.com
- **客服邮箱：** support@futunn.com
- **帮助文档：** https://www.futunn.com/help

---

## 📝 下一步

安装完成后运行：

```bash
# 测试富途数据收集器
python3 skills/data-collector/futu_collector.py --send

# 更新持仓监控使用富途数据源
python3 agents/holding-analyzer/run.py --futu --send
```

---

*最后更新：2026-03-24*
