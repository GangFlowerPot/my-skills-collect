# 端到端测试 V2：ynwl 项目的门禁全链路演示

> 这是**当前有效版本**，基于 **Node A/B/C 功能里程碑 + `plan_confirmed` 事件驱动门禁**。
>
> 与 `references/code-review-protocol.md` §6.1（功能里程碑对照表）、`references/status-report-schema.md`（触发事件枚举）、`SKILL.md` Step 3.75（开发计划确认硬门）对齐。
>
> **历史版本**：`ct1-workspace/e2e-test-context-injection.md`（基于 33%/66%/100% 百分比门禁，Iteration A 前旧记录）。

> 测试目标：
> 1. **开发计划确认硬门**（Step 3.75）：契约冻结后、Agent 开发启动前，必须等用户明确确认
> 2. **技术基线验证**（Step 1.5）：数据层一致性、环境就绪、凭证方案
> 3. **功能里程碑**（Node A/B/C）：骨架+认证 → 核心业务交互 → 最终验收，绑定触发事件（非百分比）
> 4. **用户业务审查点**：每个功能节点 reviewer 审查后，leader 做轻量用户业务确认
> 5. **Agent 只读约束**：`plan_confirmed` 前 dev 角色只读

---

## 0. 项目背景（来自已部署的 TEAM_PROTOCOL.md）

- 项目 ynwl：前后端分离的管理系统
- 前端 ynwl_front：Vue 2.6 + Element UI + AVUE + Axios；dev server 端口 2890
- 后端 ynwl_back：Java 8 + Spring Boot 2.1 + Spring Cloud + BladeX 2.5 微服务（Maven 多模块）
- 微服务：blade-gateway(10100)、blade-auth、blade-system、blade-user、blade-fileserver、blade-apires、blade-log
- 注册中心 Nacos

假设项目已有结构化文档（req.md 18KB、architecture.md 14KB、decisions.md 7KB）。

---

## 1. 上下文合约（Context Contract）— 一次性建立，跨任务复用

（与 V1 相同，此处省略。详见 `ct1-workspace/e2e-test-context-injection.md` §1。）

---

## 2. Step 1.5 需求澄清 — 技术基线验证

**新增**：Requirement Brief 包含「技术基线验证」章节。

### 数据层一致性

| 检查项 | 状态 | 结果 |
|---|---|---|
| DDL 语义 vs ADR-006 裁定 | ⚠️ 冲突 | ADR-006 裁定用 CHAR，实际库表是 BYTE（100 中文字 = 200 字节 > 100 字节上限） |
| 现有 schema 支持需求字段 | ✅ | ... |
| 数据迁移/兼容性风险 | ✅ | ... |

> 数据层语义冲突 → 标记为 `user-required` 问题 → **必须由用户确认**（本次 BYTE vs CHAR 冲突在此步捕获，而非执行中暴露）。

### 环境就绪

- ✅ DB 连通（监听/端口/凭证）
- ✅ 构建工具可用（JDK 8/Maven 3.6/Node 14）
- ✅ 依赖服务可达（Nacos、Redis）

### 凭证 / 密钥配置方案

- 来源：✅ 环境变量
- 敏感信息不落库保障：application-local.yml 加入 .gitignore

---

## 3. Step 3.75 开发计划确认硬门 — 验证「启动前用户检查点」

**场景**：契约已冻结（Step 2.5）、团队已生成（Step 3）、上下文合约已定位（Step 3.5）。

### 3.1 Leader 呈报开发计划

leader 向用户呈报：

