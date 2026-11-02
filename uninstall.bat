@echo off
title Blitz AdBlocker Uninstall
cd /d "%~dp0"

echo ============================================================
echo  Blitz AdBlocker - Restoring Stock Files
echo ============================================================
echo.

python "%~dp0patch_blitz.py" --restore --launch
if %errorlevel% neq 0 (
    echo.
    echo [-] Failed to restore stock files.
    pause
    exit /b %errorlevel%
)

echo.
echo [+] Success! Stock Blitz files restored.
pause
