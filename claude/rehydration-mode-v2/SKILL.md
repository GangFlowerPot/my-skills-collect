---
name: rehydration-mode-v2
description: 项目上下文再水化记忆系统 —— 通过结构化 Markdown 文件实现会话间状态持久化与无缝恢复。无论用户说"再水化""rehydration""记忆恢复""会话恢复""上下文恢复""继续上次""上次做到哪了""接着做""项目记忆""脱水""dehydrate""memory restore""resume work""continue where I left off""what was I doing""restore context""/rehydration""/memory"还是类似的表达，只要是涉及跨会话保持工作状态、恢复上次进度、或是初始化项目记忆系统，都使用此 Skill。
---

# Rehydration Mode V2 — 项目上下文再水化记忆系统

## 核心理念

编程会话中断后重新开始时，最大痛点不是"不记得代码"，而是**不记得当时在做什么、做到哪了、为什么这样写**。传统做法是在脑子里记忆或零散笔记，但这些随会话关闭而消失。

再水化系统的解决思路：**把会话状态写成结构化的 Markdown 文件放在项目里**，每次启动时自动读取，就像把脱水食品重新泡发——从干瘪的文件恢复到鲜活的上下文。

## 何时使用这个 Skill

这个 Skill 覆盖三个关键时机：

1. **项目首次使用** — 用户说"初始化记忆系统""创建项目记忆""setup rehydration"，或你检测到项目没有 `CLAUDE.md` + `docs/` 结构
2. **会话启动恢复** — 用户表达"继续上次的工作""上次做到哪了""恢复上下文"，或使用了 `/rehydration` 命令
3. **会话结束保存** — 用户说"保存进度""持久化""结束会话""脱水"，或使用了 `/memory dehydrate` 命令

## 总体工作流

```
         ┌──────────────┐
         │  检测项目状态  │
         └──────┬───────┘
                │
        ┌───────┴───────┐
        │               │
    未初始化         已初始化
        │               │
        v               v
   ┌─────────┐    ┌─────────┐
   │ 能力 A   │    │ 能力 B   │
   │ 初始化   │    │ 再水化   │
   └────┬────┘    └────┬────┘
        │               │
        └───────┬───────┘
                │
        ┌───────┴───────┐
        │   工作中使用    │
        │   能力 C       │
        │ /memory xxx   │
        └───────┬───────┘
                │
        ┌───────┴───────┐
        │  会话结束时     │
        │   能力 D       │
        │   脱水保存     │
        └───────────────┘
```

---

## 能力 A：初始化再水化系统

### 何时触发
- 项目没有 `CLAUDE.md` 且没有 `docs/` 目录
- 用户明确说"初始化项目记忆""创建再水化文件"
- 用户调用 `/rehydration init`

### 执行步骤

**A1. 先跑检测脚本**（确定性操作，减少猜测）

```bash
python <skill_dir>/scripts/detect_project.py <project_root>
```

这会输出项目名、语言、框架、数据库、是否 Git 仓库等结构化的 JSON。以此为基线向用户确认，而不是空口猜测。

**A2. 向用户确认基本信息**

基于脚本输出，用这样的格式交互：

```
📋 项目检测结果:
   名称: {project_name}
   技术栈: {inferred_stack}
   Git 仓库: {是/否}

我将创建以下记忆文件:

  ✅ CLAUDE.md          — 启动指令（Claude Code 每次进入自动加载）
  ✅ docs/PROJECT_MEMORY.md — 项目整体记忆（架构/模块/API/技术债务）
  ✅ docs/CURRENT_TASK.md   — 当前任务状态（热恢复核心）
  ✅ docs/SESSION_LOG.md    — 会话日志（每次会话摘要）
  ✅ docs/DECISIONS.md      — 架构决策记录（ADR）

确认以上信息？有什么需要补充或修改的？
```

**A3. 生成文件**

从 `assets/` 目录读取模板，把 `{占位符}` 替换为实际信息后写入项目。关键原则：

- **技术栈自动填充**：脚本检测到的内容直接填入，减少用户手动输入
- **保留模板注释**：模板中的 `<!-- -->` 注释解释了每个部分怎么填，不要删除
- **已存在文件先询问**：不要静默覆盖。问用户"X 文件已存在，覆盖/跳过/合并？"
- **UTF-8 编码**：所有 `.md` 文件用 UTF-8

**A4. 完成后提示**

```
✅ 再水化系统初始化完成！

现在可以：
  - 开始工作，过程中用 /memory update 保存进度
  - 会话结束时用 /memory dehydrate 持久化状态
  - 下次启动时自动恢复上下文

如果这是 Git 仓库，建议在 .gitignore 中添加：
  CLAUDE.local.md
```

