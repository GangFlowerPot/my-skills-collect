# ct1 Skill 改进实施规范

> 本文件面向负责维护、重构和测试 `ct1` Skill 的 Agent。
> 它不是用户说明书，而是一份可执行的工程改造任务书。

## 1. 文档元信息

| 字段 | 值 |
|---|---|
| 目标 Skill | `ct1` |
| 当前定位 | 多角色 Agent 团队创建与协作协议部署 |
| 目标定位 | 从软件需求到开发、审查、测试、验收和交付的多 Agent 编排器 |
| 改造原则 | 先统一协议，再补齐交付闭环，最后增强可靠性和效率 |
| 实施方式 | 分阶段、小步修改；每阶段完成后运行对应 eval |
| 禁止事项 | 不得在没有验证证据时宣称任务、测试或交付完成 |

## 2. Agent 执行要求

维护本 Skill 时遵守以下要求：

1. 修改前完整读取：
   - `SKILL.md`
   - 本文件
   - 本次任务涉及的 `references/*.md`
   - `evals/evals.json`
2. 保留现有有价值的能力：
   - 角色化上下文切片
   - 五要素任务模板
   - `[CONTEXT ADDENDUM]`
   - 问题升级和答复路由
   - 代码审查的独立角色
   - 跨会话协议持久化
3. 不同时大范围重写多个协议。每完成一个协议的修改，先检查引用关系和旧模板残留。
4. 静态规则、项目配置和运行状态必须分离：
   - 静态规则保存在 Skill 的 `references/`
   - 项目团队配置保存在项目 `.claude/teams/<team-id>/`
   - 任务、问题和 Agent 状态保存在运行状态文件
5. 所有完成状态必须有可核验的产物、命令结果或验收记录。
6. 不得使用主观进度百分比代替任务状态、测试结果或交付门禁。
7. 更新功能后同步更新 eval；旧 eval 不得继续验证已经废弃的行为。

## 3. 目标生命周期

`ct1` 最终应支持以下完整生命周期：

```text
判断任务规模与运行模式
  → 收集项目上下文
  → 需求澄清与验收标准
  → 选择或复用团队
  → 建立任务图与文件所有权
  → 方案及接口契约
  → 并行开发
  → 风险驱动的代码审查
  → 集成与测试
  → 修复与回归
  → Definition of Done 检查
  → 用户验收或交付确认
  → 生成交付报告
  → 持久化最终状态
```

## 4. 运行模式

必须支持两种显式模式：

### 4.1 `create-only`

适用于用户只要求创建团队、建立协议或准备后续工作。

完成条件：

- 团队配置已确认；
- 必需 Agent 已启动；
- 团队状态已持久化；
- 用户收到团队说明和使用方式；
- 不自动假定存在开发需求。

### 4.2 `delivery`

适用于用户已经给出需求，或者明确要求团队完成开发、测试和交付。

完成条件：

- 需求验收标准已经建立；
- 任务板中的必需任务全部满足项目级 DoD；
- 必需测试有真实执行结果；
- 严重审查问题已经关闭；
- 最终交付报告已经生成；
- 未完成、未测试和已知风险已明确披露。

默认决策：

- 有明确需求时默认使用 `delivery`；
- 只有组队意图、没有需求时使用 `create-only`；
- 简单、单文件、低风险任务允许降级为单 Agent，不创建完整团队。

---

# 第一阶段：P0 协议与定义一致性

## P0-01 重新定义 Skill 定位

### 当前问题

`SKILL.md` 主要把成功定义为创建团队、建立规则和部署进度查询，不能保证需求被推进到交付。

### 必须修改

1. 更新 `SKILL.md` frontmatter：
   - 同时描述团队创建和项目交付；
   - 加入“分工开发、代码审查、测试验收、交付”等触发语义；
   - 保留纯组队场景；
   - 加入近似负例边界，避免普通小任务过度触发。
2. 在主工作流最前面加入：
   - 任务规模判断；
   - `create-only` / `delivery` 模式判断。
