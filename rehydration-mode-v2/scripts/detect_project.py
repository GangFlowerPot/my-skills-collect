#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检测项目类型和技术栈，输出 JSON 格式结果。

Usage: python detect_project.py [project_root]
Output: JSON with detected languages, frameworks, and tools.
"""
import os
import sys
import json
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

DETECTORS = {
    # Language/framework → files that indicate its presence
    "Go": ["go.mod", "go.sum"],
    "Python": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
    "Node.js": ["package.json"],
    "TypeScript": ["tsconfig.json"],
    "React": ["src/App.tsx", "src/App.jsx", "next.config.js"],
    "Next.js": ["next.config.js", "next.config.mjs", "next.config.ts"],
    "Vue": ["vue.config.js", "vite.config.ts", "nuxt.config.ts"],
    "Rust": ["Cargo.toml"],
    "Java": ["pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle"],
    "Kotlin": ["build.gradle.kts"],
    "Ruby": ["Gemfile"],
    "PHP": ["composer.json"],
    "C#": ["*.csproj", "*.sln"],
    "Dart/Flutter": ["pubspec.yaml"],
    "Swift": ["Package.swift"],
}

DB_DETECTORS = {
    "PostgreSQL": ["pg", "postgres", "postgresql"],
    "MySQL": ["mysql"],
    "MongoDB": ["mongodb", "mongoose"],
    "Redis": ["redis"],
    "SQLite": ["sqlite"],
}

FRAMEWORK_DETECTORS = {
    "Gin": ["gin"],
    "Echo": ["echo"],
    "Fiber": ["fiber"],
    "Django": ["django"],
    "Flask": ["flask"],
    "FastAPI": ["fastapi"],
    "Express": ["express"],
    "NestJS": ["@nestjs/core"],
    "Spring Boot": ["spring-boot"],
    "Rails": ["rails"],
    "Laravel": ["laravel"],
}

def detect_languages() -> list[str]:
    found = []
    for lang, indicators in DETECTORS.items():
        for indicator in indicators:
            if list(ROOT.glob(f"**/{indicator}")):
                found.append(lang)
                break
    return found

def detect_from_deps() -> dict[str, list[str]]:
    """Scan package files for frameworks and databases."""
    frameworks = []
    databases = []

    # Check go.mod
    go_mod = ROOT / "go.mod"
    if go_mod.exists():
        content = go_mod.read_text(encoding="utf-8", errors="ignore")
        for fw, keywords in FRAMEWORK_DETECTORS.items():
            if any(kw.lower() in content.lower() for kw in keywords):
                frameworks.append(fw)
        for db, keywords in DB_DETECTORS.items():
            if any(kw.lower() in content.lower() for kw in keywords):
                databases.append(db)

    # Check package.json
    pkg_json = ROOT / "package.json"
    if pkg_json.exists():
        try:
            data = json.loads(pkg_json.read_text(encoding="utf-8"))
            all_deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            for fw, keywords in FRAMEWORK_DETECTORS.items():
                if any(kw in str(all_deps).lower() for kw in keywords):
                    frameworks.append(fw)
            for db, keywords in DB_DETECTORS.items():
                if any(kw in str(all_deps).lower() for kw in keywords):
                    databases.append(db)
        except (json.JSONDecodeError, KeyError):
            pass

    # Check requirements.txt
    req_txt = ROOT / "requirements.txt"
    if req_txt.exists():
        content = req_txt.read_text(encoding="utf-8", errors="ignore")
        for fw, keywords in FRAMEWORK_DETECTORS.items():
            if any(kw.lower() in content.lower() for kw in keywords):
                frameworks.append(fw)
        for db, keywords in DB_DETECTORS.items():
            if any(kw.lower() in content.lower() for kw in keywords):
                databases.append(db)

    return {
        "frameworks": list(set(frameworks)),
        "databases": list(set(databases))
    }

def main():
    languages = detect_languages()
    extras = detect_from_deps()
    is_git = (ROOT / ".git").exists()

    result = {
        "project_root": str(ROOT.resolve()),
        "project_name": ROOT.resolve().name,
        "languages": languages,
        "frameworks": extras["frameworks"],
        "databases": extras["databases"],
        "is_git_repo": is_git,
        "has_claude_md": (ROOT / "CLAUDE.md").exists(),
        "has_memory_docs": (ROOT / "docs" / "PROJECT_MEMORY.md").exists(),
    }

    stack_parts = []
    if languages:
        stack_parts.append(" + ".join(languages))
    if extras["frameworks"]:
        stack_parts.append(" + ".join(extras["frameworks"]))
    if extras["databases"]:
        stack_parts.append(" + ".join(extras["databases"]))
    result["inferred_stack"] = " + ".join(stack_parts) if stack_parts else "未知"

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result

if __name__ == "__main__":
    main()
