# ct1 下一轮优化建议与 Agent 整改计划

> 适用目录：`D:\claudeCode\skills\my-skills-collect\claude\ct1`  
> 文档用途：交给后续 Agent 阅读并执行下一轮 ct1 重构。  
> 本轮主题：**协议收敛、Markdown 去重、Python 3 运行基线、结构化状态、真实可执行门禁**。

---

## 1. 背景与本轮目标

ct1 已经完成第一轮架构升级，具备以下基础能力：

- `create-only` 与 `delivery` 两种运行模式；
- Pre-team 项目理解；
- Requirement Brief；
- Task Graph；
- 基于任务图动态生成团队；
- 文件所有权与写入范围；
- 延迟启动 tester、reviewer 和专项角色；
- Agent 健康检查与替补；
- 测试门禁、Definition of Done 和 Delivery Report；
- references、assets、scripts、evals 分层目录。

第一轮已经解决“固定前端、后端、测试角色组队”的核心问题，但当前仍存在：

1. 新旧协议同时存在；
2. 多个 Markdown 文件内容重叠；
3. “唯一真相源”实际存在多个副本；
4. StatusReport/v2 字段数量描述错误；
5. 固定 `33% / 66% / 100%` 里程碑仍残留；
6. Python 校验脚本默认依赖 Python 3，但没有明确运行基线；
7. 当前环境中的 `python` 可能指向 Python 2；
8. 校验脚本主要检查文件和关键词，没有校验真实运行状态；
9. 动态角色 schema 与固定前后端示例仍有冲突；
10. `create-only` 在无需求时仍可能过早启动执行 Agent。

本轮不以增加更多协议和角色为目标，而是完成以下收敛：

> 保持入口简单，把必要复杂度放入单一协议、结构化运行状态和可执行校验中。

---

## 2. 总体设计原则

整改 Agent 必须遵守以下原则。

### 2.1 简单入口

`SKILL.md` 只承担：

1. 触发边界；
2. 模式选择；
3. 生命周期主流程；
4. 按场景加载 reference 的路由；
5. 不可违反的核心约束；
6. 最终完成条件。

完整 schema、长示例、迁移说明和模板不得重复堆入 `SKILL.md`。

### 2.2 单一真相源

每个概念只能有一个正式定义文件。

其他文件只能：

- 引用该定义；
- 提供不重复 schema 的简短说明；
- 提供独立示例；
- 提供运行时生成的实例。

不得在多个文件内复制同一完整字段表、状态机或协议模板。

### 2.3 事件驱动

审查、测试、提问和交接使用事件驱动：

- `design_ready`
- `contract_ready`
- `review_ready`
- `test_ready`
- `acceptance_ready`

不得继续使用主观百分比作为正式流程条件。

### 2.4 Markdown 供人和 Agent 阅读，结构化数据供程序判断

- Markdown：解释规则、原因、流程和人工可读报告；
- JSON/YAML：保存任务、角色、状态、验证证据和交付判定；
- Python 3：执行一致性、依赖、所有权和交付门禁检查。

### 2.5 Python 3 是唯一受支持的 Python 运行版本

ct1 中所有 `.py` 脚本必须以 Python 3 为运行基线。

- 最低版本建议：Python `3.10+`；
- 不支持 Python 2；
- 不允许因为系统中存在名为 `python` 的命令，就假定它是 Python 3；
- 所有运行入口必须先检查解释器主版本；
- 找不到 Python 3 时应明确失败并给出安装或配置提示，不得跳过校验后继续交付。

---

## 3. 目标架构

建议最终结构：

```text
ct1/
├── SKILL.md
├── references/
│   ├── lifecycle.md
│   ├── requirement-brief.md
│   ├── task-graph.md
│   ├── dynamic-team-selection.md
│   ├── role-context.md
│   ├── status-report.md
│   ├── decision-routing.md
│   ├── review-gate.md
│   ├── testing-gate.md
│   ├── recovery-protocol.md
│   └── delivery-gate.md
├── assets/
│   ├── REQUIREMENT_BRIEF.template.md
│   ├── TASK_BOARD.template.yaml
│   ├── TEST_PLAN.template.md
│   ├── TEST_REPORT.template.md
│   └── DELIVERY_REPORT.template.md
├── schemas/
│   ├── task-graph.schema.json
│   ├── role-roster.schema.json
│   ├── team-state.schema.json
│   ├── status-report.schema.json
│   ├── test-report.schema.json
│   └── delivery-state.schema.json
├── scripts/
│   ├── ct1_validate.py
│   ├── validate_protocol.py
│   ├── validate_task_graph.py
│   ├── validate_write_scopes.py
│   └── check_delivery_gate.py
└── evals/
    ├── evals.json
    ├── protocol-evals.json
    ├── delivery-evals.json
    └── trigger-evals.json
```

