#!/usr/bin/env python3
"""Shared helpers for ZSH scripts."""

import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

MIN_PYTHON = (3, 8)
MEMORY_ROOT = "zsh"


def require_python():
    if sys.version_info < MIN_PYTHON:
        raise SystemExit("ZSH scripts require Python 3.8 or newer.")


def project_root(value):
    root = Path(value).expanduser().resolve()
    if not root.is_dir():
        raise ValueError("Project root is not a directory: {}".format(root))
    return root


def safe_path(root, relative):
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        raise ValueError("Path escapes project root: {}".format(relative))
    return candidate


def read_text(path):
    # utf-8-sig accepts both BOM and BOM-less UTF-8, which is common on Windows.
    return path.read_text(encoding="utf-8-sig")


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".zsh-", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        Path(temp_name).read_text(encoding="utf-8")
        os.replace(temp_name, str(path))
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def render(template, values):
    result = template
    for key, value in values.items():
        result = result.replace("{{" + key + "}}", str(value))
    return result


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def emit(data):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(json.dumps(data, ensure_ascii=False, indent=2))


require_python()
