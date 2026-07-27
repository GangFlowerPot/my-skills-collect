# ct1 动态团队生成整改任务书

> 用途：将本文件交给负责修改 `ct1` Skill 的 Agent。
> 核心目标：把“先确定固定角色，再给角色找任务”改造成“先分析需求并建立任务图，再根据任务边界动态生成最小可行团队”。

## 一、可直接复制给整改 Agent 的提示词

```text
你是一名负责重构 Claude/Codex 本地 Skill 的高级 Agent 编排架构师。

当前工作目录是 ct1 Skill。请将它从“固定角色组队”重构为“依据任务图动态生成角色”的团队编排 Skill。

在执行任何修改前，必须完整读取：
1. SKILL.md
2. AGENT_IMPROVEMENT_PLAN.md
3. DYNAMIC_TEAM_REFACTOR_PROMPT.md
4. references/ 下与团队、上下文、任务、进度、测试和审查有关的文件
5. evals/ 下现有评测

一、核心设计原则

1. 不再默认机械启动 leader + frontend-dev + backend-dev + tester + reviewer。
2. 先解析用户需求和项目结构，生成 Requirement Brief 和初始任务图。
3. 根据任务图中的业务边界、技术边界、依赖关系、写入范围、风险和并行收益生成最小可行团队。
4. 角色必须服务于任务；不得先创建空闲角色，再等待任务。
5. leader 是固定的编排责任，但执行角色必须动态生成。
6. tester、reviewer、DBA、DevOps、安全等角色按交付物、风险和阶段延迟启动。
7. 一个任务只有在具有明确输入、输出、验收标准和独立写入范围时，才适合交给独立 Agent。
8. 如果两个任务高度依赖、频繁修改相同文件或无法定义稳定契约，应合并给同一 Agent，而不是为了并行强行拆分。
9. 简单、单文件、低风险任务应降级为单 Agent；不要为了使用团队而创建团队。
10. 完成标准不是 Agent 启动或进度达到 100%，而是验收标准、测试、审查和交付门禁通过。
11. 正式团队人数必须在理解项目方向并形成初始任务图之后决定；项目方向不明时不得启动完整执行团队。
12. 前置分析阶段只能使用主线程或一个最小 `planning-leader`，不得预先启动前端、后端、测试和审查等候选角色。
13. 简单和中型需求由主线程完成前置分析；大型、陌生、多模块或高风险项目可先启动一个 `planning-leader`。
14. `planning-leader` 完成 Requirement Brief 和初始任务图后，可以继续担任正式 leader，无需重复创建同类角色。
15. 初始团队人数不是永久配置。任务图变化时允许扩容、合并、替换和结束角色。

二、目标工作流

把主流程调整为：

Pre-team：仅主线程或 planning-leader
→ 任务规模判断
→ 项目上下文探测
→ Requirement Brief
→ 达到团队设计最低充分信息
→ 初始任务图
→ 任务聚类与角色候选生成
→ 并行收益/冲突/风险评估
→ 生成最小可行团队
→ 向用户展示“任务图摘要 + 动态团队方案 + 为什么这样分”
→ 用户确认或按安全默认值继续
→ Execution Team：启动当前阶段必需 Agent
→ 按任务图派发具体任务
→ 根据任务状态延迟启动 tester/reviewer/专项角色
→ Runtime Scaling：根据任务图变化扩容、缩容、替换或结束角色
→ 开发、审查、测试、验收、交付

三、必须新增或修改的能力

1. 新增 Task Graph schema：
   - task_id
   - title
   - domain
   - task_type
   - inputs
   - outputs
   - acceptance_criteria
   - depends_on
   - write_scope
   - read_scope
   - risk
   - required_capabilities
   - estimated_parallel_value
   - status

2. 新增 Role Candidate schema：
   - role_id
   - display_name
   - mission
   - owned_tasks
   - capabilities
   - write_scope
   - read_scope
   - dependencies
   - activation
   - deactivation
   - merge_reason 或 split_reason

3. 新增动态团队选择算法：
   - 从任务图提取能力需求；
   - 按高内聚、低耦合原则聚类任务；
   - 检查文件写入冲突；
   - 检查任务依赖是否允许并行；
   - 检查角色协调成本是否高于并行收益；
   - 生成最少角色数；
   - 根据高风险任务增加 tester/reviewer/专项角色；
   - 给每个角色生成明确的 owned_tasks 和 write_scope。

4. 增加角色合并规则：
   - 小型前后端修改可合并为 fullstack-dev；
   - 同一模块内强依赖任务优先交给同一角色；
   - 共享文件比例高或契约不稳定时优先合并；
   - 总工作量很小或无法并行时使用单执行 Agent。

5. 增加角色拆分规则：
   - 任务拥有独立交付物和验收标准；
   - 写入范围基本不重叠；
   - 依赖可以通过稳定契约隔离；
   - 每个任务有足够工作量；
   - 并行能缩短关键路径；
   - 高风险专项需要独立复核。

6. 增加阶段性角色：
   - tester 在验收标准形成后可参与测试计划，在产生可测交付物时进入执行阶段；
   - reviewer 在出现 review-ready 代码时启动；
   - DBA 在涉及 schema、SQL、数据迁移或高风险查询时启动；
   - DevOps 在涉及构建、部署、环境、CI/CD 时启动；
   - security-reviewer 在涉及认证、权限、密钥、外部输入或敏感数据时启动。

7. 角色命名不得只使用 dev-1/dev-2。
   应按任务边界命名，例如：
   - waybill-ui-dev
   - waybill-service-dev
   - customer-integration-dev
   - migration-specialist
   - auth-security-reviewer

8. 动态团队方案必须解释：
   - 为什么需要这些角色；
   - 每个角色负责哪些任务；
   - 为什么某些任务合并；
   - 为什么某些角色延迟启动；
   - 哪些角色没有创建以及原因；
   - 预计并行关系与关键依赖。

四、必须避免

1. 不要把“前端、后端、测试”继续写成不可变默认。
2. 不要仅根据文件扩展名生成角色。
3. 不要为每个任务都创建一个 Agent。
4. 不要让多个 Agent 在没有 ownership 的情况下修改同一文件。
5. 不要让 tester 和 reviewer 从团队创建开始一直空闲。
6. 不要只用主观百分比决定审查和测试时机。
7. 不要因追求并行而拆开强依赖任务。
8. 不要覆盖用户已有改动或现有团队状态。

五、至少覆盖以下决策场景

1. 一个 README 拼写修改：
   - 不创建团队，使用单 Agent。

2. 小型 CRUD，前后端各只改少量文件：
   - leader + fullstack-dev；
   - tester/reviewer 按风险延迟启动。

3. 标准管理后台模块：
   - leader + UI/前端实现角色 + 后端服务角色；
   - tester 在契约形成后加入；
   - reviewer 在代码可审查时加入。

4. 多微服务需求：
   - 按业务服务或稳定边界拆分，不使用一个 backend-dev 包办全部。

5. 数据库迁移：
   - 增加 migration/DBA 角色；
   - 明确备份、迁移验证和回滚任务。

6. 权限和认证功能：
   - 增加安全审查能力；
   - 相关关键决策不得由普通开发 Agent 自行假设。

7. 前后端频繁修改同一契约且需求尚不稳定：
   - 先由一个设计/全栈角色稳定契约；
   - 契约冻结后再决定是否拆分。

六、必须更新的文件

至少评估并按需修改：
- SKILL.md
- references/team-protocol.md
- references/context-contract.md
- references/five-element-prompt.md
- references/code-review-protocol.md
- evals/evals.json

建议新增：
- references/task-graph-schema.md
- references/dynamic-team-selection.md
- references/role-lifecycle.md
- assets/TASK_GRAPH.template.md
- assets/TEAM_PROPOSAL.template.md
- evals/dynamic-team-evals.json

七、实施要求

1. 先输出当前固定角色逻辑清单和计划修改点。
2. 再建立 task graph、role candidate 和 team proposal schema。
3. 然后重构 SKILL.md 主流程。
4. 最后更新协议和 eval。
5. 每次修改后搜索旧的固定团队描述，避免残留冲突。
6. 不删除仍有价值的上下文切片、问题升级、动态补充和代码审查能力；应将它们接入动态角色生命周期。
7. 修改完成后运行静态一致性检查和至少一组动态团队决策 eval。

八、完成验收

只有满足以下条件才可以宣布完成：
- 简单任务能降级为单 Agent；
- 小型跨层任务能合并为 fullstack 角色；
- 标准前后端任务能根据任务图拆分；
- 多微服务任务能按业务或服务边界拆分；
- 高风险任务能增加专项角色；
- 每个角色都有 owned_tasks、write_scope 和启动条件；
- 团队方案能解释拆分和合并理由；
- reviewer/tester 支持延迟启动；
- 不存在多个 Agent 未协调修改同一文件；
- 新增动态团队 eval 全部有明确 evidence；
- 旧的固定四人/五人默认描述已经删除或降级为示例模板。

完成后向用户报告：
1. 修改文件；
2. 新的团队生成算法；
3. 与旧固定团队逻辑的差异；
4. eval 结果；
5. 尚未覆盖的边界和风险。
```

