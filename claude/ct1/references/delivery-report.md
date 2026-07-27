# Delivery Report（交付报告）

## 是什么

`delivery` 模式的最终产物。报告内容与任务板、测试报告和审查记录一致，不掩盖未测试、环境限制或遗留问题。

## 项目状态机

```
discovery
  → planned
  → executing
  → integrating
  → verifying
  → conditionally_deliverable
  → delivered

任意非终态均可进入 blocked / cancelled。
```

> `delivered` 是项目状态，不是任务状态。项目 delivered 必须经过项目级交付门禁（所有必需任务 accepted、所有必需 AC 通过、P0/P1 缺陷为零、严重审查问题为零、user-required 决策无未确认项）。

## 报告格式

```markdown
# Delivery Report

## 交付结论
通过 / 有条件通过 / 未通过

## 需求完成情况
| AC | 结果 | 证据 |
|---|---|---|
| AC-001 | ... | ... |

## 变更摘要
## 修改文件
## 接口、数据库和配置变化
## 构建与测试结果
## Code Review 结果
## 部署或使用说明
## 数据迁移说明
## 回滚说明
## 已知限制与风险
## 未完成事项
## 用户下一步操作
```

## 交付判定

| 结论 | 条件 |
|---|---|
| `通过` | 所有门禁满足 |
| `有条件通过` | 只剩非阻断风险，并已明确披露 |
| `未通过` | 存在严重问题、测试失败或关键 AC 未完成 |

## 验收标准

- 每次 `delivery` 模式均产生报告
- 报告内容与任务板、测试报告和审查记录一致
- 不掩盖未测试、环境限制或遗留问题

## 模板

完整模板见 `assets/DELIVERY_REPORT.template.md`。
