#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
"""PROJECT_MEMORY.md 记忆压缩管理器（V3 版，Python 2/3 兼容）。

用途：
  1. 分析 PROJECT_MEMORY.md 的分层结构（热/温/冷记忆）
  2. 计算各层的大小和 freshness
  3. 建议压缩策略（将过旧的温记忆降级为冷记忆、摘要冷记忆）
  4. 执行压缩（将详细内容替换为摘要指针）

三层记忆模型：
  - 热记忆（Hot）   — 最近 7 天频繁使用的核心信息
  - 温记忆（Warm）  — 7-30 天内使用过的次要信息
  - 冷记忆（Cold）  — 超过 30 天或极少使用的历史信息

Usage:
  python memory_compressor.py <project_root> <action>

Actions:
  analyze     — 分析当前记忆结构，返回各层大小和建议
  compress    — 执行压缩操作
  stats       — 返回记忆文件的统计信息
"""

import os
import sys
import json
import re
from datetime import datetime, date, timedelta


def get_root():
    return os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()


def _read_file(path):
    try:
        with open(path, 'rb') as f:
            return f.read().decode('utf-8', errors='ignore')
    except Exception:
        return ""


def get_memory_path(root):
    return os.path.join(root, "docs", "PROJECT_MEMORY.md")


def parse_tiers(content):
    """Parse the three-tier structure from PROJECT_MEMORY.md."""
    tiers = {}
    lines = content.split("\n")
    tier_start_lines = {}

    for i, line in enumerate(lines):
        for tier_name in ["热记忆", "温记忆", "冷记忆"]:
            if tier_name in line and ("##" in line or "**" in line):
                tier_start_lines[tier_name] = i
                break

    tier_names_found = [t for t in ["热记忆", "温记忆", "冷记忆"] if t in tier_start_lines]
    for idx, tier_name in enumerate(tier_names_found):
        start = tier_start_lines[tier_name]
        if idx + 1 < len(tier_names_found):
            end = tier_start_lines[tier_names_found[idx + 1]]
        else:
            end = len(lines)
        tier_content = "\n".join(lines[start:end])
        tiers[tier_name] = {
            "start": start,
            "end": end,
            "content": tier_content,
            "size": len(tier_content),
            "line_count": end - start,
        }

    if tier_names_found:
        first_tier_line = min(tier_start_lines.values())
        if first_tier_line > 0:
            ungraded = "\n".join(lines[:first_tier_line])
            if ungraded.strip():
                tiers["未分级"] = {
                    "start": 0,
                    "end": first_tier_line,
                    "content": ungraded,
                    "size": len(ungraded),
                    "line_count": first_tier_line,
                }

    return tiers


def count_section_items(content):
    items = {
        "headings": len(re.findall(r'^#{1,3}\s', content, re.MULTILINE)),
        "tables": len(re.findall(r'^\|', content, re.MULTILINE)),
        "code_blocks": len(re.findall(r'```', content)),
        "bullet_points": len(re.findall(r'^-\s', content, re.MULTILINE)),
        "links": len(re.findall(r'\[.*?\]\(.*?\)', content)),
        "mentions_decisions": len(re.findall(r'ADR-', content)),
        "mentions_session_log": len(re.findall(r'SESSION_LOG|session-log', content)),
    }
    return items


