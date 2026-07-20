# 项目记忆 — my-skills-collect

**最后更新**: 2026-07-16（跨日会话，起于 2026-07-15）

⚠️ 本仓库是 **skills 集合仓**（本身是产品），不是使用 skill 的应用项目。
日常工作 = 开发/改进本仓内的 skill（git-rule、rehydration-mode-v3、zsh 等）。

## 🔥 热记忆

### 项目概述

个人 Claude Code / Codex skills 多机同步仓。每个子目录是一个完整的、自包含的 skill，
可通过 `install.py` 全局安装到 `~/.agents/skills/` + `~/.claude/skills/`。
仓库同时产出 `zsh-skill-diff-vs-yesterday.txt`（当前 vs 昨日推送的对比文件）。

**双树结构**：`claude/` = Claude Code skill，`codex/` = Codex skill，同名同架构。
skill 内部用 `{{UPPER_SNAKE}}` 占位符 + `_common.render` 渲染。

### 当前活跃模块

| 模块 | 路径 | 职责 | 状态 |
|---|---|---|---|
| zsh（Claude 版） | `claude/zsh/` | 跨 Agent 项目记忆 + 上下文恢复，CLAUDE.md ZSH:MEMORY 托管区块 | ✅ 已推送 d4490bc |
| zsh（Codex 版） | `codex/zsh/` | 跨 Agent 项目记忆，AGENTS.md ZSH:START 托管区块 | ✅ 已推送 d4490bc |
| rehydration-mode-v3 | `claude/rehydration-mode-v3/` | 三层热/温/冷记忆 + 周封存 + claude-mem 集成 | ✅ 独立 skill（zsh 仅参考其格式） |

### 关键约定

- **模板升级哲学**：zsh 模板采用「选择性吸收 v3 优点 + 规避其冗余」，不原样对齐。
  - 决策单一真相源 = DECISIONS.md；PROJECT_MEMORY 热记忆只放指针。
  - 任务单一真相源 = CURRENT_TASK.md；SESSION_LOG 不重复任务状态。
  - mermaid 可选非强制；分层降级规则写明（热→温 14 天未引用）。
- **薄适配层**：`AGENTS.md` = 跨 agent 通用入口（codex/OpenCode/cursor）；
  `CLAUDE.md` 的 `ZSH:MEMORY` = Claude 专属。不做通用注入脚本。
- **跨 agent 归档**：session_log_manager.py 做自然周归档；无 skill agent 写完记忆后
  给交接提示，归档挂靠装 skill agent 的下次启动检查（脚本本身零 token）。
- 详细决策指针：参见 `docs/DECISIONS.md#adr-001` ~ `#adr-004`。

---

## 🌡️ 温记忆

### 项目架构（本仓 convention）

- SKILL.md ≤ 500 行，溢出拆到 `references/`。
- 脚本兼容 Python 2.7+ AND 3.x（但 zsh 实际要求 Python 3.8+ 因用 pathlib；
  仓内实践以 zsh 的 `compatibility` 字段为准：3.8+）。
- Windows 链接用 `mklink /J`（免管理员），Unix 用 `ln -s`。
- 占位符风格 `{{UPPER_SNAKE}}`（zsh）/ `{中文占位符}`（rehydration）。

### 已知问题 / 技术债务

1. **zsh detect_project.py 的 `**_v3()` 解包**
   - 问题: Py3.5+ 语法，本仓默认 `python` 指向 Py2.7.18，`py_compile` 会报 SyntaxError
   - 影响: 本地无法用 `python` 跑/校验脚本（但目标环境 Py3.8+ 正常）
   - 实操: 本仓所有 Py3 脚本的 py_compile 报错均为环境误报，非代码缺陷

2. **zsh SESSION_LOG R2 风险**
   - session_log_manager archive 切分逻辑需对「日汇总」pattern 生效
   - 状态: 模板已改为小时条目（R1 通过），R2 需 apply+archive 真跑一次确认（未实测）

### 环境信息

- 仓路径: `D:\claudeCode\skills\my-skills-collect`
- Remote: `origin https://github.com/GangFlowerPot/my-skills-collect.git`
- 默认分支: main

### 中间件配置

- 不涉及；本产品无运行时中间件。

---

## ❄️ 冷记忆

### 已废弃内容

- zsh 早期「重定向薄适配层到 CLAUDE.md = 通用入口」思路（已纠正为独立 Claude 托管区块）。
  参见 `docs/DECISIONS.md#adr-002`。

### 已完成的里程碑

- [x] 初始 zsh skill 落地（推送 7fb84da，含薄适配层、auto-memory、claude-mem）2026-07-15
- [x] 薄适配层重设计推送（AGENTS.md 通用 + CLAUDE.md ZSH:MEMORY Claude 专属）2026-07-15
- [x] zsh 模板选择性吸收升级 + v3→zsh 迁移功能推送（d4490bc）2026-07-16
- [x] 产出 zsh-skill-diff-vs-yesterday.txt（当前 vs 7fb84da）2026-07-16

---

📋 记忆维护提示：本仓是 skill 集合仓，“项目事实”主要是 convention 与决策，
热记忆保持精简，决策细节统一沉淀到 DECISIONS.md。
