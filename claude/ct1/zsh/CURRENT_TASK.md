# Current Task — ynwl

**最后更新**: 2026-07-31 15:20 +08:00 by Claude (Opus 4.8)

## 当前阶段

✅ 项目架构分析、zsh 记忆构建、团队组建、ct1 skill 创建与 eval、子 Agent 上下文灌输机制设计与实现、问题升级循环设计与实现、**Reviewer 角色 + 代码审查循环设计与实现**均已完成。✅ **zsh 记忆架构从旧布局整改到最新 `zsh/` 布局**已完成。✅ **ct1 skill 全生命周期重构 Iteration 1~5 全部完成**。✅ **ct1 下一轮优化（协议收敛/Python 3 基线/结构化状态/真实门禁）Iteration A~E 全部完成**。✅ **ct1 交付模式门禁优化（Step 3.75 硬门 + Node A/B/C 功能里程碑）完成并推送**。✅ **项目根 CLAUDE.md 路径示例修正 + docs/ 过时 v3 快照清理完成并推送**。✅ **ct1 产品可用性门禁（用户旅程 + 冷启动走查 + 交付硬门）完成，待推送**。

## 已完成

- [x] 识别 `ynwl_front/` Vue 2 前端架构、入口、路由、状态管理、API 层与开发代理。
- [x] 识别 `ynwl_back/` BladeX/Spring Cloud Maven 多模块架构、服务入口与基础拓扑。
- [x] 初始化 zsh 导航、项目记忆、任务、日志、决策与归档索引。
- [x] 将架构事实、风险、待验证项及接手入口写入 `PROJECT_MEMORY.md`。
- [x] 组建四人团队（leader / frontend-dev / backend-dev / qa-engineer），建立协作协议与进度查询机制。
- [x] 解决 tester 名字被 harness 残留注册问题：停止 tester-2，改用干净名字 `qa-engineer` 重建测试角色。
- [x] 部署进度查询协议到 `zsh/TEAM_PROTOCOL.md` 并挂载 `AGENT_MEMORY.md` 导航。
- [x] 创建 `ct1` skill（全局安装于 `~/.claude/skills/ct1/`）：可复用多人 Agent 团队组建 + 进度查询机制，默认四人配置，支持自定义角色/人数，宽泛触发（中英文）。
- [x] 对 ct1 执行完整 eval（6/6 run）：with-skill 平均 95.8% vs baseline 63.1%（+32.7%）。
- [x] 根据 eval 结果改进 ct1：增加 flat-roster 回退指引、协议文件双写 + 并发处理。
- [x] 同步 ct1 skill 及相关记忆到 `D:/claudeCode/skills/my-skills-collect/claude/` 并推送到 origin/main。
- [x] **设计并实现 Reviewer 角色 + 代码审查循环**：
  - 新建 `references/code-review-protocol.md`（314 行）：reviewer 角色定义（十年全栈经验，精通 Java 后端/前端/中间件）、Code Review 报告 schema（严重/建议/需用户决策）、leader 分流规则、三轮循环(33/66/100%)、dev 报告扩展（本轮完成文件）、边界情况、工作示例
  - 扩展 `references/team-protocol.md`（131→156 行）：默认团队加 reviewer；状态模板加【本轮完成文件】字段；reviewer 状态示例
  - 扩展 `references/context-contract.md`：新增 reviewer 切片（架构+规范+审查标准清单）
  - 更新 `references/question-escalation-protocol.md`：补充 reviewer 审查作为问题来源
  - 更新 `SKILL.md`（207→210 行）：默认团队加 reviewer；协作规则摘要+注意事项加审查规则
  - 端到端测试：ynwl 项目演示 33% 审查→分流→修改→66% 再审→100% 终态全链路 + 边界情况
  - 提交并推送到 origin/main（commit a96d4b1，待推送）
- [x] **整改 zsh 记忆架构到最新版本（单 skill 级别，`claude/ct1/`）**：
  - 运行 `detect_project.py` 探测布局（根目录 + `skill-docs/` 旧布局）
  - 执行 `migrate_layout.py --apply`：`AGENT_MEMORY.md`/`CURRENT_TASK.md`/`SESSION_LOG.md` → `zsh/`
  - 手动补建 3 个缺失文件（`PROJECT_MEMORY.md`/`DECISIONS.md`/`memory-archive/INDEX.md` 最小合法空壳）
  - 修正迁移副作用：导航中错误的 `zsh/TEAM_PROTOCOL.md` → `TEAM_PROTOCOL.md`（不属于 zsh，保留根目录）
  - 创建 `CLAUDE.md` ZSH:MEMORY 托管区块
  - 验证：`check_structure.py` 返回 `ok: true`，6 个必需文件全部存在
  - 约束遵守：非 zsh 文件（`SKILL.md`/`references/`/`evals/`/`ct1-workspace/`/`TEAM_PROTOCOL.md` 等）均未改动
