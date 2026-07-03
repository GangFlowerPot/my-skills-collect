# my-skills-collect

Personal Claude Code skills collection — each subdirectory is a complete, self-contained skill.

## Available Skills

| Skill | Description |
|-------|-------------|
| [`moduleskill2global`](./moduleskill2global/) | Move skills between project-level and global-level installation |
| [`rehydration-mode-v3`](./rehydration-mode-v3/) | 再水化记忆系统 V3 — 三层记忆模型 + 周文件封存 + claude-mem 集成 + Java 全栈检测 |
| [`rehydration-mode-v2`](./rehydration-mode-v2/) | 再水化记忆系统 V2 — 会话间状态持久化与无缝恢复（中英双语触发） |

> ~~V1 已废弃，仅保留目录作为历史参考，安装时请跳过。~~
> V2 仍可用，但推荐使用 V3（功能全面升级）。

---

## rehydration-mode — 再水化记忆系统

项目上下文再水化（Rehydration）系统，通过结构化 Markdown 文件实现会话间状态持久化。每次新会话启动时自动恢复上一次工作的上下文，确保无缝继续。

### V3 新版本（推荐）

相比 V2 的全面升级：

| 改进点 | V2 | V3 |
|--------|----|----|
| Java 框架检测 | 基础 Spring Boot | Spring Boot/Cloud + Nacos + Kafka + Oracle + Redis + Feign + Gateway + ... |
| 中间件检测 | 无 | Nacos/Eureka/Redis/Kafka/ES/ShardingSphere/Druid/... |
| SESSION_LOG | 单文件，头部插入 | **小时级 + 天级汇总 + 周文件封存**，追加写入 |
| PROJECT_MEMORY | 单层扁平结构 | **热/温/冷三层记忆** + 自动压缩建议 |
| claude-mem 集成 | 无 | 结构化摘要与原始内容互补，去重恢复 |
| 脚本数量 | 2 | **4**（+session_log_manager + memory_compressor） |

### 功能概览（V3）

| 能力 | 命令 | 说明 |
|------|------|------|
| 初始化系统 | `/rehydration init` | 全栈检测 + 生成 CLAUDE.md + docs/ 下记忆文件（三层结构） |
| 再水化恢复 | `/rehydration` | 自动封存旧周 + 读取热记忆 + 汇报状态 |
| 查看状态 | `/memory status` | 汇总记忆文件 + 记忆健康度 |
| 更新任务 | `/memory update` | 同步 CURRENT_TASK.md 中的任务进度 |
| 记录日志 | `/memory log` | 追加小时级条目到 SESSION_LOG.md（支持日汇总） |
| 记录决策 | `/memory decision` | 追加架构决策记录（ADR）到 DECISIONS.md |
| 记忆压缩 | `/memory compress` | 分析三层结构 + 建议压缩策略 |
| 脱水保存 | `/memory dehydrate` | 同步状态 + 追加日志 + 检查封存 + 提示用户 |

### 创建的文件结构（V3）

```
project-root/
├── CLAUDE.md                         # 自动加载的启动指令（含 claude-mem 集成说明）
├── docs/
│   ├── PROJECT_MEMORY.md             # 项目记忆（🔥热/🌡️温/❄️冷三层）
│   ├── CURRENT_TASK.md               # 当前任务状态（热恢复核心）
│   ├── SESSION_LOG.md                # 当前周会话日志（追加写入）
│   ├── session-log-YYYY-WXX.md       # 历史周封存文件（只读）
│   └── DECISIONS.md                  # 架构决策记录（ADR）
```

### 使用流程

```bash
# 1. 初始化项目记忆系统（含全栈检测）
/rehydration init

# 2. 正常工作中随时更新状态
/memory update
/memory decision
/memory log

# 3. 定期维护（每周/每月）
/memory compress                  # 检查记忆健康度 + 获取压缩建议

# 4. 会话结束前持久化
/memory dehydrate                 # 自动检查跨周封存

# 5. 下次会话一键恢复
/rehydration                      # 自动封存 + 恢复上下文
```

### 安装（V3）

```bash
# 全局安装（所有项目可用）
npx skills add https://github.com/<your-username>/my-skills-collect --skill rehydration-mode-v3 -g -y

# 本地安装
cp -r "D:/claudeCode/skills/my-skills-collect/rehydration-mode-v3" "$HOME/.agents/skills/"
ln -s "$HOME/.agents/skills/rehydration-mode-v3" "$HOME/.claude/skills/rehydration-mode-v3"
```