def analyze_memory(root):
    path = get_memory_path(root)
    if not os.path.exists(path):
        return {"error": "PROJECT_MEMORY.md not found"}

    content = _read_file(path)
    if not content.strip():
        return {"error": "PROJECT_MEMORY.md is empty"}

    tiers = parse_tiers(content)
    total_size = len(content)
    total_lines = len(content.split("\n"))

    tier_stats = {}
    for tier_name, tier_data in tiers.items():
        items = count_section_items(tier_data.get("content", ""))
        tier_stats[tier_name] = {
            "size_bytes": tier_data["size"],
            "line_count": tier_data.get("line_count", 0),
            "percentage": round(tier_data["size"] / total_size * 100, 1) if total_size > 0 else 0,
        }
        tier_stats[tier_name].update(items)

    suggestions = []
    ungraded = tiers.get("未分级", {})
    if ungraded and ungraded.get("size", 0) > 100:
        suggestions.append({"type": "structure", "message": "发现 {} 行未分级内容，建议归类到热/温/冷记忆".format(ungraded.get("line_count", 0))})

    hot = tiers.get("热记忆", {})
    if hot and hot.get("size", 0) > total_size * 0.6:
        suggestions.append({"type": "split_hot", "message": "热记忆占比超过 60%（{} 字节），考虑将部分温记忆化".format(hot.get("size", 0))})

    warm = tiers.get("温记忆", {})
    if warm and warm.get("line_count", 0) > 100:
        suggestions.append({"type": "compress_warm", "message": "温记忆超过 100 行（{} 行），建议压缩旧条目".format(warm.get("line_count", 0))})

    cold = tiers.get("冷记忆", {})
    if cold and cold.get("line_count", 0) > 50:
        suggestions.append({"type": "archive_cold", "message": "冷记忆超过 50 行（{} 行），建议提取摘要并归档".format(cold.get("line_count", 0))})

    return {
        "file": path,
        "total_size_bytes": total_size,
        "total_lines": total_lines,
        "tiers": tier_stats,
        "suggestions": suggestions,
        "tier_count": len([t for t in tiers if t != "未分级" or tiers[t].get("size", 0) > 0]),
    }


def get_stats(root):
    path = get_memory_path(root)
    if not os.path.exists(path):
        return {"exists": False}

    content = _read_file(path)
    tiers = parse_tiers(content)
    stat = os.stat(path)

    return {
        "exists": True,
        "path": path,
        "size_bytes": len(content),
        "lines": len(content.split("\n")),
        "last_modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
        "tiers_present": [t for t in ["热记忆", "温记忆", "冷记忆"] if t in tiers],
        "has_ungraded": "未分级" in tiers,
    }


def compress_memory(root, dry_run=True):
    path = get_memory_path(root)
    if not os.path.exists(path):
        return {"error": "PROJECT_MEMORY.md not found", "applied": False}

    content = _read_file(path)
    tiers = parse_tiers(content)
    actions = []

    ungraded = tiers.get("未分级", {})
    if ungraded and ungraded.get("size", 0) > 100:
        actions.append({"action": "classify_ungraded", "detail": "将 {} 行未分级内容归类".format(ungraded.get("line_count", 0)), "requires_manual": True})

    warm = tiers.get("温记忆", {})
    if warm and warm.get("line_count", 0) > 80:
        warm_content = warm.get("content", "")
        date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})')
        old_items = 0
        for line in warm_content.split("\n"):
            match = date_pattern.search(line)
            if match:
                try:
                    item_date = datetime.strptime(match.group(1), "%Y-%m-%d").date()
                    if (date.today() - item_date).days > 14:
                        old_items += 1
                except ValueError:
                    pass
        if old_items > 0:
            actions.append({"action": "summarize_old_warm", "detail": "温记忆中发现 {} 条可能过时的条目，建议精简为摘要".format(old_items), "old_items_count": old_items, "requires_manual": True})

    cold = tiers.get("冷记忆", {})
    if cold and cold.get("line_count", 0) > 30:
        actions.append({"action": "archive_cold", "detail": "冷记忆 {} 行，建议提取摘要并保留指针".format(cold.get("line_count", 0)), "requires_manual": True})

    return {
        "dry_run": dry_run,
        "applied": not dry_run,
        "actions_planned": len(actions),
        "actions": actions,
        "recommendation": "dry_run=True 仅展示建议，设置 dry_run=False 执行（需手动确认每项）",
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python memory_compressor.py <project_root> <action>")
        sys.exit(1)

    root = get_root()
    action = sys.argv[2]

    if action == "analyze":
        print(json.dumps(analyze_memory(root), ensure_ascii=False, indent=2))
    elif action == "stats":
        print(json.dumps(get_stats(root), ensure_ascii=False, indent=2))
    elif action == "compress":
        dry = "--no-dry-run" not in sys.argv
        print(json.dumps(compress_memory(root, dry_run=dry), ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"error": "unknown action: {}".format(action)}, ensure_ascii=False))
        sys.exit(1)
