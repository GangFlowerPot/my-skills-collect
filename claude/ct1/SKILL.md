---
name: ct1
description: 多 Agent 项目编排器——从需求拆分、动态组队、分工开发、代码审查、测试验收到交付的全生命周期编排。默认根据任务图生成最小可行团队（leader 固定 + 按任务边界动态生成执行/质量/审查/专项角色），同时支持纯组队（create-only）和端到端交付（delivery）两种模式。触发语义：(1) 组队类——"创建/组建/搭建/成立/拉起/搞一个/建个 + 团队/小队/工作组/队伍"，英文 create team / build a team / set up a team / spin up a team / team up；(2) 交付类——"开发/实现/做一个/完成 + 需求/功能/模块/系统"，英文 build / implement / develop / deliver + feature/module；(3) 隐式意图——用户描述了一个需要多种角色协作完成的项目，即使没提"团队"。负例边界（不触发）：修正 README 拼写、解释现有代码、查询现有团队状态、非软件开发团队、无需并行的一步小任务（这些由单 Agent 处理）。进度查询（"进度/status/progress"等）是本 skill 部署的团队的配套能力，由生成的协议文件定义，不在此 skill 触发。
---

# ct1 — 多 Agent 项目编排器

## 运行依赖

ct1 校验脚本需要 **Python 3.10+**。Python 2 不支持。

### 统一运行入口

```powershell
# Windows（显式指定 Python 3 路径）
$env:CT1_PYTHON = "C:\Path\To\Python313\python.exe"
& $env:CT1_PYTHON scripts/ct1_validate.py
```

```bash
# Unix
python3 scripts/ct1_validate.py
```

### Python 探测策略

1. 优先使用显式配置的 `CT1_PYTHON`
2. 探测 `python3`
3. 探测 `py -3`
4. 探测 `python`，但必须验证 `sys.version_info.major == 3`
5. 如果可用，可使用 `uv run python`
6. 所有候选均不可用时，停止 Python 门禁并报告阻塞（不伪造通过）

找不到 Python 3 时交付门禁状态为 `blocked`，不是 `passed`。

## 何时使用

只要用户想搭建一个**有多角色分工、能并行工作、可查询进度**的 Agent 协作小组，或者要**推进一个需求从开发到交付**，就用这个 skill。典型触发：

- **组队类**：`创建团队`、`组建一个团队`、`搭建工作组`、`拉起一个小队`、`搞一个前后端测试组`、`成立专项小组`、`建个队伍`、`create a team`、`build a team`、`set up a team`、`spin up a team`、`team up`
- **交付类**：`开发一个运单模块`、`实现权限隔离`、`完成这个需求并交付`、`build a feature`、`implement the payment module`、`deliver this requirement`
- **隐式意图**：用户描述了一个需要多种角色协作完成的项目，即使没提"团队"二字

### 不应触发（负例边界）

以下场景**不创建完整团队**，由单 Agent 处理：

- 修正 README 拼写、解释现有代码、查询现有团队状态
- 非软件开发团队（如写作、翻译、调研小组）
- 无需并行的一步小任务（单文件修改、简单查询）

> 简单、单文件、低风险任务应降级为单 Agent，不为了使用团队而创建团队。

## 运行模式

本 skill 支持两种显式模式：

### `create-only`（仅组队）

适用于用户只要求创建团队、建立协议或准备后续工作。完成条件：

- 团队配置已确认；必需 Agent 已启动；团队状态已持久化；用户收到团队说明和使用方式；**不自动假定存在开发需求**。

触发：只有组队意图、没有需求。

### `delivery`（端到端交付）

适用于用户已经给出需求，或明确要求团队完成开发、测试和交付。完成条件：

- 需求验收标准已经建立；任务板中的必需任务全部满足项目级 DoD；必需测试有真实执行结果；严重审查问题已经关闭；最终交付报告已经生成；未完成、未测试和已知风险已明确披露。

触发：有明确需求；默认使用 `delivery`。

### 模式判断规则

| 场景 | 模式 |
|---|---|
| 只有组队意图，无需求 | `create-only` |
| 有明确需求 | `delivery`（默认） |
| 简单、单文件、低风险任务 | 单 Agent 降级（不建团队） |

## 这个 skill 做什么

按全生命周期编排，按顺序：

