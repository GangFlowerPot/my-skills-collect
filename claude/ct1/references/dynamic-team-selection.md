# Dynamic Team Selection（动态团队选择）

## 是什么

从任务图推导最小可行团队的算法。角色是任务图的执行视图，不是团队设计的起点。

## Role Candidate schema

```yaml
role_candidates:
  - role_id: waybill-service-dev
    display_name: 运单服务开发
    mission: 完成运单领域后端服务、数据访问和接口实现
    owned_tasks:
      - BE-001
      - BE-002
    capabilities:
      - spring-service-development
      - api-implementation
      - transaction-design
    read_scope:
      - docs/api/**
      - backend/common/**
      - backend/waybill/**
    write_scope:
      - backend/waybill/**
    dependencies:
      - ARCH-001
    activation:
      when: ARCH-001 accepted
    deactivation:
      when: BE-001 and BE-002 accepted
    split_reason: 后端任务工作量充分，且与前端通过冻结契约隔离
```

### 必须包含

- 角色使命；负责的任务 ID；所需能力
- 读写范围；依赖；启动条件；结束条件
- 合并或拆分理由

## 角色生命周期

```
planned
→ ready
→ active
→ waiting
→ completed
→ retired

异常状态：blocked / failed / replaced
```

### 角色退场

角色负责的任务全部 accepted，且没有待答复问题、审查遗留或交接事项时，可以：标记 completed；输出 Handoff Brief；退出活跃团队；保留状态供会话恢复。

## 团队生成算法

1. **能力提取**：从任务图的 `required_capabilities` 汇总能力需求
2. **任务聚类**：按高内聚、低耦合原则聚类任务（相同业务域、重叠写入范围、强依赖、相近能力、独立交付物）
3. **合并评分**：任务总工作量小、强依赖、写入范围重叠、契约不稳定时合并
4. **拆分评分**：有独立交付物、写入范围不重叠、契约稳定、各部分有足够工作量、并行能缩短关键路径时拆分
5. **冲突检查**：任意两个角色的 write_scope 明显重叠时，细化 ownership 或合并
6. **并行价值判断**：两个任务是否能同时开始、是否有未冻结共享契约、是否频繁修改相同文件、能否缩短关键路径

## 验收标准

- 简单任务能降级为单 Agent
- 小型跨层任务能合并为 fullstack
- 多微服务能按业务边界拆分
- 高风险任务能增加专项角色
- 每个角色都有 owned_tasks 和 write_scope
- 每个团队方案都解释拆分和合并理由
