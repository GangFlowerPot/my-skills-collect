#!/usr/bin/env python3
"""Migrate a project from the legacy zsh layout to the unified zsh/ layout.

Legacy layout:  AGENT_MEMORY.md at project root + skill-docs/*
New layout:     everything under zsh/ (including AGENT_MEMORY.md)

One-time data move. Rewrites internal path references
(skill-docs/ -> zsh/) in AGENT_MEMORY.md and refreshes the ZSH:MEMORY
block in CLAUDE.md. docs/ is left untouched as a historical snapshot.
"""

import argparse
from pathlib import Path

from _common import MEMORY_ROOT, atomic_write, emit, project_root, read_text, safe_path
from detect_project import _zsh_layout
from update_agent_entry import update


def plan(root):
    layout = _zsh_layout(root)
    if layout == "zsh":
        return {"files": [], "layout": layout, "reason": "already_migrated"}
    if layout != "skill-docs":
        return {"files": [], "layout": layout, "reason": "not_zsh_project"}

    files = []
    if (root / "AGENT_MEMORY.md").is_file():
        files.append({"source": "AGENT_MEMORY.md", "target": MEMORY_ROOT + "/AGENT_MEMORY.md", "action": "move"})

    skill_docs = root / "skill-docs"
    if skill_docs.is_dir():
        for p in sorted(skill_docs.rglob("*")):
            if p.is_file():
                rel = p.relative_to(skill_docs)
                files.append({
                    "source": str(p.relative_to(root)),
                    "target": MEMORY_ROOT + "/" + str(rel),
                    "action": "move",
                })
        files.append({"source": "skill-docs/", "target": MEMORY_ROOT + "/", "action": "remove_empty_dir"})

    return {"files": files, "layout": layout, "reason": None}


def apply_migration(root, plan):
    moved = []
    for f in plan["files"]:
        if f["action"] == "remove_empty_dir":
            continue
        src = root / f["source"]
        dst = safe_path(root, f["target"])
        dst.parent.mkdir(parents=True, exist_ok=True)
        content = read_text(src)
        # Rewrite legacy path references to the new layout.
        content = content.replace("skill-docs/", "{}/".format(MEMORY_ROOT))
        atomic_write(dst, content)
        src.unlink()
        moved.append(f["target"])

    # Remove the now-empty skill-docs/ directory tree (bottom-up).
    skill_docs = root / "skill-docs"
    if skill_docs.is_dir():
        for dirpath in sorted(skill_docs.rglob("*"), reverse=True):
            if dirpath.is_dir() and not any(dirpath.iterdir()):
                dirpath.rmdir()
        if not any(skill_docs.iterdir()):
            skill_docs.rmdir()

    # Refresh the CLAUDE.md ZSH:MEMORY block (template now uses zsh/ paths).
    adapter = update(root, "apply")
    return {"moved": moved, "adapter": adapter}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    root = project_root(args.project_root)
    plan_result = plan(root)
    result = {
        "ok": plan_result["reason"] is None,
        "mode": "apply" if args.apply else "dry-run",
        "layout": plan_result["layout"],
        "files": plan_result["files"],
    }
    if plan_result["reason"]:
        result["reason"] = plan_result["reason"]
    elif args.apply:
        result["result"] = apply_migration(root, plan_result)
    emit(result)
    raise SystemExit(0 if result["ok"] else 2)


if __name__ == "__main__":
    main()
