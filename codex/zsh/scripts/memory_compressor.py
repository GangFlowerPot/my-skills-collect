#!/usr/bin/env python3
"""Analyze three-tier project memory and return non-mutating advice."""

import argparse
import re

from _common import MEMORY_ROOT, emit, project_root, read_text

TIERS = [("hot", "🔥 热记忆", 200), ("warm", "🌡️ 温记忆", 100), ("cold", "❄️ 冷记忆", 50)]


def tier_sections(content):
    positions = []
    for key, heading, limit in TIERS:
        match = re.search(r"^##\s+.*{}.*$".format(re.escape(heading.split(" ", 1)[-1])), content, re.MULTILINE)
        if match:
            positions.append((match.start(), key, heading, limit))
    positions.sort()
    result = {}
    for index, (start, key, heading, limit) in enumerate(positions):
        end = positions[index + 1][0] if index + 1 < len(positions) else len(content)
        section = content[start:end]
        result[key] = {"heading": heading, "lines": len(section.splitlines()), "characters": len(section), "recommended_max_lines": limit}
    return result


def analyze(root):
    path = root / MEMORY_ROOT / "PROJECT_MEMORY.md"
    if not path.is_file():
        return {"ok": False, "error": "missing_project_memory", "path": str(path)}
    tiers = tier_sections(read_text(path))
    suggestions = []
    for key, _, limit in TIERS:
        data = tiers.get(key)
        if not data:
            suggestions.append({"type": "missing_tier", "tier": key})
        elif data["lines"] > limit:
            suggestions.append({"type": "over_limit", "tier": key, "lines": data["lines"], "recommended_max_lines": limit})
    return {"ok": len(tiers) == 3, "tiers": tiers, "suggestions": suggestions}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root")
    parser.add_argument("action", choices=["analyze", "compress", "stats"])
    args = parser.parse_args()
    result = analyze(project_root(args.project_root))
    result["action"] = args.action
    if args.action == "compress":
        result["dry_run"] = True
        result["message"] = "No files were modified. Apply suggestions only after user confirmation."
    emit(result)
    raise SystemExit(0 if result.get("ok") else 2)


if __name__ == "__main__":
    main()