---

# 二、整改设计规范

## 1. 设计目标

旧逻辑是：

```text
选择固定角色
  → 启动所有角色
  → 等待需求
  → leader 给角色分配任务
```

目标逻辑是：

```text
理解需求
  → 构建任务图
  → 判断哪些任务适合合并或并行
  → 从任务能力和边界推导角色
  → 启动最小可行团队
  → 随任务阶段动态扩缩
```

核心原则：

> 角色是任务图的执行视图，不是团队设计的起点。

## 2. 两阶段组队与人数确定时序

### 2.1 强制时序

正式团队人数不得在理解项目方向之前确定。采用以下两阶段模型：

```text
阶段一：Pre-team（侦察与规划）
  主线程或一个 planning-leader
  → 理解用户目标和项目方向
  → 探测项目结构
  → 生成 Requirement Brief
  → 建立初始任务图
  → 判断并行任务簇、写入范围和风险

阶段二：Execution Team（正式执行团队）
  根据初始任务图确定人数和角色
  → 启动当前阶段必需 Agent
  → 按任务图执行
  → 随任务图变化动态扩缩
```

在 Pre-team 阶段，不得为了“先把团队准备好”而启动候选执行角色。此时最多只能存在：

- 当前主线程；或
- 当前主线程加一个 `planning-leader`。