```
📋 开发计划确认 · 运单管理模块

## 团队架构
- leader（统筹）
- frontend-dev（运单列表页 UI）
- backend-dev（运单接口）
- reviewer（延迟启动，功能里程碑触发）
- tester（延迟启动，test-ready 触发）

## 任务拆分与执行顺序
| 任务 | 负责人 | 依赖 | 验收标准 |
|---|---|---|---|
| 运单列表页组件 | frontend-dev | 接口契约 AC-001 | AC-001 |
| 运单列表接口 | backend-dev | 数据模型 AC-002 | AC-002 |
| 权限控制 | backend-dev | AC-002 | AC-003 |

## Reviewer 功能里程碑（Node A/B/C）
| 节点 | 标签 | 触发事件 | 用户业务确认 |
|---|---|---|---|
| Node A | 骨架+认证 | review_ready | 确认骨架+认证方向 |
| Node B | 核心业务交互 | review_ready | 确认核心业务交互 |
| Node C | 最终验收 | acceptance_ready | 最终验收 |

## 技术基线状态
- 数据层：⚠️ BYTE vs CHAR 冲突待你确认（ADR-006 裁定 CHAR，实际库 BYTE）
- 环境：✅ 已就绪
- 凭证：✅ 环境变量方案

请确认上述计划（或提出修改意见）。确认后启动 Agent 开发。
```

### 3.2 ⏸ 硬门：等待用户确认

**规则**：
- 工作流**必须停止**，等用户明确确认后才进 Step 4
- 计划驳回 → leader 修改后重新呈报
- **确认前 dev 角色只读**，不写业务代码或配置文件

### 3.3 用户确认后

用户回复「确认，但 BYTE 用 CHAR，按 ADR-006 执行」。

leader 写入 TEAM_STATE：
```json
{
  "confirmed_events": ["plan_confirmed"],
  "reviewer_milestones": [
    { "node": "A", "label": "骨架+认证", "trigger_event": "review_ready", "description": "登录流、JWT、页面路由、骨架结构" },
    { "node": "B", "label": "核心业务交互", "trigger_event": "review_ready", "description": "创建/填写/统计主流程" },
    { "node": "C", "label": "最终验收", "trigger_event": "acceptance_ready" }
  ]
}
```

各角色 StatusReport 状态从 `等待用户确认` 转为 `执行中`。

### 3.4 边界情况验证

**场景 A：用户驳回计划**
- 用户回复「前端拆成两个角色：列表页 + 详情页」
- leader 修改团队方案 + 任务拆分 → 重新呈报
- **不启动 Agent 开发**，直到用户确认 ✅

**场景 B：确认前 Agent 尝试写文件**
- frontend-dev 在 plan_confirmed 前创建 package.json
- ❌ 违反只读约束 → leader 制止，要求只输出计划
- 机制：`role-roster.activation.read_only_until = "plan_confirmed"` ✅

**场景 C：用户跳过确认（不应发生）**
- 硬门设计：无确认则 Step 4 不执行
- 区别于旧"或按安全默认值继续"——新门**不允许跳过** ✅

---

## 4. 问题升级循环演示 — 验证「事件驱动检查点」

> 迁移说明：旧版用 33%/66%/100% 百分比检查点，现改为**事件驱动**（review_ready / acceptance_ready）。

**场景**：frontend-dev 在 Node A（骨架+认证）遇到 2 个问题，backend-dev 在 Node A 遇到 1 个问题。用户触发「进度」查询。

### 4.1 子 agent 内部问题记录（功能里程碑触发）

**frontend-dev 的 question_log**（Node A 触发后）：
```
Q-FE-001 | Node A | 运单列表筛选条件是否跨页保持？
       | 关联任务: 运单列表页 | 状态: 已上报
Q-FE-002 | Node A | 运单状态标签的颜色规范是否沿用旧版？
       | 关联任务: 运单列表页 | 状态: 已上报
```

**backend-dev 的 question_log**（Node A 触发后）：
```
Q-BE-001 | Node A | 运单列表接口是否支持按状态数组筛选（多选）？
       | 关联任务: 运单列表接口 | 状态: 已上报
```

### 4.2 用户说「进度」，leader 查询，收到回复

