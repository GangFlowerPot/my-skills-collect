# my-skills-collect

Personal Claude Code skills collection — each subdirectory is a complete, self-contained skill.

## Available Skills

| Skill | Description |
|-------|-------------|
| [`moduleskill2global`](./moduleskill2global/) | Move skills between project-level and global-level installation |
| [`rehydration-mode-v1`](./rehydration-mode-v1/) | [V1] 再水化记忆系统 — 基础版（手动创建） |
| [`rehydration-mode-v2`](./rehydration-mode-v2/) | [V2] 再水化记忆系统 — 增强版（skill-creator 标准流程，含辅助脚本） |

---

## rehydration-mode — 再水化记忆系统

项目上下文再水化（Rehydration）系统，通过结构化 Markdown 文件实现会话间状态持久化。每次新会话启动时自动恢复上一次工作的上下文，确保无缝继续。

### 版本对比

| 特性 | V1（基础版） | V2（推荐） |
|------|:-----------:|:---------:|
| 创建方式 | 手动编写 | skill-creator 标准流程 |
| 自动触发 | 中文触发词 | 中英双语触发（含口语化表达） |
| 辅助脚本 | ❌ | ✅ detect_project.py + check_structure.py |
| 指令优化 | 基础指令 | 含原理说明 + 精确步骤 |
| 评测验证 | ❌ 未测试 | ✅ 3 组测试，100% 通过率 |

**推荐使用 V2**，V1 保留作为参考对比。

### 功能概览（V1/V2 通用）

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
# V2（推荐全局安装）
npx skills add https://github.com/<your-username>/my-skills-collect --skill rehydration-mode-v2 -g -y

# V1（基础版）
npx skills add https://github.com/<your-username>/my-skills-collect --skill rehydration-mode-v1 -g -y

# 本地安装 V2
cp -r "D:/claudeCode/skills/my-skills-collect/rehydration-mode-v2" "$HOME/.agents/skills/"
ln -s "$HOME/.agents/skills/rehydration-mode-v2" "$HOME/.claude/skills/rehydration-mode-v2"
```

### V2 Skill 文件结构

```
rehydration-mode-v2/
├── SKILL.md                  # 主指令（含原理说明 + 四大能力 + 完整工作流）
├── scripts/
│   ├── detect_project.py     # 自动检测项目类型和技术栈
│   └── check_structure.py    # 检查再水化文件结构状态
└── assets/
    ├── CLAUDE.md.tmpl             # 启动指令模板
    ├── PROJECT_MEMORY.md.tmpl     # 项目记忆模板
    ├── CURRENT_TASK.md.tmpl       # 当前任务模板
    ├── SESSION_LOG.md.tmpl        # 会话日志模板
    └── DECISIONS.md.tmpl          # 架构决策模板
```

### 评测结果（V2, Iteration 1）

| 评测 | with_skill | without_skill | 差异 |
|------|:----------:|:-------------:|:----:|
| init（初始化） | 7/7 (100%) | 3/7 (42.9%) | **+57.1%** |
| rehydrate（恢复） | 6/6 (100%) | 6/6 (100%) | 持平 |
| dehydrate（脱水） | 4/4 (100%) | 4/4 (100%) | 持平 |
| **总计** | **17/17 (100%)** | **13/17 (76.5%)** | **+23.5%** |

> 核心价值在初始化阶段：有 skill 能创建完整的 5 文件结构，无 skill 只创建了 CLAUDE.md，漏掉 docs/ 目录。

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
npx skills add https://github.com/<your-username>/my-skills-collect --skill rehydration-mode-v2 -g -y

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
