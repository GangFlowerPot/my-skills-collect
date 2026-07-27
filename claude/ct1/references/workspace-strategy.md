# Workspace Strategy（文件所有权与工作区策略）

## 是什么

多 Agent 并行开发时，明确文件修改范围和公共文件 owner，避免未协调修改同一文件。

## 配置示例

```yaml
workspace_mode: shared
write_scope:
  frontend-dev:
    - frontend/src/**
  backend-dev:
    - backend/**
shared_files:
  owner: leader
  paths:
    - openapi.yaml
    - package-lock.json
```

## 强制规则

| 规则 | 说明 |
|---|---|
| 修改前检查 | 开始修改前检查工作区已有变化 |
| 不覆盖 | 不覆盖用户或其他任务的修改 |
| 声明 write_scope | 每个任务声明 `write_scope` |
| 公共文件 ownership | 修改公共文件前获得 ownership |
| 只读角色 | tester 和 reviewer 默认只读 |
| 中大型项目 | 优先使用独立 worktree 或分支 |
| 合并责任 | 合并由 leader 或 integrator 负责 |
| 冲突处理 | 不允许通过直接覆盖解决冲突 |

## 公共文件示例

- OpenAPI 文档
- 根级依赖锁文件
- 全局路由
- 数据库公共迁移入口
- 公共权限定义
- 项目构建配置

## 验收标准

- 每个变更文件能关联任务和 owner
- 同一文件不会被多个 Agent 无协调修改
- 用户已有改动得到保留
- 冲突有明确处理责任人