1. **判断任务规模与运行模式**：决定单 Agent / `create-only` / `delivery`
2. **收集项目上下文**：快速了解项目全貌
3. **需求澄清与验收标准**（delivery）：建立 Requirement Brief
4. **选择或复用团队**：根据任务图动态生成最小可行团队
5. **建立任务图与文件所有权**：拆分为可验证任务
6. **方案及接口契约**：前后端契约生命周期
7. **并行开发**：按角色切片注入上下文
8. **风险驱动的代码审查**：reviewer 延迟启动、事件触发
9. **集成与测试**：tester 质量门禁
10. **修复与回归**：缺陷回流开发
11. **Definition of Done 检查**：任务级 + 项目级 DoD
12. **用户验收或交付确认**：生成交付报告
13. **持久化最终状态**

## 默认团队配置（动态生成，非固定）

> **核心原则：角色是任务图的执行视图，不是团队设计的起点。** 正式团队人数必须在理解项目方向并形成初始任务图之后决定；项目方向不明时不得启动完整执行团队。

### 角色分类

| 类别 | 角色 | 启动规则 |
|---|---|---|
| **固定角色** | `leader`（统筹领导决策者） | 始终存在，唯一 |
| **执行角色** | 前端、后端、全栈等（如 `frontend-dev`、`backend-dev`、`waybill-service-dev`） | 根据项目任务和边界动态生成 |
| **质量角色** | `tester` | 有可验收交付物时启用 |
| **审查角色** | `reviewer` | 有代码产出且进入审查阶段时延迟启动 |
| **专项角色** | DBA、DevOps、安全、UI 等（如 `migration-specialist`、`security-reviewer`） | 风险或任务需要时启用 |

### leader 职责

需求/方向沟通；汇总各方方案；方向决策；协调团队；分流审查意见；维护任务图与团队状态。**默认对话对象**。

### 默认 Web 团队（示例模板，非强制）

当项目是标准 Web 应用且需求明确时，可作为起点：

- **核心成员**：leader、frontend-dev、backend-dev、tester
- **延迟角色**：reviewer（代码可审查时启动）

> 这是"示例模板"，不是不可变默认。实际团队由任务图推导：小型前后端 CRUD 可合并为 `fullstack-dev`；多微服务按业务边界拆分；数据库迁移增加 `migration-specialist`；权限安全增加 `security-reviewer`。

### 角色命名

按任务边界命名，避免 `dev-1`/`dev-2`/`backend-dev-2`。推荐：`waybill-ui-dev`、`customer-service-dev`、`auth-integration-dev`、`migration-specialist`。

### 团队人数推导

人数由当前阶段可独立执行的任务簇推导，不是由技术栈数量推导：

```
初始执行人数 ≈ 当前阶段可并行任务簇数量 + 必要的独立质量或专项职责
```

受以下约束：每个角色有足够且明确的工作量、独立交付物和验收标准；写入范围可隔离或指定唯一 owner；并行能缩短关键路径；协调成本低于并行收益；不超过当前环境的可用并发数量。

### 角色动态扩缩

任务图变化时允许扩容、合并、替换和结束角色（详见 `references/dynamic-team-selection.md`）。

### model_policy（不绑定具体版本）

| 角色类别 | 模型级别 |
|---|---|
| leader | high-reasoning |
| reviewer | high-reasoning |
| developer（执行角色） | default |
| tester | default |
| 状态整理 / 信息收集 | lightweight |

平台无法指定模型时，继承当前会话模型。用户指定模型时，以用户配置为准。

## 工作流（按顺序执行）

### 第 0 步：判断任务规模与运行模式

**最先执行**，决定后续路径：

| 场景 | 决策 |
|---|---|
| 单文件、低风险、一步完成 | **单 Agent**（不建团队） |
| 只有组队意图，无需求 | **`create-only`** |
| 跨模块但职责单一 | leader + 1 个执行 Agent |
| 前后端联动且需要验收 | 标准开发团队（`delivery`） |
| 安全、迁移、部署或大型项目 | 增加专项角色（`delivery`） |

> 单 Agent 降级时，直接交付结果，不创建团队、不生成协议文件。

### 第 1 步：收集项目上下文（Pre-team）