---

## 能力 B：再水化（会话启动恢复）

这是整个系统最关键的能力——让用户感觉"好像没有离开过"。

### 何时触发
- 已初始化的项目，用户表达继续工作的意图
- 用户说"继续""接着做""上次做到哪了""恢复进度""resume""continue where I left off"
- 用户调用 `/rehydration`（不带参数）

### 执行步骤

**B1. 检查文件结构**

```bash
python <skill_dir>/scripts/check_structure.py <project_root>
```

这个脚本告诉你哪些文件存在、CURRENT_TASK.md 中提取的阶段信息。

**B2. 读取核心文件**

必须按顺序读取，这是"热恢复"的数据源：

1. `docs/CURRENT_TASK.md` — **最先读**，这里记录了用户上次编辑的文件、行号、阻塞项
2. `docs/PROJECT_MEMORY.md` — 了解项目全貌（架构、模块划分、技术债务）
3. `CLAUDE.md` — 了解项目规则和约束（如果还没被自动加载的话）

`CLAUDE.local.md` 如果存在也要读，但**只读不写**——这是用户的私有指令。

**B3. 结构化汇报**

汇报的目的是让用户**5 秒内**了解当前状态，然后决定下一步。使用以下模板：

```
📋 {project_name} — 工作状态已恢复

🎯 阶段: {current_phase}（最后更新: {time}）

🔄 进行中 ({count} 项):
   {for each task:}
   ▸ {task_name} — {progress}%
     位置: `{file}:{line}`
     下一步: {next_step}

❌ 阻塞 ({count} 项):
   ▸ {blocker}（预计 {date} 解决）

💡 建议: {来自 CURRENT_TASK.md 的"下次会话建议"}
```

**原则**：
- 如果 CURRENT_TASK.md 中没有"进行中"任务，如实说"没有进行中的任务，当前阶段为 X"
- 如果记忆文件存在但内容为模板默认值（全是占位符），告诉用户"记忆系统已初始化但尚未记录具体工作，请问今天要做什么？"
- 不要编造信息——所有内容必须来自已读取的文件

**B4. 确认方向**

```
是否从这个位置继续？或者你今天想做别的事？
```

---

## 能力 C：会话中的记忆管理

会话过程中，用户可以随时操作记忆。每个子命令都是轻量的，不会打断工作流。

### `/memory status` — 快速概览

不需要逐字读所有文件——提取摘要即可：

```
📊 记忆状态

项目: {name} | 阶段: {phase}
任务: {in_progress} 进行中 / {completed} 已完成 / {pending} 待开始
阻塞: {blocker_count} 项
最近会话: {从 SESSION_LOG.md 取最近 1-2 条的日期和摘要}
最近决策: {从 DECISIONS.md 取最近 1-2 条 ADR 编号和标题}
```

### `/memory update` — 更新当前任务

这是使用频率最高的子命令。用户在工作过程中随时更新进度。

交互流程：
1. 快速回顾 CURRENT_TASK.md 中的当前任务列表
2. 询问变更有哪些（哪种状态变化了、新增了什么、完成了什么）
3. 更新"最后更新"时间戳
4. 写入文件

**重要**：不要让用户填表格。用对话的方式：
```
当前记录的任务: {列出进行中的}
有什么变化？
  - 完成了 XX？我把它移到"已完成"
  - 新增了 YY？加到"进行中"
  - ZZ 遇到阻塞？加到"阻塞项"
```

### `/memory log` — 追加会话日志

通常配合 `/memory dehydrate` 使用，也可以单独调用来记录重要事件。

- 自动记录：时间、模型
- 尝试 `git diff --stat` 获取代码变更（Git 仓库下自动执行）
- 询问：本次完成了什么、有什么决策、遗留了什么
- 追加到 SESSION_LOG.md **顶部**（最新在前）

### `/memory decision` — 记录架构决策

- 自动分配 ADR 编号（读 DECISIONS.md，取最大编号 +1）
- 日期自动填今天
- 状态默认"已决定 ✅"
- 只问必要的：背景、决策、原因、影响

---

## 能力 D：会话结束脱水

### 何时触发
- 用户调用 `/memory dehydrate` 或 `/rehydration dehydrate`
- 用户说"保存进度""结束工作""持久化""今天到这""wrap up for today"

### 为什么需要脱水
如果不在会话结束时主动保存状态，下次启动时 CURRENT_TASK.md 还是旧数据，"再水化"就失去了意义。脱水是把"现在的大脑状态"写进文件。

### 执行步骤

