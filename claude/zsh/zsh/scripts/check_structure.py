#!/usr/bin/env python3
"""Report the health and sizes of a project's ZSH memory files."""

import argparse
import os
from datetime import datetime

from _common import MEMORY_ROOT, emit, project_root
from validate_navigation import validate

FILES = [
    "CLAUDE.md",
    "AGENT_MEMORY.md",
    MEMORY_ROOT + "/CURRENT_TASK.md",
    MEMORY_ROOT + "/PROJECT_MEMORY.md",
    MEMORY_ROOT + "/SESSION_LOG.md",
    MEMORY_ROOT + "/DECISIONS.md",
    MEMORY_ROOT + "/memory-archive/INDEX.md",
]


def check_claude_mem():
    """Check if the claude-mem plugin is installed (Claude-exclusive).

    Reads ~/.claude/plugins/installed_plugins.json (official registry) and falls
    back to directory scan for older installs. Returns installed/version/path.
    """
    import json as _json
    home = os.path.expanduser("~")
    registry = os.path.join(home, ".claude", "plugins", "installed_plugins.json")
    if os.path.isfile(registry):
        try:
            with open(registry, "r", encoding="utf-8") as f:
                data = _json.load(f)
            plugins = data.get("plugins", {})
            for key, entries in plugins.items():
                if "claude-mem" in key.lower():
                    if entries and isinstance(entries, list) and entries[0]:
                        info = entries[0]
                        return {
                            "installed": True,
                            "version": info.get("version"),
                            "path": info.get("installPath"),
                        }
        except (OSError, _json.JSONDecodeError, KeyError, IndexError):
            pass
    # Fallback: directory scan (older installs)
    locations = [
        os.path.join(home, ".claude", "plugins", "claude-mem"),
        os.path.join(home, ".agents", "plugins", "claude-mem"),
    ]
    for loc in locations:
        if os.path.exists(loc):
            return {"installed": True, "path": loc}
    return {"installed": False}


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
    return {"ok": navigation["ok"], "files": result, "archived_weeks": len(list(archive.glob("session-log-*.md"))) if archive.is_dir() else 0, "navigation": navigation, "claude_mem": check_claude_mem()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root", nargs="?", default=".")
    args = parser.parse_args()
    result = inspect(project_root(args.project_root))
    emit(result)
    raise SystemExit(0 if result["ok"] else 2)


if __name__ == "__main__":
    main()
