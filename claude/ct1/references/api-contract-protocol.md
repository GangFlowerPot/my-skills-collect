# API 契约生命周期（API Contract Protocol）

## 是什么

前后端接口的正式创建、评审、冻结和变更流程。避免接口变化只通知单个角色。

## 契约状态

```
draft
  → frontend-reviewed
  → tester-reviewed
  → frozen
  → implemented
  → verified
```

## 契约必需字段

```yaml
endpoint: POST /api/waybills
owner: backend-dev
consumers:
  - frontend-dev
  - tester
status: draft
request: {}
response: {}
errors: []
permissions: []
version: 1
```

## 变更规则

- **frozen 后的修改**必须增加版本或变更记录
- leader 找出所有 consumer 和受影响任务
- 使用 `[CONTEXT ADDENDUM]` 通知相关角色
- 受影响任务重新评估状态
- tester 更新测试用例

## 状态转换

| 当前状态 | 下一状态 | 触发条件 |
|---|---|---|
| draft | frontend-reviewed | 前端 review 通过 |
| frontend-reviewed | tester-reviewed | 测试 review 通过 |
| tester-reviewed | frozen | leader 确认冻结 |
| frozen | implemented | 后端实现完成 |
| implemented | verified | 前端集成测试通过 |

## 验收标准

- 前端、后端和 tester 使用同一契约版本
- 契约变化不会只通知单个角色
- 最终报告列出已交付的契约变化
