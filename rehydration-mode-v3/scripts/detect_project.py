#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
"""检测项目类型和技术栈，输出 JSON 格式结果（Python 2/3 兼容）。

V3 改进：
  - 全面覆盖 Java 主流框架（Spring Boot/Spring Cloud/Spring MVC/MyBatis/MyBatis-Plus）
  - 覆盖常用中间件（Nacos/Redis/Kafka/Zookeeper/Elasticsearch/ShardingSphere）
  - 覆盖构建工具（Maven/Gradle）和多模块项目
  - 覆盖数据库（Oracle/MySQL/PostgreSQL/MongoDB/SQLite/达梦）
  - 覆盖微服务相关（Feign/LoadBalancer/Hystrix/Gateway/Nacos Config）

Usage: python detect_project.py [project_root]
Output: JSON with detected languages, frameworks, middleware, databases, and tools.
"""

import os
import sys
import json
import re


def get_root():
    return os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()


ROOT = get_root()


# ---------------------------------------------------------------------------
# Language / build-tool detectors (by file existence)
# ---------------------------------------------------------------------------
LANG_DETECTORS = {
    "Java":       ["pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle"],
    "Python":     ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
    "Node.js":    ["package.json"],
    "TypeScript": ["tsconfig.json"],
    "Go":         ["go.mod", "go.sum"],
    "Rust":       ["Cargo.toml"],
    "C#":         [".csproj", ".sln"],
    "PHP":        ["composer.json"],
    "Ruby":       ["Gemfile"],
    "Dart":       ["pubspec.yaml"],
}

BUILD_TOOL_DETECTORS = {
    "Maven":  ["pom.xml", "mvnw", ".mvn"],
    "Gradle": ["build.gradle", "build.gradle.kts", "gradlew"],
}


# ---------------------------------------------------------------------------
# Framework keyword scanners (by content)
# ---------------------------------------------------------------------------
FRAMEWORK_DETECTORS = {
    "Spring Boot":       ["spring-boot", "spring-boot-starter"],
    "Spring Cloud":      ["spring-cloud", "spring-cloud-starter"],
    "Spring MVC":        ["spring-webmvc", "spring-web"],
    "Spring Security":   ["spring-security"],
    "Feign":             ["spring-cloud-openfeign", "feign"],
    "Gateway":           ["spring-cloud-gateway"],
    "Hystrix":           ["hystrix", "spring-cloud-netflix-hystrix"],
    "LoadBalancer":      ["spring-cloud-loadbalancer"],
    "Dubbo":             ["dubbo"],
    "Mybatis":           ["mybatis", "mybatis-spring"],
    "Mybatis-Plus":      ["mybatis-plus", "baomidou"],
    "Hibernate":         ["hibernate"],
    "Django":            ["django"],
    "Flask":             ["flask"],
    "FastAPI":           ["fastapi"],
    "Express":           ["express"],
    "NestJS":            ["@nestjs/core"],
    "React":             ["react"],
    "Vue":               ["vue"],
    "Gin":               ["gin-gonic/gin"],
    "Rails":             ["rails"],
}

MIDDLEWARE_DETECTORS = {
    "Nacos":             ["nacos", "alibaba-nacos"],
    "Eureka":            ["eureka"],
    "Zookeeper":         ["zookeeper", "curator"],
    "Kafka":             ["kafka", "spring-kafka"],
    "RabbitMQ":          ["rabbitmq", "amqp"],
    "RocketMQ":          ["rocketmq"],
    "Redis":             ["redis", "spring-data-redis", "lettuce", "jedis"],
    "Elasticsearch":     ["elasticsearch", "spring-data-elasticsearch"],
    "ShardingSphere":    ["sharding", "shardingsphere"],
    "Druid":             ["druid"],
    "Prometheus":        ["prometheus", "micrometer"],
    "SkyWalking":        ["skywalking"],
    "Thymeleaf":         ["thymeleaf"],
    "Dynamic-Datasource":["dynamic-datasource"],
}

