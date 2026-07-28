# 代码审查者（Reviewer）+ 审查循环

## 为什么做

当前流程中，子 agent（前端/后端）完成编码后直接汇报 leader，**没有代码审查环节**。代码质量、架构合理性、安全/性能问题无法在开发阶段被系统性发现。

本协议在 StatusReport/v2 流程上叠加**审查层**：dev 完成编码 → leader 送审 → reviewer 出报告 → leader 分流（下发修改 / 升级用户）→ dev 修复 → 再审。

## 设计原则

1. **Reviewer 是延迟启动角色**：不在团队创建时启动，有代码产出且进入审查阶段时启动
2. **触发时机 = 事件驱动**：review-ready 事件节点触发审查，dev 汇报编码完成后触发
3. **审查范围 = 全面审查**：代码质量、架构合理性、安全、性能、编码规范、中间件使用
4. **复用现有机制**：审查意见下发复用 `[CONTEXT ADDENDUM]`，需用户决策项复用问题升级循环

---

## 1. Reviewer 角色定义

| 属性 | 值 |
|---|---|
| 角色名 | 🔍 代码审查者 |
| Agent 名 | reviewer |
| 模型 | high-reasoning（继承会话或用户指定） |
| 职责 | 审查前端/后端代码；按严重程度分类问题；不写生产代码 |
| 与用户关系 | 通过 leader（审查报告 → leader → 用户） |
| 人设 | 十年全栈开发经验，精通 Java 后端、前端、中间件使用与运维 |

### Reviewer 不做的

- **不写生产代码**（包括不写 demo、不复现 bug）
- **不直接联系用户**（审查报告 → leader → 用户）
- **不修改自己的审查结论**（除非 leader 要求复评）

---

## 2. Reviewer 的上下文注入（5 要素）

spawn 时按五要素模板注入：

- **角色**：「你是 [项目名] 的代码审查者，十年全栈开发经验，精通 Java 后端、前端、中间件使用与运维。你不写生产代码，只审查代码并输出结构化审查报告。」
- **上下文**：项目架构文档 + 编码规范 + 技术栈约束 + 审查标准清单（见 `references/context-contract.md` 的 reviewer 切片）
- **任务**：「审查 [dev] 的 [模块] 代码，按严重程度分类问题」
- **文档引用**：相关架构/规范文档路径
- **输出格式**：Code Review 报告模板（见 §4）

---

## 3. 审查触发流程

```
review-ready 事件节点
    │
    ▼
dev 完成编码 → 汇报 leader（StatusReport/v2 + 变更文件列表）
    │
    ▼
leader 决策送审 → 将代码文件路径 + 审查要求发给 reviewer
    │
    ▼
reviewer Read 代码文件 → 输出 Code Review 报告
    │
    ▼
leader 分流：
    ├─ 严重问题 + 建议改进 → [CONTEXT ADDENDUM] 下发对应 dev 修改
    └─ 需用户决策项 → 升级用户（复用问题升级循环）
    │
    ▼
dev 修复代码 → 汇报 leader
    │
    ▼
下一 review-ready → 再次送审
    │
    ▼
最终审查完成 → leader 汇总最终结果 + 遗留未决策问题 → 展示用户
```

---

## 4. Code Review 报告 schema（reviewer → leader）

```
## Code Review 报告
审查对象: {frontend-dev / backend-dev} 的 {模块名}
审查轮次: 第 {N} 轮（触发事件: {design_ready/review_ready/acceptance_ready}）
审查文件: {file1, file2, ...}

### 严重问题（必须修复）— 阻塞项
| 编号 | 位置 | 问题描述 | 修复建议 | 分类 |
|------|------|----------|----------|------|
| R-{dev}-001 | src/X.java:42 | ... | ... | 安全/性能/架构/规范/中间件 |

### 建议改进（建议修复）— 非阻塞
| 编号 | 位置 | 问题描述 | 修复建议 | 分类 |
|------|------|----------|----------|------|
| R-{dev}-002 | ... | ... | ... | ... |

### 需用户决策
| 编号 | 问题描述 | 选项 | 影响范围 |
|------|----------|------|----------|
| R-{dev}-U01 | ... | A / B | ... |

### 总结
- 是否通过: 否（存在 N 个严重问题）/ 是（无严重问题）
- 整体评价: ...
- 本轮重点: ...
```

### 分类枚举

安全 / 性能 / 架构 / 规范 / 中间件 / 可维护性 / 测试覆盖

### 严重程度定义