前端、后端、fullstack、tester、reviewer、DBA、DevOps 和安全等角色，必须在任务图提供足够依据后才可以启动。

### 2.2 主线程与 planning-leader 的选择

默认由主线程完成前置分析，只有满足以下任一条件时才建议启动 `planning-leader`：

- 项目规模较大，涉及多个模块或服务；
- 项目陌生，现有上下文不足；
- 用户需求包含多个交付阶段；
- 存在明显的安全、数据迁移、部署或跨系统风险；
- 主线程需要在继续与用户沟通的同时，让独立 Agent 深入探测项目；
- 预计任务图包含多个依赖层级，需要专门维护。

以下情况不应启动 `planning-leader`：

- 单文件或一步修改；
- 项目结构简单且需求明确；
- 主线程能在短时间内完成探测；
- 创建额外 Agent 不会带来新的分析价值。

`planning-leader` 的初始任务不是开发，而是输出：

```text
1. Project Direction Brief
2. Requirement Brief
3. Initial Task Graph
4. Risk Register
5. Dynamic Team Proposal
```

规划完成后，`planning-leader` 可以直接转为正式 leader。不要停止后再创建另一个重复 leader。

### 2.3 团队设计最低充分信息

决定正式人数前，至少必须掌握以下信息：

```yaml
team_design_readiness:
  project_goal: 项目或本次需求要解决什么问题
  deliverables: 本次必须产生哪些交付物
  affected_domains: 涉及哪些业务域、模块或服务
  technical_surfaces: 是否涉及前端、后端、数据、部署、安全等
  major_dependencies: 主要任务依赖和不可并行部分
  risk_areas: 安全、迁移、性能、兼容性等风险
  probable_write_scopes: 预计修改的目录、模块和公共文件
  acceptance_criteria: 可验证的主要完成条件
```

