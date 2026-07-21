#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""my-skills-collect 一键安装脚本（Windows / Linux / macOS）。

安装内容:
  - moduleskill2global    : skill — 项目级/全局级 skill 互转
  - rehydration-mode-v3   : skill — 再水化记忆系统 V3
  - zsh                   : skill — 跨 Agent 项目记忆与上下文恢复系统（兼容 auto-memory / claude-mem）
  - claude-mem            : plugin — 原始会话内容存储（通过 Claude Code /plugin 命令引导安装）

安装目标（全局）:
  - Windows: %USERPROFILE%\.agents\skills\  +  %USERPROFILE%\.claude\skills\
  - Unix:    ~/.agents/skills/               +  ~/.claude/skills/

用法:
  python install.py                # 安装全部（默认）
  python install.py --skills-only  # 只装 skill，不提示 claude-mem
  python install.py --skip-mem     # 同上
  python install.py --link-to-source  # 链接到源模式：直接 Junction 到仓内源（git pull 即自动生效）
  python install.py rehydration-mode-v3 moduleskill2global  # 指定安装
  python install.py --list         # 列出可安装的 skill
  python install.py --uninstall    # 卸载（删除已安装的文件）
"""
from __future__ import print_function

import os
import sys
import shutil
import platform

# ────────────────────────────────────────────────────────────
# 跨平台路径与命令适配
# ────────────────────────────────────────────────────────────
IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

HOME = os.path.expanduser("~")
AGENTS_DIR = os.path.join(HOME, ".agents", "skills")
CLAUDE_DIR = os.path.join(HOME, ".claude", "skills")
COLLECTION_DIR = os.path.dirname(os.path.abspath(__file__))

# 可安装的 skill 列表（目录名 = skill 名）
AVAILABLE_SKILLS = ["moduleskill2global", "rehydration-mode-v3", "zsh"]


def _mkdir_p(path):
    """递归创建目录（Python 2/3 兼容）。"""
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError:
            if not os.path.exists(path):
                raise


def _rmtree(path):
    """递归删除目录（Windows 下需要处理只读文件）。"""
    if not os.path.exists(path):
        return

    if IS_WINDOWS:
        def on_rm_error(func, path, exc_info):
            import stat
            os.chmod(path, stat.S_IWRITE)
            os.unlink(path)
        shutil.rmtree(path, onerror=on_rm_error)
    else:
        shutil.rmtree(path)


def _make_link(src, link_name):
    """创建符号链接 / 目录联接（跨平台）。"""
    _mkdir_p(os.path.dirname(link_name))

    # 已存在则先删除
    if os.path.islink(link_name) or os.path.exists(link_name):
        if os.path.isdir(link_name) and not os.path.islink(link_name):
            _rmtree(link_name)
        else:
            os.remove(link_name)

    if IS_WINDOWS:
        # Windows: 使用目录联接（Junction，不需要管理员权限）
        import subprocess
        # mklink /J 要求目标存在且 link_name 不存在
        cmd = ["cmd", "/c", "mklink", "/J", link_name, src]
        # 需要 shell=True 才能执行 cmd 内置命令
        ret = subprocess.call(" ".join(cmd), shell=True)
        if ret != 0:
            # 回退到 shutil.copytree
            print("  [warn] mklink 失败，回退到完整复制模式")
            shutil.copytree(src, link_name)
    else:
        # Linux / macOS: 使用符号链接
        os.symlink(src, link_name)


def _copy_skill(skill_name, link_to_source=False):
    """复制 skill 到 agents/skills 并创建符号链接到 .claude/skills。

    link_to_source=True 时跳过复制，直接创建指向仓内源的 Junction（方案 B）。
    适合仓路径固定的多机同步仓：git pull 后自动生效，无需重装。
    """
    src = os.path.join(COLLECTION_DIR, skill_name)
    dst = os.path.join(AGENTS_DIR, skill_name)
    link = os.path.join(CLAUDE_DIR, skill_name)

    if not os.path.isdir(src):
        print("  [error] skill 目录不存在: {}".format(src))
        return False

    if link_to_source:
        # 方案 B：直接联接仓内源，跳过副本
        _make_link(src, link)
        link_type = "联接" if IS_WINDOWS else "符号链接"
        print("  [ok] {}: {} -> {} (链接到源)".format(link_type, link, src))
        return True

    # 方案 A（默认）：复制到 agents/skills
    _mkdir_p(AGENTS_DIR)
    if os.path.exists(dst):
        _rmtree(dst)
    shutil.copytree(src, dst)
    print("  [ok] 复制到: {}".format(dst))

    # 2. 创建符号链接 / 联接
    _make_link(dst, link)

    link_type = "联接" if IS_WINDOWS else "符号链接"
    print("  [ok] {}: {} -> {}".format(link_type, link, dst))
    return True


def _remove_skill(skill_name):
    """卸载 skill（删除 agents 副本 + 链接）。"""
    dst = os.path.join(AGENTS_DIR, skill_name)
    link = os.path.join(CLAUDE_DIR, skill_name)

    removed = False
    if os.path.exists(dst):
        _rmtree(dst)
        print("  [ok] 已删除: {}".format(dst))
        removed = True

    if os.path.islink(link) or os.path.exists(link):
        if os.path.isdir(link) and not os.path.islink(link):
            _rmtree(link)
        else:
            os.remove(link)
        print("  [ok] 已删除链接: {}".format(link))
        removed = True

    if not removed:
        print("  [info] {} 未安装，跳过".format(skill_name))
    return removed


def install_skills(skill_names, link_to_source=False):
    """安装指定的 skill 列表。"""
    if not skill_names:
        return

    print("")
    print("=" * 60)
    print("安装 {} 个 skill".format(len(skill_names)))
    if link_to_source:
        print("模式: 链接到源（git pull 即自动生效）")
    print("=" * 60)
    print("系统:   {}".format(platform.system()))
    print("代理目录: {}".format(AGENTS_DIR))
    print("Claude目录: {}".format(CLAUDE_DIR))
    print("")

    success = []
    for name in skill_names:
        print("[{}] ".format(name))
        if _copy_skill(name, link_to_source=link_to_source):
            success.append(name)
        print("")

    print("=" * 60)
    print("完成: {}/{} 个 skill 安装成功".format(len(success), len(skill_names)))
    print("=" * 60)
    print("")

    # 下一步提示
    print("下一步:")
    print("  1. 在 Claude Code 中输入: /reload-plugins")
    print("  2. 验证安装: npx skills list -g")
    print("")


def uninstall_skills(skill_names):
    """卸载指定的 skill 列表。"""
    if not skill_names:
        return

    print("")
    print("=" * 60)
    print("卸载 {} 个 skill".format(len(skill_names)))
    print("=" * 60)
    print("")

    for name in skill_names:
        print("[{}]".format(name))
        _remove_skill(name)
        print("")

    print("=" * 60)
    print("卸载完成")
    print("=" * 60)
    print("在 Claude Code 中输入: /reload-plugins")
    print("")


def guide_claude_mem():
    """输出 claude-mem 插件的安装引导。"""
    print("")
    print("=" * 60)
    print("claude-mem 插件安装")
    print("=" * 60)
    print("")
    print("claude-mem 需要通过 Claude Code 内置的 /plugin 命令安装。")
    print("")
    print("请在 Claude Code 中执行以下任一命令:")
    print("")
    print("  方式 1（推荐，从 marketplace 安装）:")
    print("    /plugin install thedotmack/claude-mem")
    print("")
    print("  方式 2（先添加 marketplace 再安装）:")
    print("    /plugin marketplace add thedotmack/claude-mem")
    print("")
    print("安装完成后，claude-mem 会随 Claude Code 自动加载。")
    print("")
    print("分工说明:")
    print("  - rehydration-mode-v3 : 存储结构化摘要（架构/任务/日志/决策）")
    print("  - zsh                 : 跨 Agent 项目记忆（AGENT_MEMORY.md 导航 + skill-docs/），兼容 auto-memory")
    print("  - claude-mem          : 存储原始会话内容（代码/命令/输出）")
    print("  - rehydration-mode-v3 / zsh 与 claude-mem 互补，不冗余")
    print("")
    print("=" * 60)
    print("")


def list_available():
    """列出可安装的 skill。"""
    print("")
    print("可安装的 skill（来自目录）:")
    for name in AVAILABLE_SKILLS:
        skill_dir = os.path.join(COLLECTION_DIR, name)
        has_skill_md = os.path.exists(os.path.join(skill_dir, "SKILL.md"))
        status = "✅" if has_skill_md else "❌ (缺少 SKILL.md)"
        print("  {}  {}  {}".format(status, name, status))
    print("")


def main():
    args = sys.argv[1:]

    if not args:
        # 默认：安装全部 skill + 引导 claude-mem
        install_skills(AVAILABLE_SKILLS)
        guide_claude_mem()
        return

    if "--help" in args or "-h" in args:
        print(__doc__)
        return

    if "--list" in args:
        list_available()
        return

    if "--uninstall" in args:
        # 过滤掉 --uninstall 本身，剩余参数为要卸载的 skill
        to_uninstall = [a for a in args if not a.startswith("--")]
        if not to_uninstall:
            to_uninstall = AVAILABLE_SKILLS
        uninstall_skills(to_uninstall)
        return

    skip_mem = False
    if "--skills-only" in args or "--skip-mem" in args:
        skip_mem = True
        args = [a for a in args if a not in ("--skills-only", "--skip-mem")]

    link_to_source = False
    if "--link-to-source" in args:
        link_to_source = True
        args = [a for a in args if a != "--link-to-source"]

    # 剩余参数为要安装的 skill 名
    to_install = args if args else AVAILABLE_SKILLS

    # 验证 skill 是否存在
    valid = []
    for name in to_install:
        if name in AVAILABLE_SKILLS:
            valid.append(name)
        else:
            print("[warn] '{}' 不在可安装列表中，跳过。可用: {}".format(name, AVAILABLE_SKILLS))

    install_skills(valid, link_to_source=link_to_source)

    if not skip_mem:
        guide_claude_mem()


if __name__ == "__main__":
    main()