| 程度 | 定义 | 处理 |
|---|---|---|
| 严重问题 | 安全漏洞、数据丢失风险、性能瓶颈、架构缺陷、生产事故隐患 | 必须修复，阻塞下一触发事件 |
| 建议改进 | 代码规范、可读性、可维护性、轻微性能优化 | 建议修复，不阻塞 |
| 需用户决策 | 涉及产品方向、技术选型、资源投入的取舍 | 升级用户决策 |

---

## 5. Leader 分流规则

| 报告项 | 处理方式 | 机制 |
|---|---|---|
| 严重问题（必须修复） | 下发对应 dev 修改 | `[CONTEXT ADDENDUM]` 来源=reviewer 审查 |
| 建议改进（建议修复） | 下发对应 dev 修改 | `[CONTEXT ADDENDUM]` 来源=reviewer 审查 |
| 需用户决策 | 升级用户 | 复用问题升级循环（`references/question-escalation-protocol.md`） |

### 下发 dev 的 CONTEXT ADDENDUM 格式

```
[CONTEXT ADDENDUM]
来源：reviewer 审查（第 {N} 轮 / {dev} / {触发事件}）
关联任务：{模块} 代码修复
审查问题：
  1. [R-{dev}-001][严重][安全] src/X.java:42 — 问题描述。修复建议：...
  2. [R-{dev}-002][建议][规范] ...
对原有上下文的变更：需修复上述问题后重新提交审查
```

### 需用户决策项的升级

reviewer 的「需用户决策」项，leader 按问题升级循环的格式填入【待答复问题】：
```
[R-{dev}-U01][review_ready] 是否使用 Redis 缓存运单列表？ (关联任务: 运单列表接口)
```
用户回答后，leader 通过 `[CONTEXT ADDENDUM]`（来源=用户答复）分发给对应 dev。

---

## 6. 风险驱动审查（替代固定三轮）

> 小任务不被强制执行三轮；高风险任务保持充分审查。

### 风险策略

| 风险 | 示例 | 审查方式 |
|---|---|---|
| 低 | 文案、局部样式、简单配置 | 最终审查一次 |
| 中 | 普通业务页面、普通接口 | 契约或设计审查 + 最终审查 |
| 高 | 权限、安全、支付、数据迁移 | 设计、实现中、最终三轮 |

### 事件触发

使用以下事件替代固定百分比：

```text
design_ready
contract_ready
review_ready
test_ready
acceptance_ready
```

### 审查轮次

| 轮次 | 触发事件 | 审查内容 | 输出 |
|---|---|---|---|
| 设计审查（高风险） | design_ready | 架构合理性、安全、性能 | 报告 → 下发修改 |
| 实现中审查（高风险） | review_ready | 已完成代码 + 架构 | 报告 → 下发修改 |
| 最终审查 | acceptance_ready | 修复验证 + 新增代码 + 遗留问题 | 最终报告 → 汇总展示用户 |

### 最终审查特殊处理

- reviewer 输出最终报告
- leader 汇总：最终进度结果 + 遗留未决策问题
- **用户业务确认**（见 §6.1 Node C）
- 展示用户：「审查通过」或「存在 N 个未决策问题需你决定」

---

## 6.1 功能里程碑对照表（Node A/B/C）

> reviewer 启动条件 = 事件驱动 + 功能里程碑。**功能里程碑在 Step 3 组队时写入 TEAM_STATE**（`reviewer_milestones` 字段），而非事后补充。**不得使用百分比**，使用功能节点绑定触发事件。

### 功能节点定义

| 节点 | 标签 | 触发事件 | 审查内容 | 用户业务确认 |
|---|---|---|---|---|
| **Node A** | 骨架 + 认证 | review_ready | 登录流、JWT、页面路由、骨架结构、认证方向 | ☐ 确认骨架 + 认证方向 |
| **Node B** | 核心业务交互 | review_ready | 创建/填写/统计主流程、核心业务交互正确性 | ☐ 确认核心业务交互 |
| **Node C** | 最终验收 | acceptance_ready | 修复验证 + 新增代码 + 遗留问题 + 业务完整性 | ☐ 最终验收 |

### 与触发事件的关系

```text
Node A (review_ready) ──reviewer 审查──▶ 用户业务确认 ──▶ Node B
Node B (review_ready) ──reviewer 审查──▶ 用户业务确认 ──▶ Node C
Node C (acceptance_ready) ──reviewer 审查──▶ 用户业务确认 ──▶ 交付
```

### 用户业务确认（开发中用户检查点）

> **reviewer 不替用户验收业务方向**。每个功能节点审查后，leader 必须做轻量用户业务确认，避免业务方向偏差到最终交付才暴露。

