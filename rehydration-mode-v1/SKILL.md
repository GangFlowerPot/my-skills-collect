---
name: rehydration-mode-v1
description: [V1] 项目上下文再水化记忆系统 —— 通过结构化 Markdown 文件实现会话间状态持久化，确保每次启动新会话时能无缝恢复工作上下文。触发方式：进入项目目录时自动检测，或用户主动调用 /rehydration 命令。
---

# Rehydration Mode — 项目上下文再水化记忆系统

通过结构化 Markdown 文件将项目关键信息永久持久化，每次启动编程 Agent 时强制读取，实现"再水化（Rehydration）"——无缝恢复上一次会话的工作上下文。

## 推荐文件结构

```
project-root/
├── CLAUDE.md                    # 自动加载的指令文件（核心）
├── CLAUDE.local.md             # gitignored，私有指令
├── .claude/
│   ├── rules/                  # 按目录懒加载的规则
│   └── skills/                 # 自定义 skills
├── docs/                       # 项目记忆文档（核心）
│   ├── PROJECT_MEMORY.md       # 项目整体记忆
│   ├── SESSION_LOG.md          # 会话日志
│   ├── DECISIONS.md            # 架构决策记录
│   └── CURRENT_TASK.md         # 当前任务状态
└── README.md                   # 标准项目说明
```

## 核心文件职责

| 文件 | 职责 | 加载时机 |
|------|------|----------|
| `CLAUDE.md` | 自动加载的启动指令，定义强制规则和记忆文件位置 | 每次进入项目自动加载 |
| `docs/PROJECT_MEMORY.md` | 项目整体记忆：概述、架构、模块、API、里程碑、技术债务 | 会话启动时读取 |
| `docs/CURRENT_TASK.md` | 当前任务状态（热恢复核心）：阶段、进度、阻塞项、代码片段 | 会话启动时**必读** |
| `docs/SESSION_LOG.md` | 会话日志：每次会话的摘要和变更记录 | 会话结束时追加 |
| `docs/DECISIONS.md` | 架构决策记录（ADR）：背景、决策、原因、影响 | 有决策时同步 |

---

## 能力 A：初始化再水化系统

### 触发条件
- 用户首次使用 `/rehydration` 或 `/rehydration init`
- 检测到项目中没有 `CLAUDE.md` 和 `docs/` 结构
- 用户明确要求初始化项目记忆系统

### 执行流程

1. **检测当前状态**：检查项目根目录是否已存在 `CLAUDE.md` 和 `docs/` 目录
2. **如不存在，引导创建**：
   - 询问项目名称、技术栈、核心模块（至少 3 个问题）
   - 如果检测到项目类型（如 Go、Python、React、Node.js 等），自动推断技术栈并确认
   - 自动生成 `CLAUDE.md` 和 `docs/` 目录下的 4 个核心文件模板
3. **如已存在**，直接执行能力 B"再水化"流程

### 初始化时的交互模板

```
检测到项目: {project_name}
技术栈推断: {detected_stack}（请确认或修改）

我将创建以下文件：
  ✅ CLAUDE.md — 启动指令文件
  ✅ docs/PROJECT_MEMORY.md — 项目整体记忆
  ✅ docs/CURRENT_TASK.md — 当前任务状态
  ✅ docs/SESSION_LOG.md — 会话日志
  ✅ docs/DECISIONS.md — 架构决策记录

请确认以下信息：
  1. 项目名称？
  2. 技术栈（后端/前端/数据库/部署）？
  3. 核心模块有哪些？

确认后我将生成所有文件模板。
```

### 生成文件时的注意事项
- 所有文件使用 **UTF-8** 编码
- 使用模板文件（见 `assets/` 目录）生成内容，根据项目信息填充占位符
- 自动检测 Git 仓库，如存在则建议在 `.gitignore` 中添加 `CLAUDE.local.md`
- 如果已存在某些文件，询问是否覆盖

---

## 能力 B：再水化（会话启动）

### 触发条件
- 用户启动新会话时（CLAUDE.md 中定义了启动协议）
- 用户主动调用 `/rehydration` 或 `/rehydration restore`
- 检测到记忆文件已存在但尚未读取

### 执行流程

严格按照以下步骤执行：