不要求一次性机械改成上述所有文件名，但最终职责边界应与之接近。

项目运行状态不得写回 Skill 安装目录。建议项目内状态目录：

```text
<project>/.claude/teams/<team-id>/
├── requirement-brief.yaml
├── task-graph.json
├── role-roster.json
├── team-state.json
├── decisions.jsonl
├── test-report.json
├── delivery-state.json
└── DELIVERY_REPORT.md
```

---

## 4. P0：必须优先修复的问题

## P0-01 修正 StatusReport/v2 字段定义

### 当前问题

文档声明 StatusReport/v2 为 11 字段，但实际包含：

1. 协议版本
2. 任务 ID
3. 状态
4. 当前任务
5. 进展
6. 阻塞项
7. 下一步
8. 需要的输入
9. 触发事件
10. 待答复问题
11. 变更文件
12. 验证结果

### 改动方向

推荐不再把字段数量写进普通说明，统一描述为：

> 严格按照 StatusReport/v2 schema 的固定字段和顺序输出。

如果保留字段数量，则所有位置统一改为 12。

### 涉及文件

- `SKILL.md`
- `references/status-report-schema.md`
- `references/team-protocol.md`
- `TEAM_PROTOCOL.md`
- `evals/evals.json`
- `evals/protocol-evals.json`
- 有效运行记忆和迁移说明

### 验收标准

- 全目录不存在“StatusReport/v2（11 字段）”；
- 正式 schema 只有一个；
- 其他文件不再复制完整 schema；
- 校验脚本能检查字段集合和顺序。

---

## P0-02 移除固定 33% / 66% / 100% 流程

### 当前问题

部分新文档使用事件驱动，旧审查和问题升级协议仍使用固定百分比，导致 Agent 可能恢复旧的三轮审查流程。

### 改动方向

正式运行协议全部使用：

```text
design_ready
contract_ready
review_ready
test_ready
acceptance_ready
```

示例中的：

```text
33% → review_ready
66% → 修复完成后再次 review_ready
100% → acceptance_ready
```

但不要机械地把百分比替换成事件名；应根据事件真正含义重写示例。

旧版迁移说明如需保留，移动到：

```text
references/migrations/v1-to-v2.md
```

运行时默认不得加载迁移文档。

### 涉及文件

- `references/code-review-protocol.md`
- `references/question-escalation-protocol.md`
- `references/team-protocol.md`
- `ct1-workspace/` 中仍作为有效测试依据的旧案例
- `zsh/CURRENT_TASK.md`
- `zsh/SESSION_LOG.md`

历史日志可以保留历史事实，但必须明确标记为旧版本，不得成为当前运行指令。

### 验收标准

- 当前正式协议中不存在以百分比触发审查、提问或交付；
- reviewer 是否启动由风险或 `review_ready` 事件决定；
- 同一任务允许多次触发 `review_ready`，但不要求固定轮数；
- 低风险任务允许一次最终审查；
- 高风险任务允许设计审查和实现审查。

---

## P0-03 明确 Python 3 运行版本

### 当前问题

现有脚本使用：

```python
#!/usr/bin/env python3
```

但在部分 Windows 环境中：

```text
python -> Python 2.7
py      -> 不存在
python3 -> 不存在
```

因此脚本文件虽然存在，实际无法执行。

### 改动方向

在 `SKILL.md` frontmatter 或运行依赖章节明确：

```yaml
compatibility: Requires Python 3.10+ for validation scripts. Python 2 is unsupported.
```

如果当前 Skill 平台不推荐 frontmatter compatibility，则在 `SKILL.md` 增加“运行依赖”小节。

统一运行策略：

