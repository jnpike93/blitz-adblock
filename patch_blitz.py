"""
Blitz AdBlocker Patcher
Disables display ads, tracking telemetry, video ad units, and in-game overlay ads in the Blitz.gg desktop app.
"""

import os
import sys
import shutil
import subprocess
import tempfile
import re
from pathlib import Path

DEFAULT_BLITZ_PATH = Path(os.path.expandvars(r"%LOCALAPPDATA%\Programs\Blitz"))
RESOURCES_DIR = DEFAULT_BLITZ_PATH / "resources"
ASAR_FILE = RESOURCES_DIR / "app.asar"
BACKUP_FILE = RESOURCES_DIR / "app.asar.backup"
UNPACKED_DIR = RESOURCES_DIR / "app.asar.unpacked"
BACKUP_UNPACKED_DIR = RESOURCES_DIR / "app.asar.unpacked.backup"


def get_blitz_core_nodes():
    nodes = []
    bin1 = RESOURCES_DIR / "binaries" / "blitz_core.node"
    if bin1.exists():
        nodes.append(bin1)
    deps_dir = Path(os.path.expandvars(r"%APPDATA%\Blitz\blitz-deps"))
    if deps_dir.exists():
        for p in deps_dir.glob("*/blitz_core.node"):
            nodes.append(p)
    return nodes


def kill_blitz():
    print("[*] Terminating running Blitz processes...")
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", "Blitz.exe"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        print("[+] Blitz processes stopped.")
    except Exception as e:
        print(f"[-] Warning: Failed to execute taskkill: {e}")


def is_node_binary_patched(fp):
    try:
        with open(fp, "rb") as f:
            f.seek(0x158b0)
            b = f.read(1)
            return b == b"\xc3"
    except Exception:
        return False


def patch_blitz_core_nodes():
    print("[*] Patching anti-tamper checks in blitz_core.node binaries...")
    nodes = get_blitz_core_nodes()
    if not nodes:
        print("  [-] No blitz_core.node binaries found.")
        return

    for fp in nodes:
        if is_node_binary_patched(fp):
            print(f"  [+] Anti-tamper bypass already active in {fp.name} ({fp.parent.name})")
            continue
        bak = fp.with_suffix(".node.backup")
        if not bak.exists():
            try:
                shutil.copy2(fp, bak)
            except Exception as e:
                print(f"  [-] Warning saving backup for {fp}: {e}")

        try:
            with open(fp, "r+b") as f:
                # Patch call VerifyApp at 0x6279 to NOPs (90 90 90 90 90)
                f.seek(0x6279)
                curr_call = f.read(5)
                if curr_call == b"\xe8\x32\xf6\x00\x00":
                    f.seek(0x6279)
                    f.write(b"\x90\x90\x90\x90\x90")

                # Patch start of VerifyApp at 0x158b0 to RET (c3)
                f.seek(0x158b0)
                curr_start = f.read(1)
                if curr_start == b"\x48":
                    f.seek(0x158b0)
                    f.write(b"\xc3")
            print(f"  [+] Patched anti-tamper bypass in {fp}")
        except Exception as e:
            print(f"  [-] Warning patching {fp}: {e}")


def restore_blitz_core_nodes():
    print("[*] Restoring blitz_core.node backups...")
    nodes = get_blitz_core_nodes()
    for fp in nodes:
        bak = fp.with_suffix(".node.backup")
        if bak.exists():
            try:
                shutil.copy2(bak, fp)
                print(f"  [+] Restored {fp}")
            except Exception as e:
                print(f"  [-] Failed to restore {fp}: {e}")


def clean_blitz_caches():
    print("[*] Purging stale Blitz cache and ad storage...")
    app_data = Path(os.path.expandvars(r"%APPDATA%\Blitz"))
    cache_dirs = [
        app_data / "Cache",
        app_data / "DawnGraphiteCache",
        app_data / "DawnWebGPUCache",
        app_data / "GPUCache",
        app_data / "Service Worker" / "CacheStorage",
    ]
    for cd in cache_dirs:
        if cd.exists():
            try:
                shutil.rmtree(cd, ignore_errors=True)
                print(f"  [+] Cleared {cd.name}")
            except Exception:
                pass


