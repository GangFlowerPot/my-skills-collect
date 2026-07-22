#!/usr/bin/env python3
"""Validate ZSH navigation targets and the CLAUDE.md memory block (agent-neural markers)."""

import argparse
import re

from _common import MEMORY_ROOT, emit, project_root, read_text, safe_path
from detect_project import _zsh_layout
from update_agent_entry import classify


def _memory_root(root):
    """Resolve the actual memory-root directory for this project.

    New layout ("zsh"): everything lives under zsh/.
    Legacy layout ("skill-docs"): AGENT_MEMORY.md sits at the project root
    while the other memory files live under skill-docs/.
    """
    return "zsh" if _zsh_layout(root) == "zsh" else "skill-docs"


def _required(root):
    """Build REQUIRED file list based on the project's zsh layout."""
    memory_root = _memory_root(root)
    root_memory = memory_root + "/AGENT_MEMORY.md" if memory_root == "zsh" else "AGENT_MEMORY.md"
    return [
        root_memory,
        memory_root + "/CURRENT_TASK.md",
        memory_root + "/PROJECT_MEMORY.md",
        memory_root + "/SESSION_LOG.md",
        memory_root + "/DECISIONS.md",
        memory_root + "/memory-archive/INDEX.md",
    ]


REQUIRED_METADATA = ["schema", "project", "memory_root", "updated_at", "status"]


def metadata(content):
    if not content.startswith("---\n") or "\n---\n" not in content[4:]:
        return {}
    frontmatter = content.split("\n---\n", 1)[0].splitlines()[1:]
    result = {}
    for line in frontmatter:
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"')
    return result


def validate(root):
    layout = _zsh_layout(root)
    memory_root = "zsh" if layout == "zsh" else "skill-docs"
    checks = []
    for relative in _required(root):
        path = safe_path(root, relative)
        checks.append({"path": relative, "exists": path.is_file()})
    nav = root / memory_root / "AGENT_MEMORY.md" if layout == "zsh" else root / "AGENT_MEMORY.md"
    meta = metadata(read_text(nav)) if nav.is_file() else {}
    missing_metadata = [key for key in REQUIRED_METADATA if not meta.get(key)]
    metadata_errors = []
    if meta.get("memory_root") and meta["memory_root"] not in ("zsh", "skill-docs"):
        metadata_errors.append("memory_root_must_be_zsh_or_skill-docs")
    agents = root / "CLAUDE.md"
    adapter_state = classify(read_text(agents)) if agents.is_file() else "missing"
    referenced = []
    if nav.is_file():
        pattern = r"`((?:{}/)[^`]+\.md)`".format(re.escape(memory_root))
        for relative in sorted(set(re.findall(pattern, read_text(nav)))):
            try:
                exists = safe_path(root, relative).is_file()
            except ValueError:
                exists = False
            referenced.append({"path": relative, "exists": exists})
    ok = all(item["exists"] for item in checks) and not missing_metadata and not metadata_errors and adapter_state == "present" and all(item["exists"] for item in referenced)
    return {"ok": ok, "required_files": checks, "missing_metadata": missing_metadata, "metadata_errors": metadata_errors, "adapter_state": adapter_state, "referenced_files": referenced}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root", nargs="?", default=".")
    args = parser.parse_args()
    result = validate(project_root(args.project_root))
    raise SystemExit(0 if result["ok"] else 2)


if __name__ == "__main__":
    main()
