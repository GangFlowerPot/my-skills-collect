# Team Selection（团队选择）

## 是什么

根据任务图选择或复用团队的规则。

## 团队设计最低充分信息

决定正式人数前，至少必须掌握：

```yaml
team_design_readiness:
  project_goal: 项目或本次需求要解决什么问题
  deliverables: 本次必须产生哪些交付物
  affected_domains: 涉及哪些业务域、模块或服务
  technical_surfaces: 是否涉及前端、后端、数据、部署、安全等
  major_dependencies: 主要任务依赖和不可并行部分
  risk_areas: 安全、迁移、性能、兼容性等风险
  probable_write_scopes: 预计修改的目录、模块和公共文件
  acceptance_criteria: 可验证的主要完成条件
```

缺失到无法判断任务边界时，继续探测或向用户提出必要问题，不能通过套用固定团队模板弥补信息不足。

## 团队复用

如果项目已有活跃团队，给用户三个选项：

- **重建**：停旧的重建，协议文件重置
- **复用**：不重建，只刷新当前任务
- **另建**：自动加 `-2`/`-3` 后缀，协议文件另存

默认推荐"复用"。

## 多团队隔离

多个团队可并存，通过 `team_id` 隔离运行状态：

```text
.claude/
└── teams/
    └── <team-id>/
        ├── TEAM_CONFIG.yaml
        ├── TEAM_STATE.json
        ├── TASK_BOARD.md
        ├── QUESTION_REGISTRY.json
        ├── REVIEW_LOG.md
        ├── TEST_REPORT.md
        └── DELIVERY_REPORT.md
```

导航标记：`<!-- ct1:teams:start -->` ... `<!-- ct1:teams:end -->`