1. 优先使用显式配置的 `CT1_PYTHON`；
2. 探测 `python3`；
3. 探测 `py -3`；
4. 探测 `python`，但必须验证 `sys.version_info.major == 3`；
5. 如果可用，可使用 `uv run python`；
6. 所有候选均不可用时，停止 Python 门禁并报告阻塞。

建议提供统一入口：

```text
scripts/ct1_validate.py
```

由它依次调用其他校验模块，避免用户和 Agent 记忆多条命令。

建议命令示例：

```powershell
$env:CT1_PYTHON = "C:\Path\To\Python311\python.exe"
& $env:CT1_PYTHON scripts/ct1_validate.py
```

跨平台示例：

```bash
python3 scripts/ct1_validate.py
```

### 脚本要求

所有脚本顶部增加明确版本检查：

```python
import sys

if sys.version_info < (3, 10):
    raise SystemExit(
        "ct1 validation requires Python 3.10+. "
        f"Current interpreter: {sys.version}"
    )
```

所有包含中文的 Python 文件显式保存为 UTF-8。可增加：

```python
# -*- coding: utf-8 -*-
```

虽然 Python 3 默认使用 UTF-8 源码编码，但显式声明有利于避免错误解释器和编辑器产生歧义。

### 验收标准

- 文档明确写出 Python 3.10+；
- Python 2 执行时输出清晰错误；
- 不允许将 SyntaxError 误判成业务校验失败；
- 找不到 Python 3 时交付门禁状态为 `blocked`，不是 `passed`；
- README/SKILL 中提供 Windows 与 Unix 两种运行示例；
- 所有脚本通过同一入口运行。

---

## P0-04 将“文件存在检查”升级为真实语义校验

### 当前问题

现有脚本主要检查：

- reference 是否存在；
- `SKILL.md` 是否提到某个文件名；
- eval 是否包含某个 ID；
- 是否存在部分旧关键词。

这些检查不能证明任务图、测试结果和交付结论正确。

### 改动方向

增加结构化 schema 和运行数据校验。

#### Task Graph 必须检查

- task ID 唯一；
- 依赖引用存在；
- 不存在依赖环；
- 必需任务至少关联一个 AC；
- owner 唯一；
- owner 存在于 role roster；
- `ready` 任务的依赖已满足；
- `accepted` 任务具有验证证据；
- 不允许跳过必要状态直接 accepted；
- write scope 格式合法。

#### Role Roster 必须检查

- role ID 唯一；
- 每个执行角色至少拥有一个有效任务；
- 激活条件可解析；
- owned tasks 与 Task Graph 一致；
- 多角色 write scope 冲突已经指定唯一 owner 或协调策略；
- 已退场角色没有未完成任务。

#### Delivery Gate 必须检查

- 所有必需 AC 有验证证据；
- 所有必需任务为 accepted；
- P0/P1 缺陷为零；
- 必需测试真实执行并通过；
- 环境不可用不得记为通过；
- 严重审查问题为零；
- user-required 决策没有未确认项；
- 已知风险已进入交付报告；
- 交付结论与证据一致。

### 验收标准

- 删除一个依赖任务时校验失败；
- 制造循环依赖时校验失败；
- 两个角色无协调地写同一文件时校验失败；
- 未运行测试时不能得到 `passed`；
- 缺少关键 AC 时不能得到 `delivered`；
- 只有全部门禁通过时才返回退出码 0。

---

## 5. P1：Markdown 内容重叠优化

## P1-01 建立 Markdown 职责清单

整改前先生成一张“文档职责矩阵”，至少包含：

| 文件 | 唯一职责 | 是否定义 schema | 是否包含示例 | 谁引用它 |
|---|---|---:|---:|---|
| `SKILL.md` | 主流程和路由 | 否 | 少量 | Skill 入口 |
| `status-report-schema.md` | 状态报告唯一 schema | 是 | 1 个 | team protocol、review、test |
| `team-protocol.md` | 进度查询动作 | 否 | 1 个 | 项目副本 |
| `code-review-protocol.md` | 审查触发和问题分流 | 否 | 1 个 | delivery 流程 |

没有独立职责的文件应合并或删除。

## P1-02 重叠内容处理规则

发现两个 Markdown 文件表达相同规则时，按以下顺序处理：

