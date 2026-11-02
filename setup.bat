@echo off
title Blitz AdBlocker Setup
cd /d "%~dp0"

echo ============================================================
echo  Blitz AdBlocker - One-Click Installer
echo ============================================================
echo.

python "%~dp0patch_blitz.py" --patch --launch
if %errorlevel% neq 0 (
    echo.
    echo [-] An error occurred during setup.
    pause
    exit /b %errorlevel%
)

echo.
echo [+] Installation complete! Blitz is now running ad-free.
pause
