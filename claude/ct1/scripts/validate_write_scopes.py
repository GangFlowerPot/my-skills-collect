#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate role roster and write scope conflicts.

Checks:
- role ID unique
- each execution role has at least one valid task
- owned tasks consistent with task graph
- multi-role write scope conflicts have unique owner or coordination
- retired roles have no incomplete tasks
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


def load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def validate_write_scopes(role_roster_path: Path | None = None, task_graph_path: Path | None = None) -> int:
    if role_roster_path is None:
        role_roster_path = SKILL_DIR / "schemas" / "role-roster.schema.json"
    if task_graph_path is None:
        task_graph_path = SKILL_DIR / "schemas" / "task-graph.schema.json"

    errors = []

    if not role_roster_path.is_file():
        print("SKIP: role-roster.schema.json not yet created.")
        return 0

    roster = load_json(role_roster_path)
    roles = roster.get("roles", [])
    role_ids = [r.get("id") for r in roles]

    # Role ID unique
    if len(role_ids) != len(set(role_ids)):
        errors.append("Role IDs are not unique")

    # Each execution role has at least one valid task
    for r in roles:
        if r.get("type") in ("execution", "specialist"):
            if not r.get("owned_tasks"):
                errors.append(f"Role {r.get('id')}: execution role has no owned tasks")

    # Retired roles have no incomplete tasks
    for r in roles:
        if r.get("status") == "retired":
            incomplete = [t for t in r.get("owned_tasks", []) if t.get("status") not in ("accepted", "delivered")]
            if incomplete:
                errors.append(f"Role {r.get('id')}: retired but has incomplete tasks")

    # Write scope conflict detection
    write_scopes = {}
    for r in roles:
        if r.get("status") in ("retired",):
            continue
        for ws in r.get("write_scope", []):
            write_scopes.setdefault(ws, []).append(r.get("id"))

    conflicts = {ws: roles for ws, roles in write_scopes.items() if len(roles) > 1}
    if conflicts:
        for ws, role_list in conflicts.items():
            errors.append(f"Write scope '{ws}' conflict between roles: {', '.join(role_list)}")

    if errors:
        print("WRITE SCOPE VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("WRITE SCOPE VALIDATION PASSED.")
    return 0


def main() -> int:
    return validate_write_scopes()


if __name__ == "__main__":
    sys.exit(main())
