#!/usr/bin/env python3
"""Validate ZSH navigation targets and the CLAUDE.md memory block (agent-neural markers)."""

import argparse
import re

from _common import MEMORY_ROOT, emit, project_root, read_text, safe_path
from update_agent_entry import classify

REQUIRED = [
    "AGENT_MEMORY.md",
    MEMORY_ROOT + "/CURRENT_TASK.md",
    MEMORY_ROOT + "/PROJECT_MEMORY.md",
    MEMORY_ROOT + "/SESSION_LOG.md",
    MEMORY_ROOT + "/DECISIONS.md",
    MEMORY_ROOT + "/memory-archive/INDEX.md",
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
    checks = []
    for relative in REQUIRED:
        path = safe_path(root, relative)
        checks.append({"path": relative, "exists": path.is_file()})
    nav = root / "AGENT_MEMORY.md"
    meta = metadata(read_text(nav)) if nav.is_file() else {}
    missing_metadata = [key for key in REQUIRED_METADATA if not meta.get(key)]
    metadata_errors = []
    if meta.get("memory_root") and meta["memory_root"] != MEMORY_ROOT:
        metadata_errors.append("memory_root_must_be_{}".format(MEMORY_ROOT))
    agents = root / "CLAUDE.md"
    adapter_state = classify(read_text(agents)) if agents.is_file() else "missing"
    referenced = []
    if nav.is_file():
        pattern = r"`((?:{}/)[^`]+\.md)`".format(re.escape(MEMORY_ROOT))
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
    emit(result)
    raise SystemExit(0 if result["ok"] else 2)


if __name__ == "__main__":
    main()
