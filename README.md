# my-skills-collect

Personal Claude Code skills collection — each subdirectory is a complete, self-contained skill.

## Available Skills

| Skill | Description |
|-------|-------------|
| [`moduleskill2global`](./moduleskill2global/) | Move skills between project-level and global-level installation |
| [`rehydration-mode`](./rehydration-mode/) | 项目上下文再水化记忆系统 — 会话间状态持久化与无缝恢复 |

---

## rehydration-mode — 再水化记忆系统

项目上下文再水化（Rehydration）系统，通过结构化 Markdown 文件实现会话间状态持久化。每次新会话启动时自动恢复上一次工作的上下文，确保无缝继续。

### 功能概览

| 能力 | 命令 | 说明 |
|------|------|------|
| 初始化系统 | `/rehydration init` | 检测项目结构，生成 CLAUDE.md + docs/ 下 4 个核心记忆文件 |
| 再水化恢复 | `/rehydration` | 读取记忆文件，汇报当前工作状态（阶段/任务/阻塞项/建议） |
| 查看状态 | `/memory status` | 汇总展示所有记忆文件的关键信息 |
| 更新任务 | `/memory update` | 同步 CURRENT_TASK.md 中的任务进度 |
| 记录日志 | `/memory log` | 追加本次会话记录到 SESSION_LOG.md |
| 记录决策 | `/memory decision` | 追加架构决策记录（ADR）到 DECISIONS.md |
| 脱水保存 | `/memory dehydrate` | 会话结束时同步所有状态、追加日志、提示用户 |

### 创建的文件结构

```
project-root/
├── CLAUDE.md                    # 自动加载的启动指令
├── docs/
│   ├── PROJECT_MEMORY.md        # 项目整体记忆（架构/模块/API/技术债务）
│   ├── CURRENT_TASK.md          # 当前任务状态（热恢复核心）
│   ├── SESSION_LOG.md           # 会话日志（每次会话摘要）
│   └── DECISIONS.md             # 架构决策记录（ADR）
```

### 使用流程

```bash
# 1. 初始化项目记忆系统
/rehydration init

# 2. 正常工作中随时更新状态
/memory update
/memory decision

# 3. 会话结束前持久化
/memory dehydrate

# 4. 下次会话一键恢复
/rehydration
```

### 安装

```bash
# 全局安装（所有项目可用）
npx skills add https://github.com/<your-username>/my-skills-collect --skill rehydration-mode -g -y

# 本地安装
cp -r "D:/claudeCode/skills/my-skills-collect/rehydration-mode" "$HOME/.agents/skills/"
ln -s "$HOME/.agents/skills/rehydration-mode" "$HOME/.claude/skills/rehydration-mode"
```

### Skill 文件结构

```
rehydration-mode/
├── SKILL.md                  # 主指令（四大能力 + 完整工作流）
└── assets/
    ├── CLAUDE.md.tmpl             # 启动指令模板
    ├── PROJECT_MEMORY.md.tmpl     # 项目记忆模板
    ├── CURRENT_TASK.md.tmpl       # 当前任务模板
    ├── SESSION_LOG.md.tmpl        # 会话日志模板
    └── DECISIONS.md.tmpl          # 架构决策模板
```

### 交互规范

- 状态图标：✅ 已完成 | 🔄 进行中 | ⏳ 待开始 | ❌ 阻塞
- 优先级：P0（阻塞）| P1（高）| P2（中）| P3（低）
- 文件编码：UTF-8
- 路径格式：相对路径（基于项目根目录）

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