3. 在主工作流末尾加入：
   - DoD 检查；
   - 交付报告；
   - 最终状态持久化。

### 验收标准

- 给出完整需求时，团队创建后继续推进需求，不停在“等待首个需求”；
- 只要求组队时，不擅自实施未知需求；
- 简单任务可以选择单 Agent；
- `delivery` 模式一定产生交付结论。

## P0-02 统一默认团队定义

### 当前问题

文档同时存在默认四人和默认五人的描述；`reviewer` 在主表中存在，但旧 eval 不要求启动。

### 目标设计

区分以下三类角色：

| 类别 | 角色 | 启动规则 |
|---|---|---|
| 固定角色 | `leader` | 始终存在 |
| 执行角色 | 前端、后端、全栈等 | 根据项目和任务选择 |
| 质量角色 | `tester` | 有可验收交付物时启用 |
| 审查角色 | `reviewer` | 有代码产出且进入审查阶段时延迟启动 |
| 专项角色 | DBA、DevOps、安全、UI 等 | 风险或任务需要时启用 |

### 必须修改

1. 删除所有“默认四人”或“默认五人”的冲突表述。
2. 将默认 Web 团队描述为：
   - 核心成员：leader、frontend-dev、backend-dev、tester；
   - 延迟角色：reviewer。
3. `TEAM_CONFIG` 记录：
   - 配置角色；
   - 当前已启动角色；
   - 延迟角色及启动条件。
4. 更新所有相关 eval。

### 验收标准

- `SKILL.md`、协议模板、运行状态和 eval 对角色定义一致；
- reviewer 不在无代码阶段长期空闲；
- reviewer 启动后自动加入状态查询范围。

## P0-03 建立 `StatusReport/v2`

### 当前问题

现有协议混用 6、8 和 9 字段，导致主线程、leader 和执行者可能使用不同格式。

### 目标 schema

创建 `references/status-report-schema.md`，定义：

```text
【协议版本】StatusReport/v2
【任务ID】任务板中的唯一 ID
【状态】空闲 / 就绪 / 工作中 / 阻塞 / 审查中 / 测试中 / 完成
【当前任务】一句话描述
【进展】已经完成的可验证结果
【阻塞项】无 / 问题或依赖 ID
【下一步】下一个具体动作
【需要的输入】无 / 所需输入
【触发事件】无 / 设计完成 / 契约就绪 / 可审查 / 可测试 / 待验收
【待答复问题】无 / 问题列表
【变更文件】无 / 文件路径列表
【验证结果】未执行 / 命令、结果和限制
```

### 必须修改

1. `SKILL.md` 不再内嵌旧六字段完整模板，只引用新 schema。
2. `references/team-protocol.md` 使用新 schema。
3. `question-escalation-protocol.md` 不再声称“扩展六字段为八字段”。
4. `code-review-protocol.md` 不再自行扩展字段。
5. 项目旧协议在恢复时执行版本检查：
   - v1：提示或自动迁移；
   - v2：直接使用；
   - 未知版本：停止自动覆盖，报告给用户。

### 验收标准

- 全仓库不再存在可执行的旧六字段模板；
- 所有角色使用同一协议版本；
- 状态报告能够关联任务、代码、问题和验证结果；
- 缺少必填字段时能标记报告不完整。

## P0-04 建立真正的唯一真相源

### 当前问题

相同规则被复制到 `SKILL.md`、`TEAM_PROTOCOL.md` 和多个扩展协议，修改后容易漏同步。

### 必须修改

权威文件规划：

```text
SKILL.md                               编排入口
references/lifecycle.md                生命周期
references/team-selection.md           团队选择
references/status-report-schema.md     状态格式
references/question-escalation-protocol.md
references/code-review-protocol.md
references/testing-gate.md
references/delivery-report.md
```

规则：

- 一个 schema 只能在一个文件中完整定义；
- 其他文档使用链接和简短说明；
- 项目运行目录记录协议版本，不复制全部 Skill 内容；
- 静态协议与运行状态不得写在同一文件。

### 验收标准

