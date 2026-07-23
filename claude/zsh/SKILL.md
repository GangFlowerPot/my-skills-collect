---
name: zsh
description: 跨 Agent 项目记忆与上下文恢复系统。通过 AGENTS.md 通用薄适配层（跨 codex/OpenCode/cursor 等）+ CLAUDE.md 托管区块（Claude Code 专属，标记 ZSH:MEMORY）、AGENT_MEMORY.md 统一导航、当前任务、三层项目记忆、会话日志、决策记录和历史索引，让多 Agent 共享项目上下文。兼容 Claude Code auto-memory（CLAUDE.md / CLAUDE.local.md 自动加载的原生会话记忆），原生记忆仅作候选、ZSH 项目记忆权威优先。可与 claude-mem 插件互补集成（结构化摘要 ↔ 原始会话内容）。用户提到继续上次、恢复上下文、项目记忆、保存进度、记录决策、跨 Agent 接力、auto-loaded memory、自动加载记忆、rehydrate、dehydrate、memory restore，或希望初始化/维护持久化项目记忆时，都应使用此 Skill。
compatibility: Requires Python 3.8+ for bundled scripts. Markdown-only recovery remains possible without Python.
---

# ZSH — 跨 Agent 项目记忆系统

## 核心原则

把平台入口、记忆导航和具体记忆分开：

```text
AGENTS.md（通用薄适配层，跨 codex/OpenCode/cursor 等）    ← 跨 Agent 统一入口
CLAUDE.md 中的 ZSH:MEMORY 托管区块（Claude Code 专属）   ← 让 Claude 启动时感知 ZSH
  -> zsh/AGENT_MEMORY.md      唯一导航与读写协议
      -> zsh/CURRENT_TASK.md
      -> zsh/PROJECT_MEMORY.md
      -> zsh/SESSION_LOG.md
      -> zsh/DECISIONS.md
      -> zsh/memory-archive/INDEX.md
```

不要把任务状态或项目历史复制进适配层。具体事实只保存在记忆文件中，避免形成多个事实来源。

关于 auto-memory（Agent 原生记忆）的权威规则见 `zsh/references/native-agent-memory.md`。

## 触发后的路由

先调用只读探测，再按结果分支：

```powershell
python <skill_dir>/zsh/scripts/detect_project.py <project_root>
```

### 第 0 步：检测 v3 记忆（一次性迁移机会）

仅当 `has_v3_memory: true` 且 `has_agent_memory: false`（项目已通过 rehydration-mode-v3 初始化、但尚无 zsh 记忆）时进入本分支；否则跳到第 1 步。

向用户提示：

> 检测到本项目已通过 rehydration-mode-v3 初始化（`docs/` 下有项目记忆/当前任务/决策/会话日志）。是否把这些记忆迁移到 zsh 的 `zsh/` 命名空间？
>
> A. 迁移，`docs/` 保留为历史快照（推荐）
> B. 迁移后清空 `docs/` 中的 v3 记忆文件
> C. 暂不迁移，直接初始化一套新的 zsh 记忆

- 用户选 A 或 B 后：
  1. `python <skill_dir>/zsh/scripts/migrate_from_v3.py <project_root> --dry-run` — 展示迁移计划。
  2. 用户二次确认后 `python <skill_dir>/zsh/scripts/migrate_from_v3.py <project_root> --apply`。
  3. 迁移完成后 `docs/` 不会被改动；若选 B，仅在迁移成功后删除 `docs/{PROJECT_MEMORY,CURRENT_TASK,SESSION_LOG,DECISIONS}.md` 与 `docs/session-log-*.md`（仅删文件，保留 `docs/` 目录）。
- 用户选 C：跳到第 1 步走 fresh 初始化。

`migrate_from_v3.py` 只迁移、不改写源、不动 `docs/`；已存在的 `zsh/` 文件按 `skip_existing` 保留。

### 第 1-5 步

1. 如果项目没有 zsh 记忆（`zsh/AGENT_MEMORY.md` 或旧布局的 `AGENT_MEMORY.md` 均不存在，且未命中第 0 步），走"初始化"。
2. 如果用户要继续历史工作，走"恢复上下文"。
3. 如果用户要保存进度，走"脱水保存"。
4. 如果用户要更新任务、日志、决策或整理记忆，走对应的"会话中管理"。
5. 只需检查健康度时，运行只读验证脚本，不修改项目。
6. 如果项目仍在使用旧布局（根目录 `AGENT_MEMORY.md` + `skill-docs/`），走"迁移布局"。

## 迁移布局

把旧布局（根目录 `AGENT_MEMORY.md` + `skill-docs/`）升级为新布局（全部收进 `zsh/`）。一次性数据移动，不改写 `docs/` 历史快照：

```powershell
python <skill_dir>/zsh/scripts/migrate_layout.py <project_root> --dry-run
python <skill_dir>/zsh/scripts/migrate_layout.py <project_root> --apply
```

