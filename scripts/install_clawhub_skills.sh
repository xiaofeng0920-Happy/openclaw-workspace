#!/bin/bash
# 自动安装 clawhub 技能脚本
# 等待 30 分钟后开始安装（避免速率限制）

echo "⏳ 等待 30 分钟，让 clawhub 速率限制恢复..."
sleep 1800

echo ""
echo "🚀 开始安装 clawhub 技能..."
echo "================================"

SKILLS=(
    "email-daily-summary"
    "openclaw-whatsapp"
    "agent-telegram"
    "crm-manager"
    "reddit-readonly"
    "youtube-watcher"
    "twitter-x-api"
)

for skill in "${SKILLS[@]}"; do
    echo ""
    echo "📦 安装：$skill"
    clawhub install "$skill" --force 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ $skill 安装成功"
    else
        echo "❌ $skill 安装失败，等待 60 秒后重试..."
        sleep 60
        clawhub install "$skill" --force 2>&1
    fi
    
    # 每个技能之间等待 90 秒，避免速率限制
    echo "⏳ 等待 90 秒..."
    sleep 90
done

echo ""
echo "================================"
echo "✅ 所有技能安装完成！"
echo ""

# 列出已安装的技能
echo "📋 已安装技能列表:"
ls -la /home/admin/openclaw/workspace/skills/ | grep -E "^d" | awk '{print $9}' | grep -v "^\."