**frontend-dev 回复**：
```
【状态】工作中
【当前任务】运单列表页组件拆分
【进展】完成组件树设计与状态管理规划（Node A 骨架完成）
【阻塞项】无
【下一步】等待答复后决定筛选状态管理方案，继续组件实现
【需要的输入】无
【最近上报里程碑】Node A
【待答复问题】
1. [Q-FE-001][Node A] 运单列表筛选条件是否跨页保持？ (关联任务: 运单列表页)
2. [Q-FE-002][Node A] 运单状态标签的颜色规范是否沿用旧版？ (关联任务: 运单列表页)
```

**backend-dev 回复**：
```
【状态】工作中
【当前任务】运单列表接口开发
【进展】完成数据模型与基础 SQL（Node A 骨架完成）
【阻塞项】无
【下一步】等待答复后决定是否支持多选状态筛选
【需要的输入】无
【最近上报里程碑】Node A
【待答复问题】
1. [Q-BE-001][Node A] 运单列表接口是否支持按状态数组筛选（多选）？ (关联任务: 运单列表接口)
```

### 4.3 Leader 聚合后展示给用户

```
📊 团队进度报告 · 2026-07-28 14:00

## 一、进度总览
| 角色 | 状态 | 当前任务 | 进展 | 阻塞项 | 下一步 | 需要的输入 | 最近上报里程碑 |
|------|------|----------|------|--------|--------|------------|----------------|
| frontend-dev | 工作中 | 运单列表页组件拆分 | Node A 骨架完成 | 无 | 继续组件实现 | 无 | Node A |
| backend-dev | 工作中 | 运单列表接口开发 | Node A 骨架完成 | 无 | 决定是否多选状态筛选 | 无 | Node A |
| reviewer | 空闲 | 等待 Node A 审查 | — | 无 | 待 leader 送审 | — | — |
| tester | 空闲 | 等待需求 | — | 无 | 待派发 | 需求文档 | 无 |

## 二、待答复问题（共 3 题）
| 编号 | 来源 | 里程碑 | 问题 | 关联任务 | 提出次数 |
|------|------|--------|------|----------|----------|
| Q-FE-001 | frontend-dev | Node A | 运单列表筛选条件是否跨页保持？ | 运单列表页 | 1 |
| Q-FE-002 | frontend-dev | Node A | 运单状态标签的颜色规范是否沿用旧版？ | 运单列表页 | 1 |
| Q-BE-001 | backend-dev | Node A | 运单列表接口是否支持按状态数组筛选（多选）？ | 运单列表接口 | 1 |

请回答上述问题。可部分回答，格式如「Q-FE-001: 保持」；跳过的题目将保留至下次询问。
```

### 4.4 用户回答 + 分发（与 V1 相同，省略）

（答复分发逻辑同 `ct1-workspace/e2e-test-context-injection.md` §7.4-7.6。）

### 4.5 边界情况验证

**场景 A：跳过功能里程碑**
- frontend-dev 在 Node A 记录 Q-FE-003，之后直接推进到 Node B
- 检查点触发：Node A → Node B 转换时补报 Q-FE-003
- 结果：Q-FE-003 在 Node A→B 转换时被上报，不会丢失 ✅

**场景 B：跨 agent 重复问题**（同 V1 场景 B）✅

**场景 C：用户只回答部分问题**（同 V1 场景 C）✅

**验证点**：
- 收集 ✅：子 agent 在 Node A 记录的问题，leader 查询后正确聚合
- 展示 ✅：进度报告含「进度总览 + 待答复问题」两个 section
- 事件驱动 ✅：无百分比，里程碑为 Node A/B/C
- 部分回答 ✅：用户回答部分问题后，leader 只路由答复到对应 agent
- 继续不暂停 ✅：agent 收到答复→已答复，未答复→已作废（自行裁决），继续工作

---

## 5. 代码审查循环演示 — 验证「Reviewer + 功能里程碑 + 用户业务确认」

