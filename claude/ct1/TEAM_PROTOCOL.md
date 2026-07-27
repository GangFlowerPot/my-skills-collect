# 团队进度查询协议

本文件是进度查询机制的唯一真相源，由 `ct1` skill 部署。

## 触发词

用户发送以下任一短语，主线程启动一次**进度同步**：

- 中文：`进度` / `查进度` / `进度如何` / `同步进度`
- 英文：`status` / `progress` / `check progress` / `where are we` / `how's it going`

## 查询流程（主线程执行）

1. 识别触发词
2. **并行**向以下非 leader 成员发送「状态请求模板」（同一消息多个 `SendMessage`，避免串行）
3. 收集回复，按「汇总表格格式」整理为 Markdown 表格
4. 超时未回复者对应行显示 `⏳ 未响应`，表后提示"可再次发送触发词重新查询"

## 本团队成员（进度查询范围，不含 leader）

- 🖥️ 前端（frontend-dev）
- ⚙️ 后端（backend-dev）
- 🧪 测试（tester）

## 项目上下文（注入每个 Agent）

项目 ynwl 是前后端分离的管理系统。
- 前端 ynwl_front：Vue 2.6 + Element UI + AVUE + Axios；dev server 端口 2890；代理 /api → 127.0.0.1:10100。
- 后端 ynwl_back：Java 8 + Spring Boot 2.1 + Spring Cloud + BladeX 2.5 微服务（Maven 多模块）。
- 微服务清单：blade-gateway(10100)、blade-auth、blade-system、blade-user、blade-fileserver、blade-apires、blade-log。
- 注册中心 Nacos。凭据与 Token 不得写入记忆或输出。
- 技术栈约束：必须基于现有技术栈工作，不引入项目未使用的框架。

## 状态请求模板（发给每位执行者）

所有角色统一使用 **StatusReport/v2**。完整 schema 见 `references/status-report-schema.md`。

```
请按 StatusReport/v2 格式报告你当前的状态：
【协议版本】StatusReport/v2
【任务ID】任务板中的唯一 ID
【状态】空闲 / 就绪 / 工作中 / 阻塞 / 审查中 / 测试中 / 完成
【当前任务】一句话描述
【进展】已经完成的可验证结果
【阻塞项】无 / 问题或依赖 ID
【下一步】下一个具体动作
【需要的输入】无 / 所需输入
【触发事件】无 / design_ready / contract_ready / review_ready / test_ready / acceptance_ready
【待答复问题】无 / 当前卡点的问题
【变更文件】无 / 本轮新增或修改的文件列表
【验证结果】未执行 / 命令、结果和限制
```

## 汇总表格格式

```
| 成员 | 状态 | 任务ID | 当前任务 | 进展 | 阻塞项 | 下一步 | 触发事件 | 待答复问题 | 变更文件 | 验证结果 |
|---|---|---|---|---|---|---|---|---|---|---|
```

## 执行者回复规范

执行者收到状态请求后，**严格按 StatusReport/v2、固定顺序**回复，不额外寒暄，便于主线程解析。示例：

```
【协议版本】StatusReport/v2
【任务ID】BE-003
【状态】空闲
【当前任务】等待分配需求
【进展】—
【阻塞项】无
【下一步】待 leader 派发任务
【需要的输入】首个需求描述
【触发事件】无
【待答复问题】无
【变更文件】无
【验证结果】未执行
```

## 协议复用说明

本文件是进度查询机制的唯一真相源。主线程识别到触发词后，按本文件规定的模板和流程执行，不依赖临时记忆。会话重建后，通过项目记忆导航 → 本文件恢复机制。
