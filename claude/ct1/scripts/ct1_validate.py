#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ct1 validation unified entry point.

Calls all validation modules in sequence. Requires Python 3.10+.
"""

import sys

if sys.version_info < (3, 10):
    raise SystemExit(
        "ct1 validation requires Python 3.10+. "
        f"Current interpreter: {sys.version}"
    )

import argparse
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description="ct1 validation suite")
    parser.add_argument("--skill-dir", default=str(SKILL_DIR), help="ct1 skill directory")
    args = parser.parse_args()
    skill_dir = Path(args.skill_dir)

    if not (skill_dir / "SKILL.md").is_file():
        print(f"ERROR: {skill_dir} does not contain SKILL.md")
        return 2

    from validate_protocol import main as validate_protocol
    from validate_task_graph import main as validate_task_graph
    from validate_write_scopes import main as validate_write_scopes
    from check_delivery_gate import main as check_delivery_gate

    checks = [
        ("Protocol", validate_protocol),
        ("Task Graph", validate_task_graph),
        ("Write Scopes", validate_write_scopes),
        ("Delivery Gate", check_delivery_gate),
    ]

    failed = []
    for name, fn in checks:
        print(f"\n=== {name} ===")
        try:
            rc = fn()
        except Exception as e:
            print(f"ERROR: {e}")
            rc = 1
        if rc != 0:
            failed.append(name)

    print("\n" + "=" * 40)
    if failed:
        print(f"VALIDATION FAILED: {', '.join(failed)}")
        return 1
    print("ALL VALIDATIONS PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