**Step 1：读取记忆文件**
- 强制读取 `CLAUDE.md` 获取项目规则和协议
- **必须读取** `docs/CURRENT_TASK.md` 和 `docs/PROJECT_MEMORY.md`
- 如果 `CLAUDE.local.md` 存在，读取但不修改

**Step 2：解析当前状态**
- 解析当前阶段（如 v0.5）
- 提取进行中任务清单（含进度百分比）
- 提取阻塞项（含状态和预计解决时间）
- 提取关键文件状态

**Step 3：向用户汇报**
使用以下结构化格式汇报：

```
📋 项目记忆已恢复 — {project_name}

🎯 当前阶段: {current_phase}
   最后更新: {last_update_time} by {model} (会话ID: {session_id})

🔄 进行中任务:
   1. {task_name}（进度: {percentage}%）
      - 当前问题: {current_issue}
      - 下一步: {next_step}
      - 关键代码: {file_path}:{line_range}

⏳ 待开始任务:
   - {task_name}

❌ 阻塞项:
   1. {blocker_description}
      - 状态: {status}
      - 预计解决: {expected_date}
      - 方案 B: {plan_b}

📁 关键文件:
   - {file_path} — {status} — {description}

💡 建议: {next_session_suggestion}
```

**Step 4：询问用户**
```
是否继续当前任务？我将从上次中断的位置继续工作。
```

---

## 能力 C：会话工作流支持

会话中支持以下命令，处理对应的记忆文件操作：

### `/memory status` — 查看当前记忆状态

读取并汇总所有记忆文件，展示：
- 项目概览（从 PROJECT_MEMORY.md 提取）
- 当前任务进度（从 CURRENT_TASK.md 提取）
- 最近 3 条会话记录（从 SESSION_LOG.md 提取）
- 最近架构决策（从 DECISIONS.md 提取）

### `/memory update` — 更新 CURRENT_TASK.md

与用户交互，更新当前任务状态：
- 询问任务进度变化（哪些完成了、哪些在进行、新增哪些）
- 询问当前编辑的文件和行号
- 询问是否有新的阻塞项或已解决的阻塞项
- 更新 `最后更新` 时间戳
- 写入 CURRENT_TASK.md

### `/memory log` — 追加 SESSION_LOG.md 条目

为当前会话追加一条会话日志：
- 自动记录时间、模型信息
- 询问：本次完成的任务、关键决策、遇到的问题、遗留工作
- 尝试运行 `git diff --stat` 获取代码变更统计
- 按 SESSION_LOG.md 模板格式追加条目

### `/memory decision` — 记录架构决策

向 DECISIONS.md 追加一条 ADR：
- 自动分配 ADR 编号（检查已有编号，递增）
- 询问：背景、决策内容、原因、影响、替代方案、代码位置
- 日期自动填充
- 状态默认为"已决定 ✅"
- 按 DECISIONS.md 模板格式追加条目

### `/memory dehydrate` — 会话结束脱水

执行能力 D 的完整脱水流程。

---

## 能力 D：会话结束（脱水）

### 触发条件
- 用户调用 `/memory dehydrate` 或 `/rehydration dehydrate`
- CLAUDE.md 中定义了会话结束协议时自动触发
- 用户表示要结束当前会话

### 执行流程

严格按照以下 4 步执行：

**Step 1：更新 CURRENT_TASK.md**
- 同步任务进度：刷新已完成/进行中/待开始清单
- 记录当前编辑的文件和行号
- 更新阻塞项状态（已解决/仍在等待）
- 更新 `最后更新` 字段（时间、模型、会话ID）
- 更新"下次会话建议"

**Step 2：追加 SESSION_LOG.md**
- 记录本次会话时间、模型
- 记录完成的任务（编号列表）
- 记录关键决策（决定、原因、记录位置）
- 记录遇到的问题和解决方案
- 记录遗留工作
- 尝试运行 `git diff --stat` 记录代码变更

**Step 3：同步 DECISIONS.md**
- 检查本次会话中是否有新架构决策
- 如有且未记录，追加到 DECISIONS.md

**Step 4：提示用户**
输出确认信息：
```
✅ 记忆已持久化

已更新:
  📝 docs/CURRENT_TASK.md — 任务进度已同步
  📋 docs/SESSION_LOG.md — 会话日志已追加
  {如有: 📐 docs/DECISIONS.md — 架构决策已同步}

下次启动时会自动恢复当前状态。使用 /rehydration 即可。
```