- [x] **ct1 skill 全生命周期重构 Iteration 1（一致性修复）**：
  - 新建 `references/status-report-schema.md`（StatusReport/v2，11 字段，唯一真相源）
  - 更新 `SKILL.md`：frontmatter（+delivery 语义 + 负例边界）、运行模式（create-only/delivery）、任务规模判断、两阶段组队（Pre-team/Execution Team）、需求澄清、任务图、动态团队生成、DoD、交付报告、统一团队定义（固定/执行/质量/审查/专项）、model_policy（不绑定具体版本）
  - 更新 `references/team-protocol.md`：引用 StatusReport/v2，默认团队改为动态生成
  - 更新 `references/question-escalation-protocol.md`：不再声称"扩展六字段"，改为引用 StatusReport/v2 的【待答复问题】
  - 更新 `references/code-review-protocol.md`：不再自行扩展字段，审查触发改为事件驱动（review-ready）
  - 更新 `evals/evals.json`：对齐新协议，新增单 Agent 降级 + 动态团队 eval
  - 静态一致性检查通过：skill 运行文件不再有旧的固定团队描述和 6/8/9 字段模板残留
  - 新建 3 个 validation scripts（validate_protocol / validate_task_board / check_delivery_gate）并全部通过
- [x] **ct1 下一轮优化（NEXT_ROUND_OPTIMIZATION_PLAN.md）Iteration A~E**：
  - **Iteration A**（协议清理）：修正 StatusReport 字段数（11→12）、清除百分比流程（33/66/100%→事件驱动）、统一事件名为英文下划线、长示例移入 examples/、建立文档职责矩阵
  - **Iteration B**（Python 3 基线）：新建统一入口 ct1_validate.py、所有脚本增加版本检查、SKILL.md 增加运行依赖章节、明确 Python 3.10+ 和探测策略
  - **Iteration C**（结构化运行状态）：新建 6 个 JSON schemas（task-graph/role-roster/team-state/status-report/test-report/delivery-state）、删除 Skill 目录双写、分离任务状态与项目状态
  - **Iteration D**（真实门禁）：新建 validate_task_graph.py（依赖图/owner/AC/验证证据）和 validate_write_scopes.py（role roster/write scope 冲突）
  - **Iteration E**（评估与回归）：补充 14 个真实运行测试场景（Python 2/3、create-only、多项目隔离等）、新建 complexity-metrics.json
  - 最终静态一致性检查通过：skill 文件无百分比和"11 字段"残留
- [x] **ct1 skill 全生命周期重构 Iteration 2~5**：
  - **Iteration 2**（需求和任务管理）：新建 requirement-brief/task-board-schema/api-contract-protocol 3 个 references + 2 个 templates
  - **Iteration 3**（测试和交付）：新建 testing-gate/delivery-report 2 个 references + 2 个 templates
  - **Iteration 4**（工程可靠性）：新建 workspace-strategy/recovery-protocol/dynamic-team-selection/decision-level/lifecycle/team-selection 6 个 references
  - **Iteration 5**（效率和最终评测）：code-review 风险驱动审查 + 新建 trigger-evals/protocol-evals/delivery-evals 3 个 eval 文件 + 3 个 validation scripts
  - SKILL.md 贯穿 4 个 Iteration 的多处引用与补充
  - 最终静态一致性检查通过
- [x] **项目根 CLAUDE.md 路径示例修正 + docs/ 过时 v3 快照清理**（commit 63aa15c 已推送）：
  - 修正根 `CLAUDE.md` 第 93 行示例路径（`claude/ct1/CURRENT_TASK.md` → `claude/ct1/zsh/CURRENT_TASK.md`），与 ct1 的 ZSH:MEMORY 块一致
  - 行为规则§3 明确"记忆脱水仅适用于采用 zsh 的 skill"，裸文件名加 `zsh/` 前缀
  - 删除 `docs/` 下 4 个过时的集合级 v3 记忆文件（7-21，-519 行）
