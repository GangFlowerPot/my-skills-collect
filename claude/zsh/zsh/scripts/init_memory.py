#!/usr/bin/env python3
"""Preview or initialize a ZSH memory structure in a project."""

import argparse
from datetime import date, datetime, timedelta
from pathlib import Path

from _common import MEMORY_ROOT, atomic_write, emit, now_iso, project_root, read_text, render, safe_path
from detect_project import _zsh_layout
from detect_project import detect
from git_policy import apply_git_policy
from update_agent_entry import update

TEMPLATES = {
    MEMORY_ROOT + "/AGENT_MEMORY.md": "AGENT_MEMORY.md.tmpl",
    MEMORY_ROOT + "/PROJECT_MEMORY.md": "PROJECT_MEMORY.md.tmpl",
    MEMORY_ROOT + "/CURRENT_TASK.md": "CURRENT_TASK.md.tmpl",
    MEMORY_ROOT + "/SESSION_LOG.md": "SESSION_LOG.md.tmpl",
    MEMORY_ROOT + "/DECISIONS.md": "DECISIONS.md.tmpl",
    MEMORY_ROOT + "/memory-archive/INDEX.md": "ARCHIVE_INDEX.md.tmpl",
}


def values(root):
    info = detect(root)
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    tech = ", ".join(info["languages"]) if info["languages"] else "待检测或待补充"
    return {
        "PROJECT_NAME": root.name,
        "UPDATED_AT": now_iso(),
        "PROJECT_SUMMARY": "待 Agent 与用户确认后补充项目目标和边界。",
        "TECH_STACK": "- {}".format(tech),
        "WEEK_ID": "{}-W{:02d}".format(*today.isocalendar()[:2]),
        "WEEK_START": monday.isoformat(),
        "WEEK_END": sunday.isoformat(),
        "TODAY": today.isoformat(),
        "CURRENT_TIME": datetime.now().astimezone().strftime("%H:%M"),
    }


def initialize(root, apply_changes, git_policy):
    assets = Path(__file__).resolve().parent.parent / "assets"
    replacements = values(root)
    actions = []
    # Guard: if the project already uses zsh memory in any layout (new zsh/ or
    # legacy skill-docs/), refuse to (re-)initialize. Otherwise a legacy project
    # would get a duplicate zsh/ tree created next to its existing files.
    if _zsh_layout(root) is not None:
        return {"ok": False, "mode": "apply" if apply_changes else "dry-run", "files": [], "reason": "already_initialized", "zsh_layout": _zsh_layout(root)}
    # Validate the managed marker structure before creating any memory files.
    preflight = update(root, "dry-run")
    if not preflight.get("ok"):
        return {"ok": False, "mode": "apply" if apply_changes else "dry-run", "files": [], "adapter": preflight}
    git_preflight = apply_git_policy(root, git_policy, False)
    if not git_preflight.get("ok"):
        return {"ok": False, "mode": "apply" if apply_changes else "dry-run", "files": [], "adapter": preflight, "git_policy": git_preflight}
    for relative, template_name in TEMPLATES.items():
        target = safe_path(root, relative)
        if target.exists():
            actions.append({"path": relative, "action": "skip_existing"})
            continue
        content = render(read_text(assets / template_name), replacements)
        actions.append({"path": relative, "action": "create"})
        if apply_changes:
            atomic_write(target, content)
    adapter = update(root, "apply") if apply_changes else preflight
    git_result = apply_git_policy(root, git_policy, True) if apply_changes else git_preflight
    return {"ok": adapter.get("ok", False) and git_result.get("ok", False), "mode": "apply" if apply_changes else "dry-run", "files": actions, "adapter": adapter, "git_policy": git_result}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--apply", action="store_true")
    parser.add_argument("--git-policy", choices=["auto", "shared", "local", "unchanged"], default="auto")
    args = parser.parse_args()
    result = initialize(project_root(args.project_root), args.apply, args.git_policy)
    emit(result)
    raise SystemExit(0 if result["ok"] else 2)


if __name__ == "__main__":
    main()
