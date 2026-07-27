# 问题升级循环（Question Escalation Loop）

## 是什么

子 agent 在工作中遇到疑问时，**主动记录 → 在触发事件节点上报给 leader → leader 聚合后展示给用户回答 → leader 分发给子 agent** 的闭环。

## 为什么需要

进度查询只能汇报「状态/进展/阻塞项」，**无法把子 agent 遇到的具体疑问升级给用户**。子 agent 遇到决策点只能自行猜测或卡住，用户也无法在进度汇报时集中回答。

**问题来源**包括：
- 子 agent 工作中遇到的决策点（本子协议主要覆盖）
- reviewer 代码审查中发现的「需用户决策」项（见 `references/code-review-protocol.md`）——reviewer 的审查报告经 leader 分流后，需决策项也走此升级循环

## 设计原则

1. **复用 StatusReport/v2**：问题通过 StatusReport/v2 的【待答复问题】字段上报，随状态回复一并收集。**不新增独立收集轮次**。
2. **跳过并继续**：子 agent 汇报问题后**不停留**，跳过该工作项继续做其他工作，等回答回来再补。无「暂停等待」语义。
3. **不造新消息类型**：答复分发复用现有 `[CONTEXT ADDENDUM]` 信封。
4. **事件驱动**：审查、测试、提问和交接使用事件驱动（`design_ready` / `contract_ready` / `review_ready` / `test_ready` / `acceptance_ready`），不得使用主观百分比作为正式流程条件。

---

## 子 agent 问题记录（question_log）

每个子 agent 在自身工作内存中维护一份**问题清单**，每条记录包含：

| 字段 | 说明 |
|---|---|
| 问题ID | `Q-{role}-{seq}`，如 `Q-FE-001`、`Q-BE-001`。role 用 FE/BE/TE，seq 按 agent 自增 |
| 所属触发事件 | `design_ready` / `contract_ready` / `review_ready` / `test_ready` / `acceptance_ready` |
| 决策等级 | `agent-assumption` / `cross-agent` / `leader-decidable` / `user-required`（详见 `references/decision-level.md`） |
| 问题内容 | 具体问题，可直接转述给用户 |
| 关联任务 | 任务标识（如「前端登录模块」） |
| 状态 | `待上报` / `已上报` / `已答复` / `已作废` |
| 答复内容 | 收到答复后填入 |
| 作废原因 | `自行裁决` / `已由{来源}解决` / `重复` |

### 记录触发条件

agent 遇到决策点，且满足**两者**时记录一条问题：
- (a) 存在多个可行方案
- (b) 选择会实质影响后续工作

**避免琐碎问题**：纯事实查询（如某个 API 的参数）应自行 Read 文档解决，不记录。

### 跳过并继续行为规范

1. **识别卡点**：任务推进中遇到信息缺失、歧义、或依赖未就绪
2. **记录问题**：在本地 question_log 中记下（不暂停）
3. **跳过该部分**：把卡点任务标记为 `⏸ 待回填`，继续推进**不依赖该问题的其他部分**
4. **触发事件汇报**：任务推进到触发事件节点时，把待回填问题填入状态回复的【待答复问题】字段
5. **答案到达后回填**：收到 leader / 用户 / 跨 agent 输出的答案后，回填到 `⏸ 待回填` 位置，更新相关产出

---

## 触发事件检查点

子 agent 维护一个指针 `last_reported_event`，记录上一次上报的触发事件。

**每次进度更新时**执行检查：当任务推进到触发事件节点时，上报该节点的问题。

### 关键语义

- 问题在**到达触发事件节点时才被"上报"**（待上报 → 已上报），未达前仅内部持有。
- **跳过节点**（如从设计直接到可测试）：依次补报中间节点的积压问题。
- **acceptance_ready 检查点**是最终检查：上报所有剩余问题。agent 继续做能做的部分，回答回来后再补，完成后进入空闲。

---

## 状态回复中的问题上报

问题通过 StatusReport/v2 的【待答复问题】字段上报，随状态回复一并收集。完整 schema 见 `references/status-report-schema.md`。

### 有问题时，【待答复问题】格式

```
【触发事件】review_ready
【待答复问题】
1. [Q-FE-001][review_ready] 是否采用方案A（JWT+refresh token）或方案B（session）实现登录态？ (关联任务: 前端登录模块)
2. [Q-FE-002][review_ready] 表单验证错误提示文案是否沿用旧版？ (关联任务: 前端登录模块)
```

### 上报范围

状态回复包含所有 `status ∈ {待上报, 已上报}` 的问题。已答复/已作废的问题**不出现**在回复中。

