# my-skills-collect

Personal skills collection for AI coding agents. Each subdirectory contains platform-specific skills.

## Structure

```
my-skills-collect/
├── README.md          # this file
├── claude/            # Claude Code skills (see claude/README.md)
└── codex/             # Codex skills (see codex/README.md)
```

## Adding a New Skill

When adding a new skill, create it in **both** directories with the same name:

1. Create `claude/<skill-name>/SKILL.md` — follow existing Claude skill conventions
2. Create `codex/<skill-name>/SKILL.md` — follow existing Codex skill conventions

Each platform has its own SKILL.md format and path conventions. Refer to existing skills in each directory for the expected style.

## Installation

```bash
# For Claude Code users
cd claude && python install.py

# For Codex users
cd codex && python install.py
```

## Sync Across Machines

This repo is designed for multi-machine sync via Git. After pulling on a new machine, run the install script for your platform.