# my-skills-collect

个人 Claude Code skill 集合仓。每个子目录是一个完整、自包含的 skill，可通过 `install.py` 一键安装到全局。所有变更通过 Git 推送到远程，实现多机同步。

## 记忆系统状态

本仓曾提供两套项目记忆系统，目前已完成收敛：

- **zsh** — **当前推荐使用的记忆系统**。跨 Agent 项目记忆与上下文恢复，兼容 auto-memory（原生记忆仅作候选）+ 可与 claude-mem 互补集成。
- **rehydration-mode-v3** — **已废弃**，由 zsh 取代。仓内目录保留作历史参考，不再推荐安装使用。

> 新项目请直接使用 `zsh`。已在使用 v3 的项目可按 `zsh` SKILL.md 的指引迁移。

## 可用 Skills

| Skill | 说明 | 状态 |
|-------|------|------|
| `zsh` | 跨 Agent 项目记忆与上下文恢复 — 兼容 auto-memory（原生记忆仅作候选）+ 可与 claude-mem 互补集成 | **推荐（记忆系统）** |
| `ct1` | 多 Agent 项目编排器——从需求拆分、动态组队、分工开发、代码审查、测试验收到交付的全生命周期编排。支持 create-only（仅组队）与 delivery（端到端交付）双模式 | Active |
| `git-rule` | Git 工作流准则 — 会话同步、推送确认、推送重试策略。涉及 commit/push/pull/sync 时自动触发 | Active |
| `moduleskill2global` | 在项目级和全局级安装之间移动 skill | Active |
| `rehydration-mode-v3` | 再水化记忆系统 V3 — 三层记忆 + 周封存 + claude-mem 集成 | **已废弃，由 zsh 取代** |
| `rehydration-mode-v2` | 再水化记忆系统 V2（旧版，仍可用） | Legacy |
| `rehydration-mode-v1` | 已废弃，仅作历史参考 | Deprecated |

## 安装

```bash
# 安装全部 skill（默认）
python install.py

# 只装 skill，不提示 claude-mem
python install.py --skills-only

# 链接到源模式：直接 Junction 到仓内源（git pull 即自动生效，无需重装）
python install.py --link-to-source

# 指定安装（名称与子目录名一致）
python install.py ct1 git-rule

# 列出可安装的 skill
python install.py --list

# 卸载（删除已安装的文件）
python install.py --uninstall
```

安装目标（全局）：

- Windows: `%USERPROFILE%\.agents\skills\` + `%USERPROFILE%\.claude\skills\`
- Unix: `~/.agents/skills/` + `~/.claude/skills/`

安装完成后，在 Claude Code 中输入 `/reload-plugins` 加载。

## 新增 Skill

新增 skill 时，需在 **claude/** 与 **codex/** 两个平台目录下同步创建同名 skill，分别遵循各自范式：

1. 创建 `claude/<skill-name>/SKILL.md` — 遵循 Claude skill 规范（含 YAML frontmatter）
2. 创建 `codex/<skill-name>/SKILL.md` — 遵循 Codex skill 规范
3. 可选添加 `scripts/`、`references/`、`assets/`
4. 更新本 README 的可用 Skills 表格
5. 更新两侧 `install.py` 的 `AVAILABLE_SKILLS`

每个平台有各自的 SKILL.md 格式与路径约定，参考各自目录下已有的 skill。

## 多机同步

本仓通过 Git 实现多机同步。在新机器上 pull 后，运行 `python install.py` 完成安装。

```bash
git pull origin main
python install.py
```
