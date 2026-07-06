@echo off
REM ================================================================
REM  my-skills-collect Codex install launcher (Windows)
REM ================================================================

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

echo [error] Python not found. Install Python 2.7+ or Python 3.x
echo Download: https://www.python.org/downloads/
pause
exit /b 1

:done
echo.
echo Restart Codex to load the new skills.
pause