> 迁移说明：旧版用 33%/66%/100% 百分比里程碑，现改为 **Node A/B/C 功能里程碑**绑定触发事件（review_ready / acceptance_ready）。

**场景**：frontend-dev 在 Node A（骨架+认证）完成编码，leader 送 reviewer 审查；reviewer 出报告；leader 分流；dev 修复；Node B 再审；Node C 最终验收。

### 5.1 功能里程碑对照表（来自 TEAM_STATE）

| 节点 | 标签 | 触发事件 | 审查内容 | 用户业务确认 |
|---|---|---|---|---|
| **Node A** | 骨架+认证 | review_ready | 登录流、JWT、页面路由、骨架结构 | ☐ 确认骨架+认证方向 |
| **Node B** | 核心业务交互 | review_ready | 创建/填写/统计主流程 | ☐ 确认核心业务交互 |
| **Node C** | 最终验收 | acceptance_ready | 修复验证+遗留问题+业务完整性 | ☐ 最终验收 |

### 5.2 Dev 汇报（Node A，含本轮完成文件）

```
【状态】工作中
【当前任务】运单列表页组件拆分
【进展】Node A 骨架完成（组件树设计 + 状态管理规划 + 登录流）
【阻塞项】无
【下一步】等待审查通过后继续交互实现
【需要的输入】无
【最近上报里程碑】Node A
【触发事件】review_ready
【待答复问题】无
【本轮完成文件】
- src/components/WaybillList.vue（新增）
- src/store/waybill.js（修改）
- src/api/waybill.js（新增）
- src/router/auth.js（新增，登录流）
```

### 5.3 Leader 送审

leader 向 reviewer 发送：
```
请审查 frontend-dev 的运单列表页代码（Node A / 骨架+认证）：
- src/components/WaybillList.vue
- src/store/waybill.js
- src/api/waybill.js
- src/router/auth.js

审查范围：代码质量、架构合理性、安全、性能、编码规范、中间件使用。
按 Code Review 报告模板输出（严重问题/建议改进/需用户决策 + 总结）。
```

### 5.4 Reviewer 输出报告

```
## Code Review 报告
审查对象: frontend-dev 的 运单列表页
审查轮次: 第 1 轮（里程碑: Node A / 骨架+认证 / 触发事件: review_ready）
审查文件: src/components/WaybillList.vue, src/store/waybill.js, src/api/waybill.js, src/router/auth.js

### 严重问题（必须修复）— 阻塞项
| 编号 | 位置 | 问题描述 | 修复建议 | 分类 |
|------|------|----------|----------|------|
| R-FE-001 | WaybillList.vue:58 | 列表数据未做空值保护，data 可能为 null 导致渲染崩溃 | 添加 v-if="data && data.length" 或默认空数组 | 安全 |

### 建议改进（建议修复）— 非阻塞
| 编号 | 位置 | 问题描述 | 修复建议 | 分类 |
|------|------|----------|----------|------|
| R-FE-002 | waybill.js:23 | mutation 命名 WAYBILL_LIST 不符合项目驼峰规范 | 改为 setWaybillList | 规范 |
| R-FE-003 | WaybillList.vue:112 | 分页逻辑与筛选逻辑耦合在同一方法，难以维护 | 拆分为 fetchList / handleFilter / handlePage 三个方法 | 架构 |

### 需用户决策
| 编号 | 问题描述 | 选项 | 影响范围 |
|------|----------|------|----------|
| R-FE-U01 | 运单列表是否需要跨页保持筛选条件？ | A. 保持（持久化 localStorage） B. 不保持（刷新重置） | 用户体验与 waybillStore 设计 |

### 总结
- 是否通过: 否（存在 1 个严重问题）
- 整体评价: 组件结构清晰，状态管理基本合理；需修复空值保护与命名规范
- 本轮重点: 数据安全性与代码规范
```

### 5.5 Leader 分流 + 用户业务确认

