#!/usr/bin/env python3
"""Plan or apply ZSH's repository-local Git exclusion policy."""

from pathlib import Path

from _common import MEMORY_ROOT, atomic_write, read_text

START = "# ZSH:START"
END = "# ZSH:END"


def is_git_repo(root):
    return (root / ".git").exists()


def managed_block(policy):
    lines = [START]
    if policy == "local":
        lines.extend(["/AGENT_MEMORY.md", "/{}/".format(MEMORY_ROOT)])
    lines.append("/AGENTS.md.zsh-backup")
    lines.append(END)
    return "\n".join(lines)


def replace_block(current, block):
    starts = current.count(START)
    ends = current.count(END)
    if starts == 0 and ends == 0:
        return current.rstrip() + ("\n\n" if current.strip() else "") + block + "\n"
    if starts != 1 or ends != 1 or current.index(START) > current.index(END):
        raise ValueError(".git/info/exclude contains invalid ZSH markers")
    start = current.index(START)
    end = current.index(END) + len(END)
    return current[:start] + block + current[end:]


def apply_git_policy(root, requested, apply_changes):
    git = is_git_repo(root)
    effective = ("shared" if git else "unchanged") if requested == "auto" else requested
    result = {"ok": True, "requested": requested, "effective": effective, "git_repo": git, "changed": False, "track_memory": effective == "shared"}
    if effective == "unchanged":
        return result
    if not git:
        result.update({"ok": False, "error": "git_policy_requested_for_non_git_project"})
        return result
    git_dir = root / ".git"
    if not git_dir.is_dir():
        result.update({"ok": False, "error": "git_worktree_file_requires_manual_exclude_update"})
        return result
    exclude = git_dir / "info" / "exclude"
    current = read_text(exclude) if exclude.is_file() else ""
    try:
        proposed = replace_block(current, managed_block(effective))
    except ValueError as error:
        result.update({"ok": False, "error": str(error)})
        return result
    result.update({"path": str(exclude), "changed": proposed != current})
    if effective == "shared":
        result["note"] = "ZSH does not change project .gitignore rules; verify existing rules do not exclude AGENT_MEMORY.md or skill-docs/."
    if not apply_changes:
        result["proposed_block"] = managed_block(effective)
    elif result["changed"]:
        atomic_write(exclude, proposed)
    return result
