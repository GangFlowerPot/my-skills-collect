#!/usr/bin/env python3
"""Safely inspect, preview, or update the ZSH memory block in CLAUDE.md.

Uses agent-neutral markers ZSH:MEMORY:START / ZSH:MEMORY:END managed by the skill's
zsh_memory.block.tmpl (distinct from codex/zsh's ZSH:START in AGENTS.md).
"""

import argparse
import shutil
from pathlib import Path

from _common import atomic_write, emit, project_root, read_text

# Agent-neutral markers, isolated from codex/zsh's "ZSH:START" in AGENTS.md.
START = "<!-- ZSH:MEMORY:START -->"
END = "<!-- ZSH:MEMORY:END -->"


def block_template():
    return read_text(Path(__file__).resolve().parent.parent / "assets" / "zsh_memory.block.tmpl").strip()


def classify(content):
    starts = content.count(START)
    ends = content.count(END)
    if starts == 0 and ends == 0:
        return "absent"
    if starts != 1 or ends != 1 or content.index(START) > content.index(END):
        return "invalid"
    return "present"


def proposed_content(current, block):
    state = classify(current)
    if state == "invalid":
        raise ValueError("CLAUDE.md contains incomplete, reversed, or duplicate ZSH:MEMORY markers")
    if state == "present":
        start = current.index(START)
        end = current.index(END) + len(END)
        return current[:start] + block + current[end:]
    if current.strip():
        return current.rstrip() + "\n\n" + block + "\n"
    return "# CLAUDE.md\n\n" + block + "\n"


def update(root, mode):
    path = root / "CLAUDE.md"
    exists = path.exists()
    current = read_text(path) if exists else ""
    state = classify(current)
    result = {"path": str(path), "exists": exists, "state": state, "mode": mode, "changed": False}
    if state == "invalid":
        result["ok"] = False
        result["error"] = "invalid_zsh_memory_markers"
        return result
    proposed = proposed_content(current, block_template())
    result["changed"] = proposed != current
    result["ok"] = True
    if mode == "dry-run":
        result["proposed_content"] = proposed
    elif mode == "apply" and result["changed"]:
        if exists:
            backup = path.with_name(path.name + ".zsh-backup")
            shutil.copy2(str(path), str(backup))
            result["backup"] = str(backup)
        atomic_write(path, proposed)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    mode = "apply" if args.apply else "dry-run" if args.dry_run else "check"
    result = update(project_root(args.project_root), mode)
    emit(result)
    raise SystemExit(0 if result.get("ok") else 2)


if __name__ == "__main__":
    main()
