#!/usr/bin/env bash
# 安装 portfolio-source-reader skill 到本地 agent skills 目录
# 用法：./install.sh [skills-dir]
# 默认装到 ~/.zcode/skills/portfolio-source-reader

set -euo pipefail
SKILL_NAME="portfolio-source-reader"
DEFAULT_DIR="$HOME/.zcode/skills"
TARGET_DIR="${1:-$DEFAULT_DIR}/$SKILL_NAME"

if [ -d "$TARGET_DIR" ]; then
  echo "⚠️  $TARGET_DIR 已存在，先备份再覆盖"
  mv "$TARGET_DIR" "${TARGET_DIR}.bak.$(date +%s)"
fi

mkdir -p "$TARGET_DIR"
cp -r SKILL.md README.md LICENSE references assets "$TARGET_DIR"/
echo "✅ 已安装到 $TARGET_DIR"
echo ""
echo "下一步："
echo "1. 在你的 portfolio 仓库根目录创建 SOURCES.md（参考 assets/sources-map.example.md）"
echo "2. 对 agent 说：'按 portfolio-source-reader skill 帮我挖 <项目名>'"
echo ""
echo "其他 agent 的安装位置："
echo "  Codex:     ~/.codex/skills/portfolio-source-reader"
echo "  Claude:    ~/.claude/skills/portfolio-source-reader"
echo "  自定义:    ./install.sh /path/to/skills"