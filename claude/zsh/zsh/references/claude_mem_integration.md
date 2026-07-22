# claude-mem 集成指南（zsh，Claude 独占）

> 本文件是 Claude Code 独占功能。薄适配层（`AGENT_MEMORY.md` 导航）与 claude-mem 职责分离：
> 前者告诉 agent「去哪里读记忆」，后者补充「原始会话细节」。

## 分工原则

zsh 和 claude-mem 插件**互补使用，不冗余**：

| 职责 | zsh | claude-mem |
|------|-----|------------|
| 导航入口 | ✅ `AGENT_MEMORY.md`（统一导航与读写协议） | ❌ 不重复 |
| 项目架构记忆（三层） | ✅ `skill-docs/PROJECT_MEMORY.md`（热/温/冷） | ❌ 不重复 |
| 当前任务状态 | ✅ `skill-docs/CURRENT_TASK.md` | ❌ 不重复 |
| 会话进度日志 | ✅ `skill-docs/SESSION_LOG.md`（小时+天+周） | ❌ 不重复 |
| 架构决策记录 | ✅ `skill-docs/DECISIONS.md`（ADR） | ❌ 不重复 |
| 历史归档索引 | ✅ `skill-docs/memory-archive/INDEX.md` | ❌ 不重复 |
| 会话原始内容 | ❌ 不存储 | ✅ claude-mem 存储 |
| 代码片段/命令历史 | ❌ 不存储 | ✅ claude-mem 存储 |
| 自动触发恢复 | ✅ 会话开始时（读导航/热记忆） | ✅ 按需查询 |

## 核心区别

- **zsh** 存储「结构化摘要」—— 经过整理的关键信息，保存在项目 Markdown 文件中
- **claude-mem** 存储「原始会话内容」—— 完整的对话历史、代码片段和命令历史

两者互补：zsh 提供可核查的跨 Agent 工作状态，claude-mem 保留当次会话的细粒度细节。

## 恢复上下文的推荐流程

### 会话启动时

1. **先读 `AGENT_MEMORY.md`**（导航入口）→ 了解记忆布局与读写协议
2. **读 `skill-docs/PROJECT_MEMORY.md` 热记忆** → 获取项目全局状态
3. **读 `skill-docs/CURRENT_TASK.md`** → 了解当前任务进度与精确续接位置
4. **检查 `skill-docs/SESSION_LOG.md`** 最新条目 → 了解最近的工作
5. **按需查询 claude-mem** → 获取具体的代码片段、命令历史、API 调用细节

> 前 4 步在每次会话开始时执行；第 5 步只在需要具体代码/命令细节时才触发。

### 会话结束时

1. **更新 `skill-docs/CURRENT_TASK.md`** → 同步任务进度、精确续接位置
2. **追加 `skill-docs/SESSION_LOG.md`** → 记录本次会话摘要
3. **如有新架构决策，追加 `skill-docs/DECISIONS.md`**
4. **claude-mem 自动保存** → 原始会话内容由插件自动处理

## 去重规则

### 不写入 zsh 的内容

- 完整的代码片段（claude-mem 会保存）
- 命令行输出（claude-mem 会保存）
- 错误堆栈（claude-mem 会保存）
- 完整的 API 响应（claude-mem 会保存）

### 必须写入 zsh 的内容

- 架构决策（`DECISIONS.md`）
- 任务进度与续接位置（`CURRENT_TASK.md`）
- 会话摘要（`SESSION_LOG.md`）
- 项目记忆更新（`PROJECT_MEMORY.md`）

## 协作示例

### 场景：用户问"上次那个模块是怎么实现的？"

1. 先读 `AGENT_MEMORY.md` → 定位记忆布局
2. 再读 `skill-docs/CURRENT_TASK.md` → 确认当前相关工作上下文
3. 再读 `skill-docs/SESSION_LOG.md` → 找到上次修改的会话记录
4. 最后查 claude-mem → 获取具体的代码实现细节

### 场景：用户问"上次我们讨论的架构决策是什么？"

1. 先读 `skill-docs/DECISIONS.md` → 找到相关 ADR
2. 再读 `skill-docs/PROJECT_MEMORY.md` 温记忆 → 找到相关模块说明
3. 最后查 claude-mem → 获取讨论过程中的具体示例

## 安装 claude-mem

```bash
# 从 marketplace 安装
/plugin install thedotmack/claude-mem

# 或先添加 marketplace 再安装
/plugin marketplace add thedotmack/claude-mem
```

安装后，zsh 的 `check_structure.py` 会在健康检查的 JSON 输出中报告 `claude_mem` 字段
（检测 `~/.claude/plugins/claude-mem` 或 `~/.agents/plugins/claude-mem`）。

不安装 claude-mem **不影响** zsh 正常运行——zsh 是薄适配层与记忆目录；claude-mem 只是可选的细节补充。

## 注意事项

- 不要将 claude-mem 的内容复制到 zsh 的 Markdown 文件中
- 不要将 zsh 的结构化摘要重复写入 claude-mem
- 恢复上下文时，先读 zsh 获取全局状态与续接位置，再查 claude-mem 获取细节
- zsh 项目记忆是跨 Agent 权威来源；claude-mem 是单会话的细节补充