**前置分析阶段只能使用主线程或一个最小 `planning-leader`，不得预先启动前端、后端、测试和审查等候选角色。**

主线程需要快速了解项目全貌。按以下顺序探测，**取第一个能用的**：

1. 读项目根目录的 `CLAUDE.md` 或 `.claude/CLAUDE.md`（如果存在）
2. 读项目记忆导航入口（`zsh/AGENT_MEMORY.md` → `PROJECT_MEMORY.md`，如果存在）
3. 探测构建文件：`package.json`、`pom.xml` / `build.gradle`、`go.mod`、`pyproject.toml` 等
4. 以上都没有 → 简短问用户："项目用什么技术栈？主要做什么？"

从上述来源提取一段**项目上下文摘要**（3–8 行即可），至少包含：项目名/领域、前端技术栈、后端技术栈、关键入口/命令。

#### 主线程 vs planning-leader 的选择

默认由主线程完成前置分析，只有满足以下任一条件时才建议启动 `planning-leader`：

- 项目规模较大，涉及多个模块或服务
- 项目陌生，现有上下文不足
- 用户需求包含多个交付阶段
- 存在明显的安全、数据迁移、部署或跨系统风险
- 主线程需要在继续与用户沟通的同时，让独立 Agent 深入探测项目
- 预计任务图包含多个依赖层级，需要专门维护

以下情况**不应**启动 `planning-leader`：单文件或一步修改、项目结构简单且需求明确、主线程能在短时间内完成探测、创建额外 Agent 不会带来新的分析价值。

`planning-leader` 完成分析后直接转为正式 leader，不要停止后再创建另一个重复 leader。

### 第 1.5 步：需求澄清与验收标准（仅 delivery）

`create-only` 模式跳过本步。

将自然语言需求转化为结构化规格。生成 Requirement Brief（详见 `references/requirement-brief.md`）：

- 目标 / 范围 / 不在范围 / 用户场景
- **验收标准**（每个 AC 使用唯一 ID，如 `AC-001`）
- 技术与业务约束 / 风险 / 假设 / 待确认问题

**决策规则**：

- 局部、可逆、低风险问题可以记录假设后继续
- 数据删除、权限、安全、费用、外部发布和不可逆迁移必须由用户确认
- **数据层语义冲突**（DDL 语义 vs 现有 ADR 裁定 vs 实际库表，如 BYTE vs CHAR）必须由用户确认
- 每个开发任务至少关联一个 AC；tester 必须把测试用例映射到 AC
- **技术基线**（数据层一致性、环境就绪、凭证方案）按 `references/requirement-brief.md` 的"技术基线验证"章节执行

### 第 2 步：建立任务图与文件所有权

`create-only` 模式可简化为高层任务列表。

leader 或主线程按以下顺序构建初始任务图（详见 `references/task-board-schema.md`）：

1. 从用户需求提取业务目标和验收标准
2. 检查项目目录、模块和技术栈
3. 识别必要交付物
4. 将交付物分解为可验证任务（每任务含 task_id、交付物、acceptance_criteria、depends_on、write_scope、required_capabilities、risk）
5. 标注安全、数据、部署和兼容性风险
6. 识别关键路径
7. 判断哪些任务当前信息不足

> 禁止直接用 `.vue` → frontend-dev、`.java` → backend-dev 的映射替代任务分析。文件类型只能作为辅助证据。

### 第 2.5 步：方案及接口契约

前后端接口需建立正式契约（详见 `references/api-contract-protocol.md`）：

- 契约字段：endpoint、owner、consumers、status、request/response/errors、permissions、version
- 契约状态：draft → frontend-reviewed → tester-reviewed → frozen → implemented → verified
- frozen 后的修改必须增加版本；leader 找出所有 consumer，用 `[CONTEXT ADDENDUM]` 通知相关角色

### 第 3 步：动态生成最小可行团队

**正式团队人数必须在理解项目方向并形成初始任务图之后决定。**

详见 `references/dynamic-team-selection.md`（团队生成算法、Role Candidate schema、角色生命周期）和 `references/team-selection.md`（团队设计最低充分信息、多团队隔离）。

团队方案生成后进入第 3.5 步。**仅 delivery 模式**在第 3.75 步等待用户对"团队架构 + 开发计划"的明确确认，再启动 Agent 开发。

