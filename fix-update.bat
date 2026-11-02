@echo off
title Blitz AdBlocker - Fix After Update
cd /d "%~dp0"

echo ============================================================
echo  Blitz AdBlocker - Re-applying Patch After Update
echo ============================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [*] Python not detected in PATH. Running full setup...
    call "%~dp0setup.bat"
    exit /b %errorlevel%
)

python "%~dp0patch_blitz.py" --patch --launch
if %errorlevel% neq 0 (
    echo.
    echo [-] Failed to re-apply patch. Running setup to verify prerequisites...
    call "%~dp0setup.bat"
    exit /b %errorlevel%
)

echo.
echo [+] Success! Blitz has been re-patched ad-free.
pause
