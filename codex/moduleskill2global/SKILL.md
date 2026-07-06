---
name: moduleskill2global
description: Move Codex skills between project-level and global-level installation. Use when the user wants to install a project skill globally for all projects, or localize a global skill to a single project. Triggers on phrases like "install this skill globally", "move the skill to global", "make this skill available everywhere", "move this global skill to the project", "convert project skill to global", or anytime a user wants to change the scope of an installed skill.
---

# Module Skill to Global

Move Codex skills between project-level (`.codex/skills/`) and global-level (`~/.agents/skills/` or `~/.codex/skills/`) installation scopes.

## Background

In Codex, skills are discovered from two locations:

| Scope | Location | How to install |
|-------|----------|----------------|
| **Project** | `<project>/.codex/skills/` | Place skill directory here for project-only access |
| **Global** | `~/.agents/skills/` or `~/.codex/skills/` | Place skill directory here for all-projects access |

Codex auto-scans these directories via `skills.list` and loads skill definitions from `SKILL.md` files. Project skills only work within that project. Global skills are available across all projects.

## Core Workflow

Moving a skill between scopes follows the same pattern regardless of direction:

1. **Identify** the skill's current location
2. **Remove** the skill from the current scope
3. **Move/Copy** to the target scope
4. **Verify** the new installation is complete

## Operation 1: Project -> Global

Move a skill installed in one project so it is available everywhere.

### Steps

1. **Locate** the project-level skill:
   ```
   <project>/.codex/skills/<skill-name>/
   ```

2. **Copy** to global directory:
   ```bash
   cp -r "<project>/.codex/skills/<skill-name>" ~/.agents/skills/
   cp -r "<project>/.codex/skills/<skill-name>" ~/.codex/skills/
   ```
   - On Windows: use `xcopy /E /I` or `robocopy`

3. **Remove** the project-level copy:
   ```bash
   rm -rf "<project>/.codex/skills/<skill-name>"
   ```

4. **Verify**:
   ```bash
   ls ~/.agents/skills/
   ls ~/.codex/skills/
   ```

## Operation 2: Global -> Project

Move a globally-installed skill into a specific project.

### Steps

1. **Remove** the global skill:
   ```bash
   rm -rf ~/.agents/skills/<skill-name>
   rm -rf ~/.codex/skills/<skill-name>
   ```

2. **Copy** to the project:
   ```bash
   mkdir -p "<project>/.codex/skills"
   cp -r <source> "<project>/.codex/skills/<skill-name>"
   ```

3. **Verify**:
   ```bash
   ls "<project>/.codex/skills/<skill-name>"
   ```

## Troubleshooting

### Skill not available after moving

Codex scans skill directories at session start. If a skill does not appear after moving:
- Restart the Codex session
- Ensure the skill has a valid `SKILL.md` with YAML frontmatter (`name` + `description`)
- Verify the directory is in one of the scanned paths

### Symlink issues on Windows

On Windows, if `~/.agents/skills/` uses directory junctions:
```cmd
rmdir "<path-to-skill>"
mklink /J "<link>" "<target>"
```

### Path Reference

| Platform | `~/.agents/skills/` | `~/.codex/skills/` |
|----------|---------------------|---------------------|
| Windows | `%USERPROFILE%\.agents\skills\` | `%USERPROFILE%\.codex\skills\` |
| macOS/Linux | `~/.agents/skills/` | `~/.codex/skills/` |

## Quick Reference

```bash
# Project -> Global
cp -r "<project>/.codex/skills/<name>" ~/.agents/skills/
rm -rf "<project>/.codex/skills/<name>"

# Global -> Project
cp -r ~/.agents/skills/<name> "<project>/.codex/skills/"
rm -rf ~/.agents/skills/<name>
```