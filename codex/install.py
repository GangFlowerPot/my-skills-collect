#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""my-skills-collect Codex install script (Windows / Linux / macOS).

Installs:
  - moduleskill2global    : skill - move skills between project/global scope
  - rehydration-mode-v3   : skill - rehydration memory system V3

Install targets (global):
  - Windows: %USERPROFILE%\.agents\skills\  +  %USERPROFILE%\.codex\skills\
  - Unix:    ~/.agents/skills/               +  ~/.codex/skills/

Usage:
  python install.py                # install all (default)
  python install.py --skills-only  # only skills, no extra prompts
  python install.py rehydration-mode-v3 moduleskill2global  # specific skills
  python install.py --list         # list available skills
  python install.py --uninstall    # uninstall (remove installed files)
"""
from __future__ import print_function

import os
import sys
import shutil
import platform

# Cross-platform paths
IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

HOME = os.path.expanduser("~")
AGENTS_DIR = os.path.join(HOME, ".agents", "skills")
CODEX_DIR = os.path.join(HOME, ".codex", "skills")
COLLECTION_DIR = os.path.dirname(os.path.abspath(__file__))

AVAILABLE_SKILLS = ["moduleskill2global", "rehydration-mode-v3"]


def _mkdir_p(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError:
            if not os.path.exists(path):
                raise


def _rmtree(path):
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


def _copy_skill(skill_name):
    src = os.path.join(COLLECTION_DIR, skill_name)
    dst_agents = os.path.join(AGENTS_DIR, skill_name)
    dst_codex = os.path.join(CODEX_DIR, skill_name)

    if not os.path.isdir(src):
        print("  [error] skill not found: {}".format(src))
        return False

    # Copy to agents/skills
    _mkdir_p(AGENTS_DIR)
    if os.path.exists(dst_agents):
        _rmtree(dst_agents)
    shutil.copytree(src, dst_agents)
    print("  [ok] copied to: {}".format(dst_agents))

    # Copy to .codex/skills
    _mkdir_p(CODEX_DIR)
    if os.path.exists(dst_codex):
        _rmtree(dst_codex)
    shutil.copytree(src, dst_codex)
    print("  [ok] copied to: {}".format(dst_codex))
    return True


def _remove_skill(skill_name):
    dst_agents = os.path.join(AGENTS_DIR, skill_name)
    dst_codex = os.path.join(CODEX_DIR, skill_name)

    removed = False
    if os.path.exists(dst_agents):
        _rmtree(dst_agents)
        print("  [ok] removed: {}".format(dst_agents))
        removed = True

    if os.path.exists(dst_codex):
        _rmtree(dst_codex)
        print("  [ok] removed: {}".format(dst_codex))
        removed = True

    if not removed:
        print("  [info] {} not installed, skipping".format(skill_name))
    return removed


def install_skills(skill_names):
    if not skill_names:
        return

    print("")
    print("=" * 60)
    print("Installing {} skill(s)".format(len(skill_names)))
    print("=" * 60)
    print("System:     {}".format(platform.system()))
    print("Agents dir: {}".format(AGENTS_DIR))
    print("Codex dir:  {}".format(CODEX_DIR))
    print("")

    success = []
    for name in skill_names:
        print("[{}] ".format(name))
        if _copy_skill(name):
            success.append(name)
        print("")

    print("=" * 60)
    print("Done: {}/{} skills installed".format(len(success), len(skill_names)))
    print("=" * 60)
    print("")
    print("Restart Codex to load the new skills.")
    print("")


def uninstall_skills(skill_names):
    if not skill_names:
        return

    print("")
    print("=" * 60)
    print("Uninstalling {} skill(s)".format(len(skill_names)))
    print("=" * 60)
    print("")

    for name in skill_names:
        print("[{}]".format(name))
        _remove_skill(name)
        print("")

    print("=" * 60)
    print("Uninstall complete")
    print("=" * 60)
    print("Restart Codex to apply changes.")
    print("")


def list_available():
    print("")
    print("Available skills:")
    for name in AVAILABLE_SKILLS:
        skill_dir = os.path.join(COLLECTION_DIR, name)
        has_skill_md = os.path.exists(os.path.join(skill_dir, "SKILL.md"))
        status = "ok" if has_skill_md else "MISSING SKILL.md"
        print("  {}  {}".format(status, name))
    print("")


def main():
    args = sys.argv[1:]

    if not args:
        install_skills(AVAILABLE_SKILLS)
        return

    if "--help" in args or "-h" in args:
        print(__doc__)
        return

    if "--list" in args:
        list_available()
        return

    if "--uninstall" in args:
        to_uninstall = [a for a in args if not a.startswith("--")]
        if not to_uninstall:
            to_uninstall = AVAILABLE_SKILLS
        uninstall_skills(to_uninstall)
        return

    skip_mem = False
    if "--skills-only" in args or "--skip-mem" in args:
        skip_mem = True
        args = [a for a in args if a not in ("--skills-only", "--skip-mem")]

    to_install = args if args else AVAILABLE_SKILLS

    valid = []
    for name in to_install:
        if name in AVAILABLE_SKILLS:
            valid.append(name)
        else:
            print("[warn] '{}' not in list. Available: {}".format(name, AVAILABLE_SKILLS))

    install_skills(valid)


if __name__ == "__main__":
    main()