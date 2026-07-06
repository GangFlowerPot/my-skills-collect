# CODEX.md

本目录是 **Codex 专用 skills 集合**,每个子目录对应一个完整的 Codex skill。

## 与 claude/ 目录的区分

| 目录 | 用途 | 安装位置 |
|------|------|----------|
| `claude/` | Claude Code 专属 skills | `~/.agents/skills/` + `~/.claude/skills/` |
| `codex/` | Codex 专属 skills | `~/.agents/skills/` + `~/.codex/skills/` |

两个目录互不可见、互不干扰。新增 skill 时需要**同步创建同名 skill** 于两个目录下,分别遵循各自的 skill 范式:
- `claude/<skill-name>/SKILL.md` — 遵循 Claude Code skill 规范
- `codex/<skill-name>/SKILL.md` — 遵循本目录已有 skill 的写法风格

## 当前可用 Skills

| Skill | 说明 | 安装位置 |
|-------|------|----------|
| `moduleskill2global` | 在项目级和全局级之间移动 skill | `~/.agents/skills/` + `~/.codex/skills/` |
| `rehydration-mode-v3` | 再水化记忆系统 V3 — 三层记忆 + 周封存 | `~/.agents/skills/` + `~/.codex/skills/` |

## 安装

```bash
# 一键安装
python install.py

# 或手动复制
cp -r moduleskill2global ~/.agents/skills/
cp -r moduleskill2global ~/.codex/skills/
cp -r rehydration-mode-v3 ~/.agents/skills/
cp -r rehydration-mode-v3 ~/.codex/skills/
```

## 新增 Skill 规范

1. 创建同名子目录:`<skill-name>/`
2. 编写 `SKILL.md`(必须含 YAML frontmatter:`name` + `description`)
3. 可选添加 `scripts/`、`references/`、`assets/` 子目录
4. 模仿已有 skill 的写法风格