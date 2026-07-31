# User Value Gate（用户价值门禁）

## 是什么

用户价值协议的唯一真相源。定义 `user-value` 能力、user advocate 职责、AC/US 分离、信息来源与置信度、三阶段门禁、角色边界。

> **核心结论**：ct1 的交付对象不是一组完成的技术任务，而是一个目标用户能够理解、使用并获得预期结果的产品增量。

---

## 1. 用户价值是必需能力

每个 `delivery` 项目的能力覆盖检查必须包含：

```yaml
required_project_capabilities:
  - delivery-leadership
  - implementation
  - verification
  - user-value
```

`user-value` 是否创建独立 Agent 由任务复杂度动态决定：

| 项目情况 | 建议承担方式 |
|---|---|
| 小型、目标用户单一、需求明确、低交互风险 | leader 兼任 `user-advocate` |
| 多页面、多步骤、有明显交互设计 | 创建独立 `user-advocate` |
| 多种用户、复杂权限或复杂业务规则 | 创建 `product-owner`，必要时增加 UX/领域专家 |
| 需求高度不确定或缺乏用户问题定义 | 先启动产品发现角色，暂停完整开发团队生成 |
| 纯内部技术改造且无直接用户交互 | leader 承担轻量用户/下游消费者价值检查 |

禁止仅因为项目包含前端就自动创建 `user-advocate`。是否拆分角色取决于产品不确定性、用户类型数量、交互复杂度、错误成本和返工风险。

---

## 2. user advocate 职责与独立性

### 职责

- 维护用户模型（目标用户、用户问题、使用环境）
- 挑战产品假设（区分用户事实与团队假设）
- 审查用户旅程（入口、反馈、失败恢复）
- 评估 demo 可用性
- 出具用户价值结论（`user_value_decision`）

### 独立性约束

若存在独立 `user-advocate`：

- 不承担主要业务代码的实现
- 不以 developer 的任务完成情况作为自己的通过证据
- 可读取需求、原型、运行结果和演示环境
- 默认只写产品分析、体验审查和价值验证产物
- 可以提出阻断项，但不能自行扩大产品范围
- 对缺乏证据的判断必须标为假设
- 与 developer 意见冲突时，由 leader 按决策等级处理

小项目由 leader 兼任时，也必须分别输出：

- `technical_delivery_decision`
- `user_value_decision`

不能将两个结论合并成一句"整体通过"而不提供独立证据。

---

## 3. AC 与 US 分离

### 定义

- `AC-*`：系统功能或行为的可验证要求（技术规格）
- `US-*`：目标用户是否完成目标并获得结果的可验证要求（用户成功）

### 规则

- 每个面向用户的核心任务至少关联一个 `US-*`
- 一个 `US-*` 可以关联多个 `AC-*`
- 所有 `AC-*` 通过，不代表所有 `US-*` 通过
- 技术性任务可不直接关联 `US-*`，但必须说明其支撑的上游交付物
- `delivery` 通过必须同时满足必需 AC 和必需 US

### 推荐映射

```yaml
user_success_criteria:
  - id: US-001
    goal: 首次用户完成运单查询
    evidence_required:
      - fresh_user_walkthrough
      - observable_result
    supported_by:
      - AC-001
      - AC-002
      - AC-005
```

---

## 4. 信息来源与置信度

所有用户相关判断应标注来源：

| 来源类型 | 说明 |
|---|---|
| `user-stated` | 用户明确表达 |
| `project-evidence` | 现有文档、日志、数据或产品行为 |
| `domain-evidence` | 明确的领域规范或业务规则 |
| `team-assumption` | 团队推断 |
| `unknown` | 信息不足 |

`team-assumption` 不得伪装成用户事实。高影响、不可逆或会改变产品方向的低置信度假设必须升级给用户。

---

## 5. 三阶段用户价值门禁

### Gate A：开发前 User Value Gate

- **触发事件**：`requirement_ready`
- **检查项**：
  1. 目标用户是否明确（主要/次要用户、使用环境、熟练程度）
  2. 用户问题是否明确（场景、困难、影响、期望结果）
  3. 用户目标是否区别于功能列表（以用户目标组织需求，而非以界面/接口组织）
  4. 信息来源和置信度是否披露（user-stated/project-evidence/domain-evidence/team-assumption/unknown）
  5. 关键假设是否已分类（区分用户事实与团队假设）
  6. 高影响低置信度假设是否已升级给用户
  7. 用户成功标准（US-*）是否可验证
  8. 最小用户旅程是否包含入口、核心价值和必要前置条件
  9. 体验风险（可发现性、空状态、错误反馈、失败恢复）是否进入任务图
  10. 团队是否覆盖 `user-value` 能力
- **结论**：`passed` / `conditional` / `blocked`
- **`blocked` 时不得开始主要功能实现**

### Gate B：可演示版本 Usability Gate

- **触发事件**：`demo_ready`
- **检查项**：
  1. 用户是否知道从哪里开始（入口与首次使用）
  2. 核心操作是否可发现（引导与可发现性）
  3. 文案是否面向目标用户而不是内部实现
  4. 空状态是否提供下一步
  5. 加载状态是否清晰
  6. 错误反馈是否可理解且可行动
  7. 失败后是否可以恢复
  8. 权限不足是否解释原因和可选动作
  9. 危险操作是否有确认、撤销或明确后果
  10. 核心目标是否存在明显多余步骤
  11. 默认值、输入格式和校验提示是否合理