如果上述信息仍缺失到无法判断任务边界，应继续探测或向用户提出必要问题，不能通过套用固定团队模板弥补信息不足。

达到最低充分信息不等于读完整个仓库。前置分析只需足以：

- 确定任务的主要边界；
- 识别关键依赖；
- 判断能否安全并行；
- 判断是否需要专项能力；
- 形成第一版团队方案。

更深入的实现细节由正式执行角色按各自任务继续分析。

### 2.4 正式团队人数推导

人数由当前阶段可独立执行的任务簇推导，而不是由技术栈数量推导：

```text
初始执行人数
≈ 当前阶段可并行任务簇数量
+ 必要的独立质量或专项职责
```

该公式不是机械计数，还必须受以下条件约束：

- 每个角色有足够且明确的工作量；
- 每个角色有独立交付物和验收标准；
- 写入范围可以隔离或指定唯一 owner；
- 角色之间不会因未冻结契约而长期等待；
- 并行确实能够缩短关键路径；
- 协调成本低于并行收益；
- 不超过当前环境的可用并发数量。

如果三个任务属于同一强依赖链，当前并发宽度仍可能只有一，不应因此创建三个同时等待的 Agent。

### 2.5 人数不是一次性永久确定

初始任务图只能决定第一版执行团队。运行过程中必须支持：

#### 扩容条件

- 新增独立业务域、模块或服务；
- 关键路径出现可独立并行的大任务；
- 新增数据库迁移、部署、安全或性能专项工作；
- 某角色负载明显超过其他角色；
- 新任务拥有独立写入范围和稳定契约。

#### 缩容或退场条件

- 角色负责的任务全部 accepted；
- 后续任务不再需要该能力；
- 原本可并行的任务转为强依赖；
- 角色长期处于等待状态且没有独立工作；
- 协调成本开始高于并行收益。

#### 合并或替换条件

- 两个角色频繁修改相同文件；
- 契约不稳定导致持续来回沟通；
- 某角色失败或无法继续；
- 任务范围缩小后不再支持独立角色；
- 新专项角色更适合接管后续任务。

团队变化必须更新：

- Task Graph；
- Role Candidate；
- Team Proposal 或 TEAM_STATE；
- owned tasks；
- write scope；
- handoff 信息。

## 3. 为什么需要先构建任务图

只根据“这是一个 Web 项目”生成前端和后端角色，无法回答：

- 前后端工作量是否足以拆成两个 Agent；
- 后端是否跨多个微服务；
- 是否存在数据库迁移；
- 是否需要部署和安全专项；
- 哪些任务可以并行；
- 哪些文件会发生写入冲突；
- tester 和 reviewer 何时真正有工作；
- 哪个任务位于关键路径。

任务图应先暴露这些事实，团队结构再据此生成。

## 4. Task Graph schema

建议新增 `references/task-graph-schema.md`。

```yaml
task_graph:
  version: 1
  requirement_id: REQ-001
  tasks:
    - task_id: ARCH-001
      title: 定义运单接口契约
      domain: waybill
      task_type: design
      inputs:
        - requirements/waybill.md
      outputs:
        - docs/api/waybill-contract.yaml
      acceptance_criteria:
        - AC-001
        - AC-002
      depends_on: []
      read_scope:
        - docs/**
        - backend/waybill/**
        - frontend/src/api/**
      write_scope:
        - docs/api/waybill-contract.yaml
      required_capabilities:
        - api-design
        - frontend-integration-awareness
        - backend-domain-awareness
      risk:
        level: medium
        reasons:
          - 前后端公共契约
      estimated_effort: medium
      estimated_parallel_value: low
      status: ready
```

