#!/bin/bash
# 富途 OpenD 安装脚本（Wine + Windows 版）
# 适用于 Ubuntu/Debian Linux

set -e

echo "=============================================="
echo "🍷 富途 OpenD 安装脚本（Wine 版）"
echo "=============================================="

# 检查是否 root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用 sudo 运行此脚本"
    echo "   sudo bash $0"
    exit 1
fi

echo ""
echo "📦 步骤 1/5: 添加 i386 架构..."
dpkg --add-architecture i386

echo ""
echo "📦 步骤 2/5: 更新软件包列表..."
apt update

echo ""
echo "📦 步骤 3/5: 安装 Wine..."
apt install -y wine64 wine32

echo ""
echo "📦 步骤 4/5: 创建 OpenD 目录..."
mkdir -p /home/admin/OpenD
chown admin:admin /home/admin/OpenD

echo ""
echo "📦 步骤 5/5: 创建配置文件目录..."
mkdir -p /home/admin/.futu
chown admin:admin /home/admin/.futu

echo ""
echo "=============================================="
echo "✅ Wine 安装完成！"
echo "=============================================="
echo ""
echo "Wine 版本："
wine --version
echo ""
echo "下一步操作："
echo "1. 下载富途 OpenD Windows 版安装包"
echo "   访问：https://www.futunn.com/download/opend"
echo "   或联系富途客服获取"
echo ""
echo "2. 将下载的 OpenD_Setup.exe 放到 ~/OpenD/ 目录"
echo ""
echo "3. 运行安装："
echo "   cd ~/OpenD"
echo "   wine OpenD_Setup.exe"
echo ""
echo "4. 安装完成后创建配置文件："
echo "   cat > ~/.futu/futu_config.ini << EOF"
echo "[client]"
echo "host = 127.0.0.1"
echo "port = 11111"
echo ""
echo "[connection]"
echo "connect_timeout = 30"
echo "heartbeat_interval = 10"
echo "EOF"
echo ""
echo "5. 启动 OpenD："
echo "   cd ~/OpenD"
echo "   wine OpenD.exe"
echo ""
echo "=============================================="