---

## 交互规范

| 规范项 | 规则 |
|--------|------|
| 编码 | 所有文件操作使用 **UTF-8** |
| 语言 | 支持中文和英文项目，汇报语言跟随用户 |
| 路径 | 文件路径使用相对路径（基于项目根目录） |
| 状态图标 | ✅ 已完成、🔄 进行中、⏳ 待开始、❌ 阻塞 |
| 优先级 | P0（阻塞）、P1（高）、P2（中）、P3（低） |
| 汇报格式 | 结构化，包含：当前阶段、进行中任务（带进度百分比）、阻塞项、建议下一步 |
| 时间格式 | 统一使用 `YYYY-MM-DD HH:MM` 格式 |

---

## 约束与边界

- **绝不**修改用户未明确授权的文档
- **绝不**暴露文件中的敏感信息（密钥、密码、Token 等）
- **如果** `CLAUDE.local.md` 存在，**读取但不写入**（纯私有指令文件）
- **如果** Git 仓库存在，建议在 `.gitignore` 中添加 `CLAUDE.local.md`
- **每月**提醒用户归档旧的 SESSION_LOG 条目（保留最近 3 个月，其余归档）
- **如果**检测到项目类型（Go、Python、React、Node.js 等），自动填充对应的技术栈模板
- **绝不**在模型间切换同一任务（保持任务连续性，会话恢复时使用同一模型系列）

---

## 模板文件

模板文件位于本 Skill 的 `assets/` 目录下。生成文件时，读取对应模板并根据项目信息填充所有 `{占位符}`。

| 模板文件 | 路径 | 用途 |
|----------|------|------|
| CLAUDE.md 模板 | `assets/CLAUDE.md.tmpl` | 启动指令文件模板 |
| PROJECT_MEMORY.md 模板 | `assets/PROJECT_MEMORY.md.tmpl` | 项目整体记忆模板 |
| CURRENT_TASK.md 模板 | `assets/CURRENT_TASK.md.tmpl` | 当前任务状态模板 |
| SESSION_LOG.md 模板 | `assets/SESSION_LOG.md.tmpl` | 会话日志模板 |
| DECISIONS.md 模板 | `assets/DECISIONS.md.tmpl` | 架构决策记录模板 |

生成文件时：
1. 先读取对应的模板文件
2. 将 `{占位符}` 替换为用户提供的实际信息
3. 对技术栈部分，根据检测到的项目类型自动填充
4. 保留模板中的所有注释和结构，让用户了解每个部分的作用

---

## 完整使用流程示例

### 场景：新项目初始化 → 工作 → 结束

```
[用户] /rehydration init
[Agent] 检测到项目: my-ecommerce-app
        技术栈推断: Go + React + PostgreSQL
        我将创建记忆文件结构，请确认以上信息...
[用户] 确认，后端是 Go 1.22 + Gin，前端 React 18 + TypeScript
[Agent] ✅ 已创建 CLAUDE.md 和 docs/ 目录下的 4 个核心文件

--- 用户开始工作 ---

[用户] 帮我实现订单取消接口
[Agent] （读取 CURRENT_TASK.md，了解当前阶段）
        （工作过程中...）
[用户] /memory update
[Agent] 已更新 CURRENT_TASK.md，同步了任务进度

--- 用户记录决策 ---

[用户] /memory decision
[Agent] 请问决策的背景和内容？
[用户] 选择 cursor-based 分页方案...
[Agent] ✅ 已记录 ADR-005 到 docs/DECISIONS.md

--- 会话结束 ---

[用户] /memory dehydrate
[Agent] ✅ 记忆已持久化
        📝 docs/CURRENT_TASK.md — 任务进度已同步
        📋 docs/SESSION_LOG.md — 会话日志已追加
        📐 docs/DECISIONS.md — 架构决策已同步
        下次启动时会自动恢复当前状态。

--- 第二天，新会话 ---

[用户] /rehydration
[Agent] 📋 项目记忆已恢复 — my-ecommerce-app
        🎯 当前阶段: v0.5 订单取消和退款流程
        🔄 进行中: QueryRefundStatus() 函数（进度: 60%）
        ❌ 阻塞项: 微信支付退款证书
        💡 建议: 是否继续完成退款查询函数？
[用户] 是，继续
[Agent] （无缝继续昨天的工作...）
```