- **发现问题后**：
  - 阻断性体验问题：退回任务图，相关任务重新进入 `in_progress`
  - 非阻断问题：记录风险、影响用户和后续建议
  - 范围变化：交由 leader 判断是否需要用户确认，不能由 user advocate 自行扩展范围

### Gate C：交付前 User Outcome Gate

- **触发事件**：`acceptance_ready`
- **检查项**：
  1. fresh user 是否能够独立完成核心旅程
  2. 所有必需 `US-*` 是否具有真实证据
  3. 用户最终得到的结果是否符合预期
  4. 关键异常场景是否可理解且可恢复
  5. 已知体验限制是否明确披露
  6. Gate A/B 的阻断问题是否关闭
  7. 用户价值结论是否独立于测试和代码审查结论
- **结论字段**：

```yaml
user_value_decision: passed | conditional | blocked
journey_reachable: true | false | unknown
user_goal_achieved: true | false | unknown
evidence:
  - ...
known_limitations:
  - ...
```

### 门禁之间不得互相替代

```text
test_passed != user_value_passed
review_passed != user_value_passed
journey_reachable != user_goal_achieved
plan_confirmed != product_accepted
all_ac_passed != all_user_success_criteria_passed
```

---

## 5.5. 触发事件清单

用户价值相关触发事件（复用 StatusReport/v2 的事件机制）：

| 事件 | 触发时机 | 说明 |
|---|---|---|
| `requirement_ready` | Requirement Brief 完成后 | 触发 Gate A |
| `demo_ready` | 可演示版本就绪后 | 触发 Gate B |
| `user_value_blocked` | user advocate 出具 blocked 结论 | 阻断开发或交付 |
| `user_value_ready` | user advocate 出具 passed/conditional 结论 | 允许进入下一阶段 |
| `acceptance_ready` | 验收阶段就绪 | 触发 Gate C |

---

## 6. 角色边界

| 角色 | 负责 | 不负责 |
|---|---|---|
| developer | 实现功能并提供技术验证证据 | 独立判定自己实现的产品具有用户价值 |
| tester | 验证规格、功能、回归、环境和系统行为 | 单独定义目标用户和产品方向 |
| reviewer | 审查安全、正确性、可靠性、可维护性 | 替代用户验收产品方向 |
| user advocate | 用户模型、产品假设、旅程合理性、体验与用户结果 | 主要业务代码实现、任意扩大范围 |
| leader | 聚合结论、处理冲突、控制范围、升级决策 | 用进度完成度覆盖用户价值阻断项 |

若同一 Agent 兼任多个职责，输出中仍必须分离证据和结论。

---

## 7. 用户沟通与决策升级

用户视角不等于所有问题都询问用户。按现有 decision level 处理：

| 情况 | 决策等级 |
|---|---|
| 局部、可逆、低风险文案或布局选择 | `agent-assumption` |
| 需要其他角色提供事实或契约 | `cross-agent` |
| 不改变产品目标和范围的内部协调 | `leader-decidable` |
| 改变目标用户、核心业务规则、关键流程、范围、风险承担 | `user-required` |

向用户提问时应包含：

- 当前已知事实
- 团队假设
- 为什么影响用户结果
- 可选方案
- 各方案影响
- 推荐方案及依据

禁止只问"这个可以吗"。用户应当能够看到真实取舍。

---

## 8. 交付公式

```
必需任务 accepted
+ 必需 AC 通过
+ 必需 US 通过
+ P0/P1 缺陷为零
+ 严重审查问题为零
+ user-required 决策无未确认项
+ 用户旅程可达
+ 用户目标达成
+ user_value_decision = passed
= delivered
```

`conditional` 仅允许用于非阻断限制，并必须披露：受影响用户、受影响场景、临时规避方式、风险、后续建议。

---

## 9. 产物清单

项目运行目录建议包含：

```text
.claude/teams/<team-id>/
├── REQUIREMENT_BRIEF.md
├── TASK_BOARD.*
├── TEST_PLAN.md
├── TEST_REPORT.md
├── USER_VALUE_REVIEW.md
├── REVIEW_REPORT.md
├── DELIVERY_REPORT.md
└── TEAM_STATE.*
```

`USER_VALUE_REVIEW.md` 至少包含：

- 目标用户与问题摘要
- 关键事实、假设与置信度
- 用户成功标准结果
- 用户旅程结果
- 可发现性与理解成本
- 空状态、错误反馈与失败恢复
- 阻断问题 / 非阻断限制
- 用户价值结论

---

## 10. 与其他门禁的关系

| 门禁 | 阶段 | 关注点 |
|---|---|---|
| Step 3.75 开发计划确认 | 开发前 | 用户对**计划**的确认 |
| Gate A User Value Gate | 开发前 | 用户价值**语义**完整性 |
| Node A 骨架+认证 | 开发中 | 骨架与认证的**方向** |
| Gate B Usability Gate | demo 就绪 | **可演示版本**的体验 |
| Node B 核心业务交互 | 开发中 | 核心交互的**方向** |
| Gate C User Outcome Gate | 交付前 | **用户目标达成** |
| Node C 最终验收 | 交付前 | **技术终态**确认 |

各门禁关注点不同，不得互相替代。