**严重问题 + 建议改进 → 下发 frontend-dev**：
```
[CONTEXT ADDENDUM]
来源：reviewer 审查（第 1 轮 / frontend-dev / Node A / review_ready）
关联任务：运单列表页代码修复
审查问题：
  1. [R-FE-001][严重][安全] WaybillList.vue:58 — 列表数据未做空值保护。修复建议：添加 v-if 或默认空数组
  2. [R-FE-002][建议][规范] waybill.js:23 — mutation 命名不规范。修复建议：改为 setWaybillList
  3. [R-FE-003][建议][架构] WaybillList.vue:112 — 分页与筛选耦合。修复建议：拆分为三个方法
对原有上下文的变更：需修复上述问题后重新提交审查
```

**需用户决策 → 升级**：
leader 将 R-FE-U01 填入 Node A 的【待答复问题】：
```
1. [R-FE-U01][Node A] 运单列表是否需要跨页保持筛选条件？ A. 保持（持久化 localStorage） B. 不保持 (关联任务: 运单列表页)
```

**用户业务审查点（新增）**：
reviewer 报告 + leader 展示用户后，leader 做轻量业务确认：
```
📋 Node A 用户业务确认
- reviewer 审查：1 个严重问题（空值保护）+ 3 个建议改进
- 业务方向确认：骨架结构、登录流、页面路由是否符合预期？
- 请确认方向后继续 Node B（核心业务交互）
```

### 5.6 用户决策 + Dev 修复

用户回答「R-FE-U01: A，方向确认，继续 Node B」。leader 通过 `[CONTEXT ADDENDUM]`（来源=用户答复）分发给 frontend-dev。

frontend-dev 修复 R-FE-001/002/003 + 实现跨页保持 → 汇报 Node B（含修复说明 + 新完成文件）。

### 5.7 Node B 再审

leader 再次送 reviewer：
```
请审查 frontend-dev 的运单列表页代码（Node B / 核心业务交互 / review_ready）：
- 上轮已修复：R-FE-001/002/003（请验证）
- 本轮新增文件：[Node B 新增文件列表]
```

reviewer 输出 Node B 报告：
```
## Code Review 报告
审查对象: frontend-dev 的 运单列表页
审查轮次: 第 2 轮（里程碑: Node B / 核心业务交互 / 触发事件: review_ready）

### 上轮遗留验证
- R-FE-001: ✅ 已修复（v-if 保护已添加）
- R-FE-002: ✅ 已修复（命名已改为 setWaybillList）
- R-FE-003: ⚠️ 部分修复（已拆分 fetchList，但 handleFilter 与 handlePage 仍有耦合）

### 新发现问题
| 编号 | 位置 | 问题描述 | 修复建议 | 分类 |
|------|------|----------|----------|------|
| R-FE-004 | WaybillList.vue:135 | handlePage 仍调用 handleFilter，未彻底解耦 | handlePage 应只触发 fetchList，不直接调 handleFilter | 架构 |

### 总结
- 是否通过: 否（上轮 R-FE-003 部分修复 + 新发现 R-FE-004）
- 整体评价: 修复质量良好，但解耦不彻底
```

**Node B 用户业务审查点**：
```
📋 Node B 用户业务确认
- reviewer 审查：R-FE-003 部分修复 + 新发现 R-FE-004
- 业务方向确认：创建/填写/统计主流程是否符合预期？
- 请确认方向后继续 Node C（最终验收）
```

### 5.8 Node C 最终验收

