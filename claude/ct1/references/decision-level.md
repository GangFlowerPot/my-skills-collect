# Decision Level（问题决策等级）

## 是什么

未答复问题被 Agent 自行裁决时，区分风险等级。高风险问题不得自动作废。

## 问题 schema

```yaml
id: Q-BE-001
decision_level: user-required
question: 是否允许删除历史数据
reversible: false
impact: high
status: pending
```

## 决策等级

| 等级 | 处理方式 |
|---|---|
| `agent-assumption` | Agent 可采用可逆默认值并记录 |
| `cross-agent` | 路由给对应 owner |
| `leader-decidable` | leader 根据项目规则裁决 |
| `user-required` | 必须用户决定，不允许自动作废 |

## 默认 user-required 的问题

- 数据删除
- 权限和认证
- 安全与合规
- 付费和资源成本
- 外部发布
- 不可逆数据库迁移
- 明显改变需求范围
- **数据层语义冲突**（DDL 语义 vs 现有 ADR 裁定 vs 实际库表，如 BYTE vs CHAR）

## 验收标准

- 高风险问题不会被自动作废
- 低风险可逆问题不会阻塞整个团队
- 临时假设进入最终交付报告