DB_DETECTORS = {
    "Oracle":            ["oracle", "ojdbc"],
    "MySQL":             ["mysql", "mysql-connector"],
    "PostgreSQL":        ["postgresql", "postgres"],
    "MongoDB":           ["mongodb", "mongoose"],
    "SQLite":            ["sqlite"],
    "H2":                ["h2"],
    "达梦":       ["dmjdbc", "DmDriver"],
    "SQL Server":        ["sqlserver", "mssql"],
}


# ---------------------------------------------------------------------------
# Helpers (os.path based, no pathlib)
# ---------------------------------------------------------------------------
def _read_file(path):
    try:
        with open(path, 'rb') as f:
            data = f.read().decode('utf-8', errors='ignore')
        return data
    except Exception:
        return ""


def _find_files_relative(pattern):
    """Find files by basename pattern, return list of full paths. pattern can use * as suffix."""
    results = []
    basename_pattern = pattern.lstrip('*')
    if pattern.startswith('*'):
        for dirpath, dirnames, filenames in os.walk(ROOT):
            for fname in filenames:
                if _make_str(fname).endswith(basename_pattern):
                    results.append(os.path.join(dirpath, fname))
    else:
        for dirpath, dirnames, filenames in os.walk(ROOT):
            for fname in filenames:
                if _make_str(fname) == pattern:
                    results.append(os.path.join(dirpath, fname))
    return results


def _file_exists(filename):
    return os.path.exists(os.path.join(ROOT, filename))


def _scan_text(text, keywords):
    lowered = text.lower()
    return any(kw.lower() in lowered for kw in keywords)


# ---------------------------------------------------------------------------
# Detectors
# ---------------------------------------------------------------------------
def detect_languages():
    found = []
    for lang, indicators in LANG_DETECTORS.items():
        for ind in indicators:
            if ind.startswith('.'):
                if _find_files_relative(ind):
                    found.append(lang)
                    break
            elif _file_exists(ind):
                found.append(lang)
                break
    return found


def detect_build_tools():
    found = []
    for tool, indicators in BUILD_TOOL_DETECTORS.items():
        for ind in indicators:
            if _file_exists(ind):
                found.append(tool)
                break
    return found


def detect_multimodule():
    pom_file = os.path.join(ROOT, "pom.xml")
    if os.path.exists(pom_file):
        content = _read_file(pom_file)
        modules = re.findall(r'<module>(.*?)</module>', content)
        if modules:
            return {"is_multimodule": True, "modules": modules, "type": "maven"}
    for settings_name in ["settings.gradle", "settings.gradle.kts"]:
        settings_file = os.path.join(ROOT, settings_name)
        if os.path.exists(settings_file):
            content = _read_file(settings_file)
            includes = re.findall(r"include\s*\(?['\"](.+?)['\"]\)?", content, re.DOTALL)
            if includes:
                return {"is_multimodule": True, "modules": includes, "type": "gradle"}
    return {"is_multimodule": False}


def _make_str(s):
    """Convert to native str for Python 2/3 compatibility."""
    if sys.version_info[0] < 3:
        if isinstance(s, unicode):
            return s.encode('utf-8', errors='ignore')
        return s
    return s


def _scan_pom_files():
    """Read all pom.xml files and scan for frameworks/middleware/databases."""
    frameworks, middleware, databases = [], [], []
    pom_text = ""
    for pom_file in _find_files_relative("pom.xml"):
        pom_text += _read_file(pom_file) + "\n"
    if not pom_text:
        return frameworks, middleware, databases
    for fw, kws in FRAMEWORK_DETECTORS.items():
        if _scan_text(pom_text, kws):
            frameworks.append(fw)
    for mw, kws in MIDDLEWARE_DETECTORS.items():
        if _scan_text(pom_text, kws):
            middleware.append(mw)
    for db, kws in DB_DETECTORS.items():
        if _scan_text(pom_text, kws):
            databases.append(db)
    return frameworks, middleware, databases


