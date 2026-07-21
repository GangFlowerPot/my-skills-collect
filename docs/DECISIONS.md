# 架构决策记录

图例：✅ 已决定 | 💬 讨论中 | ❌ 已废弃

ADR 编号：ADR-{自增，从 001 开始}；新增 ADR 追加到文件顶部。

---

## ADR-006: check_structure.py 的 claude-mem 探测改用 installed_plugins.json

**日期**: 2026-07-21
**状态**: 已决定 ✅
**提出者**: 修复安装探测 bug

### 背景

`check_structure.py` 的 `check_claude_mem()` 只查两个固定路径（`~/.claude/plugins/claude-mem`、`~/.agents/plugins/claude-mem`），无法识别新版本 claude-mem（13.11.0）的实际安装位置（`~/.claude/plugins/cache/thedotmack/claude-mem/13.11.0`），导致返回 `installed: false`。

### 决策

`check_claude_mem()` 优先读 `~/.claude/plugins/installed_plugins.json`（官方注册表），检查 `claude-mem@thedotmack` 条目；失败时回退到旧逻辑目录扫描。

### 原因

- 官方注册表是 claude-mem 安装状态的最权威来源
- 目录结构可能随版本变化，硬编码路径脆弱
- 回退逻辑兼容旧版安装

### 影响

- 探测结果新增 `version` 字段（如 `13.11.0`）
- 路径指向真实安装位置

### 代码位置

- `claude/zsh/scripts/check_structure.py` 的 `check_claude_mem()`

---

## ADR-005: v3→zsh 迁移的 SESSION_LOG 头部「当前周字段注入」修复

**日期**: 2026-07-20
**状态**: 已决定 ✅
**提出者**: 讨论后确认

### 背景

R2 实测确认 bug：v3 迁移来的「日汇总」SESSION_LOG 头部无 `**当前周**: YYYY-WNN` 字段，
导致 `session_log_manager.archive()` 的 `log_week()` 返回 None，archive 返回 `week_not_detected`
静默跳过跨周切分。

### 决策

保持 log_week() 不兼容「日汇总」pattern（不做长期方案）；修复点改为 migrate_from_v3.py：
迁移时从首个 `## YYYY-MM-DD 日汇总` 提取日期，推算 ISO 周 ID，在 `# 会话日志` 后追加
`**当前周**: YYYY-WNN`。已迁移项目（articleReading 等）手动补一行头部或重跑迁移。

### 原因

- 用户明确长期方案（log_week 兼容「日汇总」）没必要：新项目用 zsh fresh 初始化自带 `**当前周**:`；
  只需覆盖已迁移的存量项目
- 修复 migrate_from_v3.py 成本最低的：改 1 文件、约 30 行、未来迁移自动生效
- 不修改识别逻辑，保持 archive 简洁

### 影响

- 未来 v3→zsh 迁移自动注入字段，不会再触达 `week_not_detected`
- 已迁移项目需人工处理（重跑迁移或手动补一行）

### 代码位置

- `claude/zsh/scripts/migrate_from_v3.py` 的 `inject_current_week_header()`

---

## ADR-004: 跨 agent 记忆归档的「交接提示 + 零 token」模型

**日期**: 2026-07-16
**状态**: 已决定 ✅
**提出者**: 用户（会话中讨论确认）

### 背景

zsh 记忆的跨周归档依赖 `session_log_manager.py archive` 脚本，
但非 Claude/Codex 的 agent（如 cursor）无法跑脚本。

### 决策

无 skill agent 写完记忆后给出交接提示「下次用 Claude/Codex 启动时会自动执行归档」；
归档操作挂靠装 skill agent 的下次会话启动检查（`docs/SESSION_LOG.md` 必读取之后的顺手一步），
脚本本身零 LLM token 消耗。

### 原因

- 会话启动读取 SESSION_LOG 是必读基线成本，归档挂靠其后不产生额外 token。
- 唯一浪费场景「专程开一次 Claude 只为归档」可通过提示措辞规避。

