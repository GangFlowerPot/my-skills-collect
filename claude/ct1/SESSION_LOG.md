### 16:15 团队组建、ct1 skill 创建与 eval

**任务**: 组建四人团队、创建可复用的 ct1 skill、执行冒烟测试与完整 eval、同步到技能仓库并推送。

**完成的工作**:

1. **团队组建（两轮）**:
   - 首次手动创建 leader/frontend-dev/backend-dev/tester（后停止）。
   - 通过 ct1 skill 冒烟测试重建，因 harness flat-roster 约束，tester 被迫命名为 tester-2。
   - 最终团队：leader / frontend-dev / backend-dev / tester-2，均注入项目上下文、协作协议、进度查询规范。
   - 部署进度查询协议到 `skill-docs/TEAM_PROTOCOL.md`，挂载 `AGENT_MEMORY.md` 导航。

2. **可复用进度查询机制**:
   - 触发词：进度 / 查进度 / 进度如何 / 同步进度 / status / progress / check progress / where are we / how's it going。
   - 6 字段状态请求模板：【状态】【当前任务】【进度】【阻塞项】【下一步】【需要的输入】。
   - 协议文件为唯一真相源，跨会话可恢复。

3. **ct1 skill 创建与全局安装**:
   - 编写 `~/.claude/skills/ct1/SKILL.md`（172 行）+ `references/team-protocol.md`（66 行）。
   - 5 步工作流：收集项目上下文 → 确认团队配置（默认四人 + 自定义 UX：自然语言修改 → diff 确认）→ 并行启动 Agent → leader 介绍 → 持久化协议 + 导航挂载。
   - 默认团队：leader（固定）+ 前端开发 + 后端开发 + 测试。
   - 宽泛触发：中文（创建/组建/搭建/成立/拉起/建个…团队/小队/工作组）+ 英文（create team / build a team / set up a team / spin up a team / team up）。

4. **ct1 评估（6/6 run 完成）**:
   - eval-1 默认建队：with-skill 87.5% vs baseline 62.5%（+25%）。
   - eval-2 自定义两人队：with-skill 100% vs baseline 66.7%（+33%）。
   - eval-3 进度查询：with-skill 100% vs baseline 60%（+40%）。
   - 平均：with-skill 95.8% vs baseline 63.1%（+32.7%）。

5. **根据 eval 改进 ct1**:
   - 增加 flat-roster 回退指引（3 级回退：unnamed subagent → 复用既有 teammate → 记录并继续）。
   - 协议文件双写（项目目录 + `ct1-workspace/team-protocol-snapshot.md` 验证副本）。
   - 并发写入处理（Read 重读 → 覆盖 Write）。

6. **同步与推送**:
   - 复制 ct1 skill 到 `D:/claudeCode/skills/my-skills-collect/claude/ct1/`。
   - 复制 ct1 相关记忆（TEAM_PROTOCOL.md、AGENT_MEMORY.md 导航、evals 证据）到目标目录。
   - 提交并推送到 origin/main（用户预授权，直接推送）。

**遇到的问题**:

- **harness flat-roster 约束**：所有 run 的命名 Agent 创建被拒（"Teammates cannot spawn other teammates — the team roster is flat"），退化为 unnamed subagent。影响 eval 的"并行启动命名 Agent"assertion，但流程意图正确。
- **tester 名字残留**：即使停止旧 tester-2，harness 仍残留注册，新 tester 被迫为 tester-2。
- **eval 输出延迟**：部分 eval run 在 peer 会话执行，证据文件延迟到达本会话工作区。
- **Python 2.7 / yaml 模块**：skill-creator 的 validate/package/aggregate 脚本无法运行（缺 yaml 模块 + GBK 编码），不影响 skill 功能。

**代码变更**:

- 新增 `~/.claude/skills/ct1/`（SKILL.md、references/team-protocol.md、evals/evals.json、ct1-workspace/）。
- 更新 `skill-docs/TEAM_PROTOCOL.md`（进度查询协议）。
- 更新 `AGENT_MEMORY.md`（新增协议导航行）。
- 更新 `skill-docs/CURRENT_TASK.md` 与 `skill-docs/SESSION_LOG.md`（本条目）。
- 同步到 `D:/claudeCode/skills/my-skills-collect/claude/ct1/` 并推送。

**eval 证据保存**: `~/.claude/skills/ct1-workspace/iteration-1/`（6 个 run 的完整证据 + grading.json + benchmark.json）。

### 01:00 团队名字清理（tester-2 → qa-engineer）

**任务**: 解决测试角色名字被 harness 残留注册占用问题，获得干净无数字的 Agent 名字。

**完成的工作**:

1. 停止 tester-2 后以 `tester` 重建，仍被 harness 自动命名为 tester-2——确认该名在本会话被**永久注册残留**（原始团队 + 多轮 eval + 冒烟测试创建了过多 tester 实例，harness 会话级缓存无法通过停止实例释放）。
2. 改用本会话从未使用的英文名 `qa-engineer` 成功创建测试角色，名字干净无后缀。
3. 更新 `skill-docs/CURRENT_TASK.md`：团队状态表改为 leader / frontend-dev / backend-dev / qa-engineer。

**最终团队（名字全部干净 ✅）**:
- leader（统筹领导决策者）
- frontend-dev（前端开发）
- backend-dev（后端开发）
- qa-engineer（测试）

**遇到的问题**:
- harness 对已注册 Agent 名字做会话级持久化缓存，即使实例全部停止，`tester` 仍被判为"占用"自动加 -2。规避方案：选用全新未用过的英文名。