1. 确定权威文件；
2. 将完整定义保留在权威文件；
3. 其他文件删除重复内容；
4. 替换为相对链接和一句用途说明；
5. 如需示例，只保留与该文件职责直接相关的示例；
6. 更新所有引用；
7. 用脚本检测重复 schema 标题和旧关键词。

### 不应重复的内容

- StatusReport 完整字段；
- Task Graph 完整字段；
- 角色生命周期；
- 缺陷状态机；
- API 契约状态机；
- 决策风险等级；
- 交付判定；
- 事件枚举；
- 团队人数推导原则。

## P1-03 建议的合并关系

### `TEAM_PROTOCOL.md` 与 `references/team-protocol.md`

- Skill 内只保留模板；
- 项目部署后生成项目实例；
- ct1 源目录中的根级 `TEAM_PROTOCOL.md` 如果只是旧实例，应移出运行规则或删除；
- 不要同时把二者都描述为唯一真相源。

### `lifecycle.md` 与 `SKILL.md`

- `SKILL.md` 保留简短生命周期导航；
- `lifecycle.md` 定义详细阶段、进入条件、退出条件；
- 不要在两个文件重复整套 13 步流程。

### `team-selection.md` 与 `dynamic-team-selection.md`

建议合并或明确拆分：

- `team-selection.md`：是否需要团队、复用团队、多团队隔离；
- `dynamic-team-selection.md`：如何从任务图生成角色。

相同的最小充分信息和人数推导只保留一次。

### `question-escalation-protocol.md` 与 `decision-level.md`

- `decision-level.md`：只定义决策等级和不可自动决定范围；
- `question-escalation-protocol.md`：只定义问题收集、路由、答复回填；
- 不重复风险分类表。

### `testing-gate.md` 与 `delivery-report.md`

- testing gate 决定测试是否通过；
- delivery gate 综合测试、审查、AC 和风险；
- delivery report 只是展示结果，不自行重新定义门禁。

## P1-04 大文件优化

超过 300 行的 reference：

- 增加目录；
- 删除旧版长流程案例；
- 将长案例放入 `examples/`；
- 正式协议文件以规则和最小示例为主；
- Agent 只有在需要案例时才读取 `examples/`。

建议优先处理：

- `references/code-review-protocol.md`
- `references/question-escalation-protocol.md`

### 验收标准

- 每个核心概念只有一个权威定义；
- `SKILL.md` 不复制完整 schema；
- Markdown 总行数明显下降，但能力不减少；
- Agent 能根据 `SKILL.md` 明确知道何时读取哪个 reference；
- 删除任意重复文档后，不影响运行流程恢复。

---

## 6. P1：动态团队与运行模式继续收敛

## P1-05 改造固定角色上下文模板

### 当前问题

`references/context-contract.md` 仍以固定的 frontend、backend、tester、reviewer 为主结构，容易重新锚定到固定角色。

### 改动方向

使用通用动态角色 schema：

```yaml
role_slices:
  <role_id>:
    mission:
    owned_tasks:
    required_documents:
    optional_documents:
    read_scope:
    write_scope:
    dependencies:
    context_hash:
```

前端、后端、测试角色只能作为示例，不能成为必备字段。

### 验收标准

- 能生成 `fullstack-dev`；
- 能生成按业务域命名的服务角色；
- 能生成迁移、安全、部署专项角色；
- 不存在“动态角色必须映射到固定四类角色”的隐含要求。

---

## P1-06 收敛 create-only

### 当前问题

无具体需求时，`create-only` 仍要求启动“必需 Agent”，但此时通常无法推导真实执行者。

### 建议行为

`create-only` 默认只完成：

- 建立 team blueprint；
- 建立项目状态目录；
- 建立 leader 或 planning-leader；
- 说明如何提交首个需求；
- 不启动没有 owned tasks 的执行角色。

首个需求进入后：

```text
Requirement Brief
→ Initial Task Graph
→ Team Proposal
→ 启动当前阶段角色
```

可以保留用户显式要求的待命团队，但必须标记：

```text
status: planned
activation: first_matching_task
```

### 验收标准

- 无需求时不启动空闲 frontend/backend/tester/reviewer；
- 执行角色必须有任务 ID 或明确激活条件；
- create-only 不伪造验收标准和任务图；
- 用户提交首个需求后可以平滑升级到 delivery。

---

## P1-07 明确团队方案确认策略

### 建议分级