- 修改状态 schema 只需改一个文件；
- `rg` 搜索不会发现多个相互冲突的完整模板；
- 每个引用文件的职责明确。

## P0-05 移除具体模型版本绑定

### 当前问题

`SKILL.md` 写死 `opus` 和具体版本，可能与运行环境不匹配，也会增加不必要成本。

### 目标策略

```yaml
model_policy:
  leader: high-reasoning
  architect: high-reasoning
  developer: default
  reviewer: high-reasoning
  tester: default
  status-collector: lightweight
```

平台无法指定模型时，继承当前会话模型。用户指定模型时，以用户配置为准。

### 验收标准

- Skill 不包含会快速过时的具体模型版本；
- 简单状态整理不强制使用高成本模型；
- 不支持模型选择的平台仍能正常执行。

---

# 第二阶段：P1 项目交付闭环

## P1-01 增加 Requirement Brief

### 当前问题

自然语言需求没有被转化为统一、可开发、可测试的规格。

### 新增文件

- `references/requirement-brief.md`
- `assets/REQUIREMENT_BRIEF.template.md`

### 模板要求

```markdown
# Requirement Brief

## 目标
## 范围
## 不在范围
## 用户场景
## 验收标准
## 技术与业务约束
## 风险
## 假设
## 待确认问题
```

每个验收标准使用唯一 ID，例如 `AC-001`。

### 决策规则

- 局部、可逆、低风险问题可以记录假设后继续；
- 数据删除、权限、安全、费用、外部发布和不可逆迁移必须由用户确认；
- 每个开发任务至少关联一个 AC；
- tester 必须把测试用例映射到 AC。

### 验收标准

- 开发开始前存在 Requirement Brief；
- 需求范围和不在范围明确；
- 最终交付报告能逐项报告 AC 结果。

## P1-02 增加任务板和依赖图

### 当前问题

leader 通过聊天分配任务，没有统一的任务状态、依赖、责任人和验收证据。

### 新增文件

- `references/task-board-schema.md`
- `assets/TASK_BOARD.template.md`

### 任务 schema

```yaml
id: BE-003
title: 实现创建运单接口
owner: backend-dev
status: in_progress
priority: high
risk: medium
depends_on:
  - ARCH-001
acceptance_criteria:
  - AC-003
write_scope:
  - backend/waybill/**
artifacts:
  - WaybillController.java
verification:
  - command: mvn test -pl waybill
handoff_to:
  - reviewer
  - tester
```

### 状态机

```text
backlog
  → ready
  → in_progress
  → review
  → test
  → accepted
  → delivered

任意非终态均可进入 blocked。
```

### 状态约束

- 依赖未完成，不能进入 `ready`；
- 没有 owner，不能进入 `in_progress`；
- 严重审查问题未关闭，不能进入 `test`；
- 测试失败，退回 `in_progress`；
- 没有验证证据，不能进入 `accepted`；
- 未满足项目级 DoD，不能进入 `delivered`。

### 验收标准

- 每项工作都有唯一 ID 和 owner；
- leader 可从任务板生成进度，不依赖聊天记忆；
- 会话恢复后可以继续任务；
- 任务状态变化符合状态机。

## P1-03 增加接口契约生命周期

### 当前问题

前后端接口变化只有增量通知，没有正式的创建、评审、冻结和变更流程。

### 新增文件

- `references/api-contract-protocol.md`

### 契约状态

```text
draft
  → frontend-reviewed
  → tester-reviewed
  → frozen
  → implemented
  → verified
```

### 契约必需字段

```yaml
endpoint: POST /api/waybills
owner: backend-dev
consumers:
  - frontend-dev
  - tester
status: draft
request: {}
response: {}
errors: []
permissions: []
version: 1
```

### 变更规则

- frozen 后的修改必须增加版本或变更记录；
- leader 找出所有 consumer 和受影响任务；
- 使用 `[CONTEXT ADDENDUM]` 通知相关角色；
- 受影响任务重新评估状态；
- tester 更新测试用例。

### 验收标准

