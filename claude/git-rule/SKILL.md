---
name: git-rule
description: Git 工作流准则 — 会话同步、推送确认、推送重试策略。当用户进行 git commit/push/pull/sync 操作、讨论 git 工作流、推送代码、同步远程仓库、或说"推送""同步""git""commit""pull""push"时，务必使用此 Skill。即使用户没有明确提到 skill 名称，只要涉及 git 仓库的推送/同步/提交流程，都应主动触发此 Skill 的规范。
---

# Git Rule — Git 工作流准则

## 何时使用这个 Skill

只要涉及以下任意一种情况，**必须**使用此 Skill 的规范：

- 用户说"推送""push""同步""sync""commit""提交""pull""拉取"
- 用户要求或暗示需要进行 git 操作
- 会话开始，需要与远程仓库同步
- 工作区有变更需要提交到远程仓库
- 任何 git remote 相关操作

## 能力 A：会话启动同步

每次新会话开始处理 Git 仓库事务前，**必须先执行 `git pull`** 拉取远程最新变更。

### 执行步骤

```bash
cd "{REPO_ROOT}" && git pull origin main
```

### 异常处理

| 情况 | 处理方式 |
|------|----------|
| 远程有新变更 | 告知用户拉取的内容摘要 |
| 本地有未提交变更 | 先 `git stash` → `git pull` → `git stash pop` |
| pull 导致冲突 | 通知用户手动解决冲突，不自动覆盖 |
| 网络失败 | 按能力 C 的重试策略执行 |

---

## 能力 B：变更推送

工作区有变更需要推送到远程仓库时，**严格按以下流程执行**。

### 推送流程

```
1. git add -A
2. git commit -m "<message>"
3. git show --stat HEAD → 展示即将推送的文件列表
4. 等待用户回复 "1" 确认
5. git push origin main
```

### 确认规则

- **用户回复 `1`** 即表示确认推送，立即执行 `git push`
- **用户回复其他内容** 视为取消或修改，不执行 push
- **不回复** 则等待，不自动推送

### 示例交互

```
📋 即将推送到 origin/main：

  docs: update CLAUDE.md with new behavior rules

  ——  CLAUDE.md    (+22 行)

回复 "1" 确认推送。
```

### Commit Message 规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 新功能 | `feat: <描述>` | `feat: add git-rule skill` |
| 修复 | `fix: <描述>` | `fix: correct retry interval to 5s` |
| 文档 | `docs: <描述>` | `docs: update README with install guide` |
| 重构 | `refactor: <描述>` | `refactor: simplify push workflow` |
| 测试 | `test: <描述>` | `test: add eval cases for git-rule` |

---

## 能力 C：推送重试策略

`git push` 失败时，**自动重试**，规则如下：

### 重试规则

| 次数 | 动作 |
|------|------|
| 第 1 次失败 | 等待 5 秒后重试 |
| 第 2 次失败 | 等待 5 秒后重试 |
| 第 3 次失败 | 停止重试，告知用户手动决策 |

### 示例交互

```
❌ 推送失败 (attempt 1/3): Failed to connect to github.com
⏳ 5 秒后重试...

❌ 推送失败 (attempt 2/3): Failed to connect to github.com
⏳ 5 秒后重试...

❌ 推送失败 (attempt 3/3): Failed to connect to github.com
⚠️ 3 次推送均失败。请手动执行：
  cd "{REPO_ROOT}" && git push origin main
```

### 重试实现

使用 Bash 工具的 `run_in_background` 配合 sleep 实现间隔重试，或直接在循环中执行：

```bash
for i in 1 2 3; do
  if git push origin main; then
    echo "✅ 推送成功"
    break
  fi
  if [ $i -lt 3 ]; then
    echo "❌ 推送失败 (attempt $i/3)，5 秒后重试..."
    sleep 5
  else
    echo "❌ 3 次推送均失败，请手动执行 git push"
  fi
done
```

---

## 交互规范

| 规范 | 规则 |
|------|------|
| 确认方式 | 用户回复 `1` = 确认；其他 = 取消/修改 |
| 时间格式 | `YYYY-MM-DD HH:MM` |
| 路径格式 | 使用 `{REPO_ROOT}` 占位符，实际使用时替换为项目根目录 |
| 分支名 | 默认 `main`，如仓库使用其他分支则适配 |

---

## 快速参考

```bash
# 会话开始同步
cd "{REPO_ROOT}" && git pull origin main

# 变更推送（自动 commit + 确认 + push）
cd "{REPO_ROOT}" && git add -A && git commit -m "<message>" && git show --stat HEAD
# → 用户回复 "1" → git push origin main

# 推送重试（3 次，间隔 5 秒）
for i in 1 2 3; do git push origin main && break || (echo "retry in 5s..." && sleep 5); done
```
