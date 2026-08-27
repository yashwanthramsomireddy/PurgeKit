"""
PurgeKit v3.0 — Cleaning Engine
MIT License — TeamExyKings
"""

import os
import shutil
import subprocess
import datetime
import string
import ctypes
import platform

def ep(path):
    return os.path.expandvars(path)

def run(cmd, timeout=120):
    try:
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=timeout)
    except Exception:
        pass

def get_drives():
    drives = []
    if platform.system() != "Windows":
        return [("C:\\", "System", 0, 0)]
    for letter in string.ascii_uppercase:
        path = f"{letter}:\\"
        if os.path.exists(path):
            try:
                total, free = 0, 0
                try:
                    stat  = shutil.disk_usage(path)
                    total = stat.total
                    free  = stat.free
                except Exception:
                    pass
                label = ""
                try:
                    buf = ctypes.create_unicode_buffer(261)
                    ctypes.windll.kernel32.GetVolumeInformationW(
                        path, buf, 261, None, None, None, None, 0)
                    label = buf.value
                except Exception:
                    pass
                if total > 0:
                    drives.append((path, label, free, total))
            except Exception:
                pass
    return drives if drives else [("C:\\", "System", 0, 0)]

def fmt_size(b):
    if b is None or b < 0:
        return "0 B"
    if b >= 1 << 30:
        return f"{b / (1<<30):.2f} GB"
    if b >= 1 << 20:
        return f"{b / (1<<20):.1f} MB"
    if b >= 1 << 10:
        return f"{b / (1<<10):.1f} KB"
    return f"{b} B"

def folder_size(path):
    total = 0
    try:
        for root, dirs, files in os.walk(path):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except Exception:
                    pass
    except Exception:
        pass
    return total

def count_files(path):
    count = 0
    try:
        for root, dirs, files in os.walk(path):
            count += len(files)
    except Exception:
        pass
    return count

def recreate(path):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        pass

def force_delete(path, log_fn, reboot_flag, dry_run=False):
    if not os.path.exists(path):
        log_fn(f"  [SKIP] Not found: {path}", "dim")
        return 0

    size = folder_size(path)

    if dry_run:
        log_fn(f"  [DRY RUN] Would delete: {path}  ({fmt_size(size)})", "warn")
        return size

    # T1 — robocopy mirror
    empty = os.path.join(os.environ.get("TEMP", r"C:\Windows\Temp"), "_purgekit_empty_")
    os.makedirs(empty, exist_ok=True)
    run(f'robocopy "{empty}" "{path}" /MIR /NFL /NDL /NJH /NJS /nc /ns /np')
    try:
        shutil.rmtree(path, ignore_errors=True)
    except Exception:
        pass

    if not os.path.exists(path):
        log_fn(f"  ✅ T1 (robocopy) — freed {fmt_size(size)}", "success")
        return size

    # T2 — takeown + icacls
    log_fn("  ⚠ T1 failed, trying T2 (takeown)...", "warn")
    run(f'takeown /f "{path}" /r /d y')
    run(f'icacls "{path}" /grant administrators:F /t /q')
    try:
        shutil.rmtree(path, ignore_errors=True)
    except Exception:
        pass

    if not os.path.exists(path):
        log_fn(f"  ✅ T2 (takeown) — freed {fmt_size(size)}", "success")
        return size

    # T3 — schedule on reboot
    log_fn("  ⚠ T2 failed, scheduling on reboot (T3)...", "warn")
    for root_dir, dirs, files in os.walk(path):
        for f in files:
            full = os.path.join(root_dir, f)
            run(f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager" '
                f'/v PendingFileRenameOperations /t REG_MULTI_SZ /d "\\??\\{full}\\0" /f')
    reboot_flag[0] = True
    log_fn(f"  🔁 T3 — scheduled for reboot: {path}", "warn")
    return 0

