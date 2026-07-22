# Current Task — ynwl

**最后更新**: 2026-07-22 01:00 +08:00 by Claude (Opus 4.8)

## 当前阶段

✅ 项目架构分析、zsh 记忆构建、团队组建、ct1 skill 创建与 eval 均已完成。

## 已完成

- [x] 识别 `ynwl_front/` Vue 2 前端架构、入口、路由、状态管理、API 层与开发代理。
- [x] 识别 `ynwl_back/` BladeX/Spring Cloud Maven 多模块架构、服务入口与基础拓扑。
- [x] 初始化 zsh 导航、项目记忆、任务、日志、决策与归档索引。
- [x] 将架构事实、风险、待验证项及接手入口写入 `PROJECT_MEMORY.md`。
- [x] 组建四人团队（leader / frontend-dev / backend-dev / qa-engineer），建立协作协议与进度查询机制。
- [x] 解决 tester 名字被 harness 残留注册问题：停止 tester-2，改用干净名字 `qa-engineer` 重建测试角色。
- [x] 部署进度查询协议到 `skill-docs/TEAM_PROTOCOL.md` 并挂载 `AGENT_MEMORY.md` 导航。
- [x] 创建 `ct1` skill（全局安装于 `~/.claude/skills/ct1/`）：可复用多人 Agent 团队组建 + 进度查询机制，默认四人配置，支持自定义角色/人数，宽泛触发（中英文）。
- [x] 对 ct1 执行完整 eval（6/6 run）：with-skill 平均 95.8% vs baseline 63.1%（+32.7%）。
- [x] 根据 eval 结果改进 ct1：增加 flat-roster 回退指引、协议文件双写 + 并发处理。
- [x] 同步 ct1 skill 及相关记忆到 `D:/claudeCode/skills/my-skills-collect/claude/` 并推送到 origin/main。

## 进行中

- 无。

## 待开始

- 按用户后续目标选择：本地启动验证、模块级深挖、数据模型分析、安全整改或技术栈升级评估。

## 关键文件状态

| 文件 | 状态 | 说明 |
|---|---|---|
| `AGENT_MEMORY.md` | ✅ | zsh 唯一导航入口（含 TEAM_PROTOCOL.md 导航行） |
| `skill-docs/PROJECT_MEMORY.md` | ✅ | 已记录架构与风险 |
| `skill-docs/CURRENT_TASK.md` | ✅ | 本文件 |
| `skill-docs/SESSION_LOG.md` | ✅ | 已记录本次分析、团队组建、ct1 创建与 eval |
| `skill-docs/DECISIONS.md` | ✅ | zsh 初始化决策 |
| `skill-docs/TEAM_PROTOCOL.md` | ✅ | 进度查询协议（默认四人，6 字段模板） |
| `CLAUDE.md` | ✅ | zsh 托管适配区块 |
| `~/.claude/skills/ct1/` | ✅ | ct1 skill（SKILL.md + references/ + evals/） |
| `D:/claudeCode/skills/my-skills-collect/claude/ct1/` | ✅ | ct1 skill 同步副本（已推送） |

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

- 文件：`skill-docs/PROJECT_MEMORY.md`
- 位置：温记忆 → "待验证"
- 状态：静态架构基线 + 团队 + ct1 已完成；后续可逐项进行运行时验证。

## 下次会话建议

1. 先读取 `AGENT_MEMORY.md` 与本文件。
2. 团队已就绪，可直接对 leader 提出开发需求。
3. 根据用户目标选择一个子系统，验证其构建、配置来源和运行调用链。
