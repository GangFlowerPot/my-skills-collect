#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查项目中的再水化文件结构状态。

Usage: python check_structure.py [project_root]
Output: JSON with status of each rehydration file.
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

FILES = {
    "claude_md": "CLAUDE.md",
    "claude_local_md": "CLAUDE.local.md",
    "project_memory": "docs/PROJECT_MEMORY.md",
    "current_task": "docs/CURRENT_TASK.md",
    "session_log": "docs/SESSION_LOG.md",
    "decisions": "docs/DECISIONS.md",
}

def file_info(path: Path) -> dict | None:
    if not path.exists():
        return None
    stat = path.stat()
    return {
        "path": str(path),
        "size_bytes": stat.st_size,
        "last_modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M"),
    }

def parse_current_task(path: Path) -> dict | None:
    """Extract key fields from CURRENT_TASK.md."""
    if not path.exists():
        return None
    content = path.read_text(encoding="utf-8", errors="ignore")
    info = {}
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("🔄 阶段:") or line.startswith("🎯 当前阶段:") or line.startswith("## 当前阶段"):
            info["phase"] = line.split(":", 1)[-1].strip() if ":" in line else line.strip("# ").strip()
        if line.startswith("最后更新") or line.startswith("## 最后更新"):
            info["last_updated"] = line.split(":", 1)[-1].strip() if ":" in line else ""
    return info

def main():
    result = {
        "project_root": str(ROOT.resolve()),
        "checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
        "is_initialized": False,
        "files": {},
    }

    for key, rel_path in FILES.items():
        fp = ROOT / rel_path
        info = file_info(fp)
        result["files"][key] = info
        if info and key in ("claude_md", "project_memory", "current_task"):
            if key == "current_task":
                extra = parse_current_task(fp)
                if extra:
                    result["files"][key]["parsed"] = extra

    # Consider "initialized" if CLAUDE.md + docs/PROJECT_MEMORY.md + docs/CURRENT_TASK.md all exist
    core = ["claude_md", "project_memory", "current_task"]
    result["is_initialized"] = all(result["files"].get(k) is not None for k in core)

    # Count in-progress tasks from CURRENT_TASK
    if result["files"].get("current_task"):
        ct = ROOT / "docs/CURRENT_TASK.md"
        content = ct.read_text(encoding="utf-8", errors="ignore")
        result["current_task_summary"] = {
            "in_progress_count": content.count("- [ ]") - content.count("- [x]"),  # rough
            "blockers_count": content.count("❌") + content.count("阻塞"),
            "has_code_snippets": "```" in content,
        }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result

if __name__ == "__main__":
    main()
