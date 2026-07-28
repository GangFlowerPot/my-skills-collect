# Decisions — claude

本文件是**决策内容的唯一真相源**（背景/原因/影响/替代方案/代码位置仅记录于此）。
PROJECT_MEMORY.md 热记忆只放简短快照 + 指向本文件的指针，不重复决策内容。

图例：✅ 已决定 | 💬 讨论中 | ❌ 已废弃

ADR 编号：ADR-{自增，从 001 开始}；新增 ADR 追加到文件顶部。

## ADR-001：采用跨 Agent 统一记忆导航

**日期**: 2026-07-28
**状态**: 已决定 ✅
**提出者**: 待确认

### 背景

项目可能由不同 Agent（Claude Code、Codex、cursor 等）在不同会话中接力处理。

### 决策

使用根目录 `AGENT_MEMORY.md` 作为跨 Agent 统一导航入口；平台入口文件（CLAUDE.md、AGENTS.md）只负责引导，不复制记忆。

### 原因

1. **避免多个平台文件中复制记忆并产生冲突**：集中存放保证单一权威来源。
2. **跨 Agent 接力时决策内容不丢失**：新 Agent 通过导航文件即可定位到完整决策上下文。

### 影响

- Agent 恢复历史任务前需要先读取导航文件。
- 决策变更只修改本文件，热记忆通过指针自动指向最新版本。

### 替代方案

- **在各平台入口文件分别复制决策摘要**：未选择 —— 多处维护易产生不一致。
- **仅在会话日志中记录决策**：未选择 —— 缺乏结构性，难以后续检索。

### 代码位置

- `claude/zsh/assets/AGENT_MEMORY.md.tmpl`（导航模板）
- `codex/zsh/assets/AGENT_MEMORY.md.tmpl`（导航模板）

<!-- 以下为新增 ADR 占位（新 ADR 追加到此行上方） -->

## ADR-002：rehydration-mode-v3 标废弃、zsh 为推荐记忆系统

**日期**: 2026-07-28
**状态**: 已决定 ✅
**提出者**: 用户确认

### 背景

本仓曾并存两套项目记忆系统：rehydration-mode-v3（再水化记忆 V3）与 zsh（跨 Agent 项目记忆）。需在文档与安装脚本中明确推荐状态，避免用户误装旧系统。

### 决策

- zsh = 当前推荐使用的记忆系统。
- rehydration-mode-v3 = 已废弃，由 zsh 取代；仓内目录保留作历史参考，但不再推荐安装使用。
- v3 **保留**在 `AVAILABLE_SKILLS`，但在 README 表格、`list_available()` 输出、`guide_claude_mem()` 文案三处加注「已废弃」。

### 原因

1. zsh 兼容 auto-memory / claude-mem，覆盖 v3 场景且更通用。
2. 保留目录而非彻底删除，便于历史项目回溯。
3. 多处标注而非仅依赖 README，确保不同入口（安装脚本、引导文案）都能感知状态。

### 影响

- 新用户默认看到 zsh 推荐。
- 已安装 v3 的用户不会被强制卸载（目录保留），但新安装会收到废弃提示。

### 替代方案

- **彻底从安装列表移除 v3**：未选择 —— 历史项目回溯会失去安装入口。
- **仅 README 标注，脚本不动**：未选择 —— 信息出口不一致，`--list` 与引导文案仍会把 v3 当作现役。

### 代码位置

- `claude/README.md`（记忆系统状态节 + skill 表格）
- `claude/install.py`（AVAILABLE_SKILLS / list_available / guide_claude_mem）
