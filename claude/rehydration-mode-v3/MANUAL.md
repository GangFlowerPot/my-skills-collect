# Rehydration Mode V3 — 使用手册

> 版本：v3.0 | 更新日期：2026-07-03

---

## 目录

1. [产品简介](#1-产品简介)
2. [安装指南](#2-安装指南)
3. [快速上手](#3-快速上手)
4. [命令参考](#4-命令参考)
5. [文件结构详解](#5-文件结构详解)
6. [工作流程](#6-工作流程)
7. [三层记忆模型](#7-三层记忆模型)
8. [SESSION_LOG 日志系统](#8-session_log-日志系统)
9. [claude-mem 集成](#9-claude-mem-集成)
10. [最佳实践](#10-最佳实践)
11. [故障排除](#11-故障排除)

---

## 1. 产品简介

**Rehydration Mode V3** 是一个跨会话状态持久化系统，通过结构化 Markdown 文件将你的工作上下文「脱水」保存到磁盘，下次会话时「再水化」恢复，让你感觉「好像没有离开过」。

### V3 相比 V2 的核心升级

| 能力 | V2 | V3 |
|------|----|----|
| Java 框架检测 | 基础 Spring Boot | Spring Boot/Cloud/Security + Mybatis-Plus + Nacos + Kafka + Redis + ShardingSphere + Oracle/达梦 |
| 中间件检测 | 无 | Nacos/Eureka/Kafka/Redis/ES/ShardingSphere/Druid/... |
| 构建工具 | 基础 Maven/Gradle | 多模块项目检测 |
| SESSION_LOG | 单文件，头部插入 | **小时级 + 天级汇总 + 自然周归档**，追加写入 |
| PROJECT_MEMORY | 单层扁平结构 | **🔥热/🌡️温/❄️冷三层记忆** + 自动压缩 |
| claude-mem 集成 | 无 | 结构化摘要与原始内容互补，去重恢复 |
| 脚本数量 | 2 | **4**（+session_log_manager + memory_compressor） |

### 核心理念

```
脱水（Dehydrate）= 把易失的会话上下文 → 序列化到磁盘
再水化（Rehydrate） = 从磁盘文件 → 恢复到工作状态
```

---

## 2. 安装指南

### 前置条件

- Claude Code 已安装
- Python 2.7+ 或 Python 3.x 可用（脚本兼容两者）

### 方式一：从 Git 仓库安装（推荐，支持多机同步）

```bash
# 全局安装（所有项目可用）
npx skills add https://github.com/<your-username>/my-skills-collect --skill rehydration-mode-v3 -g -y

# 仅当前项目安装
cd <project-dir>
npx skills add https://github.com/<your-username>/my-skills-collect --skill rehydration-mode-v3 -y
```

### 方式二：本地安装（仓库未上线前使用）

#### Windows

```bash
# 1. 复制到全局 agents 目录
xcopy /E /I "D:\claudeCode\skills\my-skills-collect\rehydration-mode-v3" "%USERPROFILE%\.agents\skills\rehydration-mode-v3"

# 2. 复制到 Claude Code skills 目录
xcopy /E /I "D:\claudeCode\skills\my-skills-collect\rehydration-mode-v3" "%USERPROFILE%\.claude\skills\rehydration-mode-v3"

# 3. 重新加载（在 Claude Code 中）
# 输入: /reload-plugins
```

#### macOS / Linux

```bash
# 一步到位
cp -r ./rehydration-mode-v3 ~/.agents/skills/ && ln -s ~/.agents/skills/rehydration-mode-v3 ~/.claude/skills/rehydration-mode-v3

# 重新加载（在 Claude Code 中）
# 输入: /reload-plugins
```

### 方式三：npx skills 安装

```bash
npx skills add ~/.agents/skills/rehydration-mode-v3 -g -y
```

### 验证安装

```bash
# 列出所有全局 skills
npx skills list -g

# 预期输出包含: rehydration-mode-v3
```

或在 Claude Code 中直接问：「你现在有哪些可用的 skills？」

### 卸载

```bash
# 删除全局 skill
rm -rf ~/.agents/skills/rehydration-mode-v3
rm -rf ~/.claude/skills/rehydration-mode-v3

# 或通过 npx
npx skills remove rehydration-mode-v3 -g -y
```

---

## 3. 快速上手

### 第一次使用（初始化项目记忆系统）

在 Claude Code 中对任意项目说：

```
帮我初始化项目的记忆系统
```

或直接：

```
/rehydration init
```

Claude 会自动：
1. 运行 `detect_project.py` 检测项目技术栈
2. 展示检测结果并请你确认
3. 生成完整的记忆文件结构

**示例交互**：

```
📋 项目检测结果:
   名称: pt_back
   技术栈: Java | Maven | Spring Boot + Spring Cloud + Spring Security +
           Mybatis + Mybatis-Plus + Hystrix |
           Nacos + Kafka + Redis + ShardingSphere + Dynamic-Datasource |
           Oracle + MySQL + SQL Server + 达梦
   Git 仓库: 否

我将创建以下记忆文件:

  ✅ CLAUDE.md               — 启动指令（每次进入自动加载）
  ✅ docs/PROJECT_MEMORY.md  — 项目整体记忆（🔥热/🌡️温/❄️冷三层）
  ✅ docs/CURRENT_TASK.md    — 当前任务状态（热恢复核心）
  ✅ docs/SESSION_LOG.md     — 会话日志（小时级 + 天级 + 周归档）
  ✅ docs/DECISIONS.md       — 架构决策记录（ADR）

确认以上信息？有什么需要补充或修改的？
```

### 日常使用

| 场景 | 你说 | Claude 做 |
|------|------|-----------|
| 继续上次工作 | `继续` | 读取记忆文件，汇报状态 |
| 更新任务进度 | `更新当前任务` | 对话式更新 CURRENT_TASK.md |
| 记录架构决策 | `记录一个决策` | 追加 ADR 到 DECISIONS.md |
| 保存进度 | `保存进度` 或 `今天到这` | 脱水：更新所有文件 |
| 快速看状态 | `现在什么情况` | 汇总所有记忆文件的关键信息 |
| 清理记忆 | `整理记忆` | 分析三层结构，给出压缩建议 |

---

## 4. 命令参考

### 完整命令表

| 命令 | 触发词 | 功能 |
|------|--------|------|
| `/rehydration init` | "初始化记忆系统"、"创建项目记忆" | 检测项目 + 生成所有记忆文件 |
| `/rehydration` | "继续"、"接着做"、"上次做到哪了" | 恢复上下文，汇报当前状态 |
| `/memory status` | "现在什么情况"、"记忆状态" | 汇总所有记忆文件的关键信息 |
| `/memory update` | "更新任务"、"任务进度" | 对话式更新 CURRENT_TASK.md |
| `/memory log` | "记录日志"、"追加日志" | 追加小时级条目到 SESSION_LOG.md |
| `/memory decision` | "记录决策"、"ADR" | 追加架构决策到 DECISIONS.md |
| `/memory compress` | "整理记忆"、"记忆压缩" | 分析三层结构 + 压缩建议 |
| `/memory dehydrate` | "保存进度"、"今天到这" | 会话结束前同步所有状态 |

### 辅助脚本（可手动运行）

```bash
# 检测项目技术栈
python <skill_dir>/scripts/detect_project.py <project_root>

# 检查记忆文件结构
python <skill_dir>/scripts/check_structure.py <project_root>

# SESSION_LOG 当前周信息
python <skill_dir>/scripts/session_log_manager.py <project_root> current_week

# SESSION_LOG 跨周封存检查
python <skill_dir>/scripts/session_log_manager.py <project_root> archive

# SESSION_LOG 读取最新日志
python <skill_dir>/scripts/session_log_manager.py <project_root> read_latest

# PROJECT_MEMORY 结构分析
python <skill_dir>/scripts/memory_compressor.py <project_root> analyze

# PROJECT_MEMORY 获取压缩建议
python <skill_dir>/scripts/memory_compressor.py <project_root> compress

# PROJECT_MEMORY 快速统计
python <skill_dir>/scripts/memory_compressor.py <project_root> stats
```

---

## 5. 文件结构详解

初始化后，项目目录结构如下：

```
project-root/
├── CLAUDE.md                         ← 自动加载的启动指令
├── CLAUDE.local.md                   ← 用户私有指令（可选，只读）
└── docs/
    ├── PROJECT_MEMORY.md             ← 项目记忆（🔥热/🌡️温/❄️冷三层）
    ├── CURRENT_TASK.md               ← 当前任务状态
    ├── SESSION_LOG.md                ← 当前周会话日志
    ├── session-log-2026-W27.md       ← 历史周归档（示例）
    ├── session-log-2026-W26.md       ← 历史周归档（示例）
    └── DECISIONS.md                  ← 架构决策记录
```

### 各文件职责

| 文件 | 更新频率 | 更新时机 | 格式 |
|------|----------|----------|------|
| `CLAUDE.md` | 极少 | 项目规则变更时 | Markdown |
| `PROJECT_MEMORY.md` | 低频 | 架构变更时 | Markdown（三层结构） |
| `CURRENT_TASK.md` | 每次会话 | 会话开始/结束时 | Markdown |
| `SESSION_LOG.md` | 每次会话 | 会话结束时追加 | Markdown（小时+天） |
| `session-log-YYYY-WXX.md` | 自动 | 跨周时自动归档 | Markdown（只读） |
| `DECISIONS.md` | 按需 | 有架构决策时 | Markdown（ADR 格式） |

---

## 6. 工作流程

### 完整的一天工作流

```
┌──────────────────────────────────────────────────────────────┐
│ 上午 09:00 — 会话开始                                         │
│                                                               │
│  用户说: "继续上次的工作"                                       │
│  Claude: 读取 CURRENT_TASK.md                                  │
│        → 读取 PROJECT_MEMORY.md 热记忆层                       │
│        → 检查 SESSION_LOG.md 是否需要跨周封存                    │
│        → 汇报: "阶段 v0.5，进行中 2 项，阻塞 1 项"               │
│        → 问: "继续还是做别的？"                                  │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ 上午 09:00-12:00 — 工作中                                     │
│                                                               │
│  用户: "更新当前任务，订单接口完成了，开始做发票接口"              │
│  Claude: 对话式更新 CURRENT_TASK.md                            │
│                                                               │
│  用户: "记录个决策：发票模块也用策略工厂，不走 AOP"               │
│  Claude: 追加 ADR-003 到 DECISIONS.md                        │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ 中午 12:00 — 午休保存                                         │
│                                                               │
│  用户: "保存进度，下午继续"                                     │
│  Claude: 1. 更新 CURRENT_TASK.md（发票接口 30%）               │
│        2. 追加 SESSION_LOG.md（小时级条目 09:00-12:00）         │
│        3. 检查跨周封存                                          │
│        → "已保存"                                              │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ 下午 14:00 — 恢复工作                                         │
│                                                               │
│  用户说: "继续"                                               │
│  Claude: 读取记忆文件 → 汇报状态 → 定位到发票接口                │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ 下午 18:00 — 下班封存                                         │
│                                                               │
│  用户: "今天到这"                                              │
│  Claude: 1. 更新 CURRENT_TASK.md（发票接口 80%）               │
│        2. 追加 SESSION_LOG.md（小时级条目 14:00-18:00）         │
│        3. 填写 ## 2026-07-03 日汇总                           │
│        4. 如有决策，更新 DECISIONS.md                          │
│        → "记忆已持久化"                                        │
└──────────────────────────────────────────────────────────────┘
```

### 跨周自动封存

```
周一早上 09:00，用户说 "继续"

Claude 检测到 SESSION_LOG.md 中有上周（W26）的条目
→ 自动将旧内容归档到 docs/session-log-2026-W26.md
→ 重置 SESSION_LOG.md 为新周（W27）头部
→ 开始记录新的一周
```

---

## 7. 三层记忆模型

### 模型概览

```
🔥 热记忆（Hot）   — 最近 7 天频繁使用的核心信息
  ├── 项目概述（2-3 句话）
  ├── 架构概览（Mermaid 图）
  ├── 当前活跃模块表
  ├── 核心 API（最近使用）
  └── 关键约定（命名/代码/分支）
  限制: < 200 行，占比 < 60%
  策略: 保持完整，不压缩

🌡️ 温记忆（Warm）  — 7-30 天内使用过的次要信息
  ├── 数据模型（实体关系图、表结构）
  ├── 已知问题 / 技术债务
  ├── 环境信息（开发/测试/生产地址）
  ├── 中间件配置
  └── 模块细节（非活跃模块）
  限制: < 100 行
  策略: 14 天未引用 → 精简为 1-2 行摘要

❄️ 冷记忆（Cold）  — 30 天+ 历史信息
  ├── 已废弃决策（标题 + ADR 指针）
  ├── 历史环境（已下线）
  ├── 历史 API（已废弃）
  └── 已完成里程碑（标题 + 日期）
  限制: < 50 行
  策略: 保留标题 + 摘要指针
```

### 记忆降级示例

**温记忆中的详细条目**（刚记录时）：

```markdown
1. **数据库连接池配置不合理**
   - 问题: Druid 连接池 maxActive=500，实际并发只有 50
   - 影响: 高并发时可能连接耗尽
   - 计划: v0.6 优化连接池配置
   - 优先级: P2
   - 更新: 2026-06-15
```

**14 天后未引用，自动精简为**：

```markdown
- **Druid 连接池配置** — maxActive=500 过高，计划 v0.6 优化（详见 SESSION_LOG 2026-W24）
```

**30 天后，降级到冷记忆**：

```markdown
- **Druid 连接池配置** — 已于 v0.6 优化完成，详见 ADR-005
```

### 压缩检查命令

```bash
# 分析当前记忆健康度
python <skill_dir>/scripts/memory_compressor.py <project_root> analyze

# 示例输出：
# {
#   "tiers": {
#     "热记忆": {"line_count": 120, "percentage": 45.0},
#     "温记忆": {"line_count": 85, "percentage": 32.0},
#     "冷记忆": {"line_count": 60, "percentage": 23.0}
#   },
#   "suggestions": [
#     {"type": "compress_warm", "message": "温记忆中发现 3 条可能过时的条目"}
#   ]
# }
```

---

## 8. SESSION_LOG 日志系统

### 文件命名规则

| 文件 | 用途 | 生命周期 |
|------|------|----------|
| `docs/SESSION_LOG.md` | 当前周活跃日志 | 本周持续追加 |
| `docs/session-log-2026-W27.md` | 第 27 周归档 | 跨周后生成，只读 |
| `docs/session-log-2026-W26.md` | 第 26 周归档 | 只读 |

### 小时级条目格式（每次会话追加）

```markdown
### 14:00 实现发票模块策略工厂钩子

**任务**: 为 SzxmYwFapiaoBeforeAdd 钩子实现校验逻辑

**完成的工作**:

1. 实现了发票金额校验钩子
   - 文件: `service/SzxmYwFapiaoMethods/SzxmYwFapiaoBeforeAdd.java`（+45 行）
   - 包含: 金额上限校验、税率一致性校验、异常抛出 veto 模式

2. 添加了单元测试
   - 文件: `test/.../SzxmYwFapiaoBeforeAddTest.java`（+80 行）
   - 覆盖: 正常金额、超限金额、边界值、异常场景

**关键决策**:
- 决定: 使用 RuntimeException 抛出而非返回错误码
- 原因: 与现有 WReqMstBeforeDelete 钩子保持一致
- 记录: 见 `docs/DECISIONS.md#adr-003`

**遇到的问题**:

1. Aviator 脚本引擎对 BigDecimal 精度处理有问题
   - 解决: 改用 SqlAviaFunction 包装 SQL 取精度

**遗留工作**:
- 需要补充集成测试

**代码变更**:

```bash
git diff --stat
 .../SzxmYwFapiaoBeforeAdd.java       | 45 +++++++++
 .../SzxmYwFapiaoBeforeAddTest.java   | 80 ++++++++++++++
 2 files changed, 125 insertions(+)
```
```

### 天级汇总格式（每天首次/末次会话）

```markdown
## 2026-07-03 日汇总

**今日完成**: 发票模块策略工厂钩子实现（80%），单元测试覆盖率 90%

**关键决策**: 策略工厂钩子统一使用 RuntimeException veto 模式（ADR-003）

**遗留问题**: 集成测试待补充，Aviator 精度问题已绕过

**明日计划**: 完成发票集成测试，开始验收模块开发
```

### 周封存规则

```
触发条件: 检测到文件中存在属于上一周（ISO 周）的日期条目
归档目标: docs/session-log-{上周标识}.md（如 session-log-2026-W26.md）
重置内容: 当前文件只保留新周头部
周标识格式: YYYY-WXX（ISO 8601 周编号，如 2026-W27 = 2026年第27周）
读取顺序: 先读当前文件末尾 → 如不足则读最近的历史周文件
```

---

## 9. claude-mem 集成

### 为什么需要两个系统

| | rehydration-mode-v3 | claude-mem |
|--|---------------------|------------|
| 存储内容 | **结构化摘要**（架构/任务/日志/决策） | **原始会话内容**（代码/命令/输出） |
| 类比 | 项目 Wiki + 工作日志 | 浏览器历史记录 |
| 特点 | 精炼、可搜索、按层管理 | 完整、按时间线、自动捕获 |

### 推荐恢复流程

```
会话开始
    │
    ▼
1. 读取 PROJECT_MEMORY.md 热记忆层 → 了解项目全貌
    │
    ▼
2. 读取 CURRENT_TASK.md → 了解当前进度
    │
    ▼
3. 读取 SESSION_LOG.md 最新条目 → 了解最近工作
    │
    ▼
4. 如需具体代码/命令细节 → 查询 claude-mem
    │
    ▼
开始工作
```

### 安装 claude-mem

```bash
# 方式 1
/plugin install thedotmack/claude-mem

# 方式 2
/plugin marketplace add thedotmack/claude-mem
```

### 去重原则

- **不写入 rehydration-mode-v3**：完整代码片段、命令输出、错误堆栈、API 响应
- **不写入 claude-mem**：项目架构概述、任务列表、ADR 决策记录（这些信息在 rehydration-mode-v3 中已结构化存储）

---

## 10. 最佳实践

### 日常习惯

1. **会话开始时**：说"继续"让 Claude 恢复上下文
2. **任务变更时**：说"更新任务"同步进度
3. **做决策时**：说"记录决策"保存 ADR
4. **会话结束时**：说"保存进度"或"今天到这"触发脱水
5. **每周一次**：说"整理记忆"检查三层结构健康度

### 周报生成

每周五下班时，Claude 可以基于 SESSION_LOG.md 的当天汇总自动生成周报：

```
用户说: "生成本周周报"
Claude: 读取本周 SESSION_LOG.md 的所有天级汇总
      → 聚合为周报格式
      → 包含: 本周完成、关键决策、遗留问题、下周计划
```

### 多人协作

- `docs/` 下的文件可以提交到 Git，团队成员共享项目记忆
- `CLAUDE.local.md` 是个人私有文件，不应提交（已在 .gitignore 建议中）
- 每个人可以有自己的 claude-mem 存储，不冲突

### Java 项目专属建议

对于 Java 企业级项目（如 Spring Cloud 微服务）：

1. **热记忆中记录**：微服务拓扑（gateway → service → mapper）、核心实体前缀约定（SzxmDm/SzxmYw/Hc）
2. **温记忆中记录**：数据库连接信息、Nacos 配置项、Kafka Topic 列表
3. **DECISIONS 中记录**：接口设计决策、中间件选型理由、版本兼容性处理
4. **SESSION_LOG 中记录**：模块开发进度、调试发现、集成问题

---

## 11. 故障排除

### 问题：记忆文件没有自动更新

**原因**：Claude 可能忘记在会话结束时脱水。

**解决**：
```
你对 Claude 说: "保存进度" 或 "今天到它"
或: /memory dehydrate
```

### 问题：恢复时信息不正确

**原因**：记忆文件可能过时或手动编辑时格式被破坏。

**解决**：
```bash
# 检查文件结构健康度
python <skill_dir>/scripts/check_structure.py <project_root>
```

根据输出修复问题，或重新运行 `/memory update` 同步状态。

### 问题：SESSION_LOG.md 文件过大

**原因**：长期未封存或从未压缩。

**解决**：
```bash
# 检查是否需要跨周封存
python <skill_dir>/scripts/session_log_manager.py <project_root> archive

# 检查周文件列表
python <skill_dir>/scripts/check_structure.py <project_root>
```

手动执行封存，或让 Claude 执行 `/memory dehydrate`（会自动触发封存检查）。

### 问题：PROJECT_MEMORY.md 热记忆层过大

**原因**：过多内容放在热记忆，未及时降级。

**解决**：
```bash
# 分析各层大小
python <skill_dir>/scripts/memory_compressor.py <project_root> analyze

# 获取压缩建议
python <skill_dir>/scripts/memory_compressor.py <project_root> compress
```

根据建议将温记忆中的旧条目精简，将冷记忆中的内容提取摘要。

### 问题：检测脚本无法运行

**原因**：Python 环境问题或 pathlib 缺失。

**解决**：
```bash
# 检查 Python 版本
python --version

# V3 脚本兼容 Python 2.7+ 和 Python 3.x
# 如果报错 ImportError: No module named pathlib，说明是 Python 2.7
# V3 脚本已移除 pathlib 依赖，使用 os.path 替代
```

### 问题：claude-mem 与 rehydration-mode-v3 内容重复

**原因**：可能把架构决策同时写入了两个系统。

**解决**：遵循去重原则：
- rehydration-mode-v3 只存**结构化摘要**
- claude-mem 只存**原始会话内容**
- 恢复时先读 rehydration-mode-v3，再按需查 claude-mem

---

## 附录：命令速查表

| 你想做什么 | 说什么/做什么 |
|-----------|--------------|
| 初始化记忆系统 | `/rehydration init` 或 "初始化记忆系统" |
| 恢复上次工作 | `/rehydration` 或 "继续" |
| 看当前状态 | `/memory status` 或 "现在什么情况" |
| 更新任务进度 | `/memory update` 或 "更新任务" |
| 记录架构决策 | `/memory decision` 或 "记录决策" |
| 追加会话日志 | `/memory log` 或 "记录日志" |
| 整理记忆结构 | `/memory compress` 或 "整理记忆" |
| 保存并结束 | `/memory dehydrate` 或 "保存进度" |

---

*本手册适用于 rehydration-mode-v3 | 最后更新: 2026-07-03*