- 仅当 `detect_project.py` 报告 `zsh_layout: "skill-docs"` 时进入本分支。
- 已在新布局（`zsh/`）的项目会直接返回 `already_migrated`，无需操作。
- 迁移后运行 `validate_navigation.py` 确认通过。

## 初始化

先预览，再得到用户确认后写入：

```powershell
python <skill_dir>/zsh/scripts/init_memory.py <project_root> --dry-run
python <skill_dir>/zsh/scripts/init_memory.py <project_root> --apply
```

默认 `--git-policy auto`：检测到有效 `.git` 时采用共享模式，让记忆文件随项目版本化；没有 Git 时不修改任何 Git 配置。个人 Git 项目如需记忆仅保存本地，明确使用 `--git-policy local`。也可使用 `shared` 或 `unchanged` 覆盖默认判断。

初始化生成：

- `zsh/AGENT_MEMORY.md`
- `zsh/PROJECT_MEMORY.md`
- `zsh/CURRENT_TASK.md`
- `zsh/SESSION_LOG.md`
- `zsh/DECISIONS.md`
- `zsh/memory-archive/INDEX.md`

并安全创建或更新 `CLAUDE.md` 中的 `ZSH:MEMORY:START` / `ZSH:MEMORY:END` 托管区块（Claude Code 专属薄适配）。已有记忆文件不静默覆盖；已有 `CLAUDE.md` 的非托管内容不得修改。如果 `CLAUDE.local.md` 存在，它是用户私有原生记忆，ZSH 只读不写。

初始化后运行：

```powershell
python <skill_dir>/zsh/scripts/validate_navigation.py <project_root>
python <skill_dir>/zsh/scripts/check_structure.py <project_root>
```

## 恢复上下文

先读 `zsh/AGENT_MEMORY.md`，再按需要选择恢复深度。如果安装了 claude-mem，遵循 `zsh/references/claude_mem_integration.md` 的分工流程。

### 最小恢复

1. 读 `zsh/CURRENT_TASK.md`。
2. 读 `zsh/SESSION_LOG.md` 最后一个会话。
3. 汇报当前阶段、进行中任务、精确续接位置、阻塞项和下一步。

### 标准恢复

在最小恢复基础上：

1. 读 `zsh/PROJECT_MEMORY.md` 的热记忆。
2. 读与当前任务相关的 `zsh/DECISIONS.md` 条目。
3. 验证当前任务引用的路径，不要把失效路径当成事实。

### 深度恢复

仅当当前记忆不足、长期中断或内容冲突时：

1. 读温记忆和冷记忆。
2. 通过 `zsh/memory-archive/INDEX.md` 定位相关周日志。
3. 区分"当前事实""历史事实""推断"和"待验证信息"。

### 按需查询 claude-mem

恢复上下文时，先读 ZSH 的结构化记忆获取全局状态（见 claude-mem 集成步骤 1-4）；**再按需查询 claude-mem** 获取具体的代码片段、命令历史、API 调用细节。不要把 claude-mem 的原始内容复制到 ZSH 的摘要中。

信息冲突时采用：用户当前明确指令 > CURRENT_TASK > 已接受的最新决策 > PROJECT_MEMORY 热记忆 > 当前日志 > 历史归档 > auto-memory（Agent 原生注入）> 当前推断。

在所有持久化历史来源中，ZSH 项目记忆高于 Agent 原生记忆（auto-memory）。原生记忆只作为候选信息；如果与 ZSH 冲突，保持 ZSH 当前基线并请求用户确认。

## claude-mem 集成（Claude 独占，可选）

zsh 存储结构化记忆；claude-mem 存储原始会话内容。两者互补，不冗余：

| 职责 | zsh | claude-mem |
|------|-----|------------|
| 结构化记忆（导航/三层/任务/日志/决策） | ✅ `zsh/AGENT_MEMORY.md`、`zsh/*` | ❌ 不重复 |
| 会话原始内容、代码片段、命令历史 | ❌ 不存储 | ✅ claude-mem 存储 |
| 自动触发恢复 | ✅ 会话开始时 | ✅ 按需查询 |

**恢复顺序**：读热记忆 → CURRENT_TASK → SESSION_LOG → **再按需** 查 claude-mem。
**去重**：zsh 与 claude-mem 不互相复制内容。

安装 claude-mem（可选，不安装不影响 zsh 运行）：

```powershell
/plugin install thedotmack/claude-mem
/plugin marketplace add thedotmack/claude-mem
```

详细分工、恢复流程与示例见 `zsh/references/claude_mem_integration.md`。`check_structure.py` 会在健康检查中报告 `claude_mem` 检测状态。

## 会话中管理

### 更新当前任务

更新 `CURRENT_TASK.md` 的状态、进度、当前编辑位置、阻塞项、下一步和时间戳。不要要求用户填写整张表，只询问缺失的必要信息。

### 记录日志

把新条目追加到 `SESSION_LOG.md` 末尾，包括目标、完成内容、关键决策、问题、遗留工作和代码变更摘要。不要自动执行会改变仓库状态的 Git 操作。

### 记录决策

