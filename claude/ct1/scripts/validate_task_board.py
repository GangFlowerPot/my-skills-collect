#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate task board schema and references.

Checks that task-board-schema.md exists and SKILL.md references it.
"""

import sys

if sys.version_info < (3, 10):
    raise SystemExit(
        "ct1 validation requires Python 3.10+. "
        f"Current interpreter: {sys.version}"
    )

from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent


def main() -> int:
    errors = []

    # Check task-board-schema.md exists
    tbs = SKILL_DIR / "references" / "task-board-schema.md"
    if not tbs.is_file():
        errors.append("references/task-board-schema.md missing")

    # Check SKILL.md references it
    skill_md = SKILL_DIR / "SKILL.md"
    if skill_md.is_file():
        text = skill_md.read_text(encoding="utf-8")
        if "task-board-schema.md" not in text:
            errors.append("SKILL.md does not reference task-board-schema.md")
        if "requirement-brief.md" not in text:
            errors.append("SKILL.md does not reference requirement-brief.md")
        if "api-contract-protocol.md" not in text:
            errors.append("SKILL.md does not reference api-contract-protocol.md")
        if "testing-gate.md" not in text:
            errors.append("SKILL.md does not reference testing-gate.md")
        if "delivery-report.md" not in text:
            errors.append("SKILL.md does not reference delivery-report.md")
        if "recovery-protocol.md" not in text:
            errors.append("SKILL.md does not reference recovery-protocol.md")
        if "workspace-strategy.md" not in text:
            errors.append("SKILL.md does not reference workspace-strategy.md")
        if "dynamic-team-selection.md" not in text:
            errors.append("SKILL.md does not reference dynamic-team-selection.md")

    if errors:
        print("TASK BOARD VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("TASK BOARD VALIDATION PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
