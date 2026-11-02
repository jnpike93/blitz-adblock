# Blitz AdBlocker

A clean, native anti-tamper compliant advertisement blocker for the **Blitz.gg** desktop application on Windows.

---

## Features

- **Automatic Prerequisites**: `setup.bat` automatically detects and installs Python 3 and Node.js via `winget` if missing.
- **No Video Ads**: Eliminates out-of-page floating video players, bottom-left sticky video units, and audio streams.
- **No Sidebar or Banner Ads**: Removes Playwire, LuckyLand Casino, Ramp, Adobe, and Dasani display units.
- **No "Remove Ads with Premium" Prompts**: Emulates Pro and Ad-Free subscriber roles.
- **Full Layout Expansion**: Collapses empty right rails and resets padding so game views take full width.
- **Anti-Tamper Bypass**: Eliminates the `E6 Error.` and crash loops caused by native integrity checks in `blitz_core.node`.
- **Zero Background Overhead**: No persistent daemons or background processes.
- **One-Click Post-Update Fix**: Run `fix-update.bat` after any Blitz update to restore ad-free functionality in seconds.

---

## Installation & Download

### Method 1: Git Clone (Recommended - No Browser Warnings)
Open PowerShell or Command Prompt and run:
```powershell
git clone https://github.com/jnpike93/blitz-adblock.git
cd blitz-adblock
.\setup.bat
```

---

### Method 2: ZIP Download
1. Click the green **`<> Code`** button on GitHub and choose **Download ZIP**.
2. Extract the ZIP folder to your PC.
3. Double-click **`setup.bat`**.

> [!NOTE]
> **Why does Google Chrome or Windows show a warning on the ZIP?**
> Google Safe Browsing and Windows SmartScreen automatically flag ZIP archives from newly created GitHub repositories containing `.bat` and `.ps1` automation scripts as "untrusted" or "dangerous" by default. This is a generic heuristic false positive.
> 
> - **In Google Chrome**: Press `Ctrl + J` (Downloads) -> find the blocked file -> click **"Download suspicious file"** (or **"Keep anyway"**).
> - **In Windows SmartScreen**: Click **"More info"** -> **"Run anyway"**.
> - Alternatively, use **Method 1 (`git clone`)** which avoids browser download heuristics entirely.

---

## Usage

### 1. Initial Installation
Double-click **`setup.bat`**.

This checks for Python 3 and Node.js (auto-installing them via `winget` if missing), patches Blitz, and launches it ad-free.

---

### 2. After a Blitz Update
Whenever Blitz auto-updates, vendor files are restored and ads will temporarily reappear.

Double-click **`fix-update.bat`**.

This closes Blitz, re-applies the complete adblock patch, and relaunches Blitz ad-free.

---

### 3. Uninstall (Restore Original Blitz)
Double-click **`uninstall.bat`**.

This restores the pristine backup copies of `app.asar` and `blitz_core.node` and relaunches stock Blitz.

---

## Repository Files

| File | Purpose |
| :--- | :--- |
| **`setup.bat`** | 1-click initial installer (auto-installs prerequisites via `setup.ps1`). |
| **`setup.ps1`** | Automated prerequisite resolver (Python 3, Node.js) and patch invoker. |
| **`fix-update.bat`** | 1-click script to run after Blitz updates. |
| **`uninstall.bat`** | 1-click uninstaller to restore stock Blitz files. |
| **`patch_blitz.py`** | Core engine: binary patcher, ASAR extractor, JS patch injector, and repacker. |
| **`README.md`** | Usage instructions and documentation. |

---

## In-Game Overlay (League of Legends)

- **Display Mode**: League of Legends must be set to **Borderless** or **Windowed** in the in-game Video settings (Exclusive Fullscreen prevents DirectX overlay hooking).
- **Default Overlay Hotkeys**: Toggle the in-game overlay using `~` (Tilde), `Tab`, or `Ctrl + G`.
- **Pre-Existing Game Detection**: Active games are automatically detected on startup and injected without needing to restart the game client.

---

## Verification

Check current patch status via Python CLI at any time:

```cmd
python patch_blitz.py --status
```
