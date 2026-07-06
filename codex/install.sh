#!/usr/bin/env bash
# ================================================================
#  my-skills-collect Codex install launcher (Linux / macOS)
# ================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON=""
for cmd in python3 python python2; do
    if command -v "$cmd" > /dev/null 2>&1; then
        PYTHON="$cmd"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "[error] Python not found. Install Python 2.7+ or Python 3.x"
    echo "  macOS: brew install python3"
    echo "  Linux: sudo apt install python3 (or yum/dnf)"
    exit 1
fi

echo "Using Python: $($PYTHON --version 2>&1)"
echo ""

exec $PYTHON install.py "$@"