#### 延迟启动规则

| 角色 | 启动条件 |
|---|---|
| tester | Requirement Brief 完成后可参与测试计划；出现 `test-ready` 交付物时进入执行阶段 |
| reviewer | 存在 review-ready 任务或高风险设计需要设计审查 |
| DBA / migration-specialist | 任务图包含 schema、SQL、索引、批量数据、迁移或回滚任务 |
| DevOps / release-engineer | 任务图包含构建、部署、环境、CI/CD、容器或发布任务 |
| security-reviewer | 涉及认证、授权、密钥、敏感数据、用户输入或外部访问 |

### 第 3.5 步：定位 / 验证上下文合约

上下文合约（`references/context-contract.md`）定义了每个角色需要哪些文档切片。本步决定"spawn 时给每个 Agent 灌什么"。

按以下顺序探测合约：项目记忆目录下的 `CONTEXT_CONTRACT.md` → `TEAM_PROTOCOL.md` 中的上下文合约章节 → 项目根目录的 `context-contract.md`。

**如果合约存在**：验证时效性；确认合约覆盖的角色与第 3 步的团队配置匹配（动态角色 ID）；通过验证后按合约做角色切片。

**如果合约不存在**：若项目有结构化文档，可询问用户是否当场生成一份合约；若用户拒绝或无结构化文档 → 回退到第 1 步的统一摘要注入。

> 上下文合约必须支持动态角色 ID（由任务图生成，非常驻固定角色）。

### 第 3.75 步：开发计划确认（硬门，仅 delivery）

`create-only` 模式跳过本步。

**前置条件**：契约已冻结（第 2.5 步）、团队已生成（第 3 步）、上下文合约已定位（第 3.5 步）。

leader 向用户呈报**开发计划**，内容至少包括：

- 团队架构与职责分工（含 reviewer 启动里程碑 Node A/B/C，详见 `references/code-review-protocol.md`）
- 前后端任务拆分、执行顺序、关键路径
- 关键设计决策与接口契约版本
- 数据层与环境就绪状态（来自第 1.5 步的"技术基线验证"）

**规则（硬门）**：

- ⏸ **必须等用户明确确认后才进入第 4 步**启动 Agent 开发。计划驳回 → leader 修改后重新呈报。
- 确认后：leader 向 TEAM_STATE 写入 `plan_confirmed` 触发事件与 `reviewer_milestones`，各角色 StatusReport 状态从 `等待用户确认` 转为 `执行中`。
- **未确认前，任何 dev 角色不得写业务代码或配置文件**（仅可读文件、输出计划）。

> 这是交付模式下**唯一的"启动前用户检查点"**。delivery 需求已存在，"请用户提第一个需求"在此失效，改为"请用户确认开发计划"。

### 第 4 步：并行启动 Agent

用 **一次消息里多个 `Agent` 调用**的方式并行启动**当前阶段必需**的角色（延迟角色不在此步启动）。

每个 Agent 的 prompt 必须按**五要素模板**（`references/five-element-prompt.md`）组装，并在角色 prompt 中新增：

- owned task IDs；write scope；dependencies；activation condition
- Definition of Done；禁止修改范围；handoff 对象

**技术栈约束**仍须注入：基于探测到的真实栈，告诉它"必须基于现有栈，不引入项目未使用的框架"。

**协作协议**与**进度查询规范**保持不变：协作规则摘要（见"协作规则摘要"节）+ StatusReport/v2 格式（见"进度查询协议"节）。

**leader 特殊处理**：leader 的 prompt 还要加上"默认对话窗口"职责，并在末尾让它向用户做一个**简短团队介绍**（角色、工作模式、进度查询触发词），**然后请用户确认开发计划**（delivery 模式下需求已存在，改为确认计划而非提出需求；计划确认前 dev 角色只读）。

**flat-roster 回退**：子 Agent 上下文（teammate）中，`Agent(name=...)` 可能被 harness 拒绝（"team roster is flat"）。遇到时按以下顺序回退，**不要中止流程**：
1. 去掉 `name` 参数，以 unnamed subagent 形式启动，把角色身份、项目上下文、协作协议、进度规范全部注入 prompt
2. 如果该角色在会话中已有活跃同名 teammate（命名冲突的"复用"路径），跳过启动，直接通过 `SendMessage` 向既有 teammate 发指令
3. 记录到 user_notes，继续后续步骤

