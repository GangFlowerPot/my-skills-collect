#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check delivery gate constraints.

Validates that delivery-evals.json contains required scenarios:
- test failure blocks delivery
- severe review issue blocks delivery
- incomplete AC blocks delivery
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

REQUIRED_SCENARIOS = {
    "d3": "tester 发现失败并退回开发",
    "d4": "reviewer 发现严重安全问题",
    "d10": "关键 AC 未完成时禁止交付通过",
}


def main() -> int:
    evals_file = SKILL_DIR / "evals" / "delivery-evals.json"
    if not evals_file.is_file():
        print("DELIVERY GATE CHECK FAILED: delivery-evals.json missing")
        return 1

    data = json.loads(evals_file.read_text(encoding="utf-8"))
    evals = {e["id"]: e for e in data.get("evals", [])}

    errors = []
    for eid, name in REQUIRED_SCENARIOS.items():
        if eid not in evals:
            errors.append(f"Missing required scenario {eid}: {name}")

    if errors:
        print("DELIVERY GATE CHECK FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("DELIVERY GATE CHECK PASSED: all required gate scenarios present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