| 情况 | 行为 |
|---|---|
| 可逆、低风险、无新增费用 | 记录假设后继续 |
| 团队角色调整但没有外部副作用 | 展示方案后继续 |
| 用户明确限制人数 | 优先遵守，能力不足时披露风险 |
| 外部费用、发布、权限、安全、数据删除、不可逆迁移 | 必须确认 |
| 环境并发不足 | 收缩团队或分波次执行 |

不得使用模糊的“用户确认或按安全默认值继续”作为全部场景的统一规则。

---

## 7. P1：运行状态与 Skill 源码隔离

## P1-08 删除 Skill 目录双写

### 当前问题

向 `<skill目录>/ct1-workspace/team-protocol-snapshot.md` 写入项目运行副本可能导致：

- Skill 安装目录只读；
- 多项目相互覆盖；
- 多团队并发冲突；
- 源码目录被运行状态污染；
- 多份副本漂移。

### 改动方向

- Skill 目录只存模板、schema、脚本和 eval；
- 项目状态只写入 `<project>/.claude/teams/<team-id>/`；
- 调试快照写入项目团队目录下的 `debug/`；
- 不把项目状态写回全局 Skill。

### 验收标准

- 两个项目同时运行不会写同一个文件；
- Skill 在只读安装目录下仍能工作；
- 删除 Skill 工作区不会丢失项目运行状态；
- 项目状态只有一个权威位置。

---

## P1-09 分离任务状态与项目状态

任务状态建议：

```text
backlog
ready
in_progress
review
test
accepted
blocked
cancelled
```

项目状态建议：

```text
discovery
planned
executing
integrating
verifying
conditionally_deliverable
delivered
blocked
cancelled
```

`delivered` 不再作为普通任务状态。

### 验收标准

- 单任务 accepted 不会使项目自动 delivered；
- 项目 delivered 必须经过项目级交付门禁；
- 条件交付与完全交付有明确区别。

---

## 8. P2：评估体系优化

## P2-01 统一 eval schema

当前部分 eval 使用 `expectations`，Skill Creator 标准流程使用 `assertions`。

整改 Agent 应选择一个规范，并确保：

- viewer、grader、aggregator 可以读取；
- assertion 名称客观、可验证；
- 不只检查文字是否出现；
- 能结合输出文件和结构化状态评分。

## P2-02 增加真实运行测试

至少增加以下场景：

1. 单文件低风险任务降级为单 Agent；
2. 小型跨层 CRUD 合并为 fullstack；
3. 多模块项目按任务簇动态拆分；
4. 高风险迁移增加专项角色；
5. 两个角色 write scope 冲突；
6. reviewer 延迟启动；
7. tester 发现 P0 后任务退回；
8. Python 2 被拒绝；
9. Python 3 缺失导致门禁 blocked；
10. 测试未执行时禁止通过；
11. 关键 AC 缺失时禁止交付；
12. create-only 无需求时不启动空闲开发者；
13. 多项目并发运行状态相互隔离；
14. 旧协议迁移后不再使用百分比里程碑。

## P2-03 增加结构与复杂度指标

评估不只看交付结果，还应记录：

- `SKILL.md` 行数；
- runtime 必须加载的 reference 数量；
- 重复 schema 数量；
- 每次启动的 Agent 数；
- 无 owned task 的 Agent 数；
- write scope 冲突数；
- 协议校验耗时；
- 交付门禁真假阳性；
- 使用 Skill 与旧版 Skill 的 token/time 差异。

目标是减少无效复杂度，而不是单纯减少文件数量。

---

## 9. 推荐执行顺序

### Iteration A：协议清理

1. 修复 StatusReport/v2 字段；
2. 清除固定百分比流程；
3. 定义事件枚举唯一来源；
4. 建立 Markdown 职责矩阵；
5. 合并或缩短重叠文档；
6. 更新引用。

### Iteration B：Python 3 基线

1. 明确 Python 3.10+；
2. 增加统一运行入口；
3. 增加版本探测；
4. 增加 Windows/Unix 运行说明；
5. 确保 Python 2 明确失败；
6. 确保找不到 Python 3 时门禁 blocked。

### Iteration C：结构化运行状态

1. 增加 schemas；
2. 生成 task graph、role roster、team state；
3. 删除 Skill 目录运行状态双写；
4. 分离任务状态和项目状态。

