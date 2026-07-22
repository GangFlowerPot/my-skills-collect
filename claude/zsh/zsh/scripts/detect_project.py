#!/usr/bin/env python3
"""Detect a project's basic technology signals without changing it."""

import argparse
from pathlib import Path

from _common import emit, project_root

SIGNALS = {
    "Python": ["pyproject.toml", "requirements.txt", "setup.py", "Pipfile"],
    "Node.js": ["package.json"],
    "TypeScript": ["tsconfig.json"],
    "Java": ["pom.xml", "build.gradle", "build.gradle.kts"],
    "Go": ["go.mod"],
    "Rust": ["Cargo.toml"],
    ".NET": ["*.sln", "*.csproj"],
}


def _zsh_layout(root):
    """Detect whether a project uses zsh memory, and which layout.

    Returns "zsh" (new layout: zsh/AGENT_MEMORY.md), "skill-docs" (legacy
    layout: root AGENT_MEMORY.md + skill-docs/), or None (no zsh memory).
    The sole signal is AGENT_MEMORY.md presence in either location, so
    legacy projects like articleReading keep being recognized.
    """
    if (root / "zsh" / "AGENT_MEMORY.md").is_file():
        return "zsh"
    if (root / "AGENT_MEMORY.md").is_file() and (root / "skill-docs").is_dir():
        return "skill-docs"
    return None


def detect(root):
    layout = _zsh_layout(root)
    languages = []
    for name, patterns in SIGNALS.items():
        if any(any(root.glob(pattern)) for pattern in patterns):
            languages.append(name)
    return {
        "project_root": str(root),
        "project_name": root.name,
        "is_git_repo": (root / ".git").exists(),
        "languages": languages,
        "has_claude_md": (root / "CLAUDE.md").is_file(),
        "has_agents_md": (root / "AGENTS.md").is_file(),
        "zsh_layout": layout,
        "has_agent_memory": layout is not None,
        **_v3(root),
    }


def _v3(root):
    """Detect rehydration-mode-v3 memory files under docs/. Read-only; writes nothing."""
    docs = root / "docs"
    archives = sorted(p.name for p in docs.glob("session-log-*.md")) if docs.is_dir() else []
    present = {
        "project_memory": (docs / "PROJECT_MEMORY.md").is_file(),
        "current_task": (docs / "CURRENT_TASK.md").is_file(),
        "session_log": (docs / "SESSION_LOG.md").is_file(),
        "decisions": (docs / "DECISIONS.md").is_file(),
    }
    return {
        "has_v3_memory": any(present.values()),
        "v3_files": {**present, "archives": archives},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root", nargs="?", default=".")
    args = parser.parse_args()
    emit(detect(project_root(args.project_root)))
    raise SystemExit(0)


if __name__ == "__main__":
    main()
