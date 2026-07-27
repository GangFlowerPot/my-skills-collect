# Question Escalation 完整工作示例

> 本文件是 `references/question-escalation-protocol.md` 的配套示例，展示问题升级循环的完整流程。

**场景**：frontend-dev 在 review_ready 遇到 2 个问题，backend-dev 在 review_ready 遇到 1 个问题。

## 1. 子 agent 内部问题清单

**frontend-dev 的 question_log**（review_ready 检查点触发后）：

```
Q-FE-001 | review_ready | user-required | 是否采用方案A（JWT+refresh token）或方案B（session）实现登录态？
       | 关联任务: 前端登录模块 | 状态: 已上报
Q-FE-002 | review_ready | leader-decidable | 表单验证错误提示文案是否沿用旧版？
       | 关联任务: 前端登录模块 | 状态: 已上报
```

**backend-dev 的 question_log**（review_ready 检查点触发后）：

```
Q-BE-001 | review_ready | user-required | 用户表是否需要新增 last_login 字段？
       | 关联任务: 后端用户模块 | 状态: 已上报
```

## 2. 用户说「进度」，leader 发送状态查询，收到回复

**frontend-dev 回复**：

```
【协议版本】StatusReport/v2
【任务ID】FE-001
【状态】工作中
【当前任务】前端登录模块开发
【进展】完成页面骨架与状态管理
【阻塞项】无
【下一步】等待答复后决定登录态实现方案，继续实现登录表单
【需要的输入】无
【触发事件】review_ready
【待答复问题】
1. [Q-FE-001][review_ready] 是否采用方案A（JWT+refresh token）或方案B（session）实现登录态？ (关联任务: 前端登录模块)
2. [Q-FE-002][review_ready] 表单验证错误提示文案是否沿用旧版？ (关联任务: 前端登录模块)
【变更文件】
- src/components/LoginForm.vue（新增）
- src/store/user.js（修改）
【验证结果】未执行
```

**backend-dev 回复**：

```
【协议版本】StatusReport/v2
【任务ID】BE-001
【状态】工作中
【当前任务】后端用户模块开发
【进展】完成数据库连接与用户表基础字段设计
【阻塞项】无
【下一步】等待答复后决定是否新增 last_login 字段
【需要的输入】无
【触发事件】review_ready
【待答复问题】
1. [Q-BE-001][review_ready] 用户表是否需要新增 last_login 字段？ (关联任务: 后端用户模块)
【变更文件】
- src/controllers/UserController.java（修改）
【验证结果】未执行
```

## 3. leader 聚合后展示给用户

```
📊 团队进度报告 · 2026-07-23 10:30

## 一、进度总览
| 角色 | 状态 | 任务ID | 当前任务 | 进展 | 阻塞项 | 下一步 | 触发事件 | 待答复问题 | 变更文件 | 验证结果 |
|------|------|--------|----------|------|--------|--------|----------|------------|----------|----------|
| frontend-dev | 工作中 | FE-001 | 前端登录模块 | 完成页面骨架 | 无 | 实现登录表单 | review_ready | 2 题 | 2 文件 | 未执行 |
| backend-dev | 工作中 | BE-001 | 后端用户模块 | 完成表设计 | 无 | 决定 last_login | review_ready | 1 题 | 1 文件 | 未执行 |
| tester | 空闲 | — | — | — | 无 | 编写测试计划 | 无 | 无 | 无 | 未执行 |

## 二、待答复问题（共 3 题）
| 编号 | 来源 | 触发事件 | 决策等级 | 问题 | 关联任务 | 提出次数 |
|------|------|----------|----------|------|----------|----------|
| Q-FE-001 | frontend-dev | review_ready | user-required | 是否采用方案A（JWT）或方案B（session）实现登录态？ | 前端登录模块 | 1 |
| Q-FE-002 | frontend-dev | review_ready | leader-decidable | 表单验证错误提示文案是否沿用旧版？ | 前端登录模块 | 1 |
| Q-BE-001 | backend-dev | review_ready | user-required | 用户表是否需要新增 last_login 字段？ | 后端用户模块 | 1 |

请回答上述问题。可部分回答，格式如「Q-FE-001: 方案A」；跳过的题目将保留至下次询问。
```

## 4. 用户回答（跳过 Q-FE-002）

```
Q-FE-001: 方案A
Q-BE-001: 需要新增
```

## 5. leader 分发答复

**发给 frontend-dev**：

```
[CONTEXT ADDENDUM]
来源：用户答复
答复时间：2026-07-23T10:32:00
答复项：
  1. 问题ID: Q-FE-001 | 答复: 方案A（JWT+refresh token） | 对原有上下文的变更: 新增
未答复（用户跳过，请自行裁决或继续等待）: Q-FE-002
```

**发给 backend-dev**：

```
[CONTEXT ADDENDUM]
来源：用户答复
答复时间：2026-07-23T10:32:00
答复项：
  1. 问题ID: Q-BE-001 | 答复: 需要新增 last_login 字段 | 对原有上下文的变更: 新增
未答复（用户跳过，请自行裁决或继续等待）: 无
```

## 6. 子 agent 处理结果

**frontend-dev**：
- `Q-FE-001` → `status = 已答复`，`answer = "方案A（JWT+refresh token）"`。采用方案 A，继续工作。
- `Q-FE-002` → 未答复 → 采用默认值（沿用旧版文案），`status = 已作废`，`void_reason = 自行裁决`。
- 整体继续工作，不暂停。

**backend-dev**：
- `Q-BE-001` → `status = 已答复`，`answer = "需要新增 last_login 字段"`。新增字段，继续工作。
