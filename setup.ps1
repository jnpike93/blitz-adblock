<#
.SYNOPSIS
    All-in-one setup script for Blitz AdBlocker with automatic prerequisite resolution.

.DESCRIPTION
    Validates environment prerequisites (Python 3, Node.js/npx, Blitz).
    If Python or Node.js is missing, automatically installs them via winget,
    refreshes the session environment PATH dynamically, patches Blitz,
    and launches Blitz ad-free.
#>

[CmdletBinding()]
param(
    [switch]$NoLaunch
)

try {
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force -ErrorAction SilentlyContinue
} catch {}

$ErrorActionPreference = "Stop"

function Write-Cyan { param([string]$Message) Write-Host "[*] $Message" -ForegroundColor Cyan }
function Write-Green { param([string]$Message) Write-Host "[+] $Message" -ForegroundColor Green }
function Write-Yellow { param([string]$Message) Write-Host "[!] $Message" -ForegroundColor Yellow }
function Write-Red { param([string]$Message) Write-Host "[-] $Message" -ForegroundColor Red }

function Update-SessionPath {
    $machinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$machinePath;$userPath"
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BlitzDir = Join-Path $env:LOCALAPPDATA "Programs\Blitz"
$AsarFile = Join-Path $BlitzDir "resources\app.asar"
$BlitzExe = Join-Path $BlitzDir "Blitz.exe"
$PatcherPy = Join-Path $ScriptDir "patch_blitz.py"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Blitz AdBlocker - Automated Setup & Installation" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Blitz installation
Write-Cyan "Checking Blitz desktop installation..."
if (-not (Test-Path $AsarFile)) {
    Write-Red "Blitz is not installed at the default path:"
    Write-Red "  $BlitzDir"
    Write-Yellow "Please install Blitz before running this setup: https://blitz.gg/download"
    exit 1
}
Write-Green "Found Blitz installation at $BlitzDir"

# 2. Check and auto-install Python 3
Write-Cyan "Checking Python 3 prerequisite..."
$hasPython = $false
try {
    $ver = (& python --version 2>&1)
    if ($LASTEXITCODE -eq 0 -or $ver -match "Python 3") {
        $hasPython = $true
        Write-Green "Found Python: $ver"
    }
} catch {}

if (-not $hasPython) {
    Write-Yellow "Python 3 is missing. Attempting automatic installation via winget..."
    try {
        $wingetProc = Start-Process -FilePath "winget" -ArgumentList "install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements" -Wait -PassThru -NoNewWindow
        if ($wingetProc.ExitCode -eq 0) {
            Update-SessionPath
            Write-Green "Python 3 installed successfully."
        } else {
            throw "winget returned code $($wingetProc.ExitCode)"
        }
    } catch {
        Write-Red "Automatic Python 3 installation failed: $_"
        Write-Yellow "Please install Python manually: winget install Python.Python.3.12"
        exit 1
    }
}

# 3. Check and auto-install Node.js / npx
Write-Cyan "Checking Node.js / npx prerequisite..."
$hasNpx = $false
try {
    $ver = (& npx --version 2>&1)
    if ($LASTEXITCODE -eq 0) {
        $hasNpx = $true
        Write-Green "Found npx: v$ver"
    }
} catch {}

if (-not $hasNpx) {
    Write-Yellow "Node.js / npx is missing. Attempting automatic installation via winget..."
    try {
        $wingetProc = Start-Process -FilePath "winget" -ArgumentList "install --id OpenJS.NodeJS.LTS -e --accept-source-agreements --accept-package-agreements" -Wait -PassThru -NoNewWindow
        if ($wingetProc.ExitCode -eq 0) {
            Update-SessionPath
            Write-Green "Node.js (npx) installed successfully."
        } else {
            throw "winget returned code $($wingetProc.ExitCode)"
        }
    } catch {
        Write-Red "Automatic Node.js installation failed: $_"
        Write-Yellow "Please install Node.js manually: winget install OpenJS.NodeJS.LTS"
        exit 1
    }
}

# Final verification of tools in current session
Update-SessionPath

# 5. Stop running Blitz instances
Write-Host ""
Write-Cyan "Terminating running Blitz instances..."
Get-Process -Name "Blitz" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1
Write-Green "Blitz processes closed."

# 6. Configure UIPI overlay injector for League of Legends (if permissions allow)
try {
    $progDir = "C:\Program Files\Blitz"
    if (-not (Test-Path $progDir)) {
        New-Item -ItemType Directory -Path $progDir -Force -ErrorAction SilentlyContinue | Out-Null
    }
    $depsDir = Join-Path $env:APPDATA "Blitz\blitz-deps"
    $latestDeps = Get-ChildItem -Path $depsDir -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending | Select-Object -First 1
    if ($latestDeps) {
        Copy-Item (Join-Path $latestDeps.FullName "safe_x64_injector_ui.exe") (Join-Path $progDir "safe_x64_injector_ui.exe") -Force -ErrorAction SilentlyContinue
        Copy-Item (Join-Path $latestDeps.FullName "safe_x86_injector_ui.exe") (Join-Path $progDir "safe_x86_injector_ui.exe") -Force -ErrorAction SilentlyContinue
        if (Test-Path (Join-Path $progDir "safe_x64_injector_ui.exe")) {
            Write-Green "UIPI injector configured in $progDir"
        }
    }
} catch {}

# 7. Apply the AdBlock Patch
Write-Host ""
Write-Cyan "Applying native anti-tamper bypass and adblock patch..."
$launchArg = if ($NoLaunch) { "" } else { "--launch" }
$patchProc = Start-Process -FilePath "python.exe" -ArgumentList "`"$PatcherPy`" --patch $launchArg" -Wait -PassThru -NoNewWindow

if ($patchProc.ExitCode -ne 0) {
    Write-Red "Patcher failed with exit code $($patchProc.ExitCode)."
    exit 1
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " Installation Complete! Blitz is now running ad-free." -ForegroundColor White
Write-Host " If Blitz ever auto-updates, double-click fix-update.bat." -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Green