### V3 Skill 文件结构

```
rehydration-mode-v3/
├── SKILL.md                              # 主指令（四大能力 + 工作流 + V3 新特性）
├── scripts/
│   ├── detect_project.py                 # 全栈检测（Java + 中间件 + 数据库）
│   ├── check_structure.py                # 文件结构检查 + 分层解析
│   ├── session_log_manager.py            # 周封存 + 日汇总 + 读取最新
│   └── memory_compressor.py              # 记忆分析 + 压缩建议
├── assets/
│   ├── CLAUDE.md.tmpl                    # 启动指令模板（含 claude-mem）
│   ├── PROJECT_MEMORY.md.tmpl            # 三层记忆模板
│   ├── CURRENT_TASK.md.tmpl              # 当前任务模板
│   ├── SESSION_LOG.md.tmpl               # 小时级 + 天级模板
│   └── DECISIONS.md.tmpl                 # 架构决策模板
└── references/
    ├── session_log_format.md             # SESSION_LOG 格式规范
    ├── memory_compression.md             # 记忆压缩算法 + 规则
    └── claude_mem_integration.md         # claude-mem 集成指南
```

### 评测结果（V2, Iteration 1，V3 尚未评测）

| 评测 | with_skill | without_skill | 差异 |
|------|:----------:|:-------------:|:----:|
| init（初始化） | 7/7 (100%) | 3/7 (42.9%) | **+57.1%** |
| rehydrate（恢复） | 6/6 (100%) | 6/6 (100%) | 持平 |
| dehydrate（脱水） | 4/4 (100%) | 4/4 (100%) | 持平 |
| **总计** | **17/17 (100%)** | **13/17 (76.5%)** | **+23.5%** |

> V3 在 V2 基础上增加了 Java 全栈检测、三层记忆、周封存等功能，预期在 Java 项目初始化场景优势更大。

### 交互规范

- 状态图标：✅ 已完成 | 🔄 进行中 | ⏳ 待开始 | ❌ 阻塞
- 优先级：P0（阻塞）| P1（高）| P2（中）| P3（低）
- 记忆层级：🔥 热记忆 | 🌡️ 温记忆 | ❄️ 冷记忆
- 文件编码：UTF-8
- 路径格式：相对路径（基于项目根目录）

---

## Quick Install (All Skills, Global)

Push this repo to GitHub, then on any machine run:

```bash
# Install all active skills (skip deprecated v1)
npx skills add https://github.com/<your-username>/my-skills-collect \
  --skill moduleskill2global \
  --skill rehydration-mode-v3 \
  -g -y
```

> 用 `--skill '*'` 会连带安装已废弃的 v1，建议显式指定 skill 名称。

---

## Install a Single Skill

```bash
# Global (all projects)
npx skills add https://github.com/<your-username>/my-skills-collect --skill moduleskill2global -g -y
npx skills add https://github.com/<your-username>/my-skills-collect --skill rehydration-mode-v3 -g -y

# Project only
cd <project-dir>
npx skills add https://github.com/<your-username>/my-skills-collect --skill moduleskill2global -y
```

---

## claude-mem Plugin（推荐配合 rehydration-mode-v3 使用）

claude-mem 插件存储原始会话内容（代码片段、命令历史），与 rehydration-mode-v3 的结构化摘要互补。

### 安装方式

通过 Claude Code 内置 marketplace 安装：

```bash
# 方式 1：命令行安装（在 Claude Code 中执行）
/plugin install thedotmack/claude-mem

# 方式 2：通过 marketplace 搜索安装（在 Claude Code 中执行）
/plugin marketplace add thedotmack/claude-mem

# 方式 3：手动添加 marketplace 后安装
/plugin marketplace add thedotmack
# 然后执行：
/plugin install thedotmack/claude-mem
```

### 分工说明

| | rehydration-mode-v3 | claude-mem |
|--|---------------------|------------|
| 存储内容 | 结构化摘要（架构/任务/日志/决策） | 原始会话内容（代码/命令/输出） |
| 文件格式 | Markdown（热/温/冷三层） | 插件内部格式 |
| 恢复方式 | 会话开始时自动加载 | 按需查询 |
| 去重原则 | 两者不冗余：先读本 Skill 获取全局状态，再查 claude-mem 获取细节 |

详细集成指南见 `rehydration-mode-v3/references/claude_mem_integration.md`。

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
