#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
"""SESSION_LOG 周文件管理器（V3 版，Python 2/3 兼容）。

用途：
  1. 确定当前日期属于哪个自然周，返回周标识符（如 2026-W27）
  2. 判断是否需要将当前 SESSION_LOG.md 封存到周文件
  3. 创建新的周文件（从当前 SESSION_LOG.md 内容复制并清空原文件）
  4. 读取最新的会话日志（默认从当前周文件读取）

SESSION_LOG 文件结构（V3）：
  - docs/SESSION_LOG.md          — 当前周的活跃日志（追加写入）
  - docs/session-log-YYYY-WXX.md — 历史周封存文件（只读）

小时级条目格式：
  ### HH:00 会话标题
  （本次会话的完成工作/决策/问题/遗留）

天级汇总格式（每天最后一次会话后追加）：
  ## YYYY-MM-DD 日汇总
  （当天所有会话的关键信息汇总）

Usage:
  python session_log_manager.py <project_root> <action>

Actions:
  current_week    — 返回当前周标识符和文件信息
  archive         — 将当前 SESSION_LOG.md 封存到周文件（如果跨周）
  ensure_daily    — 确保今日日汇总条目存在
  read_latest     — 读取最新的会话日志内容
"""

import os
import sys
import json
from datetime import datetime, date, timedelta


def get_root():
    return os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()


def get_week_id(d=None):
    """Get ISO week identifier like '2026-W27'."""
    if d is None:
        d = date.today()
    iso_year, iso_week, _ = d.isocalendar()
    return "{}-W{:02d}".format(iso_year, iso_week)


def get_week_range(d=None):
    """Get (monday, sunday) for the week containing d."""
    if d is None:
        d = date.today()
    monday = d - timedelta(days=d.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def _read_file(path):
    try:
        with open(path, 'rb') as f:
            return f.read().decode('utf-8', errors='ignore')
    except Exception:
        return ""


def _write_file(path, content):
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True) if sys.version_info[0] >= 3 else _mkdir_p(d)
    with open(path, 'wb') as f:
        f.write(content.encode('utf-8'))


def _mkdir_p(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get_current_log_path(root):
    return os.path.join(root, "docs", "SESSION_LOG.md")


def get_weekly_path(root, week_id=None):
    if week_id is None:
        week_id = get_week_id()
    return os.path.join(root, "docs", "session-log-{}.md".format(week_id))


def read_latest_log(root):
    """Read the most recent session log."""
    current = get_current_log_path(root)
    weekly = get_weekly_path(root)
    result = {
        "current_week_id": get_week_id(),
        "current_week_range": [str(d) for d in get_week_range()],
        "current_log": None,
        "latest_weekly": None,
    }

    if os.path.exists(current):
        content = _read_file(current)
        if content:
            result["current_log"] = {
                "path": current,
                "size": len(content),
                "preview": content[-2000:] if len(content) > 2000 else content,
            }

    if os.path.exists(weekly):
        content = _read_file(weekly)
        if content:
            result["latest_weekly"] = {
                "week_id": get_week_id(),
                "path": weekly,
                "size": len(content),
                "preview": content[-2000:] if len(content) > 2000 else content,
            }

    if not result["current_log"] or result["current_log"]["size"] < 100:
        last_week = date.today() - timedelta(weeks=1)
        last_weekly = get_weekly_path(root, get_week_id(last_week))
        if os.path.exists(last_weekly):
            content = _read_file(last_weekly)
            result["latest_weekly"] = {
                "week_id": get_week_id(last_week),
                "path": last_weekly,
                "size": len(content),
                "preview": content[-3000:] if len(content) > 3000 else content,
            }

    return result


def check_and_archive(root):
    """Check if current SESSION_LOG.md needs to be archived."""
    current = get_current_log_path(root)
    if not os.path.exists(current):
        return {"archived": False, "reason": "no_current_log"}

    content = _read_file(current)
    if not content.strip():
        return {"archived": False, "reason": "empty_current_log"}

    current_week_id = get_week_id()
    current_monday, current_sunday = get_week_range()

    date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})')
    dates_found = date_pattern.findall(content)

    old_entries_exist = False
    for date_str in dates_found:
        try:
            entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if entry_date < current_monday:
                old_entries_exist = True
                break
        except ValueError:
            continue

    if old_entries_exist:
        weekly_path = get_weekly_path(root, get_week_id(date.today() - timedelta(weeks=1)))

        if os.path.exists(weekly_path):
            existing = _read_file(weekly_path)
            _write_file(weekly_path, existing + "\n\n---\n\n" + content)
        else:
            last_monday = current_monday - timedelta(weeks=1)
            last_sunday = current_sunday - timedelta(weeks=1)
            header = "# 会话日志 — {}\n".format(get_week_id(date.today() - timedelta(weeks=1)))
            header += "**周期**: {} ~ {}\n\n".format(str(last_monday), str(last_sunday))
            _write_file(weekly_path, header + content)

        new_header = "# 会话日志 — {}\n".format(current_week_id)
        new_header += "**周期**: {} ~ {}\n\n".format(str(current_monday), str(current_sunday))
        _write_file(current, new_header)

        return {"archived": True, "archived_to": weekly_path, "week_id": get_week_id(date.today() - timedelta(weeks=1))}

    return {"archived": False, "reason": "no_cross_week"}


def ensure_daily_summary(root):
    """Ensure a daily summary entry exists for today."""
    current = get_current_log_path(root)
    if not os.path.exists(current):
        return {"exists": False, "reason": "no_current_log"}

    content = _read_file(current)
    today_str = date.today().strftime("%Y-%m-%d")
    summary_marker = "## {} 日汇总".format(today_str)

    if summary_marker in content:
        return {"exists": True, "date": today_str}

    return {"exists": False, "date": today_str}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python session_log_manager.py <project_root> <action>")
        sys.exit(1)

    root = get_root()
    action = sys.argv[2]

    if action == "current_week":
        print(json.dumps({
            "week_id": get_week_id(),
            "week_range": [str(d) for d in get_week_range()],
            "current_log": get_current_log_path(root),
            "weekly_file": get_weekly_path(root),
        }, ensure_ascii=False, indent=2))
    elif action == "archive":
        print(json.dumps(check_and_archive(root), ensure_ascii=False, indent=2))
    elif action == "ensure_daily":
        print(json.dumps(ensure_daily_summary(root), ensure_ascii=False, indent=2))
    elif action == "read_latest":
        print(json.dumps(read_latest_log(root), ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"error": "unknown action: {}".format(action)}, ensure_ascii=False))
        sys.exit(1)
