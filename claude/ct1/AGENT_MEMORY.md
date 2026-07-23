---
schema: zsh-memory/v1
project: "ynwl"
memory_root: skill-docs
updated_at: "2026-07-23T11:59:00+08:00"
status: active
---

# Agent Memory Navigation

这是 `ynwl` 的跨 Agent 记忆导航入口。任何 Agent 在恢复历史工作前，先读取本文件；本文件负责指路，不重复存储具体项目事实。

## 快速恢复

1. 读取 `skill-docs/CURRENT_TASK.md`，确认当前阶段、任务、阻塞和精确续接位置。
2. 读取 `skill-docs/PROJECT_MEMORY.md` 的热记忆，补足项目核心背景。
3. 读取 `skill-docs/SESSION_LOG.md` 的最后一个会话，确认最近发生的变化。
4. 读取 `skill-docs/DECISIONS.md` 中与当前任务相关且状态有效的决策。

## 记忆地图

| 内容 | 路径 | 读取时机 | 写入规则 |
|---|---|---|---|
| 当前任务 | `skill-docs/CURRENT_TASK.md` | 每次恢复必读 | 任务状态变化或会话结束时更新 |
| 项目记忆 | `skill-docs/PROJECT_MEMORY.md` | 需要项目背景时；热记忆优先 | 架构、约定或长期事实变化后更新 |
| 当前日志 | `skill-docs/SESSION_LOG.md` | 需要近期上下文时 | 会话结束时追加，禁止覆盖历史条目 |
| 决策记录 | `skill-docs/DECISIONS.md` | 涉及设计选择时 | 重要决策确认后追加 ADR |
| 历史索引 | `skill-docs/memory-archive/INDEX.md` | 当前文件不足时 | 周日志归档时更新 |
| 团队协同协议 | `skill-docs/TEAM_PROTOCOL.md` | 团队组建、进度查询、沟通模式时 | 团队结构或协议变化后更新 |

## 信息优先级

发生冲突时依次采用：

1. 用户当前明确指令
2. `skill-docs/CURRENT_TASK.md`
3. `skill-docs/DECISIONS.md` 中状态为“已接受”的最新相关决策
4. `skill-docs/PROJECT_MEMORY.md` 热记忆
5. `skill-docs/SESSION_LOG.md`
6. `skill-docs/memory-archive/` 历史归档
7. Agent 原生记忆
8. Agent 当前推断

报告发现的冲突，不要无声覆盖，也不要把推断写成事实。

## 单真相源规则（Single Source of Truth）

为避免 v3 中「同一决策三重表征 / 任务状态双重维护」的冗余，本 skill 明确：

- **决策内容**（背景 / 原因 / 影响 / 替代方案 / 代码位置）唯一真相源 = `skill-docs/DECISIONS.md`。`PROJECT_MEMORY.md` 热记忆只放简短快照 + 指向 `DECISIONS.md#adr-xxx` 的指针，**不重复**决策内容。
- **任务状态**（进度 / 阻塞 / 续接位置）唯一真相源 = `skill-docs/CURRENT_TASK.md`。`SESSION_LOG.md` 为追加型叙事，**不重复**遗留工作 / 进度（那些归 CURRENT_TASK）。
- 回写时若与上述文件冲突，以对应真相源为准；PROJECT_MEMORY 热记忆与 DECISIONS 冲突时以 DECISIONS 为准。

## Agent 原生记忆兼容

ZSH 项目记忆是跨 Agent 持久工作状态的权威来源。Agent 可以使用当前环境已经提供的原生记忆辅助工作，但不得主动扫描其他 Agent 的用户级记忆目录，也不得让原生记忆静默覆盖本项目记忆。

来自 Agent 原生记忆或当前会话的新信息必须先作为候选记忆，与现有项目记忆做增量比较：重复内容跳过，新增事实写入对应文件，状态更新保留必要历史，冲突内容等待用户确认，未验证推断不写入或明确标记“待验证”。

## 上下文重建协议

### 最小恢复

读取当前任务和最后一个会话，适合快速回答“上次做到哪了”。

### 标准恢复

在最小恢复基础上读取热记忆和相关决策，适合继续正常开发。

### 深度恢复

仅在长期中断、内容冲突或当前文件不足时读取温/冷记忆，并通过历史索引定位相关周日志。

恢复完成后向用户汇报：当前阶段、进行中任务、续接位置、阻塞项、下一步，以及需要验证的信息。

## 回写协议

回写前先提取结构化候选记忆并执行增量检查。ZSH 项目记忆是当前持久化基线：重复内容跳过，新增内容写入对应文件，更新内容必须验证旧值，冲突内容等待用户确认，敏感信息和本机用户绝对路径拒绝写入。

会话过程中：

- 任务状态变化后更新 `CURRENT_TASK.md`。
- 重要技术选择经确认后追加 `DECISIONS.md`。
- 稳定的项目事实变化后更新 `PROJECT_MEMORY.md` 对应层级。

会话结束时：

1. 更新当前任务、进度、位置、阻塞项和下一步。
2. 向当前日志末尾追加会话记录。
3. 必要时记录 ADR。
4. 检查周归档并更新历史索引。
5. 把本文件的 `updated_at` 更新为实际回写时间。

如果项目使用 Git，记忆文件默认随项目版本化；个人 Git 项目明确选择本地模式时，以 `.git/info/exclude` 为准。ZSH 不自动执行提交或推送。

## 安全

- 不记录密码、Token、Cookie、私钥、证书或其他秘密。
- 路径使用项目根目录相对路径。
- 缺失文件或失效引用必须报告。
- 历史日志默认只读，不自动删除。