- 前端、后端和 tester 使用同一契约版本；
- 契约变化不会只通知单个角色；
- 最终报告列出已交付的契约变化。

## P1-04 将 tester 升级为质量负责人

### 当前问题

tester 主要编写用例，没有明确测试执行、缺陷回流和交付阻断职责。

### 新增文件

- `references/testing-gate.md`
- `assets/TEST_PLAN.template.md`
- `assets/TEST_REPORT.template.md`

### tester 职责

1. 审查验收标准是否可测；
2. 制定测试计划；
3. 建立 AC 到测试用例的映射；
4. 检查开发自测证据；
5. 执行或指导执行自动化、集成、边界和回归测试；
6. 建立缺陷并跟踪复测；
7. 给出是否允许交付的质量结论。

### 缺陷状态机

```text
open
  → assigned
  → fixed
  → retest
  → closed

复测失败进入 reopened。
```

### 测试门禁

- 每个必需 AC 至少有一个测试；
- P0/P1 缺陷为零；
- 必需测试全部执行；
- 测试命令、结果和环境已记录；
- 未执行测试必须说明原因和风险；
- 环境不可用不得标记为“测试通过”。

### 验收标准

- tester 提供真实测试结果，而不只是建议；
- 测试失败能退回对应开发任务；
- 修复后有复测记录；
- 最终交付引用 TEST_REPORT。

## P1-05 建立 Definition of Done

### 任务级 DoD

任务进入 `accepted` 前必须满足：

- 产物已经生成；
- 符合现有技术栈和架构；
- 开发自测完成；
- 严重审查问题为零；
- 对应测试通过；
- AC 有验证证据；
- 相关文档或契约已更新；
- 临时假设已经记录。

### 项目级 DoD

项目进入 `delivered` 前必须满足：

- 所有必需任务为 `accepted`；
- 所有必需 AC 通过；
- P0/P1 缺陷为零；
- 构建和必需测试成功；
- 数据迁移和回滚要求已经处理；
- 已知限制已经披露；
- 交付报告已经生成。

### 验收标准

- 不得仅凭“100%”声明完成；
- 每个门禁都有证据；
- 不满足 DoD 时输出“有条件完成”或“未完成”。

## P1-06 增加正式交付报告

### 新增文件

- `references/delivery-report.md`
- `assets/DELIVERY_REPORT.template.md`

### 报告格式

```markdown
# Delivery Report

## 交付结论
通过 / 有条件通过 / 未通过

## 需求完成情况
| AC | 结果 | 证据 |

## 变更摘要
## 修改文件
## 接口、数据库和配置变化
## 构建与测试结果
## Code Review 结果
## 部署或使用说明
## 数据迁移说明
## 回滚说明
## 已知限制与风险
## 未完成事项
## 用户下一步操作
```

### 交付判定

- `通过`：所有门禁满足；
- `有条件通过`：只剩非阻断风险，并已明确披露；
- `未通过`：存在严重问题、测试失败或关键 AC 未完成。

### 验收标准

- 每次 `delivery` 模式均产生报告；
- 报告内容与任务板、测试报告和审查记录一致；
- 不掩盖未测试、环境限制或遗留问题。

---

# 第三阶段：P2 工程可靠性

## P2-01 增加文件所有权与工作区策略

### 当前问题

多 Agent 并行开发时，没有明确文件修改范围和公共文件 owner。

### 新增文件

- `references/workspace-strategy.md`

### 配置示例

```yaml
workspace_mode: shared
write_scope:
  frontend-dev:
    - frontend/src/**
  backend-dev:
    - backend/**
shared_files:
  owner: leader
  paths:
    - openapi.yaml
    - package-lock.json
```

### 强制规则

- 开始修改前检查工作区已有变化；
- 不覆盖用户或其他任务的修改；
- 每个任务声明 `write_scope`；
- 修改公共文件前获得 ownership；
- tester 和 reviewer 默认只读；
- 中大型项目优先使用独立 worktree 或分支；
- 合并由 leader 或 integrator 负责；
- 不允许通过直接覆盖解决冲突。