**D1. 更新 CURRENT_TASK.md**

按这个核对清单：
- [ ] 已完成的任务从"进行中"移到"已完成"
- [ ] 仍在进行的任务保留，更新进度描述和当前编辑位置
- [ ] 新增的任务加入"待开始"
- [ ] 阻塞项状态同步（解决了就标 ✅，新增的就追加）
- [ ] "最后更新"时间戳刷新
- [ ] "下次会话建议"更新——告诉未来的自己从哪里开始

**D2. 追加 SESSION_LOG.md**

记录本次会话摘要。关键是**让未来的自己能看懂**——不是流水账，而是"完成了什么、为什么这样做、还有什么没做"。

**D3. 检查架构决策**

本次会话中如果有重要决策（技术选型、方案变更、接口设计），问用户是否记录到 DECISIONS.md。如果用户说"不用"，跳过；如果 DECISIONS.md 已有相关条目，更新状态。

**D4. 确认**

```
✅ 会话状态已保存

已更新:
  📝 CURRENT_TASK.md  — {N} 项任务进度已同步
  📋 SESSION_LOG.md   — 会话日志已追加
  {如有: 📐 DECISIONS.md — {N} 条新决策已记录}

下次启动时说 /rehydration 即可恢复，说"继续"也行。
```

---

## 辅助脚本

Skill 自带两个 Python 脚本，用于确定性操作：

| 脚本 | 用途 | 何时使用 |
|------|------|----------|
| `scripts/detect_project.py` | 检测项目类型和技术栈，输出 JSON | 初始化（能力 A）的第一步 |
| `scripts/check_structure.py` | 检查再水化文件是否存在及状态，输出 JSON | 再水化（能力 B）的第一步 |

使用方式：
```bash
python <skill_install_dir>/scripts/detect_project.py [project_root]
python <skill_install_dir>/scripts/check_structure.py [project_root]
```

`<skill_install_dir>` 是本 Skill 的安装目录。如果不知道，先找到 Skill 文件位置。

---

## 模板资产

模板文件在 `assets/` 目录下，生成项目文件时使用：

| 模板 | 生成的文件 | 关键占位符 |
|------|-----------|-----------|
| `assets/CLAUDE.md.tmpl` | 项目根目录 `CLAUDE.md` | `{项目名称}`, `{技术栈条目}` |
| `assets/PROJECT_MEMORY.md.tmpl` | `docs/PROJECT_MEMORY.md` | `{项目名称}`, `{模块信息}`, `{API列表}` |
| `assets/CURRENT_TASK.md.tmpl` | `docs/CURRENT_TASK.md` | `{current_time}`, `{session_id}` |
| `assets/SESSION_LOG.md.tmpl` | `docs/SESSION_LOG.md` | `{session_id}`, `{git_diff_stat}` |
| `assets/DECISIONS.md.tmpl` | `docs/DECISIONS.md` | `{ADR编号}`, `{决策标题}` |

生成文件时：先读模板 → 替换占位符 → 写入项目。模板内的 `<!-- -->` HTML 注释是对用户的说明，不要删除。

---

## 交互规范

| 规范 | 规则 |
|------|------|
| 编码 | UTF-8 |
| 语言 | 跟随用户使用的语言（中文/英文/混合均可） |
| 路径 | 项目内用相对路径 |
| 状态图标 | ✅ 已完成 · 🔄 进行中 · ⏳ 待开始 · ❌ 阻塞 |
| 优先级 | P0 阻塞 · P1 高 · P2 中 · P3 低 |
| 时间格式 | `YYYY-MM-DD HH:MM` |

---

## 边界与安全

- **敏感信息**：生成模板或写入文件时，绝不包含密钥、密码、Token。如果用户在对话中提供了敏感信息，不要写入记忆文件。
- **CLAUDE.local.md**：读取但不写入。这是用户的私有指令文件。
- **授权边界**：只修改 `docs/` 目录下的记忆文件和 `CLAUDE.md`，不修改其他文件。
- **Git 仓库**：如果检测到 `.git` 目录，建议将 `CLAUDE.local.md` 加入 `.gitignore`。
- **日志归档**：SESSION_LOG.md 默认保留最近 3 个月内容。每月提醒用户是否需要归档旧条目。
- **覆盖保护**：生成文件前检查是否已存在，如已有内容则询问"覆盖/跳过/合并"。

---

## 快速参考

```bash
# 初始化
/rehydration init

# 恢复
/rehydration

# 工作中
/memory status          # 看状态
/memory update          # 存进度
/memory decision        # 记决策
/memory log             # 写日志

# 结束
/memory dehydrate       # 保存一切
```
