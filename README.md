# my-skills-collect

Personal Claude Code skills collection — each subdirectory is a complete, self-contained skill.

## Available Skills

| Skill | Description |
|-------|-------------|
| [`moduleskill2global`](./moduleskill2global/) | Move skills between project-level and global-level installation |

---

## Quick Install (All Skills, Global)

Push this repo to GitHub, then on any machine run:

```bash
npx skills add https://github.com/<your-username>/my-skills-collect --skill '*' -g -y
```

| Flag | Purpose |
|------|---------|
| `--skill '*'` | Install all skills in this repo |
| `-g` | Install globally (`~/.agents/skills/`) |
| `-y` | Skip confirmation prompts |

---

## Install a Single Skill

```bash
# Global (all projects)
npx skills add https://github.com/<your-username>/my-skills-collect --skill moduleskill2global -g -y

# Project only
cd <project-dir>
npx skills add https://github.com/<your-username>/my-skills-collect --skill moduleskill2global -y
```

---

## Local Install (Before Pushing to Git)

If you want to install directly from local path before the repo is online:

### Windows

```bash
# 1. Copy skill to global directory
cp -r "D:/claudeCode/skills/my-skills-collect/<skill-name>" "$HOME/.agents/skills/"

# 2. Create Claude Code symlink
ln -s "$HOME/.agents/skills/<skill-name>" "$HOME/.claude/skills/<skill-name>"

# 3. Reload in Claude Code
# Type: /reload-plugins
```

### macOS / Linux

```bash
cp -r ./<skill-name> ~/.agents/skills/
ln -s ~/.agents/skills/<skill-name> ~/.claude/skills/<skill-name>
```

---

## Verify Installation

```bash
# List all global skills
npx skills list -g

# List project skills
npx skills list
```

Expected output should include the installed skill names.

---

## How to Add a New Skill

1. Create a subdirectory with the skill name:
   ```
   my-skills-collect/
   └── your-new-skill/
       └── SKILL.md   ← required
   ```

2. Optionally add companion files:
   ```
   your-new-skill/
   ├── SKILL.md       ← required (YAML frontmatter + markdown body)
   ├── scripts/       ← optional (executable code)
   ├── references/    ← optional (documentation)
   └── assets/        ← optional (templates, icons, etc.)
   ```

3. Commit and push — the new skill becomes installable immediately.

---

## Skill Directory Structure

Each skill follows the standard Claude Code skill layout:

```
skill-name/
├── SKILL.md          # Required — name + description in YAML frontmatter
│   ├── YAML frontmatter
│   │   ├── name: skill-name
│   │   └── description: When to trigger and what it does
│   └── Markdown body (instructions for Claude)
├── scripts/          # Optional — executable scripts (Python, bash, etc.)
├── references/       # Optional — docs loaded into context as needed
└── assets/           # Optional — files used in output (templates, etc.)
```

A skill with only `SKILL.md` and no extra directories is valid and complete — scripts/references/assets are only needed when the skill logic requires them.

---

## Uninstall

```bash
# Remove a specific global skill
rm -rf ~/.agents/skills/<skill-name>
rm -rf ~/.claude/skills/<skill-name>

# Or via npx
npx skills remove <skill-name> -g -y
```