# ── Task definitions ─────────────────────────────────────────
# (id, phase, label, path_display, env_expand, default_checked, warning)
TASKS = [
    ("S1",  "System",    "Windows System Temp",              r"C:\Windows\Temp",                                                 False, True,  None),
    ("S2",  "System",    "Prefetch Files",                   r"C:\Windows\Prefetch",                                             False, True,  None),
    ("S3",  "System",    "Windows Update Cache",             r"C:\Windows\SoftwareDistribution\Download",                        False, True,  None),
    ("S4",  "System",    "Delivery Optimization Files",      r"C:\Windows\SoftwareDistribution\DeliveryOptimization",            False, True,  None),
    ("S5",  "System",    "Windows Error Reporting",          r"C:\ProgramData\Microsoft\Windows\WER",                            False, True,  None),
    ("S6",  "System",    "CBS Logs",                         r"C:\Windows\Logs\CBS",                                             False, True,  None),
    ("S7",  "System",    "Crash Dumps",                      r"C:\Windows\Minidump",                                             False, True,  None),
    ("S8",  "System",    "Windows Font Cache",               r"C:\Windows\ServiceProfiles\LocalService\AppData\Local\FontCache",  False, True,  None),
    ("S9",  "System",    "SoftwareDistribution Logs",        r"C:\Windows\SoftwareDistribution\DataStore\Logs",                  False, True,  None),
    ("S10", "System",    "Windows Installer Patch Cache",    r"C:\Windows\Installer\$PatchCache$",                               False, True,  None),
    ("S11", "System",    "DNS Cache (Flush)",                "System DNS Resolver",                                              False, True,  None),
    ("U1",  "User",      "User Temp Folder (%TEMP%)",        "%TEMP%",                                                           True,  True,  None),
    ("U1b", "User",      "LocalAppData Temp",                r"%LOCALAPPDATA%\Temp",                                             True,  True,  None),
    ("U2",  "User",      "Thumbnail Cache",                  r"%LOCALAPPDATA%\Microsoft\Windows\Explorer",                       True,  True,  None),
    ("U3",  "User",      "Recent Files & Jump Lists",        r"%APPDATA%\Microsoft\Windows\Recent",                              True,  True,  None),
    ("U4",  "User",      "IE / Legacy Edge WebCache",        r"%LOCALAPPDATA%\Microsoft\Windows\WebCache",                       True,  True,  None),
    ("U4b", "User",      "IE / Legacy INetCache",            r"%LOCALAPPDATA%\Microsoft\Windows\INetCache",                      True,  True,  None),
    ("U5",  "User",      "DirectX Shader Cache",             r"%LOCALAPPDATA%\D3DSCache",                                        True,  True,  None),
    ("U5b", "User",      "User Crash Dumps",                 r"%LOCALAPPDATA%\CrashDumps",                                       True,  True,  None),
    ("U6",  "User",      "Microsoft Teams Cache",            r"%APPDATA%\Microsoft\Teams\Cache",                                 True,  True,  None),
    ("U7",  "User",      "VS Code Cache",                    r"%APPDATA%\Code\Cache",                                            True,  True,  None),
    ("U8",  "User",      "Microsoft Office Cache",           r"%LOCALAPPDATA%\Microsoft\Office\16.0\OfficeFileCache",            True,  True,  None),
    ("U9",  "User",      "Spotify Cache",                    r"%LOCALAPPDATA%\Spotify\Storage",                                  True,  True,  None),
    ("U10", "User",      "Icon Cache",                       r"%LOCALAPPDATA%\IconCache.db",                                     True,  True,  None),
    ("U11", "User",      "Clipboard History",                "Windows Clipboard",                                                False, True,  None),
    ("U12", "User",      "Windows Store Cache (wsreset)",    "Microsoft Store",                                                  False, True,  None),
    ("B1",  "Browser",   "Chrome — Cache + Code + GPU",      r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache",            True,  True,  None),
    ("B1b", "Browser",   "Chrome — Service Worker Cache",    r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Service Worker",   True,  True,  None),
    ("B2",  "Browser",   "Firefox — Cache (All Profiles)",   r"%LOCALAPPDATA%\Mozilla\Firefox\Profiles",                         True,  True,  None),
    ("B3",  "Browser",   "Edge — Cache + Code + GPU",        r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache",           True,  True,  None),
    ("B3b", "Browser",   "Edge — Service Worker Cache",      r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Service Worker",  True,  True,  None),
    ("D1",  "Developer", "npm Cache",                        r"%APPDATA%\npm-cache",                                             True,  False, "Clears npm package cache. Packages re-download when needed."),
    ("D2",  "Developer", "pip Cache",                        r"%LOCALAPPDATA%\pip\cache",                                        True,  False, "Clears pip package cache. Packages re-download when needed."),
    ("O1",  "Optional",  "Event Logs (App + System)",        "Windows Event Viewer Logs",                                        False, False, "Clears Application, System and Security logs. Diagnostic history lost."),
    ("O2",  "Optional",  "Recycle Bin (All Drives)",         "All Drive Recycle Bins",                                           False, False, "Permanently deletes all items in Recycle Bin across all drives."),
    ("O3",  "Optional",  "Windows Telemetry Data",           r"C:\ProgramData\Microsoft\Diagnosis",                              False, False, "Removes telemetry data sent to Microsoft."),
    ("O4",  "Optional",  "Cortana / Search History",         r"%LOCALAPPDATA%\Packages\Microsoft.Windows.Search*",               True,  False, "Clears Cortana and Windows Search history."),
    ("O5",  "Optional",  "ARP Cache (Flush)",                "Network ARP Table",                                                False, False, "Flushes ARP table. Network may rebuild briefly."),
    ("O6",  "Optional",  "NetBIOS Cache (Flush)",            "NetBIOS Name Cache",                                               False, False, "Flushes NetBIOS name cache."),
    ("O7",  "Optional",  "Winsock Reset",                    "Windows Network Stack",                                            False, False, "⚠ REQUIRES REBOOT. Use only for network issues."),
    ("O8",  "Optional",  "Windows Search Index Rebuild",     "Windows Search Index",                                             False, False, "⚠ Search slow for hours while index rebuilds."),
    ("O9",  "Optional",  "DNS Cache (Extra Flush)",          "System DNS Resolver",                                              False, False, "Additional DNS flush. Useful after VPN or network changes."),
]

SKIP_RECREATE = {
    "System DNS Resolver", "Windows Clipboard", "Microsoft Store",
    "Network ARP Table", "NetBIOS Name Cache", "Windows Network Stack",
    "Windows Search Index", "All Drive Recycle Bins", "Windows Event Viewer Logs",
}

DISK_CLEANUP_CATS = [
    "Active Setup Temp Folders","BranchCache","Content Indexer Cleaner",
    "D3D Shader Cache","Delivery Optimization Files","Device Driver Packages",
    "Downloaded Program Files","Internet Cache Files","Memory Dump Files",
    "Offline Pages Files","Old ChkDsk Files","Previous Installations",
    "Recycle Bin","Service Pack Cleanup","Setup Log Files",
    "System error memory dump files","System error minidump files",
    "Temporary Files","Temporary Setup Files","Thumbnail Cache",
    "Update Cleanup","Upgrade Discarded Files","Windows Defender",
    "Windows Error Reporting Archive Files","Windows Error Reporting Files",
    "Windows Error Reporting Queue Files","Windows ESD installation files",
    "Windows Upgrade Log Files",
]

def run_task(tid, log_fn, reboot_flag, dry_run=False):
    """Run a single task by ID. Returns bytes freed."""
    task = next((t for t in TASKS if t[0] == tid), None)
    if not task:
        return 0
    tid, phase, label, path, do_exp, default, warning = task
    rp    = ep(path) if do_exp else path
    freed = 0

    if tid == "S3":
        run("net stop wuauserv"); run("net stop bits")
        freed += force_delete(rp, log_fn, reboot_flag, dry_run); recreate(rp)
        run("net start wuauserv"); run("net start bits")
    elif tid == "S4":
        run("net stop DoSvc")
        freed += force_delete(rp, log_fn, reboot_flag, dry_run); recreate(rp)
        run("net start DoSvc")
    elif tid == "S8":
        run("net stop FontCache")
        freed += force_delete(rp, log_fn, reboot_flag, dry_run); recreate(rp)
        run("net start FontCache")
    elif tid == "S9":
        run("net stop wuauserv")
        freed += force_delete(rp, log_fn, reboot_flag, dry_run); recreate(rp)
        run("net start wuauserv")
    elif tid in ("S11", "O9"):
        if not dry_run:
            run("ipconfig /flushdns")
        log_fn("  ✅ DNS cache flushed", "success")
    elif tid == "U1b":
        p = ep(r"%LOCALAPPDATA%\Temp")
        freed += force_delete(p, log_fn, reboot_flag, dry_run); recreate(p)
    elif tid == "U2":
        if not dry_run:
            run("taskkill /f /im explorer.exe")
        thumbs = ep(r"%LOCALAPPDATA%\Microsoft\Windows\Explorer")
        if os.path.exists(thumbs):
            for f in os.listdir(thumbs):
                if f.startswith("thumbcache_") and f.endswith(".db"):
                    fp = os.path.join(thumbs, f)
                    try:
                        freed += os.path.getsize(fp)
                        if not dry_run:
                            os.remove(fp)
                    except Exception:
                        pass
        if not dry_run:
            run("start explorer.exe")
        log_fn("  ✅ Thumbnail cache cleared", "success")
    elif tid == "U4":
        freed += force_delete(ep(r"%LOCALAPPDATA%\Microsoft\Windows\WebCache"), log_fn, reboot_flag, dry_run)
        recreate(ep(r"%LOCALAPPDATA%\Microsoft\Windows\WebCache"))
    elif tid == "U5b":
        freed += force_delete(ep(r"%LOCALAPPDATA%\CrashDumps"), log_fn, reboot_flag, dry_run)
        recreate(ep(r"%LOCALAPPDATA%\CrashDumps"))
    elif tid == "U6":
        if not dry_run:
            run("taskkill /f /im Teams.exe")
        for sub in [r"%APPDATA%\Microsoft\Teams\Cache", r"%APPDATA%\Microsoft\Teams\blob_storage"]:
            p = ep(sub)
            freed += force_delete(p, log_fn, reboot_flag, dry_run); recreate(p)
    elif tid == "U7":
        if not dry_run:
            run("taskkill /f /im Code.exe")
        for sub in [r"%APPDATA%\Code\Cache", r"%APPDATA%\Code\CachedData"]:
            p = ep(sub)
            freed += force_delete(p, log_fn, reboot_flag, dry_run); recreate(p)
    elif tid == "U9":
        if not dry_run:
            run("taskkill /f /im Spotify.exe")
        freed += force_delete(rp, log_fn, reboot_flag, dry_run); recreate(rp)
    elif tid == "U10":
        ic = ep(r"%LOCALAPPDATA%\IconCache.db")
        if os.path.exists(ic):
            try:
                freed += os.path.getsize(ic)
                if not dry_run:
                    run("taskkill /f /im explorer.exe")
                    os.remove(ic)
                    run("start explorer.exe")
                log_fn("  ✅ IconCache.db deleted", "success")
            except Exception:
                if not dry_run:
                    run(f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager" '
                        f'/v PendingFileRenameOperations /t REG_MULTI_SZ /d "\\??\\{ic}\\0" /f')
                    reboot_flag[0] = True
    elif tid == "U11":
        if not dry_run:
            run("cmd /c echo. | clip")
        log_fn("  ✅ Clipboard cleared", "success")
    elif tid == "U12":
        if not dry_run:
            run("wsreset.exe")
        log_fn("  ✅ Windows Store cache reset", "success")
    elif tid == "B1":
        if not dry_run:
            run("taskkill /f /im chrome.exe")
        base = ep(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default")
        for sub in ["Cache", "Code Cache", "GPUCache"]:
            p = os.path.join(base, sub)
            freed += force_delete(p, log_fn, reboot_flag, dry_run); recreate(p)
        log_fn("  ✅ Chrome cache cleared", "success")
    elif tid == "B1b":
        if not dry_run:
            run("taskkill /f /im chrome.exe")
        sw = ep(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Service Worker\CacheStorage")
        freed += force_delete(sw, log_fn, reboot_flag, dry_run); recreate(sw)
        log_fn("  ✅ Chrome Service Worker cache cleared", "success")
    elif tid == "B2":
        if not dry_run:
            run("taskkill /f /im firefox.exe")
        profiles = ep(r"%LOCALAPPDATA%\Mozilla\Firefox\Profiles")
        if os.path.exists(profiles):
            for prof in os.listdir(profiles):
                for sub in ["cache2", "startupCache", "jumpListCache"]:
                    p = os.path.join(profiles, prof, sub)
                    freed += force_delete(p, log_fn, reboot_flag, dry_run); recreate(p)
        log_fn("  ✅ Firefox cache cleared", "success")
    elif tid == "B3":
        if not dry_run:
            run("taskkill /f /im msedge.exe")
        base = ep(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default")
        for sub in ["Cache", "Code Cache", "GPUCache"]:
            p = os.path.join(base, sub)
            freed += force_delete(p, log_fn, reboot_flag, dry_run); recreate(p)
        log_fn("  ✅ Edge cache cleared", "success")
    elif tid == "B3b":
        if not dry_run:
            run("taskkill /f /im msedge.exe")
        sw = ep(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Service Worker\CacheStorage")
        freed += force_delete(sw, log_fn, reboot_flag, dry_run); recreate(sw)
        log_fn("  ✅ Edge Service Worker cache cleared", "success")
    elif tid == "D1":
        freed += force_delete(ep(r"%APPDATA%\npm-cache"), log_fn, reboot_flag, dry_run)
        recreate(ep(r"%APPDATA%\npm-cache"))
        log_fn("  ✅ npm cache cleared", "success")
    elif tid == "D2":
        freed += force_delete(ep(r"%LOCALAPPDATA%\pip\cache"), log_fn, reboot_flag, dry_run)
        recreate(ep(r"%LOCALAPPDATA%\pip\cache"))
        log_fn("  ✅ pip cache cleared", "success")
    elif tid == "S5":
        for sub in ["ReportQueue", "ReportArchive"]:
            p = rf"C:\ProgramData\Microsoft\Windows\WER\{sub}"
            freed += force_delete(p, log_fn, reboot_flag, dry_run); recreate(p)
    elif tid == "S7":
        freed += force_delete(r"C:\Windows\Minidump", log_fn, reboot_flag, dry_run)
        recreate(r"C:\Windows\Minidump")
        memdmp = r"C:\Windows\MEMORY.DMP"
        if os.path.exists(memdmp):
            try:
                freed += os.path.getsize(memdmp)
                if not dry_run:
                    os.remove(memdmp)
                    log_fn("  ✅ MEMORY.DMP deleted", "success")
            except Exception:
                if not dry_run:
                    run('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager" '
                        '/v PendingFileRenameOperations /t REG_MULTI_SZ '
                        '/d "\\??\\C:\\Windows\\MEMORY.DMP\\0" /f')
                    reboot_flag[0] = True
    elif tid == "O1":
        if not dry_run:
            for lg in ["Application", "System", "Security"]:
                run(f'wevtutil cl "{lg}"')
        log_fn("  ✅ Event logs cleared", "success")
    elif tid == "O2":
        for drv, _, _, _ in get_drives():
            rb = os.path.join(drv, "$Recycle.Bin")
            freed += force_delete(rb, log_fn, reboot_flag, dry_run)
        log_fn("  ✅ Recycle Bin emptied", "success")
    elif tid == "O3":
        freed += force_delete(r"C:\ProgramData\Microsoft\Diagnosis", log_fn, reboot_flag, dry_run)
        log_fn("  ✅ Telemetry data removed", "success")
    elif tid == "O4":
        pkg = ep(r"%LOCALAPPDATA%\Packages")
        if os.path.exists(pkg):
            for p in os.listdir(pkg):
                if "Microsoft.Windows.Search" in p:
                    dc = os.path.join(pkg, p, "LocalState", "DeviceSearchCache")
                    freed += force_delete(dc, log_fn, reboot_flag, dry_run)
        log_fn("  ✅ Cortana search history cleared", "success")
    elif tid == "O5":
        if not dry_run:
            run("arp -d *")
        log_fn("  ✅ ARP cache flushed", "success")
    elif tid == "O6":
        if not dry_run:
            run("nbtstat -R")
        log_fn("  ✅ NetBIOS cache flushed", "success")
    elif tid == "O7":
        if not dry_run:
            run("netsh winsock reset")
            reboot_flag[0] = True
        log_fn("  ✅ Winsock reset — REBOOT REQUIRED", "warn")
    elif tid == "O8":
        if not dry_run:
            run("sc config WSearch start= disabled")
            run("net stop WSearch")
            run("sc config WSearch start= auto")
            run("net start WSearch")
        log_fn("  ✅ Search index rebuild triggered", "success")
    else:
        freed += force_delete(rp, log_fn, reboot_flag, dry_run)
        if rp not in SKIP_RECREATE:
            recreate(rp)

    return freed