字段含义：

| 字段 | 用途 |
|---|---|
| `task_id` | 唯一标识和状态关联 |
| `domain` | 业务域或模块 |
| `task_type` | design、frontend、backend、data、test、review、deploy 等 |
| `inputs` | 开始任务所需输入 |
| `outputs` | 明确交付物 |
| `acceptance_criteria` | 任务要满足的 AC |
| `depends_on` | 依赖关系 |
| `read_scope` | 可读取的主要范围 |
| `write_scope` | 允许修改的范围 |
| `required_capabilities` | 推导角色的主要依据 |
| `risk` | 是否需要专项角色或额外门禁 |
| `estimated_effort` | 是否值得单独分配 Agent |
| `estimated_parallel_value` | 独立执行是否能缩短关键路径 |

## 5. 任务图构建步骤

leader 或主线程按以下顺序构建初始任务图：

1. 从用户需求提取业务目标和验收标准；
2. 检查项目目录、模块和技术栈；
3. 识别必要交付物；
4. 将交付物分解为可验证任务；
5. 为任务填写依赖关系；
6. 为任务声明读写范围；
7. 标注安全、数据、部署和兼容性风险；
8. 识别关键路径；
9. 判断哪些任务当前信息不足；
10. 再进入角色生成阶段。

禁止直接用下面的映射替代任务分析：

```text
.vue → frontend-dev
.java → backend-dev
test → tester
```

文件类型只能作为辅助证据，不能成为角色生成的唯一依据。

---

# 三、动态角色生成算法

## 1. 能力提取

从每个任务的 `required_capabilities` 汇总能力需求，例如：

```text
api-design
vue-component-development
spring-service-development
database-migration
integration-testing
security-review
deployment
```

## 2. 任务聚类

按照以下优先级聚类：

1. 相同业务域；
2. 相同或高度重叠的写入范围；
3. 强依赖、需要频繁协商；
4. 相近能力；
5. 能形成独立交付物；
6. 并行是否真正缩短关键路径。

聚类目标是：

```text
高内聚
+ 低跨角色沟通
+ 低文件冲突
+ 可验证的独立产出
```

## 3. 角色合并评分

满足以下情况时优先合并到一个角色：

- 任务总工作量较小；
- 前后端修改都集中在同一小功能；
- 任务强依赖，必须频繁来回确认；
- 写入范围重叠明显；
- API 契约尚未稳定；
- 拆分后一个 Agent 大量等待另一个 Agent；
- 协调成本高于并行收益。

示例：

```text
新增一个简单设置项：
- 前端增加一个开关
- 后端增加一个字段和保存接口
- 无复杂权限、迁移或外部依赖

推荐：
leader + settings-fullstack-dev

不推荐：
leader + frontend-dev + backend-dev + tester + reviewer 全部立即启动
```

## 4. 角色拆分评分

满足以下情况时可拆为独立角色：

- 每部分都有明确交付物；
- 写入范围基本不重叠；
- 输入输出可以通过稳定契约表达；
- 各部分有足够工作量；
- 并行能够缩短关键路径；
- 其中一部分需要明显不同的专业能力；
- 风险要求独立复核或职责分离。

示例：

```text
运单模块：
- 复杂列表和编辑页面
- 新增独立后端服务
- 数据库表和索引迁移
- 多状态业务规则

推荐候选：
- waybill-ui-dev
- waybill-service-dev
- waybill-migration-specialist
- waybill-tester（阶段性）
- reviewer（review-ready 时启动）
```

## 5. 冲突检查

生成团队前必须检查任意两个角色的 `write_scope`：

```text
如果写入范围明显重叠：
1. 尝试细化文件 ownership；
2. 指定唯一公共文件 owner；
3. 如果无法安全拆分，则合并角色；
4. 不得直接让两个 Agent 并行修改。
```

公共文件示例：

- OpenAPI 文档；
- 根级依赖锁文件；
- 全局路由；
- 数据库公共迁移入口；
- 公共权限定义；
- 项目构建配置。