def _scan_package_json():
    frameworks, middleware, databases = [], [], []
    for pkg_file in _find_files_relative("package.json"):
        if "node_modules" in pkg_file:
            continue
        try:
            data = json.loads(_read_file(pkg_file))
            all_deps = {}
            all_deps.update(data.get("dependencies", {}))
            all_deps.update(data.get("devDependencies", {}))
            dep_str = str(all_deps).lower()
            for fw, kws in FRAMEWORK_DETECTORS.items():
                if any(kw in dep_str for kw in kws):
                    frameworks.append(fw)
            for mw, kws in MIDDLEWARE_DETECTORS.items():
                if any(kw in dep_str for kw in kws):
                    middleware.append(mw)
            for db, kws in DB_DETECTORS.items():
                if any(kw in dep_str for kw in kws):
                    databases.append(db)
        except Exception:
            pass
    return frameworks, middleware, databases


def _scan_yml_files():
    middleware, databases = [], []
    yml_kw = {
        "Nacos": ["nacos"],
        "Redis": ["redis"],
        "Kafka": ["kafka"],
        "Zookeeper": ["zookeeper"],
        "Elasticsearch": ["elasticsearch"],
        "ShardingSphere": ["sharding", "shardingsphere"],
    }
    db_kw = {
        "Oracle": ["oracle"],
        "MySQL": ["mysql"],
        "PostgreSQL": ["postgresql"],
        "达梦": ["dm", "dameng"],
    }
    for dirpath, dirnames, filenames in os.walk(ROOT):
        for fname in filenames:
            fname_str = _make_str(fname)
            if fname_str.startswith("application") and (fname_str.endswith(".yml") or fname_str.endswith(".properties")):
                fpath = os.path.join(dirpath, fname)
                if "target" in fpath:
                    continue
                content = _read_file(fpath).lower()
                for mw, kws in yml_kw.items():
                    if any(kw in content for kw in kws):
                        middleware.append(mw)
                for db, kws in db_kw.items():
                    if any(kw in content for kw in kws):
                        databases.append(db)
    return middleware, databases


def main():
    languages = detect_languages()
    build_tools = detect_build_tools()
    multimodule = detect_multimodule()

    frameworks, middleware, databases = [], [], []

    # Java/Kotlin projects
    if any(l in languages for l in ("Java", "Kotlin")):
        fw, mw, db = _scan_pom_files()
        frameworks.extend(fw)
        middleware.extend(mw)
        databases.extend(db)

    # Node.js projects
    if "Node.js" in languages:
        fw, mw, db = _scan_package_json()
        frameworks.extend(fw)
        middleware.extend(mw)
        databases.extend(db)

    # YML/Properties scanning (common for Java/Node)
    mw, db = _scan_yml_files()
    middleware.extend(mw)
    databases.extend(db)

    # Deduplicate
    frameworks = sorted(set(frameworks))
    middleware = sorted(set(middleware))
    databases = sorted(set(databases))

    is_git = os.path.exists(os.path.join(ROOT, ".git"))

    # Build human-readable stack
    stack_parts = []
    if languages:
        stack_parts.append(" + ".join(languages))
    if build_tools:
        stack_parts.append(" + ".join(build_tools))
    if frameworks:
        stack_parts.append(" + ".join(frameworks[:5]))
        if len(frameworks) > 5:
            stack_parts[-1] += " (+{})".format(len(frameworks) - 5)
    if middleware:
        stack_parts.append(" + ".join(middleware[:5]))
        if len(middleware) > 5:
            stack_parts[-1] += " (+{})".format(len(middleware) - 5)
    if databases:
        stack_parts.append(" + ".join(databases))

    result = {
        "project_root": ROOT,
        "project_name": os.path.basename(ROOT),
        "languages": languages,
        "build_tools": build_tools,
        "multimodule": multimodule,
        "frameworks": frameworks,
        "middleware": middleware,
        "databases": databases,
        "is_git_repo": is_git,
        "has_claude_md": os.path.exists(os.path.join(ROOT, "CLAUDE.md")),
        "has_memory_docs": os.path.exists(os.path.join(ROOT, "docs", "PROJECT_MEMORY.md")),
        "inferred_stack": " | ".join(stack_parts) if stack_parts else "未知",
    }

    if sys.version_info[0] < 3:
        output = json.dumps(result, ensure_ascii=True, indent=2)
    else:
        output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)
    return result


if __name__ == "__main__":
    main()