### 影响

- 归档不翻倍 token（用户原始担忧被排除）。
- 多 agent 协作时归档职责自然归属装 skill agent。

### 替代方案

- **在 AGENTS.md / CLAUDE.md 写散文归档指令让 agent 自己做**: 未选择 — 逻辑复杂、切分靠推理易错。
- **每次会话都跑 archive**: 未选择 — archive 只在跨周时触发（`log_week` 对比当前 ISO 周）。

### 代码位置

- `claude/zsh/scripts/session_log_manager.py` 的 `archive()`（按 `**当前周**` 字段切分）

---

## ADR-003: zsh 薄适配层「不做通用注入脚本 + 保持 Claude/Codex 各自注入」

**日期**: 2026-07-16
**状态**: 已决定 ✅
**提出者**: 用户

### 背景

zsh 薄适配层需跨 agent 工作，但各 agent 启动时读取的文件不同
（CLAUDE.md 对 Claude Code、AGENTS.md 对 codex、.cursorrules 对 cursor）。

### 决策

保持现状：claude/zsh 管 `CLAUDE.md` ZSH:MEMORY，codex/zsh 管 `AGENTS.md` ZSH:START；
不做通用注入脚本，各 agent 手动维护各自启动文件的注入。

### 原因

- 当前设计已覆盖主力场景（Claude + codex），改动最小。
- 扩展新 agent 时按需追加即可。

### 替代方案

- **做 `update_thin_adapter.py` 自动扫描存在的启动文件并注入**: 未选择 — 增加注册表与格式适配复杂度。

---

## ADR-002: 薄适配层「独立 Claude 托管区块」取代「AGENTS.md 通用入口」

**日期**: 2026-07-15（初始讨论）→ 2026-07-16 沉淀
**状态**: 已决定 ✅
**提出者**: 用户（纠正我的设计错误）

### 背景

我错误地认为 AGENTS.md 是「跨 agent 通用薄适配入口」，并把 Claude 版重定向到 CLAUDE.md。
用户指出 AGENTS.md 本质是 codex 生态约定，非通用入口。

### 决策

薄适配层（`zsh_memory.block.tmpl`）内容 agent-agnostic；但注入目标按 agent 分派：
Claude → CLAUDE.md 托管区块；codex → AGENTS.md；其余 agent 需单独注入各自启动文件。

### 原因

- Claude Code 不读 AGENTS.md（只读 CLAUDE.md）。
- 没有「所有 agent 都读」的文件；通用入口不存在。

---

## ADR-001: zsh 模板「选择性吸收 v3 优点 + 规避其冗余」

**日期**: 2026-07-16
**状态**: 已决定 ✅
**提出者**: 用户（讨论后确认）

### 背景

v3（rehydration-mode-v3）模板更丰富（mermaid、富 ADR、小时日志），
但探索发现存在结构性冗余。

### 决策

吸收分层描述 / 富 ADR / 细节子标题等真正优点；
用 zsh 的「单真相源 + 职责分离」结构承载；规避三重表征 / 双重任务维护 / 模糊分层 / 强制 mermaid 等冗余。

### 影响

- 决策单一真相源 = DECISIONS.md（PROJECT_MEMORY 热记忆只放指针）。
- 任务单一真相源 = CURRENT_TASK.md（SESSION_LOG 不重复任务状态）。
- 输出 4 模板选择性升级（推送 d4490bc）。

### 替代方案

- **原样对齐 v3（继承冗余）**: 未选择 — 会继承三重表征等问题。

### 代码位置

- `claude/zsh/assets/PROJECT_MEMORY.md.tmpl`, `CURRENT_TASK.md.tmpl`, `DECISIONS.md.tmpl`, `SESSION_LOG.md.tmpl`

<!-- 以下为新增 ADR 占位（新 ADR 追加到此行上方） -->
