#!/usr/bin/env bash
# ┌──────────────────────────────────────────────────────────────┐
# │  my-skills-collect 一键安装脚本（Linux / macOS 启动器）        │
# │                                                               │
# │  安装内容:                                                    │
# │    - moduleskill2global     (skill)                           │
# │    - rehydration-mode-v3    (skill)                           │
# │    - claude-mem             (plugin，引导安装)                │
# │                                                               │
# │  用法:                                                         │
# │    ./install.sh               安装全部                          │
# │    ./install.sh --skills-only 只装 skill                        │
# │    ./install.sh --list        列出可安装的 skill                 │
# │    ./install.sh --uninstall   卸载                              │
# └──────────────────────────────────────────────────────────────┘

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 查找可用的 Python
PYTHON=""
for cmd in python3 python python2; do
    if command -v "$cmd" > /dev/null 2>&1; then
        PYTHON="$cmd"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "[error] 未找到 Python。请先安装 Python 2.7+ 或 Python 3.x"
    echo "  macOS: brew install python3"
    echo "  Linux: sudo apt install python3  (或 yum/dnf)"
    exit 1
fi

echo "使用 Python: $($PYTHON --version 2>&1)"
echo ""

exec $PYTHON install.py "$@"
