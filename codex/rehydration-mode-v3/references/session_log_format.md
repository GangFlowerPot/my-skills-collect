# SESSION_LOG 格式规范（V3）

## 文件结构

```
docs/
├── SESSION_LOG.md                  ← 当前周活跃日志（追加写入）
├── session-log-2026-W26.md         ← 历史周封存（只读）
├── session-log-2026-W27.md         ← 历史周封存（只读）
└── ...
```

## 小时级条目格式

每次会话结束时追加：

```markdown
### {HH:MM} {会话标题}

**任务**: {用 1-2 句话描述本次会话的目标}

**完成的工作**:

1. {完成的工作项 1}
   - 文件: `{file_path}`（{行数}行）
   - 包含: {功能点描述}

2. {完成的工作项 2}
   - 文件: `{file_path}`
   - 包含: {功能点描述}

**关键决策**:
- 决定: {决策内容}
- 原因: {决策原因}
- 记录: 见 `docs/DECISIONS.md#adr-xxx`

**遇到的问题**:

1. {问题描述}
   - 解决: {解决方案（或"暂未解决，记录为阻塞项"）}

**遗留工作**:
- {遗留工作项 1}
- {遗留工作项 2}

**代码变更**:

```bash
git diff --stat
 {file_1}  | {+++} / {---}
 {file_2}  | {+++} / {---}
```
```

## 天级汇总格式

每天第一次会话时创建标题，当天最后一次会话后填写内容：

```markdown
## {YYYY-MM-DD} 日汇总

**今日完成**: {概述当天完成的主要工作}

**关键决策**: {当天做出的重要决策，指向 DECISIONS.md}

**遗留问题**: {当天未解决的问题}

**明日计划**: {明天打算做什么}
```

## 周文件头部格式

```markdown
# 会话日志 — {YYYY-WXX}

**周期**: {YYYY-MM-DD} ~ {YYYY-MM-DD}（第 XX 周）

---

（小时级条目和天级汇总按时间顺序排列，最新在最下面）
```

## 封存规则

- 当检测到当前文件中有属于上一周的条目时，触发封存
- 封存后原内容移到 `session-log-{上周标识}.md`
- 当前文件重置为只有头部的新周文件
- 封存命令：`python <skill_dir>/scripts/session_log_manager.py <project_root> archive`

## 读取规则

- 默认读取 `docs/SESSION_LOG.md` 的最新条目（文件末尾）
- 如需历史记录，读取对应的 `session-log-YYYY-WXX.md`
- 读取命令：`python <skill_dir>/scripts/session_log_manager.py <project_root> read_latest`
