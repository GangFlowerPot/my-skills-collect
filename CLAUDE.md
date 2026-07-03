# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **personal Claude Code skills collection** — a Git repository that syncs custom skills across multiple machines. Each subdirectory is a complete, self-contained skill installable via `npx skills add` or the bundled `install.py` script.

**Repository**: `D:\claudeCode\skills\my-skills-collect\`
**Remote**: synced via Git for multi-machine use

### Available Skills

| Skill | Description | Status |
|-------|-------------|--------|
| `moduleskill2global` | Move skills between project-level and global-level installation | Active |
| `rehydration-mode-v3` | 再水化记忆系统 V3 — 三层记忆 + 周封存 + claude-mem 集成 + Java 全栈检测 | Active |
| `rehydration-mode-v2` | 再水化记忆系统 V2（旧版，仍可用） | Legacy |
| `rehydration-mode-v1` | 已废弃，仅保留作历史参考 | Deprecated |

### Repository Structure

```
my-skills-collect/
├── CLAUDE.md                              ← 本文件（行为规则）
├── README.md                              ← 面向用户的安装说明文档
├── install.py                             ← 一键安装脚本（Python，跨平台）
├── install.bat                            ← Windows 双击启动器
├── install.sh                             ← Linux/macOS 启动器
├── moduleskill2global/                    ← skill 目录
├── rehydration-mode-v3/                   ← skill 目录（含 SKILL.md/scripts/references/assets）
├── rehydration-mode-v2/                   ← skill 目录
└── rehydration-mode-v1/                   ← skill 目录（废弃）
```

---

## 行为规则

### 1. 会话启动时同步远程

每次新会话开始处理本仓库的事务前，**必须先执行 `git pull`** 拉取远程最新变更，确保本地与远程同步。

```bash
cd "D:/claudeCode/skills/my-skills-collect" && git pull origin main
```

- 如果有远程新变更，先告知用户拉取的内容
- 如果本地有未提交的变更，先 stash 再 pull，然后 pop
- 如果 pull 导致冲突，通知用户手动解决

### 2. 仓库认知

这是一个 **skill 集合仓库**，不是普通代码仓库。每次操作时需记住：
- 每个子目录是一个完整的 Claude Code skill
- 修改 skill 内容后需要同步到全局 skills 目录（`~/.claude/skills/`）
- 所有变更通过 Git 推送到远程仓库实现多机同步
- `README.md` 是面向其他用户的安装说明，应保持简洁清晰

### 3. Skill 添加/更新后的 Git 推送

每次添加新 skill、更新现有 skill、或修改安装脚本后，自动提交并推送到远程仓库。

**流程**：
```
1. git add -A
2. git commit -m "<message>"
3. git show --stat HEAD → 展示即将推送的文件列表
4. 用户回复 "1" 确认后 → git push origin main
```

> **确认方式**：用户回复 `1` 即表示确认推送。

**示例交互**：
```
📋 即将推送到 origin/main：

  docs: update CLAUDE.md with new behavior rules

  ——  CLAUDE.md    (+22 行)

回复 "1" 确认推送。
```

用户回复 `1` 后执行 `git push origin main`。

### 4. Skill 创建规范

创建或改进 skill 时，**严格遵循 `/skill-creator` skill 的规范**：

- 编写 SKILL.md 前先确定 name 和 description（触发关键词）
- description 要足够"主动触发"（pushy），覆盖各种表达方式
- SKILL.md 控制在 500 行以内，超出时拆分到 references/ 子文件
- 脚本兼容 Python 2.7+ 和 Python 3.x（避免 pathlib、f-strings、type hints）
- Windows 下链接使用 `mklink /J`（Junction，免管理员），Unix 用 `ln -s`
- 创建后编写 2-3 个测试用例并运行评估
- 迭代改进直到满意
- 最终打包为 .skill 文件

### 4. README.md 维护

每次添加/更新 skill 后，同步更新 README.md：
- Available Skills 表格中添加新 skill
- 安装命令更新
- 功能概览更新
- 评测结果更新（如有）

---

## 关键文件路径

| 文件 | 路径 |
|------|------|
| 本文件 | `D:\claudeCode\skills\my-skills-collect\CLAUDE.md` |
| 用户文档 | `D:\claudeCode\skills\my-skills-collect\README.md` |
| 安装脚本 | `D:\claudeCode\skills\my-skills-collect\install.py` |
| V3 使用手册 | `D:\claudeCode\skills\my-skills-collect\rehydration-mode-v3\MANUAL.md` |
| V3 主指令 | `D:\claudeCode\skills\my-skills-collect\rehydration-mode-v3\SKILL.md` |
