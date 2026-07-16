# Agent 薄适配协议

平台入口只负责告诉 Agent 读取 `AGENT_MEMORY.md`，不复制任务、架构、日志或决策。

## 跨 Agent 通用入口：AGENTS.md

`AGENTS.md` 是跨 Agent 的通用薄适配入口（codex / OpenCode / cursor 等），
ZSH 管理其中从 `<!-- ZSH:START -->` 到 `<!-- ZSH:END -->` 的唯一完整区块。
标记外内容属于用户。出现重复、缺失或反向标记时停止写入。

当前 Codex 版本不生成 `CLAUDE.md`、`CODEX.md` 或其他平台专属入口。其他 Agent 可读取 `AGENTS.md`，或直接读取 `AGENT_MEMORY.md`。

## Claude Code 专属入口：CLAUDE.md 托管区块

Claude Code 自动加载 `CLAUDE.md`，因此 ZSH 在 `CLAUDE.md` 中额外维护一个托管区块
（`<!-- ZSH:MEMORY:START -->` 到 `<!-- ZSH:MEMORY:END -->`），
让 Claude 在会话启动时就能感知本项目使用 ZSH 记忆系统。

设计要点：

- 托管区块使用 `ZSH:MEMORY` 标记，与 codex 版在 `AGENTS.md` 中的 `ZSH:START` 标记**互相隔离**，
  避免跨 Agent 串扰。
- 托管区块内容（`assets/zsh_memory.block.tmpl`）是 **agent-agnostic** 的：
  不含任何 agent 私有路径，只描述「读 `AGENT_MEMORY.md`、ZSH 项目记忆权威、写回协议」。
- ZSH 仅更新 `ZSH:MEMORY` 区块内部，**绝不覆写 `CLAUDE.md` 中的原生内容**（auto-memory）。
- `CLAUDE.local.md` 是用户私有原生记忆，ZSH **只读不写**。

## 权威规则

适配区块声明：ZSH 项目记忆高于 Agent 原生记忆（含 Claude Code 的 auto-memory）；
会话结束前对经过验证的项目事实执行增量回写，重复跳过，冲突先确认。

claude-mem 的分工见 `references/claude_mem_integration.md`。