### 无问题时

```
【触发事件】无
【待答复问题】无
```

---

## leader 聚合 + 用户展示 + 答复分发

### leader 聚合

复用「进度」查询轮，从各 agent 回复中提取【待答复问题】，构建 `question_registry`：

```json
{
  "Q-FE-001": {
    "source_agent": "frontend-dev",
    "trigger_event": "review_ready",
    "decision_level": "user-required",
    "content": "是否采用方案A...",
    "presented_count": 1,
    "status": "待用户答复"
  }
}
```

- `presented_count`：已向用户提出的次数（用于表格「提出次数」列）
- leader 用此表做**去重**与**提出次数追踪**，避免重复提问

### 展示给用户（同一条消息两个 section）

```
📊 团队进度报告 · {时间}

## 一、进度总览
| 角色 | 状态 | 任务ID | 当前任务 | 进展 | 阻塞项 | 下一步 | 触发事件 | 待答复问题 | 变更文件 | 验证结果 |

## 二、待答复问题（共 N 题）
| 编号 | 来源 | 触发事件 | 决策等级 | 问题 | 关联任务 | 提出次数 |
```

### 答复分发

复用现有 `[CONTEXT ADDENDUM]` 信封（来源 = `用户答复`）：

```
[CONTEXT ADDENDUM]
来源：用户答复
答复时间：{时间}
答复项：
  1. 问题ID: Q-FE-001 | 答复: 方案A（JWT+refresh token） | 对原有上下文的变更: 新增
  2. 问题ID: Q-BE-001 | 答复: 需要新增 last_login 字段 | 对原有上下文的变更: 新增
未答复（用户跳过，请自行裁决或继续等待）: Q-FE-002
```

### 分发规则

- leader 按 `question_registry.source_agent` 路由，每个 agent **只收到自己的答复项 + 未答复列表**
- 若 leader 能代答（基于已有上下文），`来源` 可填 `leader 代答`

### 子 agent 收到后

- **答复项** → 匹配问题ID → `status = 已答复`，填入答复 → 继续工作（已跳过的工作项现在可补上）
- **未答复项** → 采用合理默认值继续，`status = 已作废`，`void_reason = 自行裁决`

---

## 边界情况处理

| 边界情况 | 处理方式 |
|---|---|
| **子 agent 在触发事件无问题** | 状态回复 `【待答复问题】无`，`【触发事件】review_ready`。leader 问题表不含该 agent，进度表正常展示 |
| **用户只回答部分问题** | leader 仅分发已答复项；未答复项保留在 agent 列表中（`status = 已上报`）。下次进度查询时 agent 重新上报，leader `presented_count + 1` 并再次提出。未答复项由 agent 自行裁决（`已作废`） |
| **跨 agent 重复/相似问题** | leader 聚合时做**语义去重**（LLM 判断）：相似问题合并为一行，「来源」列写 `frontend-dev / backend-dev`，备注「合并自」。答复同时分发给所有相关 agent。若判定为重复而非相似，保留一条，另一条由 leader 通知来源 agent `已作废（重复）` |
| **问题已被另一 agent 输出解决** | agent 收到 `[CONTEXT ADDENDUM]`（来源=跨 agent 输出）或自行发现答案后，匹配问题记录 → `status = 已作废`，`void_reason = 已由{来源}解决`。该问题不再出现在状态回复中 |
| **acceptance_ready（最终检查）** | agent 在 acceptance_ready 检查点上报所有剩余问题，继续做能做的部分；回答回来后再补，完成后进入空闲。遗留问题仍保留在列表中供用户可选答复 |

---

## 完整流程与工作示例

详见 `examples/question-escalation-e2e.md`（单轮循环完整流程：dev 记录问题 → 触发事件检查点 → leader 聚合展示 → 用户回答 → leader 分发 → dev 回填继续）。

---

## 与现有系统的关系

| 现有机制 | 如何复用 / 扩展 |
|---|---|
| StatusReport/v2 | 问题通过【待答复问题】字段上报，随状态回复一并收集 |
| `[CONTEXT ADDENDUM]` | **复用**作为答复分发信封，来源 = `用户答复` |
| 上下文注入（5 要素） | 不受影响 |
| leader 枢纽角色 | 新增聚合/去重/路由职责 |
| decision-level | 问题分级与不可自动决定范围（`references/decision-level.md`） |

## 协议归属

本协议是 `references/team-protocol.md` 的扩展。部署时，StatusReport/v2 与 leader 聚合格式由 `team-protocol.md` 定义；子 agent 行为规范与触发事件检查点由本文件定义。
