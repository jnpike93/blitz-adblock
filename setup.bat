@echo off
title Blitz AdBlocker Setup
cd /d "%~dp0"

echo ============================================================
echo  Blitz AdBlocker - One-Click Installer
echo ============================================================
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1" %*
if %errorlevel% neq 0 (
    echo.
    echo [-] An error occurred during setup.
    pause
    exit /b %errorlevel%
)

echo.
pause
