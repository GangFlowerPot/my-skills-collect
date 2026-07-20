# 架构决策记录

图例：✅ 已决定 | 💬 讨论中 | ❌ 已废弃

ADR 编号：ADR-{自增，从 001 开始}；新增 ADR 追加到文件顶部。

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
