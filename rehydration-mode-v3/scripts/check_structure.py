#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
"""检查项目中的再水化文件结构状态（V3 版，Python 2/3 兼容）。

V3 改进：
  - 支持新的 SESSION_LOG 周文件结构（session-log-YYYY-WXX.md）
  - 支持 PROJECT_MEMORY.md 的分层结构解析（热/温/冷）
  - 支持 claude-mem 集成检测

Usage: python check_structure.py [project_root]
Output: JSON with status of each rehydration file.
"""

import os
import sys
import json
import re
from datetime import datetime, timezone


def get_root():
    return os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()


ROOT = get_root()

FILES = {
    "claude_md": "CLAUDE.md",
    "claude_local_md": "CLAUDE.local.md",
    "project_memory": os.path.join("docs", "PROJECT_MEMORY.md"),
    "current_task": os.path.join("docs", "CURRENT_TASK.md"),
    "decisions": os.path.join("docs", "DECISIONS.md"),
}


def file_info(path):
    if not os.path.exists(path):
        return None
    stat = os.stat(path)
    return {
        "path": path,
        "size_bytes": stat.st_size,
        "last_modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
    }


def parse_current_task(path):
    """Extract key fields from CURRENT_TASK.md."""
    if not os.path.exists(path):
        return None
    content = _read_file(path)
    info = {}
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("🔄 阶段:") or line.startswith("🎯 当前阶段:") or line.startswith("## 当前阶段"):
            info["phase"] = line.split(":", 1)[-1].strip() if ":" in line else line.strip("# ").strip()
        if line.startswith("最后更新") or line.startswith("## 最后更新"):
            info["last_updated"] = line.split(":", 1)[-1].strip() if ":" in line else ""
    return info


def _read_file(path):
    try:
        with open(path, 'rb') as f:
            return f.read().decode('utf-8', errors='ignore')
    except Exception:
        return ""


def parse_project_memory_tiers(path):
    """Parse PROJECT_MEMORY.md tier structure (热/温/冷)."""
    if not os.path.exists(path):
        return None
    content = _read_file(path)
    tiers = {}
    current_tier = None
    tier_start_lines = {}

    lines = content.split("\n")
    for i, line in enumerate(lines):
        for tier_name in ["热记忆", "温记忆", "冷记忆"]:
            if tier_name in line and ("##" in line or "**" in line):
                tier_start_lines[tier_name] = i
                current_tier = tier_name
                break

    tier_names_found = [t for t in ["热记忆", "温记忆", "冷记忆"] if t in tier_start_lines]
    for idx, tier_name in enumerate(tier_names_found):
        start = tier_start_lines[tier_name]
        if idx + 1 < len(tier_names_found):
            end = tier_start_lines[tier_names_found[idx + 1]]
        else:
            end = len(lines)
        tier_content = "\n".join(lines[start:end])
        tiers[tier_name] = {
            "line": start,
            "size_estimate": len(tier_content),
        }

    return tiers if tiers else None


def find_session_log_files():
    """Find all session log files (both current and weekly archives)."""
    logs = []
    docs_dir = os.path.join(ROOT, "docs")
    current = os.path.join(docs_dir, "SESSION_LOG.md")
    if os.path.exists(current):
        logs.append({"type": "current", "path": current, "info": file_info(current)})

    if os.path.isdir(docs_dir):
        for fname in sorted(os.listdir(docs_dir)):
            if fname.startswith("session-log-") and fname.endswith(".md"):
                fpath = os.path.join(docs_dir, fname)
                week_id = fname.replace("session-log-", "").replace(".md", "")
                finfo = file_info(fpath)
                logs.append({"type": "weekly", "week_id": week_id, "path": finfo["path"], "size_bytes": finfo["size_bytes"], "last_modified": finfo["last_modified"]})

    return logs


def check_claude_mem():
    """Check if claude-mem plugin is installed."""
    home = os.path.expanduser("~")
    locations = [
        os.path.join(home, ".claude", "plugins", "claude-mem"),
        os.path.join(home, ".agents", "plugins", "claude-mem"),
    ]
    for loc in locations:
        if os.path.exists(loc):
            return {"installed": True, "path": loc}
    return {"installed": False}


def main():
    result = {
        "project_root": ROOT,
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "is_initialized": False,
        "files": {},
        "session_logs": [],
        "claude_mem": check_claude_mem(),
    }

    for key, rel_path in FILES.items():
        fpath = os.path.join(ROOT, rel_path)
        info = file_info(fpath)
        result["files"][key] = info
        if info and key == "current_task":
            extra = parse_current_task(fpath)
            if extra:
                result["files"][key]["parsed"] = extra
        if info and key == "project_memory":
            tiers = parse_project_memory_tiers(fpath)
            if tiers:
                result["files"][key]["tiers"] = tiers

    result["session_logs"] = find_session_log_files()

    core = ["claude_md", "project_memory", "current_task"]
    result["is_initialized"] = all(result["files"].get(k) is not None for k in core)

    if result["files"].get("current_task"):
        ct = os.path.join(ROOT, "docs", "CURRENT_TASK.md")
        content = _read_file(ct)
        result["current_task_summary"] = {
            "in_progress_count": content.count("- [ ]") - content.count("- [x]"),
            "blockers_count": content.count("❌") + content.count("阻塞"),
            "has_code_snippets": "```" in content,
        }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    main()