## 6. 并行价值判断

角色拆分前回答：

1. 两个任务是否可以同时开始？
2. 是否存在未冻结的共享契约？
3. 是否频繁修改相同文件？
4. 单独执行能否缩短关键路径？
5. 每个 Agent 是否有足够独立工作量？
6. 新增一个 Agent 的沟通成本是否可接受？

如果多数答案是否定的，应合并角色。

---

# 四、Role Candidate schema

建议新增 `references/dynamic-team-selection.md`。

```yaml
role_candidates:
  - role_id: waybill-service-dev
    display_name: 运单服务开发
    mission: 完成运单领域后端服务、数据访问和接口实现
    owned_tasks:
      - BE-001
      - BE-002
    capabilities:
      - spring-service-development
      - api-implementation
      - transaction-design
    read_scope:
      - docs/api/**
      - backend/common/**
      - backend/waybill/**
    write_scope:
      - backend/waybill/**
    dependencies:
      - ARCH-001
    activation:
      when: ARCH-001 accepted
    deactivation:
      when: BE-001 and BE-002 accepted
    split_reason: 后端任务工作量充分，且与前端通过冻结契约隔离
```

必须包含：

- 角色使命；
- 负责的任务 ID；
- 所需能力；
- 读写范围；
- 依赖；
- 启动条件；
- 结束条件；
- 合并或拆分理由。

角色名应反映任务边界，避免：

```text
developer-1
developer-2
backend-dev-2
```

推荐：

```text
waybill-ui-dev
customer-service-dev
auth-integration-dev
migration-specialist
release-engineer
```

---

# 五、角色生命周期

建议新增 `references/role-lifecycle.md`。

## 1. 角色状态

```text
planned
→ ready
→ active
→ waiting
→ completed
→ retired

异常状态：
blocked
failed
replaced
```

## 2. 延迟启动

不是所有角色都在团队建立时启动。

### tester

可分两个阶段：

- Requirement Brief 完成后：审查 AC 和制定测试计划；
- 出现 `test-ready` 任务后：执行测试和缺陷回流。

### reviewer

启动条件：

```text
存在 review-ready 任务
或高风险设计需要设计审查
```

### DBA / migration-specialist

启动条件：

```text
任务图包含 schema、SQL、索引、批量数据、迁移或回滚任务
```

### DevOps / release-engineer

启动条件：

```text
任务图包含构建、部署、环境、CI/CD、容器或发布任务
```

### security-reviewer

启动条件：

```text
涉及认证、授权、密钥、敏感数据、用户输入或外部访问
```

## 3. 角色退场

角色负责的任务全部 accepted，且没有待答复问题、审查遗留或交接事项时，可以：

- 标记 completed；
- 输出 Handoff Brief；
- 退出活跃团队；
- 保留状态供会话恢复。

---

# 六、团队方案输出格式

建议新增 `assets/TEAM_PROPOSAL.template.md`。

```markdown
# 动态团队方案

## 一、需求和任务图摘要

| 任务 | 交付物 | 依赖 | 风险 | 是否可并行 |

## 二、建议团队

| 角色 | 负责任务 | 写入范围 | 启动时机 | 结束条件 |

## 三、拆分和合并理由

- 为什么使用 fullstack，而不是前后端两个角色；
- 为什么某个微服务需要独立角色；
- 为什么 reviewer/tester 延迟启动；
- 为什么没有增加 DBA/DevOps/安全角色。

## 四、并行关系

说明哪些任务并行、哪些任务需要等待。

## 五、文件冲突控制

列出公共文件 owner 和潜在冲突。

## 六、风险与可调整项

列出用户可以调整的团队配置。
```

不要只输出角色名单。团队方案必须让用户能理解：

- 角色为什么存在；
- 它对应哪些任务；
- 并行收益是什么；
- 风险在哪里。

---

# 七、典型决策示例

## 示例 1：简单文档修改

需求：

```text
修正 README 中两个错误，并补一条启动命令。
```

