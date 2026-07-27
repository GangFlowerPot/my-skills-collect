# Task Board Schema（任务板）

## 是什么

leader 通过聊天分配任务的替代——统一的任务状态、依赖、责任人和验收证据。leader 可从任务板生成进度，不依赖聊天记忆；会话恢复后可继续任务。

## 任务 schema

```yaml
id: BE-003
title: 实现创建运单接口
owner: backend-dev
status: in_progress
priority: high
risk: medium
depends_on:
  - ARCH-001
acceptance_criteria:
  - AC-003
write_scope:
  - backend/waybill/**
artifacts:
  - WaybillController.java
verification:
  - command: mvn test -pl waybill
handoff_to:
  - reviewer
  - tester
```

### 字段含义

| 字段 | 用途 |
|---|---|
| `id` | 唯一标识（格式：`{域}-{序号}`，如 `BE-003`、`FE-001`、`ARCH-001`） |
| `title` | 一句话描述 |
| `owner` | 负责角色（必须唯一） |
| `status` | 当前状态（见状态机） |
| `priority` | high / medium / low |
| `risk` | high / medium / low |
| `depends_on` | 依赖的任务 ID 列表 |
| `acceptance_criteria` | 关联的 AC ID 列表 |
| `write_scope` | 允许修改的路径范围 |
| `artifacts` | 交付物文件列表 |
| `verification` | 验证命令与预期结果 |
| `handoff_to` | 完成后移交的角色 |

## 状态机

```
backlog
  → ready
  → in_progress
  → review
  → test
  → accepted
  → delivered

任意非终态均可进入 blocked。
```

### 状态约束

| 进入条件 | 要求 |
|---|---|
| `ready` | 依赖已完成 |
| `in_progress` | 有 owner |
| `review` | 开发自测完成 |
| `test` | 严重审查问题为零 |
| `accepted` | 有验证证据 |
| `delivered` | 满足项目级 DoD |

## 任务图构建步骤

1. 从用户需求提取业务目标和验收标准
2. 检查项目目录、模块和技术栈
3. 识别必要交付物
4. 将交付物分解为可验证任务
5. 为任务填写依赖关系
6. 为任务声明读写范围
7. 标注安全、数据、部署和兼容性风险
8. 识别关键路径
9. 判断哪些任务当前信息不足
10. 再进入角色生成阶段

> 禁止直接用 `.vue` → frontend-dev、`.java` → backend-dev 的映射替代任务分析。文件类型只能作为辅助证据。

## 与 StatusReport/v2 的关系

StatusReport/v2 的【任务ID】字段关联本任务板。执行者报告状态时，通过 task_id 追溯到具体任务及其 AC、write_scope。

## 模板

完整模板见 `assets/TASK_BOARD.template.md`。
