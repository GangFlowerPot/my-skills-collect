# Push Workflow Detail — 推送流程详细规格

## 完整推送时序

```
用户完成工作，产生工作区变更
        │
        ▼
┌──────────────────────────────────────┐
│ 1. git add -A                        │
│    将所有变更加入暂存区                │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│ 2. git commit -m "<message>"          │
│    提交变更，使用规范的 commit message │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│ 3. git show --stat HEAD               │
│    展示本次 commit 的文件变更统计      │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│ 4. 输出给用户确认                      │
│    📋 即将推送到 origin/main：         │
│      <commit message>                 │
│      ——  <file>    (+N 行)            │
│    回复 "1" 确认推送。                 │
└──────────────┬───────────────────────┘
               │
         用户回复 "1"？
          /        \
        是          否
        │            │
        ▼            ▼
┌──────────────┐  ┌──────────────┐
│ 5a. git push │  │ 5b. 取消/修改 │
│    推送成功   │  │    等待新指令  │
└──────────────┘  └──────────────┘
```

## 异常分支

### pull 时本地有未提交变更

```
git pull 失败 (本地有修改)
    │
    ▼
git stash          ← 暂存本地变更
    │
    ▼
git pull origin main  ← 拉取远程
    │
    ▼
git stash pop      ← 恢复本地变更
    │
    ▼
继续正常推送流程
```

### push 时网络失败

```
git push 失败 (attempt 1/3)
    │
    ▼
sleep 5            ← 等待 5 秒
    │
    ▼
git push 失败 (attempt 2/3)
    │
    ▼
sleep 5
    │
    ▼
git push 失败 (attempt 3/3)
    │
    ▼
告知用户手动推送
```

## Commit Message 规范

### 格式

```
<type>: <description>

[optional body]

[optional footer]
```

### Type 列表

| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: add git-rule skill with cross-platform install` |
| `fix` | 修复 bug | `fix: correct session sync pull command` |
| `docs` | 文档变更 | `docs: update README with new skill entry` |
| `refactor` | 重构 | `refactor: extract git rules into standalone skill` |
| `test` | 测试 | `test: add 2 eval cases for git-rule` |
| `chore` | 杂务 | `chore: update .gitignore` |

## 确认方式说明

用户回复 `1` 是约定的确认信号，设计理由：
- 简短，不打断工作流
- 不会与正常对话混淆（没有人会在聊天中单独打"1"）
- 比 "yes" / "确认" 等更省 token

如需取消，回复任意非 "1" 内容即可（如 "等等"、"取消"、"先不推"）。