任务图：

- DOC-001：修改 README。

团队：

```text
单 Agent
```

理由：

- 单文件；
- 无并行价值；
- 无需 tester/reviewer 独立角色。

## 示例 2：小型 CRUD

需求：

```text
新增商品分类，包含简单列表、编辑表单和 CRUD API。
```

假设：

- 项目已有成熟 CRUD 模式；
- 前后端改动量均较小；
- 无复杂权限和迁移。

团队：

```text
leader
category-fullstack-dev
reviewer（最终延迟启动）
tester（根据风险由 leader 或独立角色执行）
```

理由：

- 前后端任务围绕单一功能；
- 契约简单；
- 分为两个 Agent 会增加协调成本。

## 示例 3：标准管理后台模块

需求：

```text
新增运单管理，包括复杂筛选、分页、状态操作、权限和多个后端接口。
```

团队：

```text
leader
waybill-ui-dev
waybill-service-dev
waybill-tester（契约完成后启动）
reviewer（代码可审查时启动）
```

理由：

- UI 和服务端都有充分工作量；
- 可通过冻结 API 契约隔离；
- 测试包含状态机和权限边界；
- 适合并行。

## 示例 4：多微服务需求

需求：

```text
客户冻结后，禁止新建运单，并通知运输系统取消未开始任务。
```

可能团队：

```text
leader
customer-domain-dev
waybill-domain-dev
transport-integration-dev
cross-service-tester
reviewer
```

不得简单生成：

```text
frontend-dev
backend-dev
```

原因：

- 核心复杂性来自跨服务业务一致性；
- 业务边界比技术层边界更重要。

## 示例 5：数据库迁移

需求：

```text
将历史订单状态迁移到新状态机，并保证可回滚。
```

团队：

```text
leader
order-domain-dev
migration-specialist
data-validation-tester
reviewer
```

必须包含任务：

- 备份；
- 迁移脚本；
- dry-run；
- 数据核对；
- 回滚；
- 性能评估。

## 示例 6：认证与权限

需求：

```text
增加多租户权限隔离和管理员跨租户查看能力。
```

团队可能包含：

```text
leader
authorization-service-dev
admin-ui-dev
security-reviewer
authorization-tester
```

权限模型和安全边界不得由普通开发 Agent 使用未经记录的默认假设。

---

# 八、需要修改的现有逻辑

## 1. `SKILL.md`

删除或降级：

- 固定默认四人/五人团队；
- 无条件展示固定团队让用户增删；
- 所有角色统一“确认就位，等待分配”；
- 团队创建时一次启动全部角色；
- 用前端/后端技术层作为唯一角色边界。

新增：

- 任务规模判断；
- Requirement Brief；
- Task Graph；
- 动态角色生成；
- 团队方案解释；
- 阶段性启动；
- 单 Agent 降级；
- 团队动态扩缩。

## 2. `references/context-contract.md`

从固定角色切片改为：

```text
依据 Role Candidate 的 owned_tasks、capabilities、read_scope 生成上下文切片。
```

同一个项目中，不同任务产生的角色可能不同，因此上下文合约必须支持动态角色 ID。

## 3. `references/five-element-prompt.md`

在角色 prompt 中新增：

- owned task IDs；
- write scope；
- dependencies；
- activation condition；
- Definition of Done；
- 禁止修改范围；
- handoff 对象。

## 4. `references/team-protocol.md`

成员列表由实际活跃角色生成，不再硬编码前端、后端、测试、reviewer。

状态查询应区分：

- planned；
- active；
- waiting；
- completed；
- retired；
- failed/replaced。

## 5. `references/code-review-protocol.md`

reviewer 不再固定属于初始团队。

审查对象通过任务图确定：

- review-ready 任务；
- 变更文件；
- 风险等级；
- 上轮遗留问题。

## 6. eval

旧 eval 如果硬编码固定四人团队，应重写或保留为“标准 Web 模板”测试，不得继续作为通用正确性标准。

---

# 九、静态检查和评测

## 1. 静态一致性检查

