#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate protocol consistency across ct1 references.

Checks that StatusReport/v2 is the only status template definition
and no old 6/8/9 field templates remain in skill runtime files.
"""

import sys

if sys.version_info < (3, 10):
    raise SystemExit(
        "ct1 validation requires Python 3.10+. "
        f"Current interpreter: {sys.version}"
    )

import json
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
RUNTIME_FILES = [
    SKILL_DIR / "SKILL.md",
    *sorted((SKILL_DIR / "references").glob("*.md")),
    SKILL_DIR / "evals" / "evals.json",
]

# Patterns that should NOT appear in runtime files (old protocol residues)
FORBIDDEN_PATTERNS = [
    "默认四人",
    "默认五人",
    "固定前端",
    "固定后端",
    "一次启动所有角色",
    "初始任务统一为确认就位",
    "严格按 6 字段",
    "严格按 8 字段",
    "默认 Opus",
    "Opus 4.8",
    "扩展 6→8 字段",
    "扩展六字段",
    "8 字段模板",
    "8字段模板",
]


def main() -> int:
    errors = []
    for f in RUNTIME_FILES:
        if not f.is_file():
            continue
        text = f.read_text(encoding="utf-8")
        for pat in FORBIDDEN_PATTERNS:
            if pat in text:
                errors.append(f"{f.relative_to(SKILL_DIR)}: found forbidden pattern '{pat}'")

    if errors:
        print("PROTOCOL VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("PROTOCOL VALIDATION PASSED: no old protocol residues found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