### Iteration D：真实门禁

1. 校验依赖图；
2. 校验 owner；
3. 校验 write scope；
4. 校验 AC 与测试证据；
5. 校验 review/test/decision 阻断项；
6. 生成唯一交付判定。

### Iteration E：评估与回归

1. 更新 eval；
2. 运行旧版与新版对照；
3. 检查 token、时间、团队人数和交付正确率；
4. 修复回归；
5. 最后再优化 Skill description。

---

## 10. Agent 执行要求

整改 Agent 开始工作时，应先：

1. 阅读 `SKILL.md`；
2. 阅读本文件；
3. 盘点 `references/` 的职责和交叉引用；
4. 搜索 `11 字段`、`33%`、`66%`、`100%`、`唯一真相源`；
5. 检查当前 `python --version`；
6. 检查是否存在 `python3`、`py -3`、`uv`；
7. 记录修改前的协议冲突和测试基线；
8. 再开始修改。

执行过程中：

- 不增加无独立职责的 Markdown；
- 不通过复制粘贴同步 schema；
- 不删除仍被引用的文件而不更新链接；
- 不把历史日志当作当前运行规则；
- 不在找不到 Python 3 时伪造校验通过；
- 不把“测试文件存在”当作“测试真实执行”；
- 不把 Agent 报告完成当作交付完成；
- 不为了证明动态组队而创建不必要的 Agent。

---

## 11. 最终验收清单

### 协议一致性

- [ ] StatusReport/v2 字段定义完全一致
- [ ] 正式协议不再使用 33/66/100 百分比门禁
- [ ] 事件枚举只有一个正式定义
- [ ] 每个核心 schema 只有一个真相源
- [ ] 固定角色示例不会限制动态角色

### Markdown 优化

- [ ] 已建立文档职责矩阵
- [ ] 重叠 Markdown 已合并、缩短或改为引用
- [ ] 大型协议文件有目录或拆分示例
- [ ] `SKILL.md` 只保留主流程和路由
- [ ] 不存在多个文件同时自称同一概念的唯一真相源

### Python 3

- [ ] 明确要求 Python 3.10+
- [ ] Python 2 明确不支持
- [ ] 所有脚本有版本检查
- [ ] Windows 和 Unix 都有明确运行方法
- [ ] 有统一验证入口
- [ ] 找不到 Python 3 时门禁为 blocked

### 动态团队

- [ ] create-only 无需求时不启动空闲开发者
- [ ] 每个执行角色都有 owned tasks 或激活条件
- [ ] 团队人数由任务图和并行价值决定
- [ ] write scope 冲突可检测
- [ ] 角色可以扩容、合并、替换和退场

### 交付门禁

- [ ] 依赖引用与依赖环可校验
- [ ] owner 唯一性可校验
- [ ] AC 覆盖可校验
- [ ] 测试证据可校验
- [ ] 严重审查问题会阻断交付
- [ ] user-required 问题未确认时会阻断
- [ ] 任务状态与项目状态分离
- [ ] 只有真实证据满足时才能 delivered

### 评估

- [ ] eval schema 与 grader/viewer 兼容
- [ ] 覆盖 Python 2、Python 3 缺失和 Python 3 正常场景
- [ ] 覆盖 Markdown/协议残留检查
- [ ] 覆盖单 Agent 降级和动态组队
- [ ] 覆盖失败返工与最终交付
- [ ] 与上一版本进行定量或至少结构化对比

---

## 12. 完成定义

本轮整改完成不以“新增了多少文件”判断，而以以下结果判断：

1. 用户仍然只需给出项目路径、需求和约束；
2. ct1 能先理解项目，再决定是否组队和团队人数；
3. 简单任务不会进入完整团队流程；
4. 复杂项目能按需加载必要协议；
5. Markdown 不再通过重复内容维持一致性；
6. Python 校验明确运行在 Python 3.10+；
7. 环境不满足时明确阻断，而不是静默跳过；
8. 任务、角色、测试和交付状态可以被程序校验；
9. 最终交付由证据和门禁决定；
10. 旧协议不会重新影响当前 Agent 行为。

最终目标：

> **简单入口 + 最小可靠内核 + 动态团队 + 按需协议 + Python 3 可执行校验 + 证据驱动交付。**