在 `DECISIONS.md` 追加 ADR。编号取现有最大编号加一；记录背景、决策、原因、影响、状态和日期。

### 整理记忆

先运行只读分析：

```powershell
python <skill_dir>/zsh/scripts/memory_compressor.py <project_root> analyze
python <skill_dir>/zsh/scripts/memory_compressor.py <project_root> compress
```

`compress` 只给建议，不直接改写文件。根据用户确认手动调整热/温/冷层。

## 脱水保存

用户说"保存进度""今天到这""脱水"等时：

1. 从当前会话和当前 Agent 已提供的原生记忆（auto-memory）中提取与项目有关的候选事实。
2. 执行增量回写检查：重复跳过、新增分类、更新验证旧值、冲突等待确认、敏感或本机专属信息拒绝。
3. 更新 `CURRENT_TASK.md`，保留精确续接位置。
4. 追加本次会话到 `SESSION_LOG.md`。
5. 如有重要选择，确认后追加 `DECISIONS.md`。
6. 检查并执行跨周封存：

```powershell
python <skill_dir>/zsh/scripts/session_log_manager.py <project_root> archive
```

7. 更新导航时间戳和归档索引。
8. 运行导航验证并报告新增、更新、重复、冲突、拒绝和实际写入的文件。

增量回写检查脚本接收 Agent 提取的结构化候选 JSON，只读分类，不直接修改项目：

```powershell
python <skill_dir>/zsh/scripts/check_writeback.py <project_root> <candidates.json>
```

候选格式和原生记忆（auto-memory）边界见 `zsh/references/native-agent-memory.md`。zsh 的记忆是结构化摘要；不要把 claude-mem 的原始会话内容复制进来。

## Git 策略

```powershell
python <skill_dir>/zsh/scripts/init_memory.py <project_root> --dry-run --git-policy auto
python <skill_dir>/zsh/scripts/init_memory.py <project_root> --apply --git-policy auto
```

- `auto`：存在 `.git` 时采用 `shared`，否则采用 `unchanged`。
- `shared`：记忆文件随项目版本化；只在 `.git/info/exclude` 排除 `CLAUDE.md.zsh-backup`。
- `local`：在 `.git/info/exclude` 排除 `zsh/AGENT_MEMORY.md`、`zsh/` 和备份，仅供当前工作目录中的 Agent 使用。
- `unchanged`：不修改 Git 排除配置。

ZSH 不自动执行 `git add`、`commit` 或 `push`。共享模式只确保记忆文件没有被 ZSH 排除，实际提交遵循项目现有 Git 工作流。
共享模式不擅自删除项目已有 `.gitignore` 规则；如果现有规则排除了 `zsh/AGENT_MEMORY.md` 或 `zsh/`，应报告冲突并由用户决定是否调整。

## 薄适配层

ZSH 的薄适配层是**跨 Agent 通用**的：`AGENTS.md` 是 codex / OpenCode / cursor 等 agent 的统一入口。
对于 **Claude Code**，ZSH 额外在 `CLAUDE.md` 中维护一个托管区块（`ZSH:MEMORY:START/END`），
让 Claude 在自动加载 `CLAUDE.md` 时就能感知到本项目使用 ZSH 记忆系统。

使用独立脚本管理 `CLAUDE.md` 中的托管区块：

```powershell
python <skill_dir>/zsh/scripts/update_agent_entry.py <project_root> --check
python <skill_dir>/zsh/scripts/update_agent_entry.py <project_root> --dry-run
python <skill_dir>/zsh/scripts/update_agent_entry.py <project_root> --apply
```

- 文件不存在：创建最小 `CLAUDE.md` 并注入托管区块。
- 没有托管区块：在末尾追加。
- 有且仅有一个完整区块：只更新区块内部，不覆写其他内容。
- 标记缺失、嵌套或重复：停止并报告，不写入。

详细协议按需读取：

- 导航格式：`zsh/references/memory-navigation-protocol.md`
- 上下文恢复：`zsh/references/context-reconstruction.md`
- Agent 原生记忆（auto-memory）与增量回写：`zsh/references/native-agent-memory.md`
- 日志与归档：`zsh/references/session-log-format.md`
- 记忆压缩：`zsh/references/memory-compression.md`
- claude-mem 集成：`zsh/references/claude_mem_integration.md`

## 安全边界

- 不把密码、Token、Cookie、私钥或证书写入记忆。
- 不静默覆盖已有记忆文件。
- 所有目标路径必须位于项目根目录内。
- `CLAUDE.md` 只修改 `ZSH:MEMORY` 托管区块；`CLAUDE.local.md` 只读不写。
- 写入采用临时文件校验后原子替换；修改已有 `CLAUDE.md` 前保存 `.zsh-backup`。
- 无法确认的信息标记为"待验证"，不编造上下文。
- 不自动删除历史日志。
- 不要求任务绑定某个模型；跨 Agent 接力是正常工作方式。
- 不主动扫描 `.codex`、`.claude`、`.kimi` 等用户级原生记忆目录。
