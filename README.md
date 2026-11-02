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

## Verification

Check current patch status via Python CLI at any time:

```cmd
python patch_blitz.py --status
```