### 验收标准

- 每个变更文件能关联任务和 owner；
- 同一文件不会被多个 Agent 无协调修改；
- 用户已有改动得到保留；
- 冲突有明确处理责任人。

## P2-02 增加 Agent 健康检查和替补机制

### 新增文件

- `references/recovery-protocol.md`

### 健康状态

```text
active
idle
waiting_input
unresponsive
failed
replaced
completed
```

### 恢复流程

1. 第一次无响应：重新请求一次状态；
2. 第二次无响应：检查 Agent 是否仍活跃；
3. 确认失败：保存其任务、文件、问题和最后状态；
4. leader 选择重试、重新分配或启动替补；
5. 替补 Agent 接收 `Handoff Brief`；
6. 替补先验证已有产物，再继续工作。

### Handoff Brief

```markdown
## 当前任务
## 已完成
## 未完成
## 修改文件
## 已做决策
## 待答复问题
## 验证结果
## 下一步建议
```

### 验收标准

- 单个 Agent 失败不会使项目永久停滞；
- 重试次数有限；
- 替补能够恢复任务上下文；
- 未完成工作不会被误报为完成。

## P2-03 为问题增加决策等级

### 当前问题

未答复问题可能被 Agent 自行裁决，但没有区分风险。

### 新 schema

```yaml
id: Q-BE-001
decision_level: user-required
question: 是否允许删除历史数据
reversible: false
impact: high
status: pending
```

### 决策等级

| 等级 | 处理方式 |
|---|---|
| `agent-assumption` | Agent 可采用可逆默认值并记录 |
| `cross-agent` | 路由给对应 owner |
| `leader-decidable` | leader 根据项目规则裁决 |
| `user-required` | 必须用户决定，不允许自动作废 |

以下问题默认是 `user-required`：

- 数据删除；
- 权限和认证；
- 安全与合规；
- 付费和资源成本；
- 外部发布；
- 不可逆数据库迁移；
- 明显改变需求范围。

### 验收标准

- 高风险问题不会被自动作废；
- 低风险可逆问题不会阻塞整个团队；
- 临时假设进入最终交付报告。

## P2-04 使用内容哈希验证上下文合约

### 当前问题

使用文档更新时间和 mtime 判断合约过期，容易误判。

### 目标 schema

```yaml
contract_version: 2
sources:
  - path: docs/req.md
    sha256: "<hash>"
    sections:
      - "3"
      - "4"
role_slices:
  frontend-dev:
    source_refs:
      - docs/req.md#3
```

### 必须实现

- 比较内容哈希，不依赖 mtime；
- 只重建受变化影响的角色切片；
- 动态补充改变正式契约时标记 `dirty`；
- 任务结束前将有效变化回写正式文档，或记录未回写差异。

### 验收标准

- 内容不变时不因 mtime 改变而重建；
- 内容变化时一定能发现；
- 能指出受影响的角色和任务。

## P2-05 按 `team_id` 隔离运行状态

### 当前问题

固定 `TEAM_PROTOCOL.md` 容易被不同团队或 eval 覆盖。

### 目标目录

```text
.claude/
└── teams/
    └── <team-id>/
        ├── TEAM_CONFIG.yaml
        ├── TEAM_STATE.json
        ├── TASK_BOARD.md
        ├── QUESTION_REGISTRY.json
        ├── REVIEW_LOG.md
        ├── TEST_REPORT.md
        └── DELIVERY_REPORT.md
```

### 规则

- `team_id` 必须唯一且稳定；
- 多团队可并存；
- 更新导航使用幂等标记块；
- 不直接覆盖用户已有协议；
- 创建时说明运行文件是否建议提交到 Git。

导航标记：

```markdown
<!-- ct1:teams:start -->
...
<!-- ct1:teams:end -->
```

### 验收标准

- 多个团队互不覆盖；
- 重复运行不重复插入导航；
- 恢复时能定位正确团队；
- 模板和具体项目数据不混合。

---

# 第四阶段：P3 成本与效率优化