第 3 轮（Node C / acceptance_ready）审查通过，leader 汇总展示用户：
```
📊 最终审查报告 · 运单列表页

## 审查结果: ✅ 通过（三轮审查完成）

| 轮次 | 里程碑 | 触发事件 | 严重问题 | 建议改进 | 需用户决策 | 结果 |
|------|--------|----------|----------|----------|------------|------|
| 第 1 轮 | Node A / 骨架+认证 | review_ready | 1 | 3 | 1 | 不通过 |
| 第 2 轮 | Node B / 核心业务交互 | review_ready | 0 | 2 | 0 | 不通过 |
| 第 3 轮 | Node C / 最终验收 | acceptance_ready | 0 | 1 | 0 | 通过 |

## 用户业务确认记录
- Node A：✅ 已确认（骨架+认证方向）
- Node B：✅ 已确认（核心业务交互）
- Node C：✅ 最终验收通过

## 遗留未决策问题
无（R-FE-U01 已在第 1 轮由用户决策：跨页保持筛选条件）

## 整体评价
代码质量良好，安全性、规范性、架构合理性均经过三轮迭代提升。业务方向经两次用户确认，无偏差。
```

### 5.9 边界情况验证

**场景 A：审查通过（无严重问题）**
- reviewer 输出「是否通过: 是」→ leader 告知 dev 通过 → 继续下一里程碑 ✅

**场景 B：用户跳过决策**
- R-FE-U01 被跳过 → leader 基于上下文自行裁决 → `void_reason = leader 代答` ✅

**场景 C：跨轮次遗留追踪**
- 第 2 轮报告开头列出「上轮遗留验证」→ R-FE-001/002/003 逐条标注修复状态 ✅

**场景 D：dev 不同意审查意见**
- dev 向 leader 申述 → leader 裁决：采纳或维持 ✅

**场景 E：用户业务方向偏差（新增）**
- Node B 用户业务确认时发现核心交互方向偏差
- 记录为阻断项 → dev 修复后重新送审 ✅

**验证点**：
- 角色 ✅：reviewer 作为延迟启动角色，输出结构化审查报告
- 触发 ✅：dev 在功能里程碑（Node A/B/C）完成编码后，leader 送审
- 事件驱动 ✅：无百分比，里程碑为 Node A/B/C + review_ready/acceptance_ready
- 分流 ✅：严重/建议→CONTEXT ADDENDUM 下发 dev；需决策→升级用户
- 循环 ✅：至少 3 轮（Node A/B/C），每轮 reviewer 重新审查修复后代码
- 用户业务确认 ✅：每个功能节点后 leader 做轻量业务确认
- 终态 ✅：Node C 后 leader 汇总最终结果 + 遗留未决策问题展示用户
- 边界 ✅：通过判定/跳过决策/跨轮追踪/dev 申述/业务偏差 均正确处理

---

## 6. 测试结论

| 验证项 | 结果 |
|---|---|
| 开发计划确认硬门（Step 3.75） | ✅ 契约冻结后、Agent 启动前，必须等用户确认 |
| 技术基线验证（Step 1.5） | ✅ 数据层一致性、环境就绪、凭证方案 |
| Agent 只读约束 | ✅ plan_confirmed 前 dev 角色只读 |
| 功能里程碑（Node A/B/C） | ✅ 骨架+认证 → 核心业务交互 → 最终验收 |
| 事件驱动（非百分比） | ✅ review_ready / acceptance_ready，无 33/66/100% |
| 用户业务审查点 | ✅ 每个功能节点后 leader 做轻量业务确认 |
| reviewer 角色 | ✅ 延迟启动，输出结构化审查报告 |
| 审查触发 | ✅ 功能里程碑完成编码后，leader 送审 |
| 审查分流 | ✅ 严重/建议→CONTEXT ADDENDUM；需决策→升级用户 |
| 三轮循环 | ✅ Node A/B/C，每轮重新审查修复后代码 |
| 审查终态 | ✅ Node C 后 leader 汇总最终结果 + 遗留未决策问题 |
| 审查边界 | ✅ 通过判定/跳过决策/跨轮追踪/dev 申述/业务偏差 |

**机制验证通过**。下一步：在实际项目中运行一次真实 spawn，观察子 agent 的实际输出质量与返工次数。
