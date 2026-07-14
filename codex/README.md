# Codex Skills Collection

本目录包含 Codex 专属 skills,安装到 `~/.agents/skills/` 和 `~/.codex/skills/` 后即可使用。

## 与 claude/ 目录的关系

- `claude/` — Claude Code 专属 skills(不适用于 Codex)
- `codex/` — Codex 专属 skills(本目录)

新增 skill 时需同步创建同名 skill 于两个目录下,分别遵循各自范式。

## 安装

```bash
python install.py
```

## 可用 Skills

| Skill | 说明 |
|-------|------|
| `moduleskill2global` | 在项目级和全局级之间移动 skill |
| `rehydration-mode-v3` | 再水化记忆系统 V3 — 三层记忆 + 周封存 |
| `zsh` | 跨 Agent 项目记忆：统一导航、薄适配、任务恢复与历史归档 |

## 新增 Skill

1. 创建 `<skill-name>/SKILL.md`(含 YAML frontmatter)
2. 可选添加 `scripts/`、`references/`、`assets/`
3. 模仿已有 skill 的写法风格