## P3-01 将固定三轮审查改为风险驱动

### 当前问题

所有编码任务在 33%、66%、100% 执行三轮审查，成本高且依赖主观百分比。

### 风险策略

| 风险 | 示例 | 审查方式 |
|---|---|---|
| 低 | 文案、局部样式、简单配置 | 最终审查一次 |
| 中 | 普通业务页面、普通接口 | 契约或设计审查 + 最终审查 |
| 高 | 权限、安全、支付、数据迁移 | 设计、实现中、最终三轮 |

### 事件触发

使用以下事件替代固定百分比：

```text
design-ready
contract-ready
first-runnable-slice
review-ready
release-ready
```

### 验收标准

- 小任务不被强制执行三轮；
- 高风险任务保持充分审查；
- 每轮审查有明确范围；
- 后续轮次重点检查新增代码和遗留修复。

## P3-02 增加任务规模判断

### 决策建议

```text
单文件、低风险、一步完成
  → 单 Agent

跨模块但职责单一
  → leader + 1 个执行 Agent

前后端联动且需要验收
  → 标准开发团队

安全、迁移、部署或大型项目
  → 增加专项角色
```

### 不应触发完整团队的场景

- 修正 README 拼写；
- 解释现有代码；
- 查询现有团队成员；
- 编写团队介绍文案；
- 非软件开发团队；
- 无需并行的一步任务。

### 验收标准

- 简单任务不会产生完整团队成本；
- 复杂任务仍能获得多角色分工；
- trigger eval 覆盖近似负例。

---

# 第五阶段：评测体系

## 5.1 触发评测

新增 `evals/trigger-evals.json`，至少包含：

- 8～10 个应触发用例；
- 8～10 个不应触发的近似用例；
- 中文、英文、正式、口语和隐式表达；
- `create-only`、`delivery` 和单 Agent 降级场景。

重点负例：

- 修改一个小文件；
- 解释团队角色；
- 创建非软件团队名单；
- 查询已有进度但当前没有 ct1 团队；
- 普通代码审查请求。

## 5.2 协议评测

新增 `evals/protocol-evals.json`，覆盖：

1. 默认团队配置一致；
2. reviewer 延迟启动；
3. `StatusReport/v2`；
4. 问题分级与路由；
5. Agent 无响应和替补；
6. 多团队隔离；
7. 旧协议升级；
8. 上下文哈希失效；
9. 文件 ownership 冲突。

## 5.3 端到端交付评测

新增 `evals/delivery-evals.json`，至少覆盖：

1. 前后端小功能正常交付；
2. API 契约中途变化；
3. tester 发现失败并退回开发；
4. reviewer 发现严重安全问题；
5. Agent 失败后替补接管；
6. 用户中途追加需求；
7. 多 Agent 尝试修改同一文件；
8. 测试环境不可用；
9. 最终仍有非阻断风险；
10. 关键 AC 未完成时禁止交付通过。

## 5.4 断言要求

评测不能只检查“是否生成文件”，还必须验证：

- 每个 AC 有测试映射；
- accepted 任务有验证证据；
- 测试失败时没有标记交付成功；
- 严重审查问题未关闭时不能 delivered；
- 文件变化符合 write scope；
- DELIVERY_REPORT 与真实测试结果一致；
- 所有 passed 断言都有非空 evidence；
- baseline 与 with-skill 使用相同任务和环境。

## 5.5 基准指标

至少记录：

- 任务完成率；
- AC 通过率；
- 严重问题遗漏数；
- 测试误报通过数；
- 返工次数；
- Agent 重试次数；
- 总耗时；
- Token 消耗；
- 用户必须介入的次数。

---

# 第六阶段：目标目录结构

重构完成后的建议结构：

