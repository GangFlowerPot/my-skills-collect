# ZSH 使用手册

ZSH 为项目提供跨 Agent 共享记忆。它把可核查的工作状态写入项目文件，而不是依赖某个模型保存隐式会话状态。

## 初始化

```powershell
python scripts/init_memory.py <project_root> --dry-run
python scripts/init_memory.py <project_root> --apply
```

第一次命令只显示计划，第二次才写入。已有核心记忆文件不会被覆盖。

默认 Git 策略为 `auto`：Git 项目中的记忆随项目版本化，非 Git 项目只做本地文件维护。个人 Git 项目若不希望提交记忆，可在两个命令中加入 `--git-policy local`。

## 日常使用

- “继续上次”：按 `AGENT_MEMORY.md` 恢复上下文。
- “更新当前任务”：同步当前状态和续接位置。
- “记录决策”：追加 ADR。
- “保存进度”：更新任务、追加日志并检查归档。
- “整理记忆”：分析热/温/冷三层大小并给出压缩建议。

保存进度前，Agent 会把本次会话和自身原生记忆中的项目相关信息提取为候选项，执行增量回写检查。ZSH 项目记忆是跨 Agent 的权威持久化来源；重复内容跳过，冲突内容等待确认，敏感信息拒绝写入。

## 健康检查

```powershell
python scripts/validate_navigation.py <project_root>
python scripts/check_structure.py <project_root>
```

两个命令均为只读。前者验证导航路径和适配区块，后者汇总记忆文件状态。

辅助脚本要求 Python 3.8+。没有 Python 时，Agent 仍可按照 Markdown 导航手动读取和更新记忆。
