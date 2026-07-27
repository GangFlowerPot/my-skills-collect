# Current Task — ynwl

**最后更新**: 2026-07-27 13:30 +08:00 by Claude (Opus 4.8)

## 当前阶段

✅ 项目架构分析、zsh 记忆构建、团队组建、ct1 skill 创建与 eval、子 Agent 上下文灌输机制设计与实现、问题升级循环设计与实现、**Reviewer 角色 + 代码审查循环设计与实现**均已完成。✅ **zsh 记忆架构从旧布局整改到最新 `zsh/` 布局**已完成。✅ **ct1 skill 全生命周期重构 Iteration 1~5 全部完成**。✅ **ct1 下一轮优化（协议收敛/Python 3 基线/结构化状态/真实门禁）Iteration A~E 全部完成**。

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

## 精确续接位置

- 文件：本文件 + `zsh/AGENT_MEMORY.md` + `SKILL.md` + `improve/NEXT_ROUND_OPTIMIZATION_PLAN.md`
- 位置：ct1 下一轮优化 Iteration A~E 全部完成；可按文档第 11 节最终验收清单逐项核验
- 状态：协议收敛、Python 3 基线、结构化状态、真实门禁、评估体系全部就绪

## 下次会话建议

1. 先读取 `AGENT_MEMORY.md` 与本文件。
2. 若要验证两大机制：选一个真实项目，准备结构化文档，建立合约后 spawn 子 agent，在 33% 节点触发问题升级循环，观察全流程。
3. 团队已就绪，可直接对 leader 提出开发需求。
4. 根据用户目标选择一个子系统，验证其构建、配置来源和运行调用链。