**确认内容**：
- Node A 后：确认骨架 + 认证的方向（登录流、JWT、页面路由）
- Node B 后：确认核心业务交互（创建/填写/统计的主流程）
- Node C：最终验收

**确认方式**：
- leader 向用户展示 reviewer 报告 + 功能 demo/描述
- 用户确认方向 → 继续下一节点
- 方向偏差 → 记录为阻断项，dev 修复后重新送审

### 写入时机

Step 3 组队时，leader 根据任务图将 `reviewer_milestones` 写入 TEAM_STATE：

```json
{
  "reviewer_milestones": [
    { "node": "A", "label": "骨架+认证", "trigger_event": "review_ready", "description": "登录流、JWT、页面路由、骨架结构" },
    { "node": "B", "label": "核心业务交互", "trigger_event": "review_ready", "description": "创建/填写/统计主流程" },
    { "node": "C", "label": "最终验收", "trigger_event": "acceptance_ready" }
  ]
}
```

---

## 8. Dev 的触发事件节点报告

dev 在触发事件节点的 StatusReport/v2 中，`变更文件` 字段供 leader 送审：

```
【触发事件】可审查
【待答复问题】...
【变更文件】
- src/components/WaybillList.vue（新增）
- src/store/waybill.js（修改）
- src/api/waybill.js（新增）
【验证结果】mvn test -pl waybill（通过）
```

无新增文件时：
```
【变更文件】无（本轮为设计/调研阶段，代码在下一触发事件提交）
```

---

## 9. 边界情况处理

| 边界情况 | 处理方式 |
|---|---|
| **无严重问题（审查通过）** | reviewer 输出「是否通过: 是」，leader 告知 dev 通过，无需修改；继续下一触发事件 |
| **用户跳过决策** | leader 基于已有上下文自行裁决，`status = 已作废`，`void_reason = leader 代答`；告知 reviewer |
| **跨轮次遗留问题** | reviewer 在每轮报告开头列出「上轮遗留未修复问题」，确保追踪不丢失 |
| **修复引入新问题** | reviewer 在第 2/3 轮报告中对比上一轮，标注「新发现问题」与「已修复问题」 |
| **dev 不同意审查意见** | dev 可向 leader 申述；leader 裁决：采纳 dev 意见（通知 reviewer 作废该问题）或维持原意见（dev 必须修复） |
| **acceptance_ready 后仍有严重问题** | reviewer 不允许 acceptance_ready 通过；dev 必须修复后才能进入空闲状态 |
| **零开发/新增需求** | 所有编码产出都必须经过审查循环，无例外 |

---

## 10. 完整工作示例

详见 `examples/code-review-e2e.md`（风险驱动审查完整流程：dev 汇报 → leader 送审 → reviewer 出报告 → leader 分流 → 用户决策 → dev 修复后再审）。

本节保留最小示例：

### Dev 汇报（review_ready）

```
【触发事件】review_ready
【变更文件】
- src/components/WaybillList.vue（新增）
- src/store/waybill.js（修改）
【验证结果】未执行
```

### Reviewer 报告（摘要）

```
## Code Review 报告
审查对象: frontend-dev 的 运单列表页
审查轮次: 第 1 轮（触发事件: review_ready）

### 严重问题（必须修复）
| 编号 | 位置 | 问题描述 | 修复建议 | 分类 |
| R-FE-001 | WaybillList.vue:58 | 列表数据未做空值保护 | 添加 v-if 或默认空数组 | 安全 |

### 总结
- 是否通过: 否（存在 1 个严重问题）
```

---

## 11. 与现有系统的关系

| 现有机制 | 如何复用 / 扩展 |
|---|---|
| StatusReport/v2 | reviewer 参与进度查询（汇报 审查中/空闲/完成）；dev 报告需包含「变更文件」和「验证结果」 |
| `[CONTEXT ADDENDUM]` | 复用为「reviewer → dev」的审查意见下发信封 |
| 问题升级循环 | reviewer 的「需用户决策」项走此循环 |
| 上下文注入（5 要素） | reviewer 获得独立的上下文切片（架构+规范+审查标准） |
| 触发事件节点 | 审查触发与 review-ready 事件联动 |
| 功能里程碑（Node A/B/C） | reviewer 启动条件 = 事件驱动 + 里程碑对照（§6.1），写入 TEAM_STATE |

## 12. 协议归属

本协议是 `references/team-protocol.md` 的扩展，是 reviewer 角色与审查循环的唯一真相源。部署时，reviewer 作为延迟启动角色写入 `TEAM_PROTOCOL.md`。
