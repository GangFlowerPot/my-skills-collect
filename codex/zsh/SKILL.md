---
name: zsh
description: 跨 Agent 项目记忆与上下文恢复系统。通过 AGENTS.md 薄适配层、AGENT_MEMORY.md 统一导航、当前任务、三层项目记忆、会话日志、决策记录和历史索引，让 Codex、Claude Code、Kimi CLI、OpenCode 等 Agent 共享项目上下文。用户提到继续上次、恢复上下文、项目记忆、保存进度、记录决策、跨 Agent 接力、rehydrate、dehydrate、memory restore，或希望初始化/维护持久化项目记忆时，都应使用此 Skill。
compatibility: Requires Python 3.8+ for bundled scripts. Markdown-only recovery remains possible without Python.
---

# ZSH — 跨 Agent 项目记忆系统

## 核心原则

把平台入口、记忆导航和具体记忆分开：

```text
AGENTS.md                 平台薄适配层，只负责指路
  -> AGENT_MEMORY.md      唯一导航与读写协议
      -> skill-docs/CURRENT_TASK.md
      -> skill-docs/PROJECT_MEMORY.md
      -> skill-docs/SESSION_LOG.md
      -> skill-docs/DECISIONS.md
      -> skill-docs/memory-archive/INDEX.md
```

不要把任务状态或项目历史复制进 `AGENTS.md`。具体事实只保存在记忆文件中，避免形成多个事实来源。

## 触发后的路由

1. 如果项目没有 `AGENT_MEMORY.md`，走“初始化”。
2. 如果用户要继续历史工作，走“恢复上下文”。
3. 如果用户要保存进度，走“脱水保存”。
4. 如果用户要更新任务、日志、决策或整理记忆，走对应的“会话中管理”。
5. 只需检查健康度时，运行只读验证脚本，不修改项目。

## 初始化

先预览，再得到用户确认后写入：

```powershell
python <skill_dir>/scripts/init_memory.py <project_root> --dry-run
python <skill_dir>/scripts/init_memory.py <project_root> --apply
```

默认 `--git-policy auto`：检测到有效 `.git` 时采用共享模式，让记忆文件随项目版本化；没有 Git 时不修改任何 Git 配置。个人 Git 项目如需记忆仅本地保存，明确使用 `--git-policy local`。也可使用 `shared` 或 `unchanged` 覆盖默认判断。

初始化生成：

- `AGENT_MEMORY.md`
- `skill-docs/PROJECT_MEMORY.md`
- `skill-docs/CURRENT_TASK.md`
- `skill-docs/SESSION_LOG.md`
- `skill-docs/DECISIONS.md`
- `skill-docs/memory-archive/INDEX.md`

并安全创建或更新 `AGENTS.md` 中的 `ZSH:START` / `ZSH:END` 管理区块。已有记忆文件不静默覆盖；已有 `AGENTS.md` 的非管理内容不得修改。

初始化后运行：

```powershell
python <skill_dir>/scripts/validate_navigation.py <project_root>
python <skill_dir>/scripts/check_structure.py <project_root>
```

## 恢复上下文

先读 `AGENT_MEMORY.md`，再按需要选择恢复深度。

### 最小恢复

1. 读 `skill-docs/CURRENT_TASK.md`。
2. 读 `skill-docs/SESSION_LOG.md` 最后一个会话。
3. 汇报当前阶段、进行中任务、精确续接位置、阻塞项和下一步。

### 标准恢复

在最小恢复基础上：

1. 读 `skill-docs/PROJECT_MEMORY.md` 的热记忆。
2. 读与当前任务相关的 `skill-docs/DECISIONS.md` 条目。
3. 验证当前任务引用的路径，不要把失效路径当成事实。

### 深度恢复

仅当当前记忆不足、长期中断或内容冲突时：

1. 读温记忆和冷记忆。
2. 通过 `skill-docs/memory-archive/INDEX.md` 定位相关周日志。
3. 区分“当前事实”“历史事实”“推断”和“待验证信息”。

信息冲突时采用：用户当前明确指令 > CURRENT_TASK > 已接受的最新决策 > PROJECT_MEMORY 热记忆 > 当前日志 > 历史归档。

