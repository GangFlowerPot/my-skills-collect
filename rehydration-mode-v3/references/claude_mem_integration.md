# claude-mem 集成指南（V3）

## 分工原则

rehydration-mode-v3 和 claude-mem 插件**互补使用，不冗余**：

| 职责 | rehydration-mode-v3 | claude-mem |
|------|---------------------|------------|
| 项目架构记忆 | ✅ PROJECT_MEMORY.md（结构化三层） | ❌ 不重复 |
| 当前任务状态 | ✅ CURRENT_TASK.md | ❌ 不重复 |
| 会话进度日志 | ✅ SESSION_LOG.md（小时+天+周） | ❌ 不重复 |
| 架构决策记录 | ✅ DECISIONS.md（ADR） | ❌ 不重复 |
| 会话原始内容 | ❌ 不存储 | ✅ claude-mem 存储 |
| 代码片段/命令历史 | ❌ 不存储 | ✅ claude-mem 存储 |
| 自动触发恢复 | ✅ 会话开始时 | ✅ 按需查询 |

## 核心区别

- **rehydration-mode-v3** 存储「结构化摘要」—— 经过人工整理的关键信息
- **claude-mem** 存储「原始会话内容」—— 完整的对话历史和代码片段

## 恢复上下文的推荐流程

### 会话启动时

1. **先读本 Skill 的热记忆层**（PROJECT_MEMORY.md 热记忆）→ 获取项目全局状态
2. **读取 CURRENT_TASK.md** → 了解当前任务进度
3. **读取 SESSION_LOG.md 最新条目** → 了解最近的工作
4. **按需查询 claude-mem** → 获取具体的代码片段、命令历史、API 调用细节

### 会话结束时

1. **更新 CURRENT_TASK.md** → 同步任务进度
2. **追加 SESSION_LOG.md** → 记录本次会话摘要
3. **claude-mem 自动保存** → 原始会话内容由插件自动处理

## 去重规则

### 不写入 rehydration-mode-v3 的内容

- 完整的代码片段（claude-mem 会保存）
- 命令行输出（claude-mem 会保存）
- 错误堆栈（claude-mem 会保存）
- 完整的 API 响应（claude-mem 会保存）

### 必须写入 rehydration-mode-v3 的内容

- 架构决策（DECISIONS.md）
- 任务进度变更（CURRENT_TASK.md）
- 会话摘要（SESSION_LOG.md）
- 项目记忆更新（PROJECT_MEMORY.md）

## 协作示例

### 场景：用户问"上次那个订单接口是怎么写的？"

1. 先读 PROJECT_MEMORY.md 热记忆 → 找到 API 路径 `/api/blade-system/dingDan`
2. 再读 SESSION_LOG.md → 找到上次修改该接口的会话记录
3. 最后查 claude-mem → 获取具体的代码实现细节

### 场景：用户问"上次我们讨论的策略工厂是什么？"

1. 先读 DECISIONS.md → 找到 ADR-001: 策略工厂钩子注册规范
2. 再读 PROJECT_MEMORY.md 温记忆 → 找到策略工厂的详细说明
3. 最后查 claude-mem → 获取讨论过程中的具体代码示例

## 安装 claude-mem

```bash
# 全局安装
claude plugins install claude-mem

# 或从 marketplace
# /plugin marketplace add thedotmack/claude-mem
```

## 注意事项

- 不要将 claude-mem 的内容复制到 rehydration-mode-v3 的文件中
- 不要将 rehydration-mode-v3 的结构化摘要重复写入 claude-mem
- 恢复上下文时，先读 rehydration-mode-v3 获取全局状态，再查 claude-mem 获取细节