### 第 4.5 步：运行时扩缩（Runtime Scaling）

任务图变化时允许扩容、缩容、替换和结束角色：

- **扩容**：新增独立业务域、关键路径出现可独立并行的大任务、新增数据库迁移/部署/安全专项工作
- **缩容/退场**：角色任务全部 accepted、后续任务不再需要该能力、角色长期等待且无独立工作
- **合并/替换**：两角色频繁修改相同文件、某角色失败或无法继续

团队变化必须更新：Task Graph、Role Candidate、TEAM_STATE、owned tasks、write scope、handoff 信息。角色退场时输出 Handoff Brief。

#### Agent 健康检查与替补

详见 `references/recovery-protocol.md`。健康状态：active/idle/waiting_input/unresponsive/failed/replaced/completed。恢复流程：第 1 次无响应重请求 → 第 2 次检查活跃 → 确认失败保存状态 → leader 选择重试/重分配/启动替补 → 替补接收 Handoff Brief → 先验证已有产物再继续。

#### 文件所有权与工作区

详见 `references/workspace-strategy.md`。每个任务声明 write_scope；公共文件指定唯一 owner；tester/reviewer 默认只读；不允许通过直接覆盖解决冲突。

### 第 5 步：leader 介绍团队（信息传递）

> 团队与计划的**确认**已在第 3.75 步完成。本步仅为信息传递，不再重复确认。

leader 启动后会自动发介绍消息。主线程把它**原样转述**给用户，不要改写。介绍内容：团队架构、职责分工、开发计划概要、reviewer 启动里程碑（Node A/B/C）。

### 第 6 步：持久化进度查询协议

进度查询机制要跨会话可用，所以必须写进文件。生成 `references/team-protocol.md` 的**项目副本**：

- 如果项目有记忆目录 → 写到 `TEAM_PROTOCOL.md`
- 否则如果项目有 `.claude/` → 写到 `.claude/team-protocol.md`
- 否则 → 写到项目根目录 `team-protocol.md`

协议文件内容见 `references/team-protocol.md`（触发词、StatusReport/v2 引用、汇总格式、执行规范）。部署时把"默认团队配置"替换成**本次实际组建的团队**（只列非 leader 成员）。

> 项目状态只写入 `<project>/.claude/teams/<team-id>/`，不写回全局 Skill 安装目录。调试快照写入项目团队目录下的 `debug/`。

然后**挂载导航**：
- 如果项目有 `AGENT_MEMORY.md` → 在其"记忆地图"表加一行指向该协议文件
- 否则如果项目有 `CLAUDE.md` → 在末尾加一段"团队协作"指向该文件
- 否则 → 在介绍中告知用户协议文件路径即可

### 第 7 步：Definition of Done 检查（仅 delivery）

`create-only` 模式跳过本步。

详见 `references/testing-gate.md`（测试门禁）和 `references/delivery-report.md`（交付报告）。

#### 任务级 DoD

任务进入 `accepted` 前必须满足：产物已生成；符合现有技术栈和架构；开发自测完成；严重审查问题为零；对应测试通过；AC 有验证证据；相关文档或契约已更新；临时假设已记录。

#### 项目级 DoD

项目进入 `delivered` 前必须满足：所有必需任务为 `accepted`；所有必需 AC 通过；P0/P1 缺陷为零；构建和必需测试成功；数据迁移和回滚要求已处理；**用户旅程跑通（冷启动走查通过）**；已知限制已披露；交付报告已生成。

#### 测试门禁（来自 testing-gate）

| 门禁 | 要求 |
|---|---|
| AC 覆盖 | 每个必需 AC 至少有一个测试 |
| 缺陷 | P0/P1 缺陷为零 |
| 执行 | 必需测试全部执行 |
| 记录 | 测试命令、结果和环境已记录 |
| 环境 | 环境不可用不得标记为"测试通过" |
| 用户旅程跑通 | 冷启动走查全部步骤通过；任一步骤失败则阻断交付（即使所有 AC 通过、P0/P1=0） |

> 不得仅凭"100%"声明完成；每个门禁都有证据；不满足 DoD 时输出"有条件完成"或"未完成"。

