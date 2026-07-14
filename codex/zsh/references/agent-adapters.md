# Agent 薄适配协议

平台入口只负责告诉 Agent 读取 `AGENT_MEMORY.md`，不复制任务、架构、日志或决策。

ZSH 管理 `AGENTS.md` 中从 `<!-- ZSH:START -->` 到 `<!-- ZSH:END -->` 的唯一完整区块。标记外内容属于用户。出现重复、缺失或反向标记时停止写入。

当前 Codex 版本不生成 `CLAUDE.md`、`CODEX.md` 或其他平台专属入口。其他 Agent 可读取 `AGENTS.md`，或直接读取 `AGENT_MEMORY.md`。

适配区块还应声明：ZSH 项目记忆高于 Agent 原生记忆；会话结束前对经过验证的项目事实执行增量回写，重复跳过，冲突先确认。
