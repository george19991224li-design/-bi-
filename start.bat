@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py -3 launch.py %*
) else (
    python launch.py %*
)
if errorlevel 1 (
    echo Launch failed. Install Python 3.10+ and check the error above.
    pause
    exit /b 1
)