- [x] **ct1 交付模式门禁优化**（commit 4c948db 已推送）：
  - **解决 P0**：delivery 模式下工作流从需求→设计→组队→编码一口气跑完、无用户检查点
  - 新增 `plan_confirmed` 触发事件（StatusReport 状态加「等待用户确认」）
  - SKILL.md 插入 **Step 3.75 开发计划确认硬门**（团队+计划一次性确认，⏸ 等用户明确确认后才启动 Agent）
  - Step 4 leader prompt 从「请用户提第一个需求」改为「请用户确认开发计划」
  - Step 3 删除「或按安全默认值继续」软门
  - Requirement Brief 增加「技术基线验证」（数据层一致性/环境就绪/凭证方案）
  - decision-level.md 新增「数据层语义冲突」为 user-required
  - Reviewer **功能里程碑 Node A/B/C**（骨架+认证/核心业务交互/最终验收），绑定触发事件（review_ready/review_ready/acceptance_ready，非百分比）
  - 每个功能节点后加**用户业务审查点**（reviewer 不替用户验收业务方向）
  - Agent 只读约束：`plan_confirmed` 前 dev 角色只读（role-roster.schema.json 加 `read_only_until`）
  - 新建 `e2e-test-gates-v2.md` 对齐新门禁（旧 e2e 标注为历史版本）
  - Eval 6 专门测 CP-5 硬门行为
  - 约束遵守：无 33/66/100% 百分比门禁残留，里程碑为事件驱动
- [x] **ct1 产品可用性门禁（用户旅程 + 冷启动走查 + 交付硬门）**（待推送）：
  - **解决 P0**：ct1 优化"任务完成度"而非"用户视角的产品可用性"——团队宣告交付但产品无登录页，从第一步就不可用
  - **根因**：DoD = "AC 清单全部通过"，AC 是功能清单而非用户旅程流；所有下游门禁回溯到 AC 清单，缺第一步时直到人类想用才暴露
  - **4 部分改动（9 文件，+87/-4）**：
    - **Part A** — requirement-brief.md + REQUIREMENT_BRIEF.template.md：新增强制章节「用户旅程」（从冷启动到核心价值的最小可演示路径，有序步骤 + 每步可验证完成准则）；建立步骤插入 4.5；验收标准追加一条
    - **Part B** — testing-gate.md + TEST_REPORT.template.md：tester 职责追加第 8 项「冷启动走查」（干净环境 + fresh user 逐步执行用户旅程）；测试门禁表追加「用户旅程跑通」行；TEST_REPORT 插入「冷启动走查」章节
    - **Part C** — delivery-report.md + SKILL.md + DELIVERY_REPORT.template.md：项目级交付门禁加入「用户旅程跑通（冷启动走查通过）」；交付判定表 `通过` 含跑通、`未通过` 加旅程未跑通；表下加注"旅程跑通是硬门：即使 AC 全通过、P0/P1=0，跑不通→未通过"；SKILL.md DoD bullet + 测试门禁表同步
    - **Part D** — delivery-evals.json 新增 d11（缺登录页反例：AC 全通过但旅程失败→交付=未通过）；evals.json 新增 eval 7（全链路验证：Brief 含旅程→tester 走查→交付硬门→Node A 与旅程门各司其职）
  - **兼容性**：Node A 确认"方向"（骨架+认证），新门验证"可运行实现"；前者需代码存在才触发，后者直接走查产品；各司其职
  - **命名避让**：用「用户旅程/冷启动走查/跑通」，绕开已占用的"端到端/关键路径"
  - **范围遵守**：无新角色、无角色扩责、无 StatusReport/context-contract 改动
  - **验证通过**：JSON 合法、术语一致、无百分比残留、Node A 独立

## 进行中

- 无。

## 待开始

- 在真实项目中实际 spawn 子 agent，验证上下文灌输机制的实际效果（首次输出质量、返工次数、token 消耗）
- 根据真实使用反馈迭代合约 schema / 五要素模板 / 动态补充协议
- 按用户后续目标选择：本地启动验证、模块级深挖、数据模型分析、安全整改或技术栈升级评估

## 关键文件状态

