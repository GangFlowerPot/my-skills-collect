---
name: moduleskill2global
description: Move Claude Code skills between project-level and global-level installation. Use when the user wants to install a project skill globally for all projects, or localize a global skill to a single project. Triggers on phrases like "install this skill globally", "move the skill to global", "make this skill available everywhere", "move this global skill to the project", "convert project skill to global", or anytime a user wants to change the scope of an installed skill.
---

# Module Skill to Global

Move Claude Code skills between project-level (`.agents/skills/`) and global-level (`~/.agents/skills/`) installation scopes.

## Background

In Claude Code, skills installed via `npx skills add` are scoped to either:

| Scope | Location | Flag | Command |
|-------|----------|------|---------|
| **Project** | `<project>/.agents/skills/` | *(default)* | `npx skills add <repo> --skill <name>` |
| **Global** | `~/.agents/skills/` | `-g` | `npx skills add <repo> --skill <name> -g` |

Project skills only work within that project. Global skills are available across all projects. Sometimes you install a skill in the wrong scope and need to move it.

## Core Workflow

Moving a skill between scopes follows the same pattern regardless of direction:

1. **Identify** the skill's current location and source repository
2. **Remove** the skill from the current scope
3. **Reinstall** to the target scope using the same source repository
4. **Verify** the new installation is complete

The source repository is almost always `https://github.com/anthropics/skills` (for official skills) or a similar GitHub URL.

## Operation 1: Project → Global

Move a skill installed in one project so it's available everywhere.

### Steps

1. **Delete** the project-level skill directory:
   ```bash
   rm -rf "<project>/.agents/skills/<skill-name>"
   ```

2. **Reinstall globally** using `-g`:
   ```bash
   npx skills add <source-repo> --skill <skill-name> -g -y
   ```
   - `-g` installs to `~/.agents/skills/`
   - `-y` skips confirmation prompts (safe for reinstallation)

3. **Verify**:
   ```bash
   npx skills list -g
   ```

### Example: skill-creator (Project → Global)

This real case shows moving the `skill-creator` skill from `D:\claudeCode` project to global scope.

**Before** — installed in project:
```
D:\claudeCode\.agents\skills\skill-creator\
```

**Step 1** — remove project copy:
```bash
rm -rf "D:/claudeCode/.agents/skills/skill-creator"
```

**Step 2** — install globally:
```bash
npx skills add https://github.com/anthropics/skills --skill skill-creator -g -y
```

**After** — installed globally:
```
C:\Users\<user>\.agents\skills\skill-creator\
```

**Verify**:
```bash
npx skills list -g
# Output:
# Global Skills
#   skill-creator  ~\.agents\skills\skill-creator  Agents: Claude Code, ...
```

Note: the `-y` flag is critical in agent/automated contexts. Without it, the CLI may prompt for confirmation and hang.

## Operation 2: Global → Project

Move a globally-installed skill into a specific project.

### Steps

1. **Remove** the global skill:
   ```bash
   npx skills remove <skill-name> -g -y
   ```
   Or manually:
   ```bash
   rm -rf "$HOME/.agents/skills/<skill-name>"
   ```

2. **Reinstall to the project** — run from the project root directory, without `-g`:
   ```bash
   cd <project-directory>
   npx skills add <source-repo> --skill <skill-name> -y
   ```

3. **Verify**:
   ```bash
   npx skills list
   ```

### Example: skill-creator (Global → Project)

Moving a global `skill-creator` back into `D:\claudeCode`:

```bash
# Step 1: Remove global
rm -rf "$HOME/.agents/skills/skill-creator"

# Step 2: Install to project
cd D:/claudeCode
npx skills add https://github.com/anthropics/skills --skill skill-creator -y

# Step 3: Verify
npx skills list
```

## Troubleshooting

### "PromptScript does not support global skill installation"

This error from `npx skills` is safe to ignore. It means one specific agent (PromptScript) doesn't support global installs. The skill is still installed globally and works for Claude Code and other agents.

Check with `npx skills list -g` — if the skill appears, it's installed correctly.

### Skill not available after moving

After reinstalling, you may need to restart Claude Code or run `/reload-plugins` for the change to take effect.

### Unknown source repository

If you don't know where a skill came from:
- Check `npx skills list` or `npx skills list -g` for the skill name
- Most official Anthropic skills come from `https://github.com/anthropics/skills`
- If the skill was installed from a marketplace, check `~/.claude/plugins/` for clues

### Symlink issues on Windows

On Windows, `npx skills` may use symlinks. If removal fails with permission errors:
```bash
# Use Windows command to remove symlinks
cmd /c rmdir "<path-to-skill>"
```

## Quick Reference

```bash
# Project → Global
rm -rf "<project>/.agents/skills/<name>"
npx skills add <repo> --skill <name> -g -y
npx skills list -g

# Global → Project
rm -rf "$HOME/.agents/skills/<name>"
cd <project> && npx skills add <repo> --skill <name> -y
npx skills list
```
