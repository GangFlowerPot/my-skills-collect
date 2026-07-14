#!/usr/bin/env python3
"""Report the health and sizes of a project's ZSH memory files."""

import argparse
from datetime import datetime

from _common import MEMORY_ROOT, emit, project_root
from validate_navigation import validate

FILES = [
    "AGENTS.md",
    "AGENT_MEMORY.md",
    MEMORY_ROOT + "/CURRENT_TASK.md",
    MEMORY_ROOT + "/PROJECT_MEMORY.md",
    MEMORY_ROOT + "/SESSION_LOG.md",
    MEMORY_ROOT + "/DECISIONS.md",
    MEMORY_ROOT + "/memory-archive/INDEX.md",
]


def inspect(root):
    result = []
    for relative in FILES:
        path = root / relative
        item = {"path": relative, "exists": path.is_file()}
        if path.is_file():
            stat = path.stat()
            item.update({"size_bytes": stat.st_size, "modified_at": datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(timespec="seconds")})
        result.append(item)
    archive = root / MEMORY_ROOT / "memory-archive"
    navigation = validate(root)
    return {"ok": navigation["ok"], "files": result, "archived_weeks": len(list(archive.glob("session-log-*.md"))) if archive.is_dir() else 0, "navigation": navigation}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root", nargs="?", default=".")
    args = parser.parse_args()
    result = inspect(project_root(args.project_root))
    emit(result)
    raise SystemExit(0 if result["ok"] else 2)


if __name__ == "__main__":
    main()
