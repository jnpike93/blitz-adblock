@echo off
title Blitz AdBlocker - Fix After Update
cd /d "%~dp0"

echo ============================================================
echo  Blitz AdBlocker - Re-applying Patch After Update
echo ============================================================
echo.

python "%~dp0patch_blitz.py" --patch --launch
if %errorlevel% neq 0 (
    echo.
    echo [-] Failed to re-apply patch.
    pause
    exit /b %errorlevel%
)

echo.
echo [+] Success! Blitz has been re-patched ad-free.
pause