整改后执行搜索，检查是否仍有冲突：

```text
默认四人
默认五人
固定前端
固定后端
一次启动所有角色
初始任务统一为确认就位
```

允许这些词出现在：

- 历史说明；
- 反例；
- 标准 Web 示例。

不得继续作为通用执行规则。

## 2. 动态团队 eval

建议新增 `evals/dynamic-team-evals.json`。

至少包含：

### Eval 1：单文件小任务

期望：

- 不创建完整团队；
- 使用单 Agent；
- 说明无并行价值。

### Eval 2：小型前后端 CRUD

期望：

- 优先考虑 fullstack；
- 不无条件拆为前后端；
- tester/reviewer 延迟启动。

### Eval 3：标准前后端模块

期望：

- 基于任务图拆为 UI 和服务角色；
- 有冻结契约；
- write scope 不重叠。

### Eval 4：多微服务

期望：

- 按业务或服务边界拆分；
- 不用一个 backend-dev 包办全部；
- 有跨服务测试角色。

### Eval 5：数据迁移

期望：

- 包含 migration/DBA 能力；
- 有备份、验证和回滚任务。

### Eval 6：权限安全

期望：

- 增加安全审查；
- 高风险问题要求用户决策。

### Eval 7：高文件冲突

期望：

- 合并角色或重新划分 ownership；
- 不允许两个 Agent 无协调并行修改。

### Eval 8：任务中途扩张

期望：

- 更新任务图；
- 新增角色而不是重建全部团队；
- 给新角色生成上下文和 Handoff Brief。

## 3. 关键断言

每个 eval 应检查：

- 是否先生成任务图；
- 角色是否能追溯到任务；
- 是否声明 owned_tasks；
- 是否声明 write_scope；
- 是否说明合并/拆分理由；
- 是否计算并行价值；
- 是否识别冲突；
- 是否支持延迟启动；
- 是否存在不必要角色；
- 团队是否为当前任务的最小可行配置。

---

# 十、整改完成标准

只有全部满足，才可宣布本需求完成：

- [ ] `SKILL.md` 不再以固定前后端团队作为通用默认
- [ ] 已明确采用 Pre-team 与 Execution Team 两阶段组队
- [ ] 项目方向不明时只使用主线程或一个 planning-leader
- [ ] 已定义何时由主线程分析、何时启动 planning-leader
- [ ] planning-leader 可以无缝转为正式 leader
- [ ] 已定义决定正式人数前的团队设计最低充分信息
- [ ] 团队生成发生在 Requirement Brief 和任务图之后
- [ ] 正式人数按当前可并行任务簇和必要专项职责推导
- [ ] 人数推导受工作量、依赖、写入范围、协调成本和并发上限约束
- [ ] 已定义 Task Graph schema
- [ ] 已定义 Role Candidate schema
- [ ] 已定义任务聚类规则
- [ ] 已定义角色合并规则
- [ ] 已定义角色拆分规则
- [ ] 已定义文件冲突检查
- [ ] 已定义并行价值判断
- [ ] 已定义阶段性角色生命周期
- [ ] 简单任务可以降级为单 Agent
- [ ] 小型跨层任务可以合并为 fullstack
- [ ] 多微服务可以按业务边界拆分
- [ ] 高风险任务可以增加专项角色
- [ ] 每个角色都有 owned_tasks 和 write_scope
- [ ] 每个团队方案都解释拆分和合并理由
- [ ] tester/reviewer 不必在开始时启动
- [ ] 新角色可以在任务中途加入
- [ ] 已有角色可以在完成后退场
- [ ] 任务图变化时可以扩容、缩容、合并或替换角色
- [ ] 动态团队 eval 已创建并验证
- [ ] 所有通过断言都有 evidence

## 最终判断原则

```text
角色数量多，不代表协作能力强。
角色与技术层一一对应，不代表分工合理。
只有当任务边界清晰、写入范围独立、依赖可以隔离、
并行能够缩短关键路径时，创建额外 Agent 才是有价值的。
```