```text
ct1/
├── SKILL.md
├── AGENT_IMPROVEMENT_PLAN.md
├── references/
│   ├── lifecycle.md
│   ├── team-selection.md
│   ├── requirement-brief.md
│   ├── task-board-schema.md
│   ├── status-report-schema.md
│   ├── context-contract.md
│   ├── dynamic-supplement-protocol.md
│   ├── question-escalation-protocol.md
│   ├── api-contract-protocol.md
│   ├── workspace-strategy.md
│   ├── code-review-protocol.md
│   ├── testing-gate.md
│   ├── recovery-protocol.md
│   └── delivery-report.md
├── assets/
│   ├── REQUIREMENT_BRIEF.template.md
│   ├── TASK_BOARD.template.md
│   ├── TEST_PLAN.template.md
│   ├── TEST_REPORT.template.md
│   └── DELIVERY_REPORT.template.md
├── scripts/
│   ├── validate_protocol.py
│   ├── validate_task_board.py
│   └── check_delivery_gate.py
└── evals/
    ├── trigger-evals.json
    ├── protocol-evals.json
    └── delivery-evals.json
```

---

# 第七阶段：建议实施顺序

严格按以下顺序实施，避免在基础协议未统一时继续扩展：

## Iteration 1：一致性修复

- [ ] P0-01 重新定义 Skill 定位和运行模式
- [ ] P0-02 统一团队定义
- [ ] P0-03 建立 `StatusReport/v2`
- [ ] P0-04 清理重复协议
- [ ] P0-05 移除具体模型版本
- [ ] 更新现有 eval
- [ ] 运行协议一致性检查

完成门槛：仓库中不存在互相冲突的团队人数或状态模板。

## Iteration 2：需求和任务管理

- [ ] P1-01 Requirement Brief
- [ ] P1-02 TASK_BOARD
- [ ] P1-03 API 契约生命周期
- [ ] 增加对应模板和 eval

完成门槛：一个需求可以被拆成带 AC、owner、依赖和验证方式的任务。

## Iteration 3：测试和交付

- [ ] P1-04 tester 质量职责
- [ ] P1-05 Definition of Done
- [ ] P1-06 Delivery Report
- [ ] 增加完整交付 eval

完成门槛：测试失败或严重问题未关闭时，Skill 不得报告交付通过。

## Iteration 4：工程可靠性

- [ ] P2-01 文件 ownership
- [ ] P2-02 Agent 恢复
- [ ] P2-03 问题分级
- [ ] P2-04 上下文哈希
- [ ] P2-05 多团队隔离

完成门槛：Agent 失败、文件冲突或会话恢复不会导致任务状态丢失。

## Iteration 5：效率和最终评测

- [ ] P3-01 风险驱动审查
- [ ] P3-02 任务规模判断
- [ ] 完成触发评测
- [ ] 完成协议评测
- [ ] 完成端到端交付评测
- [ ] 对比旧版和新版

完成门槛：新版在交付正确率和可靠性上提升，且不会让低风险小任务产生明显额外成本。

---

# 最终验收清单

只有全部满足时，才能认为本轮 Skill 重构完成：

- [ ] `create-only` 和 `delivery` 模式行为明确
- [ ] 团队角色定义无冲突
- [ ] 所有角色使用 `StatusReport/v2`
- [ ] 一个规则只有一个真相源
- [ ] 需求有 AC
- [ ] 任务有 ID、owner、依赖和 write scope
- [ ] API 契约有生命周期
- [ ] tester 执行真实测试并提供证据
- [ ] reviewer 使用风险驱动审查
- [ ] 测试失败会回流开发
- [ ] 严重问题未关闭时禁止交付
- [ ] Agent 故障可以恢复或替换
- [ ] 多团队运行状态互不覆盖
- [ ] 上下文合约使用内容哈希
- [ ] 最终交付报告与真实状态一致
- [ ] 所有新增功能有 eval
- [ ] 所有 passed 断言有 evidence
- [ ] 简单任务可以降级为单 Agent

## 最终原则

维护 Agent 必须始终以以下标准判断成功：

> Agent 启动、状态达到 100%、文件已经生成，都不等于项目已经完成。
> 只有验收标准通过、测试证据存在、严重问题关闭、交付物完整并且风险被如实披露，才可以宣布交付成功。