| 文件 | 状态 | 说明 |
|---|---|---|
| `zsh/AGENT_MEMORY.md` | ✅ | zsh 唯一导航入口（路径引用已修正） |
| `zsh/PROJECT_MEMORY.md` | ✅ | 三层记忆空壳（新建） |
| `zsh/CURRENT_TASK.md` | ✅ | 本文件 |
| `zsh/SESSION_LOG.md` | ✅ | 已记录团队组建、ct1 创建/eval、上下文灌输机制 |
| `zsh/DECISIONS.md` | ✅ | ADR 空壳（新建） |
| `zsh/memory-archive/INDEX.md` | ✅ | 归档索引空壳（新建） |
| `TEAM_PROTOCOL.md` | ✅ | 进度查询协议（根目录，不属于 zsh） |
| `CLAUDE.md` | ✅ | zsh 托管适配区块（新建） |
| `~/.claude/skills/ct1/` | ✅ | ct1 skill（SKILL.md + references/ + evals/） |
| `D:/claudeCode/skills/my-skills-collect/claude/ct1/` | ✅ | ct1 skill 同步副本（已推送，含上下文灌输机制） |
| `references/context-contract.md` | ✅ | 上下文合约 schema + ynwl 示例（新增） |
| `references/five-element-prompt.md` | ✅ | 五要素 prompt 模板（新增） |
| `references/dynamic-supplement-protocol.md` | ✅ | 动态补充协议（新增） |
| `references/question-escalation-protocol.md` | ✅ | 问题升级循环协议（新增） |
| `references/code-review-protocol.md` | ✅ | 代码审查协议（新增） |
| `references/team-protocol.md` | ✅ | 6→8 字段模板 + reviewer + leader 聚合格式（扩展） |
| `SKILL.md` | ✅ | Step 1.5 + Step 3 增强 + 问题升级 + reviewer（新增） |
| `references/requirement-brief.md` | ✅ | +用户旅程章节 + 建立步骤 4.5 + 验收标准（产品可用性门禁） |
| `references/testing-gate.md` | ✅ | +tester 职责第 8 项（冷启动走查）+ 门禁表跑通行（产品可用性门禁） |
| `references/delivery-report.md` | ✅ | +用户旅程跑通硬门 + 交付判定表（产品可用性门禁） |
| `assets/REQUIREMENT_BRIEF.template.md` | ✅ | +用户旅程章节（产品可用性门禁） |
| `assets/TEST_REPORT.template.md` | ✅ | +冷启动走查章节（产品可用性门禁） |
| `assets/DELIVERY_REPORT.template.md` | ✅ | +用户旅程跑通章节（产品可用性门禁） |
| `evals/delivery-evals.json` | ✅ | +d11（缺登录页反例） |
| `evals/evals.json` | ✅ | +eval 7（全链路验证） |

## 团队状态

| 成员 | Agent 名 | 状态 |
|---|---|---|
| 统筹领导决策者 | leader | ✅ 空闲待命 |
| 前端开发 | frontend-dev | ✅ 空闲待命 |
| 后端开发 | backend-dev | ✅ 空闲待命 |
| 测试 | qa-engineer | ✅ 空闲待命 |

> 协作规则：默认用户 ↔ leader；出方案时前后端分别出 + 测试出用例由 leader 汇总；需求讨论时用户同时与 leader 和 qa-engineer 沟通。进度查询触发词：进度 / status / progress 等。

## 阻塞项

- 无。完整运行验证需要可用的 JDK 8/Maven、兼容旧版 node-sass 的 Node 环境，以及 Nacos、数据库、Redis 等外部服务配置。

## 待开始

- **善后**：清理 `claude/zsh/` 下 6 个模板残留文件（之前错误迁移的回滚失败产物，与 `claude/ct1/zsh/` 真实记忆内容不同）+ `claude/CLAUDE.md.zsh-backup` 备份文件
- 在真实项目中实际 spawn 子 agent，验证 Step 3.75 硬门 + Node A/B/C 功能里程碑 + **用户旅程跑通硬门**的实际效果（首次输出质量、返工次数、token 消耗）
- 根据真实使用反馈迭代合约 schema / 五要素模板 / 动态补充协议

## 精确续接位置

- 文件：本文件 + `zsh/AGENT_MEMORY.md` + `SKILL.md` + `improve/门禁问题.md` + `references/code-review-protocol.md` §6.1
- 位置：ct1 产品可用性门禁完成（9 文件 +87/-4，待推送）；测试轮次设计（原首要议题，现被产品可用性议题覆盖，仍待讨论）
- 状态：Step 3.75 硬门 + Node A/B/C 功能里程碑 + 用户旅程跑通硬门就绪

## 下次会话建议

1. 先读取 `AGENT_MEMORY.md` 与本文件。
2. 善后：清理 `claude/zsh/` 模板残留 + zsh-backup。
3. 若要验证门禁机制：选一个真实项目，准备结构化文档，建立合约后 spawn 子 agent，在 Step 3.75 节点观察硬门拦截，在 Node A/B/C 观察功能里程碑驱动审查+测试，在交付前观察用户旅程跑通硬门拦截不可用产品。
4. 团队已就绪，可直接对 leader 提出开发需求。
