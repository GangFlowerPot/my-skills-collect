# Code Review 完整工作示例

> 本文件是 `references/code-review-protocol.md` 的配套示例，展示风险驱动审查的完整流程。

**场景**：frontend-dev 在 review_ready 完成运单列表页编码，leader 送审。

## 1. Dev 汇报（review_ready 触发事件）

```
【协议版本】StatusReport/v2
【任务ID】FE-001
【状态】工作中
【当前任务】运单列表页组件开发
【进展】完成组件树与状态管理
【阻塞项】无
【下一步】等待审查通过后继续交互实现
【需要的输入】无
【触发事件】review_ready
【待答复问题】无
【变更文件】
- src/components/WaybillList.vue（新增）
- src/store/waybill.js（修改）
【验证结果】未执行
```

## 2. Leader 送审

leader 向 reviewer 发送：
```
请审查 frontend-dev 的运单列表页代码（第 1 轮 / review_ready）：
- src/components/WaybillList.vue
- src/store/waybill.js

审查范围：代码质量、架构合理性、安全、性能、编码规范、中间件使用。
按 Code Review 报告模板输出。
```

## 3. Reviewer 输出报告

```
## Code Review 报告
审查对象: frontend-dev 的 运单列表页
审查轮次: 第 1 轮（触发事件: review_ready）
审查文件: src/components/WaybillList.vue, src/store/waybill.js

### 严重问题（必须修复）— 阻塞项
| 编号 | 位置 | 问题描述 | 修复建议 | 分类 |
|------|------|----------|----------|------|
| R-FE-001 | WaybillList.vue:58 | 列表数据未做空值保护，data 可能为 null 导致渲染崩溃 | 添加 v-if="data && data.length" 或默认空数组 | 安全 |

### 建议改进（建议修复）— 非阻塞
| 编号 | 位置 | 问题描述 | 修复建议 | 分类 |
|------|------|----------|----------|------|
| R-FE-002 | waybill.js:23 | mutation 命名 WAYBILL_LIST 不符合项目驼峰规范 | 改为 setWaybillList | 规范 |
| R-FE-003 | WaybillList.vue:112 | 分页逻辑与筛选逻辑耦合在同一方法，难以维护 | 拆分为 fetchList / handleFilter / handlePage 三个方法 | 架构 |

### 需用户决策
| 编号 | 问题描述 | 选项 | 影响范围 |
|------|----------|------|----------|
| R-FE-U01 | 运单列表是否需要跨页保持筛选条件？ | A. 保持（需持久化到 localStorage） B. 不保持（刷新重置） | 用户体验与 waybillStore 设计 |

### 总结
- 是否通过: 否（存在 1 个严重问题）
- 整体评价: 组件结构清晰，状态管理基本合理；需修复空值保护与命名规范
- 本轮重点: 数据安全性与代码规范
```

## 4. Leader 分流

**严重问题 + 建议改进 → 下发 frontend-dev**：
```
[CONTEXT ADDENDUM]
来源：reviewer 审查（第 1 轮 / frontend-dev / review_ready）
关联任务：运单列表页代码修复
审查问题：
  1. [R-FE-001][严重][安全] WaybillList.vue:58 — 列表数据未做空值保护。修复建议：添加 v-if 或默认空数组
  2. [R-FE-002][建议][规范] waybill.js:23 — mutation 命名不规范。修复建议：改为 setWaybillList
  3. [R-FE-003][建议][架构] WaybillList.vue:112 — 分页与筛选耦合。修复建议：拆分为三个方法
对原有上下文的变更：需修复上述问题后重新提交审查
```

**需用户决策 → 升级**：
leader 将 R-FE-U01 填入 review_ready 的【待答复问题】：
```
【待答复问题】
1. [R-FE-U01][review_ready] 运单列表是否需要跨页保持筛选条件？ A. 保持（持久化 localStorage） B. 不保持 (关联任务: 运单列表页)
```

## 5. 用户决策

```
R-FE-U01: A（保持）
```

leader 通过 `[CONTEXT ADDENDUM]`（来源=用户答复）分发给 frontend-dev。

## 6. Dev 修复后再审

frontend-dev 修复 R-FE-001/002/003 + 实现跨页保持 → 汇报下一个 review_ready（含修复说明 + 新完成文件）→ leader 再次送审 reviewer → reviewer 输出第 2 轮报告（对比上轮，标注已修复/新问题）→ 循环。
