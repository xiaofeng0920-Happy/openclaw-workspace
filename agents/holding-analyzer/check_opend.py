#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动富途 OpenD 检查脚本
"""

import subprocess
import sys
from pathlib import Path

print("=" * 60)
print("🔍 富途 OpenD 状态检查")
print("=" * 60)

# 检查 1: OpenD 进程
print("\n1️⃣  检查 OpenD 进程...")
result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
opend_processes = [line for line in result.stdout.split('\n') if 'OpenD' in line and 'grep' not in line]

if opend_processes:
    print("   ✅ OpenD 正在运行:")
    for proc in opend_processes[:3]:
        print(f"      {proc[:100]}")
else:
    print("   ❌ OpenD 未运行")
    print("\n   💡 启动方法:")
    print("      1. 手动启动：~/OpenD/OpenD --config ~/.futu/futu_config.ini")
    print("      2. 或使用 OpenClaw 技能：openclaw skill install-opend")

# 检查 2: 监听端口
print("\n2️⃣  检查端口监听...")
try:
    result = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True)
    ports = [line for line in result.stdout.split('\n') if ':11111' in line or ':11112' in line]
    
    if ports:
        print("   ✅ 端口已监听:")
        for port in ports:
            print(f"      {port.strip()}")
    else:
        print("   ❌ 端口 11111/11112 未监听")
        print("   💡 OpenD 可能未启动或配置了其他端口")
except Exception as e:
    print(f"   ⚠️  检查失败：{e}")

# 检查 3: 配置文件
print("\n3️⃣  检查配置文件...")
config_file = Path.home() / '.futu' / 'futu_config.ini'
if config_file.exists():
    print(f"   ✅ 配置文件存在：{config_file}")
    print("   内容预览:")
    with open(config_file, 'r') as f:
        for i, line in enumerate(f.readlines()[:10]):
            print(f"      {line.rstrip()}")
else:
    print(f"   ❌ 配置文件不存在：{config_file}")
    print("\n   💡 创建配置文件:")
    print("      mkdir -p ~/.futu")
    print("      cat > ~/.futu/futu_config.ini << 'EOF'")
    print("      [client]")
    print("      host = 127.0.0.1")
    print("      port = 11111")
    print("      EOF")

# 检查 4: Python 包
print("\n4️⃣  检查 Python 包...")
try:
    import futu
    print(f"   ✅ futu 已安装：v{futu.__version__}")
except ImportError:
    print("   ❌ futu 未安装")
    print("\n   💡 安装命令：pip3 install futu-api")

print("\n" + "=" * 60)
print("📋 下一步操作")
print("=" * 60)
print("""
如果 OpenD 未运行:
  1. 下载 OpenD: https://www.futunn.com/download/opend
  2. 安装并启动 OpenD
  3. 在 OpenD 中登录富途账户
  4. 再次运行：python3 test_futu.py

如果已运行但连接失败:
  1. 检查 ~/.futu/futu_config.ini 配置
  2. 确认端口是 11111 还是 11112
  3. 检查密码配置是否正确

快速测试:
  cd /home/admin/openclaw/workspace/agents/holding-analyzer
  python3 test_futu.py
""")
