#!/usr/bin/env python3
"""Classify structured candidate memories without modifying project files."""

import argparse
import json
import re
from pathlib import Path

from _common import MEMORY_ROOT, emit, project_root, read_text

TARGETS = {
    "current_task": "CURRENT_TASK.md",
    "project_memory": "PROJECT_MEMORY.md",
    "session_log": "SESSION_LOG.md",
    "decisions": "DECISIONS.md",
}
SENSITIVE = [
    re.compile(r"(?i)(password|passwd|token|secret|api[_-]?key|private[_-]?key)\s*[:=]\s*\S+"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)authorization:\s*(?:bearer|basic)\s+\S+"),
]
ABSOLUTE_LOCAL_PATH = re.compile(r"(?:[A-Za-z]:\\Users\\[^\\\s]+|/home/[^/\s]+|/Users/[^/\s]+)")


def normalized(value):
    return " ".join(value.split()).casefold()


def unsafe_reason(text):
    if any(pattern.search(text) for pattern in SENSITIVE):
        return "sensitive_information"
    if ABSOLUTE_LOCAL_PATH.search(text):
        return "machine_specific_absolute_path"
    return None


def classify(root, payload):
    buckets = {name: [] for name in ["add", "update", "duplicate", "conflict", "rejected"]}
    for index, item in enumerate(payload.get("candidates", [])):
        candidate_id = item.get("id", "candidate-{}".format(index + 1))
        target_key = item.get("target")
        action = item.get("action", "add")
        content = item.get("content", "")
        summary = {"id": candidate_id, "target": target_key, "source": item.get("source", "current-session")}
        if target_key not in TARGETS or action not in ("add", "update") or not isinstance(content, str) or not content.strip():
            summary["reason"] = "invalid_candidate"
            buckets["rejected"].append(summary)
            continue
        unsafe = unsafe_reason(content)
        if unsafe:
            summary["reason"] = unsafe
            buckets["rejected"].append(summary)
            continue
        path = root / MEMORY_ROOT / TARGETS[target_key]
        existing = read_text(path) if path.is_file() else ""
        if normalized(content) in normalized(existing):
            summary["reason"] = "already_recorded"
            buckets["duplicate"].append(summary)
            continue
        if action == "update":
            match = item.get("match", "")
            if not match or normalized(match) not in normalized(existing):
                summary["reason"] = "expected_current_value_not_found"
                buckets["conflict"].append(summary)
                continue
            buckets["update"].append(summary)
        else:
            buckets["add"].append(summary)
    return {
        "ok": not buckets["rejected"],
        "authoritative_source": "zsh-project-memory",
        "add": buckets["add"],
        "update": buckets["update"],
        "duplicate": buckets["duplicate"],
        "conflict": buckets["conflict"],
        "rejected": buckets["rejected"],
        "needs_confirmation": bool(buckets["conflict"]),
        "modified": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root")
    parser.add_argument("candidates_json", help="UTF-8 JSON file containing a candidates array")
    args = parser.parse_args()
    root = project_root(args.project_root)
    payload = json.loads(Path(args.candidates_json).read_text(encoding="utf-8-sig"))
    result = classify(root, payload)
    emit(result)
    raise SystemExit(0 if result["ok"] else 2)


if __name__ == "__main__":
    main()
