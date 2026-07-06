@echo off
REM ┌──────────────────────────────────────────────────────────────┐
REM │  my-skills-collect 一键安装脚本（Windows 批处理启动器）       │
REM │                                                               │
REM │  安装内容:                                                    │
REM │    - moduleskill2global     (skill)                           │
REM │    - rehydration-mode-v3    (skill)                           │
REM │    - claude-mem             (plugin，引导安装)                │
REM │                                                               │
REM │  双击运行 或 命令行参数:                                      │
REM │    install.bat               安装全部                          │
REM │    install.bat --skills-only 只装 skill                        │
REM │    install.bat --list        列出可安装的 skill                 │
REM │    install.bat --uninstall   卸载                              │
REM └──────────────────────────────────────────────────────────────┘

cd /d "%~dp0"

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python install.py %*
    goto :done
)

where python3 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python3 install.py %*
    goto :done
)

echo [error] 未找到 Python。请先安装 Python 2.7+ 或 Python 3.x
echo 下载地址: https://www.python.org/downloads/
pause
exit /b 1

:done
echo.
echo 安装完成后请在 Claude Code 中执行: /reload-plugins
pause
