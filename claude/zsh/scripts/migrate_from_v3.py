#!/usr/bin/env python3
"""Migrate rehydration-mode-v3 memory (docs/) into zsh namespace (skill-docs/).

One-time data move: remaps docs/* -> skill-docs/*, preserving content verbatim.
Adds zsh-only files (AGENT_MEMORY.md, memory-archive/INDEX.md) from templates.
docs/ is never modified or deleted — it becomes a read-only historical snapshot.
"""

import argparse
import re
from pathlib import Path

from _common import MEMORY_ROOT, atomic_write, emit, now_iso, project_root, read_text, render, safe_path
from detect_project import _v3

SKILL_ASSETS = Path(__file__).resolve().parent.parent / "assets"

SOURCE_TARGETS = [
    ("docs/PROJECT_MEMORY.md", MEMORY_ROOT + "/PROJECT_MEMORY.md"),
    ("docs/CURRENT_TASK.md", MEMORY_ROOT + "/CURRENT_TASK.md"),
    ("docs/SESSION_LOG.md", MEMORY_ROOT + "/SESSION_LOG.md"),
    ("docs/DECISIONS.md", MEMORY_ROOT + "/DECISIONS.md"),
]

PATH_REMAP = [
    ("docs/PROJECT_MEMORY.md", MEMORY_ROOT + "/PROJECT_MEMORY.md"),
    ("docs/CURRENT_TASK.md", MEMORY_ROOT + "/CURRENT_TASK.md"),
    ("docs/SESSION_LOG.md", MEMORY_ROOT + "/SESSION_LOG.md"),
    ("docs/DECISIONS.md", MEMORY_ROOT + "/DECISIONS.md"),
    ("docs/session-log-", MEMORY_ROOT + "/memory-archive/session-log-"),
    ("docs/", MEMORY_ROOT + "/"),
]


def transform_content(text):
    """Rewrite docs/ path references into skill-docs/ (path-remap only; content preserved)."""
    for source, target in PATH_REMAP:
        text = text.replace(source, target)
    return text


def archive_actions(root, archives):
    actions = []
    for name in archives:
        target = safe_path(root, MEMORY_ROOT + "/memory-archive/" + name)
        action = {"source": "docs/" + name, "target": MEMORY_ROOT + "/memory-archive/" + name, "action": "skip_existing" if target.is_file() else "migrate_archive"}
        actions.append(action)
    return actions


def plan_migration(root):
    detected = _v3(root)
    files = []
    if (root / "AGENT_MEMORY.md").is_file():
        files.append({"source": None, "target": "AGENT_MEMORY.md", "action": "skip_existing"})
    else:
        files.append({"source": None, "target": "AGENT_MEMORY.md", "action": "generate"})
    for source_relative, target_relative in SOURCE_TARGETS:
        source = root / source_relative
        if not source.is_file():
            continue
        target = safe_path(root, target_relative)
        files.append({"source": source_relative, "target": target_relative, "action": "skip_existing" if target.is_file() else "migrate"})
    files.extend(archive_actions(root, detected["v3_files"].get("archives", [])))
    if detected["v3_files"].get("archives"):
        files.append({"source": None, "target": MEMORY_ROOT + "/memory-archive/INDEX.md", "action": "generate" if not (root / MEMORY_ROOT / "memory-archive" / "INDEX.md").is_file() else "update"})
    return {"files": files, "has_v3_memory": detected["has_v3_memory"], "v3_files": detected["v3_files"]}


def rebuild_index(root, archives):
    index = safe_path(root, MEMORY_ROOT + "/memory-archive/" + "INDEX.md")
    index.parent.mkdir(parents=True, exist_ok=True)
    if index.is_file():
        content = read_text(index)
        content = re.sub(r"^\| 暂无 \|.*\n?", "", content, flags=re.MULTILINE)
    else:
        content = render(read_text(SKILL_ASSETS / "ARCHIVE_INDEX.md.tmpl"), {"PROJECT_NAME": root.name, "UPDATED_AT": now_iso()})
    for name in archives:
        week_id = name.replace("session-log-", "").replace(".md", "")
        if week_id not in content:
            content = content.rstrip() + "\n| {} | 见归档文件 | `{}` | 从 v3 迁移，按需读取 |\n".format(week_id, name)
    content = re.sub(r"\*\*最后更新\*\*:\s*[^\n]*", "**最后更新**: " + now_iso(), content)
    if "**最后更新**" not in content:
        content = content.rstrip() + "\n\n**最后更新**: " + now_iso() + "\n"
    atomic_write(index, content)


def apply_migration(root, plan):
    created = []
    values = {"PROJECT_NAME": root.name, "UPDATED_AT": now_iso()}
    for action in plan["files"]:
        target = safe_path(root, action["target"])
        if action["action"] == "skip_existing":
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if action["action"] in ("migrate", "migrate_archive"):
            atomic_write(target, transform_content(read_text(root / action["source"])))
            created.append(action["target"])
        elif action["target"] == "AGENT_MEMORY.md":
            atomic_write(target, render(read_text(SKILL_ASSETS / "AGENT_MEMORY.md.tmpl"), values))
            created.append(action["target"])
        elif action["target"].endswith("memory-archive/INDEX.md"):
            created.append(action["target"])
    archives = plan.get("v3_files", {}).get("archives", [])
    if archives:
        rebuild_index(root, archives)
    return {"created": created}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    root = project_root(args.project_root)
    plan = plan_migration(root)
    if not plan["has_v3_memory"]:
        emit({"ok": False, "mode": "apply" if args.apply else "dry-run", "reason": "no_v3_memory_detected", "files": []})
        raise SystemExit(2)
    result = {
        "ok": True,
        "mode": "apply" if args.apply else "dry-run",
        "has_v3_memory": plan["has_v3_memory"],
        "files": plan["files"],
        "note": "docs/ 将保留为历史快照，不会被删除或改写。",
    }
    if args.apply:
        result["result"] = apply_migration(root, plan)
    emit(result)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