### 第 8 步：生成交付报告（仅 delivery）

详见 `references/delivery-report.md`。报告格式：

- 交付结论：`通过 / 有条件通过 / 未通过`
- 需求完成情况（AC 结果 + 证据）
- 变更摘要 / 修改文件 / 接口、数据库和配置变化
- 构建与测试结果 / Code Review 结果
- 部署或使用说明 / 数据迁移说明 / 回滚说明
- 已知限制与风险 / 未完成事项 / 用户下一步操作

**交付判定**：所有门禁满足 → `通过`；只剩非阻断风险且已披露 → `有条件通过`；存在严重问题、测试失败或关键 AC 未完成 → `未通过`。

### 第 9 步：持久化最终状态

将团队最终状态、任务板、测试报告、审查记录、交付报告路径写入项目记忆，确保会话恢复后可定位。

## 进度查询协议

这是本 skill 部署的配套能力。协议文件是它的唯一真相源；下面摘要关键规则，细节以 `references/team-protocol.md` 为准。

### 触发词

用户说以下任一短语，主线程启动一次进度同步：

- 中文：`进度`、`查进度`、`进度如何`、`同步进度`
- 英文：`status`、`progress`、`check progress`、`where are we`、`how's it going`

### 查询流程

1. 识别触发词
2. **并行**向所有**非 leader** 执行者发送 StatusReport/v2 状态请求（同一消息多个 `SendMessage`）
3. 收集回复，汇总为一张 Markdown 表格
4. 未回复者显示 `⏳ 未响应`

### 状态回复格式

所有角色统一使用 StatusReport/v2。完整 schema 见 `references/status-report-schema.md`。

### 汇总表格格式

```
| 成员 | 状态 | 任务ID | 当前任务 | 进展 | 阻塞项 | 下一步 | 触发事件 | 待答复问题 | 变更文件 | 验证结果 |
|---|---|---|---|---|---|---|---|---|---|---|
```

表格列和行随本次实际团队角色变化。

## 协作规则摘要（注入每个 Agent）

- **默认对话**：用户 ↔ leader
- **出方案**：各技术角色各自出方案，测试同步出覆盖全栈的测试用例 → leader 汇总后呈报用户
- **沟通需求**：用户同时与 leader（产品/风险/进度/资源角度）和测试（质量/边界/用户体验/验收标准角度）对话
- **进度查询**：主线程按触发词并行查非 leader 成员，不经过 leader
- **问题升级**：子 agent 工作中遇到疑问时主动记录，在触发事件节点随 StatusReport 上报给 leader；leader 聚合后展示给用户回答，再分发给子 agent；子 agent 收到答复前跳过该工作项继续推进（不暂停）。完整规范见 `references/question-escalation-protocol.md`
- **代码审查**：风险驱动（低风险最终审查一次；中风险契约审查+最终审查；高风险设计/实现中/最终三轮）。reviewer 在 review-ready 时启动；输出结构化报告（严重问题/建议改进/需用户决策）；leader 分流：严重+建议问题通过 `[CONTEXT ADDENDUM]` 下发 dev 修改，需用户决策项走问题升级循环。完整规范见 `references/code-review-protocol.md`

## 注意事项

- **并行启动**：第 4 步必须一次消息多 Agent（当前阶段必需角色），延迟角色按条件启动
- **上下文按角色切片**：有合约时按角色注入 ~5KB 切片（不同角色内容不同）；无合约时才回退到 3–8 行统一摘要
- **凭据不入 prompt**：项目上下文摘要里不要包含密码、Token、私钥等秘密
- **技术栈跟着项目走**：角色名按任务边界动态生成，但 prompt 里的技术约束必须来自第 1 步探测到的真实栈
- **leader 是枢纽但进度查询绕过它**：进度查询直接查执行者，不增加 leader 负担
- **任务推进中的动态补充**：团队组建后，任务推进中出现新信息时，用 `[CONTEXT ADDENDUM]` 结构化消息灌入（`references/dynamic-supplement-protocol.md`）
- **完成标准不是 Agent 启动或进度达到 100%**，而是验收标准、测试、审查和交付门禁通过
- **角色数量多≠协作能力强**；只有当任务边界清晰、写入范围独立、依赖可隔离、并行能缩短关键路径时，创建额外 Agent 才有价值