在所有持久化历史来源中，ZSH 项目记忆高于 Agent 原生记忆。原生记忆只作为候选信息；如果与 ZSH 冲突，保持 ZSH 当前基线并请求用户确认。

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
python <skill_dir>/scripts/memory_compressor.py <project_root> analyze
python <skill_dir>/scripts/memory_compressor.py <project_root> compress
```

`compress` 只给建议，不直接改写文件。根据用户确认手动调整热/温/冷层。

## 脱水保存

用户说“保存进度”“今天到这”“脱水”等时：

1. 从当前会话和当前 Agent 已提供的原生记忆中提取与项目有关的候选事实。
2. 执行增量回写检查：重复跳过、新增分类、更新验证旧值、冲突等待确认、敏感或本机专属信息拒绝。
3. 更新 `CURRENT_TASK.md`，保留精确续接位置。
4. 追加本次会话到 `SESSION_LOG.md`。
5. 如有重要选择，确认后追加 `DECISIONS.md`。
4. 检查并执行跨周封存：

```powershell
python <skill_dir>/scripts/session_log_manager.py <project_root> archive
```

6. 更新导航时间戳和归档索引。
7. 运行导航验证并报告新增、更新、重复、冲突、拒绝和实际写入的文件。

增量回写检查脚本接收 Agent 提取的结构化候选 JSON，只读分类，不直接修改项目：

```powershell
python <skill_dir>/scripts/check_writeback.py <project_root> <candidates.json>
```

候选格式和原生记忆边界见 `references/native-agent-memory.md`。

## Git 策略

```powershell
python <skill_dir>/scripts/init_memory.py <project_root> --dry-run --git-policy auto
python <skill_dir>/scripts/init_memory.py <project_root> --apply --git-policy auto
```

- `auto`：存在 `.git` 时采用 `shared`，否则采用 `unchanged`。
- `shared`：记忆文件随项目版本化；只在 `.git/info/exclude` 排除 `AGENTS.md.zsh-backup`。
- `local`：在 `.git/info/exclude` 排除 `AGENT_MEMORY.md`、`skill-docs/` 和备份，仅供当前工作目录中的 Agent 使用。
- `unchanged`：不修改 Git 排除配置。

ZSH 不自动执行 `git add`、`commit` 或 `push`。共享模式只确保记忆文件没有被 ZSH 排除，实际提交遵循项目现有 Git 工作流。
共享模式不擅自删除项目已有 `.gitignore` 规则；如果现有规则排除了 `AGENT_MEMORY.md` 或 `skill-docs/`，应报告冲突并由用户决定是否调整。

## 薄适配层

使用独立脚本管理 `AGENTS.md`：

```powershell
python <skill_dir>/scripts/update_agent_entry.py <project_root> --check
python <skill_dir>/scripts/update_agent_entry.py <project_root> --dry-run
python <skill_dir>/scripts/update_agent_entry.py <project_root> --apply
```

- 文件不存在：创建最小 `AGENTS.md`。
- 没有管理区块：在末尾追加。
- 有且仅有一个完整区块：只更新区块内部。
- 标记缺失、嵌套或重复：停止并报告，不写入。

详细协议按需读取：

- 导航格式：`references/memory-navigation-protocol.md`
- 上下文恢复：`references/context-reconstruction.md`
- Agent 适配：`references/agent-adapters.md`
- Agent 原生记忆与增量回写：`references/native-agent-memory.md`
- 日志与归档：`references/session-log-format.md`
- 记忆压缩：`references/memory-compression.md`

## 安全边界

- 不把密码、Token、Cookie、私钥或证书写入记忆。
- 不静默覆盖已有记忆文件。
- 所有目标路径必须位于项目根目录内。
- `AGENTS.md` 只修改 ZSH 管理区块。
- 写入采用临时文件校验后原子替换；修改已有 `AGENTS.md` 前保存 `.zsh-backup`。
- 无法确认的信息标记为“待验证”，不编造上下文。
- 不自动删除历史日志。
- 不要求任务绑定某个模型；跨 Agent 接力是正常工作方式。
- 不主动扫描 `.codex`、`.claude`、`.kimi` 等用户级原生记忆目录。
