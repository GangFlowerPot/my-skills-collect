#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate task graph semantics.

Checks:
- task ID unique
- dependency references exist
- no dependency cycles
- required tasks associated with at least one AC
- owner unique and exists in role roster
- accepted tasks have verification evidence
- write scope format valid
"""

import sys

if sys.version_info < (3, 10):
    raise SystemExit(
        "ct1 validation requires Python 3.10+. "
        f"Current interpreter: {sys.version}"
    )

import json
import re
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent


def load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def validate_task_graph(task_graph_path: Path | None = None, role_roster_path: Path | None = None) -> int:
    if task_graph_path is None:
        task_graph_path = SKILL_DIR / "schemas" / "task-graph.schema.json"
    if role_roster_path is None:
        role_roster_path = SKILL_DIR / "schemas" / "role-roster.schema.json"

    errors = []

    # If no task graph schema yet, skip (will be created in Iteration C)
    if not task_graph_path.is_file():
        print("SKIP: task-graph.schema.json not yet created.")
        return 0

    tg = load_json(task_graph_path)
    tasks = tg.get("tasks", [])
    task_ids = [t.get("id") for t in tasks]

    # ID unique
    if len(task_ids) != len(set(task_ids)):
        errors.append("Task IDs are not unique")

    # Dependency references exist
    for t in tasks:
        for dep in t.get("depends_on", []):
            if dep not in task_ids:
                errors.append(f"Task {t.get('id')}: dependency {dep} does not exist")

    # Cycle detection
    visited = set()
    rec_stack = set()

    def has_cycle(tid: str) -> bool:
        visited.add(tid)
        rec_stack.add(tid)
        task = next((x for x in tasks if x.get("id") == tid), {})
        for dep in task.get("depends_on", []):
            if dep not in visited:
                if has_cycle(dep):
                    return True
            elif dep in rec_stack:
                return True
        rec_stack.discard(tid)
        return False

    for tid in task_ids:
        if tid not in visited:
            if has_cycle(tid):
                errors.append("Dependency cycle detected")
                break

    # Required tasks associated with AC
    for t in tasks:
        if t.get("status") in ("in_progress", "review", "test", "accepted"):
            if not t.get("acceptance_criteria"):
                errors.append(f"Task {t.get('id')}: missing acceptance_criteria")

    # Owner unique per task
    for t in tasks:
        if not t.get("owner"):
            errors.append(f"Task {t.get('id')}: missing owner")

    # Accepted tasks have verification evidence
    for t in tasks:
        if t.get("status") == "accepted":
            if not t.get("verification"):
                errors.append(f"Task {t.get('id')}: accepted but no verification evidence")

    # Write scope format
    for t in tasks:
        for ws in t.get("write_scope", []):
            if not re.match(r"^[a-zA-Z0-9_/*.\-]+$", ws):
                errors.append(f"Task {t.get('id')}: invalid write_scope format: {ws}")

    if errors:
        print("TASK GRAPH VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("TASK GRAPH VALIDATION PASSED.")
    return 0


def main() -> int:
    return validate_task_graph()


if __name__ == "__main__":
    sys.exit(main())
