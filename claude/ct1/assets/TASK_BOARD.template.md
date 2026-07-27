# Task Board

## 任务列表

| ID | 标题 | Owner | 状态 | 优先级 | 风险 | 依赖 | AC |
|---|---|---|---|---|---|---|---|
| ARCH-001 | 定义运单接口契约 | leader | ready | high | medium | — | AC-001, AC-002 |
| FE-001 | 运单列表页组件开发 | waybill-ui-dev | backlog | high | medium | ARCH-001 | AC-003 |
| BE-001 | 实现创建运单接口 | waybill-service-dev | backlog | high | medium | ARCH-001 | AC-003 |

## 任务明细

### ARCH-001：定义运单接口契约
- **write_scope**: docs/api/waybill-contract.yaml
- **artifacts**: docs/api/waybill-contract.yaml
- **verification**: 前后端 review 通过
- **handoff_to**: waybill-ui-dev, waybill-service-dev, tester

### FE-001：运单列表页组件开发
- **write_scope**: frontend/src/pages/waybill/**, frontend/src/components/waybill/**
- **artifacts**: WaybillList.vue, WaybillFilter.vue
- **verification**: npm run test -- --filter=waybill
- **handoff_to**: reviewer, tester

### BE-001：实现创建运单接口
- **write_scope**: backend/waybill/**
- **artifacts**: WaybillController.java, WaybillService.java
- **verification**: mvn test -pl waybill
- **handoff_to**: reviewer, tester