def check_blitz_installed():
    if not ASAR_FILE.exists():
        print(f"[-] Error: Could not locate Blitz app.asar at {ASAR_FILE}")
        return False
    return True


def is_already_patched(asar_path):
    try:
        with open(asar_path, "rb") as f:
            while chunk := f.read(1024 * 1024):
                if b"__BLITZ_ADBLOCK_ACTIVE__" in chunk:
                    return True
    except Exception:
        pass
    return False


def patch_preload(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    target = 'const { ipcRenderer, contextBridge, webFrame } = require("electron");'
    if target not in content:
        raise RuntimeError("Could not find electron require target in preload.js")

    injection = '''const { ipcRenderer, contextBridge, webFrame } = require("electron");

// __BLITZ_ADBLOCK_ACTIVE__
try {
  // 1. Immediate CSS injection to eliminate ad slots and collapse right rail
  webFrame.insertCSS(`
    :root, html, body, main {
      --right-rail-width: 0px !important;
      --rail-gap: 0px !important;
    }
    .content-container,
    .content-container.width-rail {
      width: 100% !important;
      max-width: 100% !important;
      grid-template-columns: minmax(0, 1fr) !important;
      gap: 0px !important;
    }
    .main-content,
    .main-content:not(.is-premium) {
      padding-block-end: 0px !important;
    }
    [class*="🤑"],
    [class*="ads-rail"],
    .ads-rail-marker,
    [data-ads-rail-anchor],
    #pw-oop-video,
    .pw-oop-video,
    [id*="pw-oop"],
    [class*="pw-oop"],
    [id*="ramp_"],
    [class*="ramp_"],
    [id*="playwire"],
    [class*="playwire"],
    [data-pw-desk],
    [data-pw-mobi],
    iframe[src*="ad"],
    iframe[src*="doubleclick"],
    iframe[src*="google"],
    iframe[id*="google_ads"],
    div[id*="google_ads"],
    div[id^="pw_"],
    div[id^="pb-slot"],
    [id*="display-rr"],
    [id*="display-desktop-anchor"],
    [class*="AdContainer"],
    [class*="ad-container"],
    [class*="sidebar-ad"],
    [class*="SidebarAd"],
    [class*="BottomLeaderboard"],
    [class*="bottom-leaderboard"],
    [id*="leaderboard"],
    [class*="leaderboard"],
    a[href*="/premium"],
    div:has(> a[href*="/premium"]),
    div:has(> [class*="🤑-placeholder"]) {
      display: none !important;
      visibility: hidden !important;
      width: 0px !important;
      height: 0px !important;
      min-width: 0px !important;
      min-height: 0px !important;
      max-width: 0px !important;
      max-height: 0px !important;
      margin: 0px !important;
      padding: 0px !important;
      pointer-events: none !important;
      opacity: 0 !important;
      position: absolute !important;
      left: -9999px !important;
      top: -9999px !important;
      z-index: -99999 !important;
      overflow: hidden !important;
    }
  `);

  // 2. Pre-seed Pro role and defuse ad globals in main world
  const proUser = {
    id: "blitz-pro-user",
    name: "BlitzUser",
    roles: [
      { code: "PRO_SUBSCRIBER" },
      { code: "AD_FREE" },
      { code: "FREE_PRO_SUBSCRIBER" },
      { code: "ADMIN" }
    ],
    subscriptions: [
      {
        tier: "pro",
        status: "active",
        interval: "year",
        periodEnd: "2099-01-01T00:00:00.000Z"
      }
    ]
  };
  try {
    window.localStorage.setItem("$blitz:app:user", JSON.stringify(proUser));
  } catch(e) {}

  webFrame.executeJavaScript(`
    (() => {
      try {
        const proUser = {
          id: "blitz-pro-user",
          name: "BlitzUser",
          roles: [
            { code: "PRO_SUBSCRIBER" },
            { code: "AD_FREE" },
            { code: "FREE_PRO_SUBSCRIBER" },
            { code: "ADMIN" }
          ],
          subscriptions: [
            {
              tier: "pro",
              status: "active",
              interval: "year",
              periodEnd: "2099-01-01T00:00:00.000Z"
            }
          ]
        };
        try {
          window.localStorage.setItem("$blitz:app:user", JSON.stringify(proUser));
        } catch(e) {}

        window.tude = { cmd: { push: () => {} }, refreshAdsViaDivMappings: () => {}, setPageTargeting: () => {} };
        window.tudeserve = { cmd: { push: () => {} } };
        window.googletag = { cmd: { push: () => {} }, display: () => {}, pubads: () => ({ refresh: () => {}, enableSingleRequest: () => {}, setTargeting: () => {} }) };
        window.Raven = { cmd: { push: () => {} } };
      } catch(e) {}
    })();
  `);
} catch(e) {}'''

    new_content = content.replace(target, injection, 1)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("  [+] Patched src/preload.js (webFrame CSS injection + Pro role seeding + Script defuser)")


def patch_electron_window_handlers(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    target = "function interceptRequests(window) {"
    if target not in content:
        raise RuntimeError("Could not find target 'interceptRequests' in electronWindowHandlers.js")

    injection = '''function interceptRequests(window) {
  // __BLITZ_ADBLOCK_ACTIVE__
  const AD_DOMAINS = [
    "doubleclick.net", "googlesyndication.com", "google-analytics.com",
    "googleads", "adservice.google", "amazon-adsystem.com", "adnxs.com",
    "criteo.com", "criteo.net", "rubiconproject.com", "pubmatic.com",
    "openx.net", "casalemedia.com", "playwire.com", "intergi.com",
    "intergient.com", "nitropay.com", "taboola.com", "outbrain.com",
    "scorecardresearch.com", "quantserve.com", "serving-sys.com",
    "tribalfusion.com", "zedo.com", "adroll.com", "bidswitch.net",
    "lijit.com", "media.net", "sharethrough.com", "smartadserver.com",
    "yieldmo.com", "sonobi.com", "indexww.com", "sovrn.com",
    "btloader.com", "confiant-integrations.net", "browsiprod.com",
    "3lift.com", "undertone.com", "adsystem.com", "adpushup.com",
    "ezoic.com", "monetizemore.com", "snigel.com", "adthrive.com",
    "mediavine.com", "googletagservices.com", "googletagmanager.com",
    "adcolony.com", "applovin.com", "unity3d.com", "vungle.com",
    "chartboost.com", "ads.pub.network", "fuseplatform.net", "districtm.io",
    "kargo.com", "gumgum.com", "connatix.com", "infolinks.com",
    "revcontent.com", "aditude.io", "inmobi.com", "primis.tech", "primis",
    "dn0qt3r0xannq.cloudfront.net"
  ];

  const AD_PATH_FRAGMENTS = [
    "/ads.js", "prebid", "ramp.js", "gpt.js", "/pubads_impl",
    "/pagead/", "/tag/js/gpt.js", "zeus.json", "bolt.js", "choice.js",
    "rev/ads"
  ];

  window.webContents.session.webRequest.onBeforeRequest(
    { urls: ["*://*/*"] },
    (details, callback) => {
      try {
        const u = (details.url || "").toLowerCase();
        for (const d of AD_DOMAINS) {
          if (u.includes(d)) return callback({ cancel: true });
        }
        for (const frag of AD_PATH_FRAGMENTS) {
          if (u.includes(frag)) return callback({ cancel: true });
        }
      } catch (err) {}
      callback({ cancel: false });
    }
  );
'''

    new_content = content.replace(target, injection, 1)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("  [+] Patched src/electronWindowHandlers.js (Network ad blocker registered)")


def patch_auth(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    fetch_user_regex = re.compile(r"async function fetchUser\(\)\s*\{[\s\S]*?module\.exports", re.MULTILINE)
    m = fetch_user_regex.search(content)
    if not m:
        raise RuntimeError("Could not match 'fetchUser' block in auth.js")

    fetch_user_replacement = '''async function fetchUser() {
  const token = await getToken();
  let baseUser = null;
  if (token?.authToken) {
    try {
      const options = {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token.authToken}`,
        },
        data: {
          query: me,
        },
      };
      const res = await axios(AUTH_GRAPHQL_URL, options);
      baseUser = res?.data?.data?.me;
    } catch (e) {
      log.error("[core]", "[AUTH] Fetch user error", e?.response?.data?.errors);
    }
  }

  const proRoles = [
    { code: "PRO_SUBSCRIBER" },
    { code: "FREE_PRO_SUBSCRIBER" },
    { code: "AD_FREE" },
    { code: "ADMIN" }
  ];

  if (!baseUser) {
    return {
      name: "BlitzUser",
      roles: proRoles
    };
  }

  baseUser.roles = [...(baseUser.roles || []), ...proRoles];
  return baseUser;
}

function hasPremiumRole(roles) {
  // __BLITZ_ADBLOCK_ACTIVE__
  return true;
}

module.exports'''

    content = fetch_user_regex.sub(fetch_user_replacement, content, count=1)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [+] Patched src/auth.js (Ad-Free and Pro roles emulated)")


def patch_overlay_settings(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    pro_target = "async function checkProStatus() {"
    pro_replacement = '''async function checkProStatus() {
  // __BLITZ_ADBLOCK_ACTIVE__
  return true;'''

    if pro_target in content:
        content = content.replace(pro_target, pro_replacement, 1)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("  [+] Patched src/gameHandlers/lol/overlaySettings.js (Overlay Pro status enabled)")


def patch_listeners_utils(file_path):
    if not file_path.exists():
        return
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    target = "const getRoles = () => {"
    replacement = '''const getRoles = () => {
  // __BLITZ_ADBLOCK_ACTIVE__
  return Promise.resolve([
    { code: "blitzPro" },
    { code: "PRO_SUBSCRIBER" },
    { code: "AD_FREE" },
    { code: "FREE_PRO_SUBSCRIBER" }
  ]);'''

    if target in content:
        content = content.replace(target, replacement, 1)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("  [+] Patched src/listeners/utils.js (Immediate pro roles)")


def patch_create_window(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Lower minimum window size so the user can freely resize without the ad sidebar width restriction
    target_width = "const DEFAULT_MIN_WIDTH = 1075;"
    replacement_width = "const DEFAULT_MIN_WIDTH = 940; // __BLITZ_ADBLOCK_ACTIVE__"
    if target_width in content:
        content = content.replace(target_width, replacement_width, 1)

    # 2. Inject DOM / CSS ad killer into browserView webContents
    target_bv = 'browserView.webContents.loadURL(url);'
    replacement_bv = '''// __BLITZ_ADBLOCK_ACTIVE__
  browserView.webContents.on("dom-ready", () => {
    browserView.webContents.insertCSS(`
      :root, html, body, main {
        --right-rail-width: 0px !important;
        --rail-gap: 0px !important;
      }
      .content-container,
      .content-container.width-rail {
        width: 100% !important;
        max-width: 100% !important;
        grid-template-columns: minmax(0, 1fr) !important;
        gap: 0px !important;
      }
      .main-content,
      .main-content:not(.is-premium) {
        padding-block-end: 0px !important;
      }
      [class*="🤑"],
      [class*="ads-rail"],
      .ads-rail-marker,
      [data-ads-rail-anchor],
      #pw-oop-video,
      .pw-oop-video,
      [id*="pw-oop"],
      [class*="pw-oop"],
      [id*="ramp_"],
      [class*="ramp_"],
      [id*="playwire"],
      [class*="playwire"],
      [data-pw-desk],
      [data-pw-mobi],
      iframe[src*="ad"],
      iframe[src*="doubleclick"],
      iframe[src*="google"],
      iframe[id*="google_ads"],
      div[id*="google_ads"],
      div[id^="pw_"],
      div[id^="pb-slot"],
      [id*="display-rr"],
      [id*="display-desktop-anchor"],
      [class*="AdContainer"],
      [class*="ad-container"],
      [class*="sidebar-ad"],
      [class*="SidebarAd"],
      [class*="BottomLeaderboard"],
      [class*="bottom-leaderboard"],
      [id*="leaderboard"],
      [class*="leaderboard"],
      a[href*="/premium"],
      div:has(> a[href*="/premium"]),
      div:has(> [class*="🤑-placeholder"]) {
        display: none !important;
        visibility: hidden !important;
        width: 0px !important;
        height: 0px !important;
        min-width: 0px !important;
        min-height: 0px !important;
        max-width: 0px !important;
        max-height: 0px !important;
        margin: 0px !important;
        padding: 0px !important;
        pointer-events: none !important;
        opacity: 0 !important;
        position: absolute !important;
        left: -9999px !important;
        top: -9999px !important;
        z-index: -99999 !important;
        overflow: hidden !important;
      }
    `);

    browserView.webContents.executeJavaScript(`
      (() => {
        const purgeAds = () => {
          try {
            const proUser = {
              id: "blitz-pro-user",
              name: "BlitzUser",
              roles: [
                { code: "PRO_SUBSCRIBER" },
                { code: "AD_FREE" },
                { code: "FREE_PRO_SUBSCRIBER" },
                { code: "ADMIN" }
              ],
              subscriptions: [
                {
                  tier: "pro",
                  status: "active",
                  interval: "year",
                  periodEnd: "2099-01-01T00:00:00.000Z"
                }
              ]
            };
            window.localStorage.setItem("$blitz:app:user", JSON.stringify(proUser));

            window.tude = { cmd: { push: () => {} }, refreshAdsViaDivMappings: () => {}, setPageTargeting: () => {} };
            window.tudeserve = { cmd: { push: () => {} } };
            window.googletag = { cmd: { push: () => {} }, display: () => {}, pubads: () => ({ refresh: () => {}, enableSingleRequest: () => {}, setTargeting: () => {} }) };
            window.Raven = { cmd: { push: () => {} } };

            const bad = [
              '#pw-oop-video', '.pw-oop-video', '[id*="pw-oop"]', '[class*="pw-oop"]',
              'iframe[src*="google"]', 'iframe[src*="doubleclick"]', 'iframe[id*="google_ads"]',
              'div[id*="google_ads"]', 'div[id^="pw_"]', 'div[id^="pb-slot"]',
              '[id*="display-rr"]', '[id*="display-desktop-anchor"]',
              '[class*="🤑"]', '[class*="ads-rail"]', '.ads-rail-marker',
              '[data-ads-rail-anchor]', '[data-pw-desk]', '[data-pw-mobi]',
              '[id*="playwire"]', '[class*="playwire"]', '[id*="ramp_"]', '[class*="ramp_"]',
              '[class*="bottom-leaderboard"]', '[class*="BottomLeaderboard"]',
              '[class*="sidebar-ad"]', '[class*="SidebarAd"]'
            ];
            for (const s of bad) {
              document.querySelectorAll(s).forEach(e => { try { e.remove(); } catch(err) {} });
            }

            document.querySelectorAll('video').forEach(v => {
              if (v.closest('#pw-oop-video, .pw-oop-video, [id*="pw-oop"], [class*="pw-oop"], [class*="ad"], [id*="ad"]')) {
                try { v.pause(); v.src = ""; v.remove(); } catch(err) {}
              }
            });

            document.querySelectorAll('a[href*="/premium"], button, span, div').forEach(el => {
              if (el.children.length === 0) {
                const t = (el.textContent || '').trim().toLowerCase();
                if (t.includes('remove ads with premium') || t === 'remove ads') {
                  let p = el.parentElement;
                  while (p && p !== document.body && p.children.length === 1) {
                    p.style.display = 'none';
                    p = p.parentElement;
                  }
                  el.style.display = 'none';
                  try { el.remove(); } catch(err) {}
                }
              }
            });
          } catch(e) {}
        };

        purgeAds();
        setInterval(purgeAds, 500);
      })();
    `);
  });

  browserView.webContents.loadURL(url);'''

    if target_bv in content:
        content = content.replace(target_bv, replacement_bv, 1)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [+] Patched src/createWindow.js (Direct CSS injection, Pro user seeding, and active DOM purging)")


def verify_js_syntax(file_path):
    res = subprocess.run(["node", "-c", str(file_path)], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Syntax verification failed for {file_path.name}: {res.stderr}")


def apply_patch():
    print("=" * 60)
    print(" Blitz AdBlocker - Applying Complete Patch")
    print("=" * 60)

    if not check_blitz_installed():
        return False

    kill_blitz()

    # 1. Patch anti-tamper in binaries
    patch_blitz_core_nodes()

    # 2. Clear stale cache files
    clean_blitz_caches()

    # Ensure app.asar.unpacked is present and intact before extracting
    if not UNPACKED_DIR.exists() and BACKUP_UNPACKED_DIR.exists():
        shutil.copytree(BACKUP_UNPACKED_DIR, UNPACKED_DIR)

    # If current app.asar is not patched, update BACKUP_FILE
    if not is_already_patched(ASAR_FILE):
        print(f"[*] Detected unpatched/updated app.asar. Creating/updating backup: {BACKUP_FILE}")
        shutil.copy2(ASAR_FILE, BACKUP_FILE)
        if UNPACKED_DIR.exists():
            if BACKUP_UNPACKED_DIR.exists():
                shutil.rmtree(BACKUP_UNPACKED_DIR, ignore_errors=True)
            shutil.copytree(UNPACKED_DIR, BACKUP_UNPACKED_DIR)
        print("[+] Backup created successfully.")
    else:
        if BACKUP_FILE.exists():
            print("[*] Rebuilding from clean backup source...")
            shutil.copy2(BACKUP_FILE, ASAR_FILE)
            if BACKUP_UNPACKED_DIR.exists():
                if UNPACKED_DIR.exists():
                    shutil.rmtree(UNPACKED_DIR, ignore_errors=True)
                shutil.copytree(BACKUP_UNPACKED_DIR, UNPACKED_DIR)
        else:
            print("[*] Warning: app.asar already contains adblock marker and no backup exists.")

    # Temporary directory for extraction
    temp_extract_dir = Path(tempfile.mkdtemp(prefix="blitz_patch_"))
    repacked_file = temp_extract_dir.parent / "repacked_app.asar"

    try:
        print("[*] Extracting app.asar (using npx @electron/asar)...")
        extract_cmd = ["npx.cmd" if os.name == "nt" else "npx", "@electron/asar", "extract", str(ASAR_FILE), str(temp_extract_dir)]
        subprocess.run(extract_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)

        print("[*] Modifying application files...")
        files_to_verify = []

        preload_path = temp_extract_dir / "src" / "preload.js"
        patch_preload(preload_path)
        files_to_verify.append(preload_path)

        handlers_path = temp_extract_dir / "src" / "electronWindowHandlers.js"
        patch_electron_window_handlers(handlers_path)
        files_to_verify.append(handlers_path)

        auth_path = temp_extract_dir / "src" / "auth.js"
        patch_auth(auth_path)
        files_to_verify.append(auth_path)

        overlay_path = temp_extract_dir / "src" / "gameHandlers" / "lol" / "overlaySettings.js"
        patch_overlay_settings(overlay_path)
        files_to_verify.append(overlay_path)

        utils_path = temp_extract_dir / "src" / "listeners" / "utils.js"
        patch_listeners_utils(utils_path)
        files_to_verify.append(utils_path)

        create_window_path = temp_extract_dir / "src" / "createWindow.js"
        patch_create_window(create_window_path)
        files_to_verify.append(create_window_path)

        print("[*] Verifying JavaScript syntax of patched files...")
        for f in files_to_verify:
            verify_js_syntax(f)
        print("[+] All patched JavaScript files passed syntax verification.")

        print("[*] Repacking app.asar...")
        pack_cmd = [
            "npx.cmd" if os.name == "nt" else "npx",
            "@electron/asar",
            "pack",
            str(temp_extract_dir),
            str(repacked_file),
            "--unpack",
            "{**/node_modules/classic-level/prebuilds/**/*,**/node_modules/lzma-native/**/*}"
        ]
        subprocess.run(pack_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)

        print("[*] Replacing app.asar and app.asar.unpacked with patched version...")
        shutil.copy2(repacked_file, ASAR_FILE)
        repacked_unpacked = Path(str(repacked_file) + ".unpacked")
        if repacked_unpacked.exists():
            if UNPACKED_DIR.exists():
                shutil.rmtree(UNPACKED_DIR, ignore_errors=True)
            shutil.copytree(repacked_unpacked, UNPACKED_DIR)
            print("[+] Synchronized app.asar.unpacked native binary dependencies.")

        print("[+] Success: Blitz has been completely patched!")
        print("[+] Anti-tamper bypassed, network ad blocker active, Pro roles emulated, and CSS/DOM ad elimination installed.")
        return True

    except Exception as e:
        print(f"[-] Error during patching: {e}")
        if BACKUP_FILE.exists():
            print("[*] Reverting changes from backup...")
            shutil.copy2(BACKUP_FILE, ASAR_FILE)
            if BACKUP_UNPACKED_DIR.exists():
                if UNPACKED_DIR.exists():
                    shutil.rmtree(UNPACKED_DIR, ignore_errors=True)
                shutil.copytree(BACKUP_UNPACKED_DIR, UNPACKED_DIR)
        return False

    finally:
        print("[*] Cleaning up temporary files...")
        if temp_extract_dir.exists():
            shutil.rmtree(temp_extract_dir, ignore_errors=True)
        if repacked_file.exists():
            try:
                repacked_file.unlink()
            except Exception:
                pass
        unpacked_tmp = Path(str(repacked_file) + ".unpacked")
        if unpacked_tmp.exists():
            shutil.rmtree(unpacked_tmp, ignore_errors=True)


def restore_backup():
    print("=" * 60)
    print(" Blitz AdBlocker - Restoring Original App")
    print("=" * 60)

    kill_blitz()
    restore_blitz_core_nodes()

    if BACKUP_FILE.exists():
        print("[*] Restoring app.asar from backup...")
        try:
            shutil.copy2(BACKUP_FILE, ASAR_FILE)
            if BACKUP_UNPACKED_DIR.exists():
                if UNPACKED_DIR.exists():
                    shutil.rmtree(UNPACKED_DIR, ignore_errors=True)
                shutil.copytree(BACKUP_UNPACKED_DIR, UNPACKED_DIR)
            print("[+] Success: Original app.asar restored successfully.")
        except Exception as e:
            print(f"[-] Error restoring backup: {e}")
            return False
    return True


def launch_blitz():
    exe = DEFAULT_BLITZ_PATH / "Blitz.exe"
    if exe.exists():
        print("[*] Launching Blitz...")
        try:
            # Use CREATE_BREAKAWAY_FROM_JOB / DETACHED_PROCESS on Windows so it survives CLI termination
            flags = 0x00000008 if os.name == "nt" else 0
            subprocess.Popen([str(exe)], creationflags=flags, close_fds=True)
            print("[+] Blitz launched successfully.")
        except Exception as e:
            print(f"[-] Warning: Failed to launch Blitz: {e}")


def print_status():
    print("=" * 60)
    print(" Blitz AdBlocker - Status Check")
    print("=" * 60)
    if not ASAR_FILE.exists():
        print(f"[-] Blitz app.asar not found at: {ASAR_FILE}")
        return False

    asar_patched = is_already_patched(ASAR_FILE)
    print(f"[*] app.asar status: {'[PATCHED - ADS BLOCKED]' if asar_patched else '[UNPATCHED]'}")

    nodes = get_blitz_core_nodes()
    all_nodes_patched = len(nodes) > 0
    for node in nodes:
        patched = is_node_binary_patched(node)
        if not patched:
            all_nodes_patched = False
        print(f"[*] {node.name} ({node.parent.name}): {'[PATCHED - BYPASS ACTIVE]' if patched else '[UNPATCHED]'}")

    overall = asar_patched and all_nodes_patched
    print(f"[*] Overall AdBlock status: {'ACTIVE' if overall else 'INACTIVE / NEEDS PATCH'}")
    return overall


if __name__ == "__main__":
    args = [a.lower() for a in sys.argv[1:]]
    do_launch = "--launch" in args or "-launch" in args
    clean_args = [a for a in args if a not in ["--launch", "-launch"]]

    if clean_args:
        arg = clean_args[0]
        if arg in ["--restore", "-restore", "restore"]:
            success = restore_backup()
            if success and do_launch:
                launch_blitz()
            sys.exit(0 if success else 1)
        elif arg in ["--patch", "-patch", "patch"]:
            success = apply_patch()
            if success and do_launch:
                launch_blitz()
            sys.exit(0 if success else 1)
        elif arg in ["--status", "-status", "status"]:
            success = print_status()
            sys.exit(0 if success else 1)
        elif arg in ["--check-only", "-check-only", "check"]:
            asar_ok = is_already_patched(ASAR_FILE)
            nodes = get_blitz_core_nodes()
            nodes_ok = len(nodes) > 0 and all(is_node_binary_patched(n) for n in nodes)
            sys.exit(0 if (asar_ok and nodes_ok) else 1)
        else:
            print(f"Unknown argument: {arg}")
            print("Usage: patch_blitz.py [--patch | --restore | --status | --check-only] [--launch]")
            sys.exit(1)
    else:
        success = apply_patch()
        if success and do_launch:
            launch_blitz()
        sys.exit(0 if success else 1)
