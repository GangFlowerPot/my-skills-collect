#!/usr/bin/env python3
"""Inspect, archive, and index weekly session logs."""

import argparse
import re
from datetime import date, timedelta

from _common import MEMORY_ROOT, atomic_write, emit, now_iso, project_root, read_text


def week_id(day=None):
    day = day or date.today()
    year, week, _ = day.isocalendar()
    return "{}-W{:02d}".format(year, week)


def week_range(day=None):
    day = day or date.today()
    monday = day - timedelta(days=day.weekday())
    return monday, monday + timedelta(days=6)


def log_week(content):
    match = re.search(r"\*\*当前周\*\*:\s*(\d{4}-W\d{2})", content)
    return match.group(1) if match else None


def fresh_log(project_name):
    monday, sunday = week_range()
    return "# Session Log — {}\n\n**当前周**: {}\n**周期**: {} ~ {}\n\n---\n".format(project_name, week_id(), monday, sunday)


def update_index(root, archived_id, filename):
    path = root / MEMORY_ROOT / "memory-archive" / "INDEX.md"
    content = read_text(path) if path.is_file() else "# Memory Archive Index\n\n| 周 | 周期 | 文件 | 摘要 |\n|---|---|---|---|\n"
    if filename not in content:
        content = re.sub(r"^\| 暂无 \|.*\n?", "", content, flags=re.MULTILINE)
        content = content.rstrip() + "\n| {} | 见归档文件 | `{}` | 自动周归档，按需读取 |\n".format(archived_id, filename)
    content = re.sub(r"\*\*最后更新\*\*:\s*.*", "**最后更新**: " + now_iso(), content)
    atomic_write(path, content)


def archive(root):
    current = root / MEMORY_ROOT / "SESSION_LOG.md"
    if not current.is_file():
        return {"ok": False, "archived": False, "reason": "missing_current_log"}
    content = read_text(current)
    old_week = log_week(content)
    if not old_week or old_week == week_id():
        return {"ok": True, "archived": False, "reason": "current_week" if old_week else "week_not_detected"}
    archive_dir = root / MEMORY_ROOT / "memory-archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    filename = "session-log-{}.md".format(old_week)
    target = archive_dir / filename
    if target.exists():
        return {"ok": False, "archived": False, "reason": "archive_exists", "path": str(target)}
    atomic_write(target, content)
    atomic_write(current, fresh_log(root.name))
    update_index(root, old_week, filename)
    return {"ok": True, "archived": True, "week": old_week, "path": str(target)}


def latest(root):
    current = root / MEMORY_ROOT / "SESSION_LOG.md"
    if not current.is_file():
        return {"ok": False, "error": "missing_current_log"}
    content = read_text(current)
    matches = list(re.finditer(r"^###\s+.+$", content, re.MULTILINE))
    excerpt = content[matches[-1].start():].strip() if matches else content[-2000:].strip()
    return {"ok": True, "week": log_week(content), "latest": excerpt}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root")
    parser.add_argument("action", choices=["current_week", "archive", "read_latest"])
    args = parser.parse_args()
    root = project_root(args.project_root)
    if args.action == "archive":
        result = archive(root)
    elif args.action == "read_latest":
        result = latest(root)
    else:
        monday, sunday = week_range()
        result = {"ok": True, "week_id": week_id(), "week_range": [monday.isoformat(), sunday.isoformat()]}
    emit(result)
    raise SystemExit(0 if result.get("ok") else 2)


if __name__ == "__main__":
    main()
