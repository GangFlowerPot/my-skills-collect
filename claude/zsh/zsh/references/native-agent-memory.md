# Agent 原生记忆（auto-memory）与增量回写

## 权威来源

用户当前明确指令始终最高。在持久化历史来源中，ZSH 项目记忆高于 Agent 原生记忆（auto-memory）；原生记忆高于未经验证的当前推断。

Agent 可以使用当前环境已经提供给它的原生记忆（auto-memory），但不得主动扫描其他 Agent 的用户级目录。原生记忆与 ZSH 重复时不回写；与 ZSH 冲突时保持 ZSH 当前基线并请求用户确认。

## 在 Claude Code 中的适配

在 Claude Code 中，「Agent 原生记忆」即 **auto-memory**，具体包括：

- `CLAUDE.md`（项目共享，自动加载）中的注入内容
- `CLAUDE.local.md`（用户私有，自动加载）中的注入内容
- 当前模型会话上下文

注意：ZSH 的薄适配托管区块也放在 `CLAUDE.md` 中（`ZSH:MEMORY:START/END` 标记内）。处理原则：

1. 把 auto-memory 内容视为**候选（candidate）**，不是权威事实来源。
2. ZSH 的托管区块仅更新 `ZSH:MEMORY` 区块内部，**绝不覆写 auto-memory 写入的原生内容**。
3. `CLAUDE.local.md` 是私有原生记忆，ZSH **只读不写**。
4. 当 auto-memory 与 ZSH 项目记忆冲突时，以 ZSH 当前基线为准，并请求用户确认。

## 候选 JSON

Agent 先把需要持久化的内容提取为 UTF-8 JSON：

```json
{
  "candidates": [
    {
      "id": "task-auth-status",
      "target": "current_task",
      "action": "update",
      "match": "认证模块：设计中",
      "content": "认证模块：实现完成，下一步补充集成测试",
      "source": "auto-memory"
    },
    {
      "id": "session-summary",
      "target": "session_log",
      "action": "add",
      "content": "完成认证模块实现，遗留集成测试。",
      "source": "current-session"
    },
    {
      "id": "claude-injected",
      "target": "project_memory",
      "action": "add",
      "content": "技术栈：Python + FastAPI。",
      "source": "auto-memory"
    }
  ]
}
```

`target` 可取 `current_task`、`project_memory`、`session_log`、`decisions`。更新必须提供 `match` 作为预期旧值；找不到旧值时归类为冲突。检查脚本只分类，不写文件。

**Claude 专属 `source` 枚举**：

- `auto-memory`：Claude Code 原生注入（来自 `CLAUDE.md` / `CLAUDE.local.md` 自动加载内容）
- `agent-native`：其他 Agent 的原生记忆
- `current-session`：当前会话上下文
- `claude-mem`：来自 claude-mem 插件（见 `references/claude_mem_integration.md`）
- `zsh-block`：来自 `CLAUDE.md` 中 ZSH:MEMORY 托管区块的指引（只读引用，不回写）

`CLAUDE.local.md` 的内容永远归类为候选，不在 ZSH 回写范围。

## 回写分类

- `add`：新的、已验证的项目事实。
- `update`：已验证旧值且需要更新。
- `duplicate`：现有 ZSH 记忆已经包含相同信息。
- `conflict`：预期旧值不存在，必须确认。
- `rejected`：候选无效、包含敏感信息或本机用户绝对路径。

Agent 只在分类完成后写入 `add` 和经确认的 `update`。不得自动处理冲突或拒绝项。

## 与 claude-mem 的去重

auto-memory（原生注入）和 claude-mem 都属于外部记忆源，都只作为候选。差异在于：

- **auto-memory**：会话入口/上下文，在启动时即注入；ZSH 按候选回写规则处理。
- **claude-mem**：原始会话内容（代码/命令），按需查询；详见 `references/claude_mem_integration.md`。

两者都不直接写入 ZSH 的记忆摘要；ZSH 只保留经过验证的项目事实。
