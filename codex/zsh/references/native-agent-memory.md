# Agent 原生记忆与增量回写

## 权威来源

用户当前明确指令始终最高。在持久化历史来源中，ZSH 项目记忆高于 Agent 原生记忆；原生记忆高于未经验证的当前推断。

Agent 可以使用当前环境已经提供给它的原生记忆，但不得主动扫描其他 Agent 的用户级目录。原生记忆与 ZSH 重复时不回写；与 ZSH 冲突时保持 ZSH 当前基线并请求用户确认。

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
      "source": "agent-native"
    },
    {
      "id": "session-summary",
      "target": "session_log",
      "action": "add",
      "content": "完成认证模块实现，遗留集成测试。",
      "source": "current-session"
    }
  ]
}
```

`target` 可取 `current_task`、`project_memory`、`session_log`、`decisions`。更新必须提供 `match` 作为预期旧值；找不到旧值时归类为冲突。检查脚本只分类，不写文件。

## 回写分类

- `add`：新的、已验证的项目事实。
- `update`：已验证旧值且需要更新。
- `duplicate`：现有 ZSH 记忆已经包含相同信息。
- `conflict`：预期旧值不存在，必须确认。
- `rejected`：候选无效、包含敏感信息或本机用户绝对路径。

Agent 只在分类完成后写入 `add` 和经确认的 `update`。不得自动处理冲突或拒绝项。

