# Recovery Protocol（Agent 健康检查与替补机制）

## 是什么

单个 Agent 失败不会使项目永久停滞。通过健康检查、重试、重新分配或启动替补来恢复任务。

## 健康状态

```
active
idle
waiting_input
unresponsive
failed
replaced
completed
```

异常状态：`blocked`、`failed`、`replaced`

## 恢复流程

| 步骤 | 动作 |
|---|---|
| 1. 第一次无响应 | 重新请求一次状态 |
| 2. 第二次无响应 | 检查 Agent 是否仍活跃 |
| 3. 确认失败 | 保存其任务、文件、问题和最后状态 |
| 4. leader 决策 | 选择重试、重新分配或启动替补 |
| 5. 替补接收 | 替补 Agent 接收 `Handoff Brief` |
| 6. 验证继续 | 替补先验证已有产物，再继续工作 |

## Handoff Brief

```markdown
## 当前任务
## 已完成
## 未完成
## 修改文件
## 已做决策
## 待答复问题
## 验证结果
## 下一步建议
```

## 验收标准

- 单个 Agent 失败不会使项目永久停滞
- 重试次数有限
- 替补能够恢复任务上下文
- 未完成工作不会被误报为完成
