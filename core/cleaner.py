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
    ("D3",  "Developer", "Maven Cache",                      r"%USERPROFILE%\.m2\repository",                                    False, False, "Clears Maven local repository cache. Packages re-download when needed."),
    ("D4",  "Developer", "Gradle Cache",                     r"%USERPROFILE%\.gradle\caches",                                    False, False, "Clears Gradle build cache. Re-downloads on next build."),
    ("D5",  "Developer", "Docker Logs",                      r"%LOCALAPPDATA%\Docker\log",                                       False, False, "Clears Docker Desktop log files."),
    ("D3",  "Developer", "Maven Cache",                      r"%USERPROFILE%\.m2\repository",                                    False, False, "Clears Maven local repository cache. Packages re-download when needed."),
    ("D4",  "Developer", "Gradle Cache",                     r"%USERPROFILE%\.gradle\caches",                                    False, False, "Clears Gradle build cache. Re-downloads on next build."),
    ("D5",  "Developer", "Docker Logs",                      r"%LOCALAPPDATA%\Docker\log",                                       False, False, "Clears Docker Desktop log files."),
    ("O1",  "Optional",  "Event Logs (App + System)",        "Windows Event Viewer Logs",                                        False, False, "Clears Application, System and Security logs. Diagnostic history lost."),
    ("O2",  "Optional",  "Recycle Bin (All Drives)",         "All Drive Recycle Bins",                                           False, False, "Permanently deletes all items in Recycle Bin across all drives."),
    ("O3",  "Optional",  "Windows Telemetry Data",           r"C:\ProgramData\Microsoft\Diagnosis",                              False, False, "Removes telemetry data sent to Microsoft."),
    ("O4",  "Optional",  "Cortana / Search History",         r"%LOCALAPPDATA%\Packages\Microsoft.Windows.Search*",               True,  False, "Clears Cortana and Windows Search history."),
    ("O5",  "Optional",  "ARP Cache (Flush)",                "Network ARP Table",                                                False, False, "Flushes ARP table. Network may rebuild briefly."),
    ("O6",  "Optional",  "NetBIOS Cache (Flush)",            "NetBIOS Name Cache",                                               False, False, "Flushes NetBIOS name cache."),
    ("O7",  "Optional",  "Winsock Reset",                    "Windows Network Stack",                                            False, False, "⚠ REQUIRES REBOOT. Use only for network issues."),
    ("O8",  "Optional",  "Windows Search Index Rebuild",     "Windows Search Index",                                             False, False, "⚠ Search slow for hours while index rebuilds."),
    ("U13", "User",      "Zoom Cache",                       r"%APPDATA%\Zoom\data",                                             True,  True,  None),
    ("U14", "User",      "Zoom Logs",                        r"%APPDATA%\Zoom\logs",                                             True,  True,  None),
    ("U15", "User",      "Discord Cache",                    r"%APPDATA%\discord\Cache",                                         True,  True,  None),
    ("U15b","User",      "Discord Code Cache",               r"%APPDATA%\discord\Code Cache",                                    True,  True,  None),
    ("U16", "User",      "WhatsApp Desktop Cache",           r"%APPDATA%\WhatsApp\Cache",                                        True,  True,  None),
    ("U17", "User",      "OneDrive Logs",                    r"%LOCALAPPDATA%\Microsoft\OneDrive\logs",                         True,  True,  None),
    ("U18", "User",      "Teams 2.0 Cache",                  r"%LOCALAPPDATA%\Packages\MSTeams_8wekyb3d8bbwe\LocalCache",       True,  True,  None),
    ("U19", "User",      "Windows Defender Scan History",    r"C:\ProgramData\Microsoft\Windows Defender\Scans\History\Store",True, True, None),
    ("U20", "User",      "Windows Update Logs",              r"C:\Windows\Logs\WindowsUpdate",                                  True,  True,  None),
    ("U21", "User",      "Downloaded Installations Cache",   r"%LOCALAPPDATA%\Downloaded Installations",                  True,  True,  None),
    ("U22", "User",      "Squirrel Temp (App Installer Cache)",r"%LOCALAPPDATA%\SquirrelTemp",                              True,  True,  None),
    ("U23", "User",      "iTunes Cache",                     r"%LOCALAPPDATA%\Apple Computer\iTunes",                     True,  True,  None),
    ("O9",  "Optional",  "DNS Cache (Extra Flush)",          "System DNS Resolver",                                              False, False, "Additional DNS flush. Useful after VPN or network changes."),
    ("U13", "User",      "Zoom Cache",                       r"%APPDATA%\Zoom\data",                                             True,  True,  None),
    ("U14", "User",      "Zoom Logs",                        r"%APPDATA%\Zoom\logs",                                             True,  True,  None),
    ("U15", "User",      "Discord Cache",                    r"%APPDATA%\discord\Cache",                                         True,  True,  None),
    ("U15b","User",      "Discord Code Cache",               r"%APPDATA%\discord\Code Cache",                                    True,  True,  None),
    ("U16", "User",      "WhatsApp Desktop Cache",           r"%APPDATA%\WhatsApp\Cache",                                        True,  True,  None),
    ("U17", "User",      "OneDrive Logs",                    r"%LOCALAPPDATA%\Microsoft\OneDrive\logs",                         True,  True,  None),
    ("U18", "User",      "Teams 2.0 Cache",                  r"%LOCALAPPDATA%\Packages\MSTeams_8wekyb3d8bbwe\LocalCache",       True,  True,  None),
    ("U19", "User",      "Windows Defender Scan History",    r"C:\ProgramData\Microsoft\Windows Defender\Scans\History",      True,  True,  None),
    ("U20", "User",      "Windows Update Logs",              r"C:\Windows\Logs\WindowsUpdate",                                  True,  True,  None),
    # ── User Phase additions ─────────────────────────────────
    ("U24", "User",      "Windows DISM Logs",                r"C:\Windows\Logs\DISM",                                           False, True,  None),
    ("U25", "User",      "MeasuredBoot Logs",                r"C:\Windows\Logs\MeasuredBoot",                                   False, True,  None),
    ("U26", "User",      "Windows Diagnostics Logs",         r"C:\Windows\diagnostics\system",                                  False, True,  None),
    ("U27", "User",      "LocalService Temp",                r"C:\Windows\ServiceProfiles\LocalService\AppData\Local\Temp",  False, True,  None),
    ("U28", "User",      "NetworkService Temp",              r"C:\Windows\ServiceProfiles\NetworkService\AppData\Local\Temp",False, True,  None),
    ("U29", "User",      "Jump List AutoDest",               r"%APPDATA%\Microsoft\Windows\Recent\AutomaticDestinations",      True,  True,  None),
    ("U30", "User",      "Jump List CustomDest",             r"%APPDATA%\Microsoft\Windows\Recent\CustomDestinations",         True,  True,  None),
    ("U31", "User",      "Temp Low Integrity",               r"%LOCALAPPDATA%\Temp\Low",                                        True,  True,  None),
    ("U32", "User",      "CrashRpt Cache",                   r"%LOCALAPPDATA%\CrashRpt",                                         True,  True,  None),
    ("U33", "User",      "Chrome Extension Storage Cache",   r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Storage\ext", True,  True,  None),
    ("U34", "User",      "Edge Extension Storage Cache",     r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Storage\ext",True,  True,  None),
    # ── Developer Phase additions ──────────────────────────────
    ("D6",  "Developer", "NuGet HTTP Cache",                 r"%LOCALAPPDATA%\NuGet\Cache",                                     True,  False, "Clears NuGet HTTP cache. Packages re-download when needed."),
    ("D7",  "Developer", "NuGet Packages Cache",             r"%USERPROFILE%\.nuget\packages",                                  False, False, "Clears local NuGet package store. Re-downloads on next build."),
    ("D8",  "Developer", "Yarn Cache",                       r"%USERPROFILE%\.cache\yarn",                                      False, False, "Clears Yarn package cache. Packages re-download when needed."),
    ("D9",  "Developer", "pnpm Cache",                       r"%LOCALAPPDATA%\pnpm-cache",                                       True,  False, "Clears pnpm package cache. Packages re-download when needed."),
    ("D10", "Developer", "Cargo Registry Cache",             r"%USERPROFILE%\.cargo\registry\cache",                           False, False, "Clears Rust/Cargo registry cache. Re-downloads on next build."),
    ("D11", "Developer", "Android Studio Cache",             r"%USERPROFILE%\.android\cache",                                   True,  False, "Clears Android Studio cache files."),
    # ── 3rd Party Apps Phase ──────────────────────────────────
    ("T1",  "ThirdParty","Slack Cache",                      r"%LOCALAPPDATA%\slack\Cache",                                     True,  False, None),
    ("T2",  "ThirdParty","Slack Code Cache",                 r"%LOCALAPPDATA%\slack\Code Cache",                                True,  False, None),
    ("T3",  "ThirdParty","Postman Cache",                    r"%LOCALAPPDATA%\Postman\Cache",                                   True,  False, None),
    ("T4",  "ThirdParty","Skype Media Cache",                r"%APPDATA%\Skype",                                                 True,  False, "Clears Skype media/chat cache. Chat history is kept."),
    ("T5",  "ThirdParty","Google Drive Logs",                r"%LOCALAPPDATA%\Google\DriveFS\Logs",                            True,  False, None),
    ("T6",  "ThirdParty","Dropbox Logs",                     r"%LOCALAPPDATA%\Dropbox\logs",                                    True,  False, None),
    ("T7",  "ThirdParty","Figma Cache",                      r"%LOCALAPPDATA%\Figma\Cache",                                     True,  False, None),
    ("T8",  "ThirdParty","WebEx Cache",                      r"%LOCALAPPDATA%\WebEx\cache",                                     True,  False, None),
    ("T9",  "ThirdParty","Brave Browser Cache",              r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Cache", True, False, None),
    ("T10", "ThirdParty","Vivaldi Cache",                    r"%LOCALAPPDATA%\Vivaldi\User Data\Default\Cache",               True,  False, None),
    ("T11", "ThirdParty","Opera Cache",                      r"%LOCALAPPDATA%\Opera Software\Opera Stable\Cache",              True,  False, None),
    ("T12", "ThirdParty","Chrome Canary Cache",              r"%LOCALAPPDATA%\Google\Chrome SxS\User Data\Default\Cache",   True,  False, None),
    ("T13", "ThirdParty","NVIDIA DXCache",                   r"%LOCALAPPDATA%\NVIDIA\DXCache",                                  True,  False, None),
    ("T14", "ThirdParty","NVIDIA GLCache",                   r"%LOCALAPPDATA%\NVIDIA\GLCache",                                  True,  False, None),
    ("T15", "ThirdParty","NVIDIA Temp",                      r"%TEMP%\nvidia",                                                   True,  False, None),
    ("T16", "ThirdParty","AMD DxCache",                      r"%LOCALAPPDATA%\AMD\DxCache",                                     True,  False, None),
    ("T17", "ThirdParty","Teams Meeting Add-in Cache",       r"%LOCALAPPDATA%\Microsoft\Teams\meeting-addin\Cache",          True,  False, None),
    ("T18", "ThirdParty","Spotify UWP Cache",                r"%LOCALAPPDATA%\Packages\SpotifyAB.SpotifyMusic_zpdnekdrzrea0\LocalCache", True, False, None),
    ("T19", "ThirdParty","CrashRpt Cache",                   r"%LOCALAPPDATA%\CrashRpt",                                        True,  False, None),
    # ── Adobe Phase ───────────────────────────────────────────
    ("A1",  "Adobe",     "Adobe Media Cache",                r"%APPDATA%\Adobe\Common\Media Cache",                            True,  False, "Clears Adobe media cache. Regenerates when opening projects."),
    ("A2",  "Adobe",     "Adobe Media Cache Files",          r"%APPDATA%\Adobe\Common\Media Cache Files",                      True,  False, "Clears Adobe media cache files. Can be very large (GB+)."),
    ("A3",  "Adobe",     "Adobe Acrobat Cache",              r"%LOCALAPPDATA%\Adobe\Acrobat\DC\Cache",                        True,  False, None),
    ("A4",  "Adobe",     "Adobe Premiere Media Cache",       r"%APPDATA%\Adobe\Premiere Pro",                                   True,  False, "Clears Premiere Pro media cache. Regenerates on next project open."),
    ("A5",  "Adobe",     "Adobe After Effects Disk Cache",   r"%APPDATA%\Adobe\After Effects",                                  True,  False, "Clears After Effects disk cache. Regenerates on next render."),
    ("A6",  "Adobe",     "Adobe Photoshop Temp",             r"%TEMP%",                                                           True,  False, "Photoshop temp files are in system %TEMP% — covered by U1."),
    ("A7",  "Adobe",     "Adobe Illustrator Cache",          r"%APPDATA%\Adobe\Adobe Illustrator",                              True,  False, None),
    ("A8",  "Adobe",     "Adobe InDesign Cache",             r"%LOCALAPPDATA%\Adobe\InDesign",                                  True,  False, None),
    ("A9",  "Adobe",     "Adobe XD Cache",                   r"%APPDATA%\Adobe\Adobe XD\Cache",                               True,  False, None),
    ("A10", "Adobe",     "Adobe Lightroom Cache",            r"%APPDATA%\Adobe\Lightroom\Cache",                              True,  False, "Clears Lightroom preview cache. Regenerates when browsing photos."),
    ("A11", "Adobe",     "Adobe Bridge Cache",               r"%APPDATA%\Adobe\Bridge",                                         True,  False, None),
    ("A12", "Adobe",     "Creative Cloud Desktop Logs",      r"%APPDATA%\Adobe\Creative Cloud Desktop\Logs",                  True,  False, None),
    ("A13", "Adobe",     "Creative Cloud CoreSync Cache",    r"%LOCALAPPDATA%\Adobe\CoreSync\CoreSyncCache",                  True,  False, None),
    # ── Optional additions ────────────────────────────────────
    ("O10", "Optional",  "Skype Media Cache (Full)",         r"%APPDATA%\Skype",                                                 True,  False, "⚠ Removes all Skype cached media. Chat history kept but media must re-download."),
    ("O11", "Optional",  "Adobe Media Cache (Full Clean)",   r"%APPDATA%\Adobe\Common",                                        True,  False, "⚠ Removes entire Adobe Common cache. Large space gain but all projects need re-cache."),
    # ── User Phase additions ─────────────────────────────────
    ("U24", "User",      "Windows DISM Logs",                r"C:\Windows\Logs\DISM",                                           False, True,  None),
    ("U25", "User",      "MeasuredBoot Logs",                r"C:\Windows\Logs\MeasuredBoot",                                   False, True,  None),
    ("U26", "User",      "Windows Diagnostics Logs",         r"C:\Windows\diagnostics\system",                                  False, True,  None),
    ("U27", "User",      "LocalService Temp",                r"C:\Windows\ServiceProfiles\LocalService\AppData\Local\Temp",  False, True,  None),
    ("U28", "User",      "NetworkService Temp",              r"C:\Windows\ServiceProfiles\NetworkService\AppData\Local\Temp",False, True,  None),
    ("U29", "User",      "Jump List AutoDest",               r"%APPDATA%\Microsoft\Windows\Recent\AutomaticDestinations",      True,  True,  None),
    ("U30", "User",      "Jump List CustomDest",             r"%APPDATA%\Microsoft\Windows\Recent\CustomDestinations",         True,  True,  None),
    ("U31", "User",      "Temp Low Integrity",               r"%LOCALAPPDATA%\Temp\Low",                                        True,  True,  None),
    ("U32", "User",      "CrashRpt Cache",                   r"%LOCALAPPDATA%\CrashRpt",                                         True,  True,  None),
    ("U33", "User",      "Chrome Extension Storage",         r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Storage\ext", True,  True,  None),
    ("U34", "User",      "Edge Extension Storage",           r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Storage\ext",True,  True,  None),
    # ── Developer additions ────────────────────────────────────
    ("D6",  "Developer", "NuGet HTTP Cache",                 r"%LOCALAPPDATA%\NuGet\Cache",                                     True,  False, "Clears NuGet HTTP cache. Re-downloads when needed."),
    ("D7",  "Developer", "NuGet Packages Store",             r"%USERPROFILE%\.nuget\packages",                                  False, False, "Clears NuGet local package store. Re-downloads on next build."),
    ("D8",  "Developer", "Yarn Cache",                       r"%USERPROFILE%\.cache\yarn",                                      False, False, "Clears Yarn package cache. Re-downloads when needed."),
    ("D9",  "Developer", "pnpm Cache",                       r"%LOCALAPPDATA%\pnpm-cache",                                       True,  False, "Clears pnpm package cache. Re-downloads when needed."),
    ("D10", "Developer", "Cargo Registry Cache",             r"%USERPROFILE%\.cargo\registry\cache",                           False, False, "Clears Rust Cargo cache. Re-downloads on next build."),
    ("D11", "Developer", "Android Studio Cache",             r"%USERPROFILE%\.android\cache",                                   True,  False, "Clears Android Studio cache files."),
    # ── 3rd Party Apps ────────────────────────────────────────
    ("T1",  "ThirdParty","Slack Cache",                      r"%LOCALAPPDATA%\slack\Cache",                                     True,  False, None),
    ("T2",  "ThirdParty","Slack Code Cache",                 r"%LOCALAPPDATA%\slack\Code Cache",                                True,  False, None),
    ("T3",  "ThirdParty","Postman Cache",                    r"%LOCALAPPDATA%\Postman\Cache",                                   True,  False, None),
    ("T4",  "ThirdParty","Skype Media Cache",                r"%APPDATA%\Skype",                                                 True,  False, "Clears Skype cached media. Chat history is kept."),
    ("T5",  "ThirdParty","Google Drive Logs",                r"%LOCALAPPDATA%\Google\DriveFS\Logs",                            True,  False, None),
    ("T6",  "ThirdParty","Dropbox Logs",                     r"%LOCALAPPDATA%\Dropbox\logs",                                    True,  False, None),
    ("T7",  "ThirdParty","Figma Cache",                      r"%LOCALAPPDATA%\Figma\Cache",                                     True,  False, None),
    ("T8",  "ThirdParty","WebEx Cache",                      r"%LOCALAPPDATA%\WebEx\cache",                                     True,  False, None),
    ("T9",  "ThirdParty","Brave Browser Cache",              r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Cache", True, False, None),
    ("T10", "ThirdParty","Vivaldi Cache",                    r"%LOCALAPPDATA%\Vivaldi\User Data\Default\Cache",               True,  False, None),
    ("T11", "ThirdParty","Opera Cache",                      r"%LOCALAPPDATA%\Opera Software\Opera Stable\Cache",              True,  False, None),
    ("T12", "ThirdParty","Chrome Canary Cache",              r"%LOCALAPPDATA%\Google\Chrome SxS\User Data\Default\Cache",   True,  False, None),
    ("T13", "ThirdParty","NVIDIA DXCache",                   r"%LOCALAPPDATA%\NVIDIA\DXCache",                                  True,  False, None),
    ("T14", "ThirdParty","NVIDIA GLCache",                   r"%LOCALAPPDATA%\NVIDIA\GLCache",                                  True,  False, None),
    ("T15", "ThirdParty","NVIDIA Temp Files",                r"%TEMP%\nvidia",                                                   True,  False, None),
    ("T16", "ThirdParty","AMD DxCache",                      r"%LOCALAPPDATA%\AMD\DxCache",                                     True,  False, None),
    ("T17", "ThirdParty","Teams Meeting Add-in Cache",       r"%LOCALAPPDATA%\Microsoft\Teams\meeting-addin\Cache",          True,  False, None),
    ("T18", "ThirdParty","Spotify UWP Cache",                r"%LOCALAPPDATA%\Packages\SpotifyAB.SpotifyMusic_zpdnekdrzrea0\LocalCache", True, False, None),
    ("T19", "ThirdParty","CrashRpt Cache",                   r"%LOCALAPPDATA%\CrashRpt",                                        True,  False, None),
    # ── Adobe Apps ────────────────────────────────────────────
    ("A1",  "Adobe",     "Adobe Media Cache",                r"%APPDATA%\Adobe\Common\Media Cache",                            True,  False, "Clears Adobe media cache. Regenerates when opening projects."),
    ("A2",  "Adobe",     "Adobe Media Cache Files",          r"%APPDATA%\Adobe\Common\Media Cache Files",                      True,  False, "Can be very large (GB+). Regenerates automatically."),
    ("A3",  "Adobe",     "Adobe Acrobat DC Cache",           r"%LOCALAPPDATA%\Adobe\Acrobat\DC\Cache",                        True,  False, None),
    ("A4",  "Adobe",     "Adobe Premiere Pro Cache",         r"%APPDATA%\Adobe\Premiere Pro",                                   True,  False, "Clears Premiere media cache. Regenerates on next project open."),
    ("A5",  "Adobe",     "Adobe After Effects Cache",        r"%APPDATA%\Adobe\After Effects",                                  True,  False, "Clears After Effects disk cache. Regenerates on next render."),
    ("A6",  "Adobe",     "Adobe Illustrator Cache",          r"%APPDATA%\Adobe\Adobe Illustrator",                              True,  False, None),
    ("A7",  "Adobe",     "Adobe InDesign Cache",             r"%LOCALAPPDATA%\Adobe\InDesign",                                  True,  False, None),
    ("A8",  "Adobe",     "Adobe XD Cache",                   r"%APPDATA%\Adobe\Adobe XD\Cache",                               True,  False, None),
    ("A9",  "Adobe",     "Adobe Lightroom Cache",            r"%APPDATA%\Adobe\Lightroom\Cache",                              True,  False, "Clears Lightroom preview cache. Regenerates when browsing photos."),
    ("A10", "Adobe",     "Adobe Bridge Cache",               r"%APPDATA%\Adobe\Bridge",                                         True,  False, None),
    ("A11", "Adobe",     "Creative Cloud Desktop Logs",      r"%APPDATA%\Adobe\Creative Cloud Desktop\Logs",                  True,  False, None),
    ("A12", "Adobe",     "Creative Cloud CoreSync Cache",    r"%LOCALAPPDATA%\Adobe\CoreSync\CoreSyncCache",                  True,  False, None),
    # ── Optional additions ─────────────────────────────────────
    ("O10", "Optional",  "Skype Media Cache (Full)",         r"%APPDATA%\Skype",                                                 True,  False, "⚠ Removes all Skype cached media. Chat history kept, media must re-download."),
    ("O11", "Optional",  "Adobe Common Cache (Full)",        r"%APPDATA%\Adobe\Common",                                        True,  False, "⚠ Removes entire Adobe Common cache. Large space gain but all projects need re-cache."),
    # ── Games & Launchers ─────────────────────────────────────
    ("G1",  "Games",     "Steam Browser Cache",              r"%LOCALAPPDATA%\Steam\htmlcache",                                 True,  False, None),
    ("G2",  "Games",     "Steam Logs",                       r"%LOCALAPPDATA%\Steam\logs",                                     True,  False, None),
    ("G3",  "Games",     "Epic Games Logs",                  r"%LOCALAPPDATA%\EpicGamesLauncher\Saved\Logs",                  True,  False, None),
    ("G4",  "Games",     "Epic Games WebCache",              r"%LOCALAPPDATA%\EpicGamesLauncher\Saved\webcache",              True,  False, None),
    ("G5",  "Games",     "GOG Galaxy Cache",                 r"%LOCALAPPDATA%\GOG Galaxy\cache",                               True,  False, None),
    ("G6",  "Games",     "GOG Galaxy Logs",                  r"%LOCALAPPDATA%\GOG Galaxy\Logs",                                True,  False, None),
    ("G7",  "Games",     "Riot Client Logs",                 r"%LOCALAPPDATA%\Riot Games\Riot Client\Data\Logs",             True,  False, None),
    ("G8",  "Games",     "Battle.net Logs",                  r"%LOCALAPPDATA%\Battle.net\Logs",                                True,  False, None),
    ("G9",  "Games",     "Overwolf Logs",                    r"%APPDATA%\Overwolf\Logs",                                       True,  False, None),
    ("G10", "Games",     "Origin Logs",                      r"%LOCALAPPDATA%\Origin\Logs",                                    True,  False, None),
    ("G11", "Games",     "Ubisoft Connect Logs",             r"%LOCALAPPDATA%\Ubisoft Game Launcher\logs",                    True,  False, None),
    ("G12", "Games",     "Ubisoft Connect Cache",            r"%LOCALAPPDATA%\Ubisoft Game Launcher\cache",                   True,  False, None),
    # ── Communication Apps ────────────────────────────────────
    ("C1",  "Communication","Telegram Desktop Cache",        r"%APPDATA%\Telegram Desktop\tdata\user_data\cache",           True,  False, "Clears Telegram media cache. Messages kept, media re-downloads."),
    ("C2",  "Communication","Signal Cache",                  r"%APPDATA%\Signal\Cache",                                        True,  False, None),
    ("C3",  "Communication","Signal Code Cache",             r"%APPDATA%\Signal\Code Cache",                                   True,  False, None),
    ("C4",  "Communication","Outlook Offline Cache",         r"%LOCALAPPDATA%\Microsoft\Outlook\offline",                    True,  False, "⚠ Clears Outlook offline cache. Emails re-sync on next open."),
    # ── Media & Creative ──────────────────────────────────────
    ("M1",  "Media",     "OBS Studio Logs",                  r"%LOCALAPPDATA%\obs-studio\logs",                                True,  False, None),
    ("M2",  "Media",     "OBS Browser Cache",                r"%LOCALAPPDATA%\obs-studio\plugin_config\obs-browser\Cache",  True,  False, None),
    ("M3",  "Media",     "DaVinci Resolve Logs",             r"%APPDATA%\DaVinci Resolve\Support\logs",                      True,  False, None),
    ("M4",  "Media",     "DaVinci Resolve Cache",            r"%LOCALAPPDATA%\Blackmagic Design\DaVinci Resolve\Support\CacheClip", True, False, "⚠ Can be very large (1-20 GB). Regenerates on next project render."),
    ("M5",  "Media",     "HandBrake Logs",                   r"%LOCALAPPDATA%\HandBrake\Logs",                                True,  False, None),
    ("M6",  "Media",     "VLC Crash Dumps",                  r"%APPDATA%\vlc\crashdump",                                      True,  False, None),
    # ── Dev Tools ─────────────────────────────────────────────
    ("V1",  "DevTools",  "JetBrains IDE Cache",              r"%APPDATA%\JetBrains",                                            True,  False, "Clears JetBrains cache (IntelliJ, PyCharm, WebStorm etc). Rebuilds on next IDE open."),
    ("V2",  "DevTools",  "JetBrains Local Cache",            r"%LOCALAPPDATA%\JetBrains",                                       True,  False, None),
    ("V3",  "DevTools",  "Visual Studio Component Cache",    r"%LOCALAPPDATA%\Microsoft\VisualStudio",                        True,  False, "Clears VS component model cache. Rebuilds on next VS launch."),
    ("V4",  "DevTools",  "Visual Studio Temp",               r"%TEMP%\VisualStudio",                                            True,  False, None),
    ("V5",  "DevTools",  "Electron Builder Cache",           r"%LOCALAPPDATA%\electron-builder",                                True,  False, None),
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
    elif tid == "D3":
        freed += force_delete(ep(r"%USERPROFILE%\.m2\repository"), log_fn, reboot_flag, dry_run)
        log_fn("  ✅ Maven cache cleared", "success")
    elif tid == "D4":
        freed += force_delete(ep(r"%USERPROFILE%\.gradle\caches"), log_fn, reboot_flag, dry_run)
        log_fn("  ✅ Gradle cache cleared", "success")
    elif tid == "D5":
        freed += force_delete(ep(r"%LOCALAPPDATA%\Docker\log"), log_fn, reboot_flag, dry_run)
        recreate(ep(r"%LOCALAPPDATA%\Docker\log"))
        log_fn("  ✅ Docker logs cleared", "success")
    elif tid == "U13":
        run("taskkill /f /im Zoom.exe")
        freed += force_delete(ep(r"%APPDATA%\Zoom\data"), log_fn, reboot_flag, dry_run)
        recreate(ep(r"%APPDATA%\Zoom\data"))
        log_fn("  ✅ Zoom cache cleared", "success")
    elif tid == "U14":
        freed += force_delete(ep(r"%APPDATA%\Zoom\logs"), log_fn, reboot_flag, dry_run)
        recreate(ep(r"%APPDATA%\Zoom\logs"))
        log_fn("  ✅ Zoom logs cleared", "success")
    elif tid == "U15":
        run("taskkill /f /im discord.exe")
        freed += force_delete(ep(r"%APPDATA%\discord\Cache"), log_fn, reboot_flag, dry_run)
        recreate(ep(r"%APPDATA%\discord\Cache"))
        log_fn("  ✅ Discord cache cleared", "success")
    elif tid == "U15b":
        freed += force_delete(ep(r"%APPDATA%\discord\Code Cache"), log_fn, reboot_flag, dry_run)
        recreate(ep(r"%APPDATA%\discord\Code Cache"))
        log_fn("  ✅ Discord code cache cleared", "success")
    elif tid == "U16":
        run("taskkill /f /im WhatsApp.exe")
        freed += force_delete(ep(r"%APPDATA%\WhatsApp\Cache"), log_fn, reboot_flag, dry_run)
        recreate(ep(r"%APPDATA%\WhatsApp\Cache"))
        log_fn("  ✅ WhatsApp cache cleared", "success")
    elif tid == "U17":
        freed += force_delete(ep(r"%LOCALAPPDATA%\Microsoft\OneDrive\logs"), log_fn, reboot_flag, dry_run)
        recreate(ep(r"%LOCALAPPDATA%\Microsoft\OneDrive\logs"))
        log_fn("  ✅ OneDrive logs cleared", "success")
    elif tid == "U18":
        freed += force_delete(ep(r"%LOCALAPPDATA%\Packages\MSTeams_8wekyb3d8bbwe\LocalCache"), log_fn, reboot_flag, dry_run)
        recreate(ep(r"%LOCALAPPDATA%\Packages\MSTeams_8wekyb3d8bbwe\LocalCache"))
        log_fn("  ✅ Teams 2.0 cache cleared", "success")
    elif tid == "U19":
        # Only clear the Store subfolder — the full History folder can take too long
        defender_path = r"C:\ProgramData\Microsoft\Windows Defender\Scans\History\Store"
        freed += force_delete(defender_path, log_fn, reboot_flag, dry_run)
        recreate(defender_path)
        log_fn("  ✅ Windows Defender scan history cleared", "success")
    elif tid == "U20":
        freed += force_delete(r"C:\Windows\Logs\WindowsUpdate", log_fn, reboot_flag, dry_run)
        recreate(r"C:\Windows\Logs\WindowsUpdate")
        log_fn("  ✅ Windows Update logs cleared", "success")
    elif tid == "U21":
        freed += force_delete(ep(r"%LOCALAPPDATA%\Downloaded Installations"), log_fn, reboot_flag, dry_run)
        recreate(ep(r"%LOCALAPPDATA%\Downloaded Installations"))
        log_fn("  ✅ Downloaded Installations cache cleared", "success")
    elif tid == "U22":
        freed += force_delete(ep(r"%LOCALAPPDATA%\SquirrelTemp"), log_fn, reboot_flag, dry_run)
        recreate(ep(r"%LOCALAPPDATA%\SquirrelTemp"))
        log_fn("  ✅ SquirrelTemp cache cleared", "success")
    elif tid == "U23":
        run("taskkill /f /im iTunes.exe")
        freed += force_delete(ep(r"%LOCALAPPDATA%\Apple Computer\iTunes"), log_fn, reboot_flag, dry_run)
        recreate(ep(r"%LOCALAPPDATA%\Apple Computer\iTunes"))
        log_fn("  ✅ iTunes cache cleared", "success")
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
    # ── User additions ───────────────────────────────────────
    elif tid in ("U24","U25","U26"):
        freed += force_delete(rp, log_fn, reboot_flag, dry_run)
        recreate(rp)
        log_fn(f"  ✅ {task[2]} cleared", "success")
    elif tid in ("U27","U28"):
        freed += force_delete(rp, log_fn, reboot_flag, dry_run)
        recreate(rp)
        log_fn(f"  ✅ {task[2]} cleared", "success")
    elif tid in ("U29","U30"):
        freed += force_delete(ep(rp), log_fn, reboot_flag, dry_run)
        recreate(ep(rp))
        log_fn(f"  ✅ {task[2]} cleared", "success")
    elif tid in ("U31","U32","U33","U34"):
        freed += force_delete(ep(rp), log_fn, reboot_flag, dry_run)
        recreate(ep(rp))
        log_fn(f"  ✅ {task[2]} cleared", "success")
    # ── Developer additions ───────────────────────────────────
    elif tid in ("D6","D7","D8","D9","D10","D11"):
        freed += force_delete(ep(rp), log_fn, reboot_flag, dry_run)
        recreate(ep(rp))
        log_fn(f"  ✅ {task[2]} cleared", "success")
    # ── 3rd Party handlers ────────────────────────────────────
    elif tid == "T1":
        run("taskkill /f /im slack.exe")
        freed += force_delete(ep(r"%LOCALAPPDATA%\slack\Cache"), log_fn, reboot_flag, dry_run)
        recreate(ep(r"%LOCALAPPDATA%\slack\Cache"))
        log_fn("  ✅ Slack cache cleared", "success")
    elif tid == "T2":
        run("taskkill /f /im slack.exe")
        freed += force_delete(ep(r"%LOCALAPPDATA%\slack\Code Cache"), log_fn, reboot_flag, dry_run)
        recreate(ep(r"%LOCALAPPDATA%\slack\Code Cache"))
        log_fn("  ✅ Slack code cache cleared", "success")
    elif tid == "T3":
        run("taskkill /f /im Postman.exe")
        freed += force_delete(ep(r"%LOCALAPPDATA%\Postman\Cache"), log_fn, reboot_flag, dry_run)
        recreate(ep(r"%LOCALAPPDATA%\Postman\Cache"))
        log_fn("  ✅ Postman cache cleared", "success")
    elif tid == "T4":
        run("taskkill /f /im Skype.exe")
        freed += force_delete(ep(r"%APPDATA%\Skype"), log_fn, reboot_flag, dry_run)
        log_fn("  ✅ Skype media cache cleared", "success")
    elif tid in ("T5","T6","T7","T8"):
        freed += force_delete(ep(rp), log_fn, reboot_flag, dry_run)
        recreate(ep(rp))
        log_fn(f"  ✅ {task[2]} cleared", "success")
    elif tid in ("T9","T10","T11","T12"):
        # Browser caches for alternative browsers
        run("taskkill /f /im brave.exe")
        run("taskkill /f /im vivaldi.exe")
        run("taskkill /f /im opera.exe")
        freed += force_delete(ep(rp), log_fn, reboot_flag, dry_run)
        recreate(ep(rp))
        log_fn(f"  ✅ {task[2]} cleared", "success")
    elif tid in ("T13","T14","T15","T16"):
        freed += force_delete(ep(rp), log_fn, reboot_flag, dry_run)
        recreate(ep(rp))
        log_fn(f"  ✅ {task[2]} cleared", "success")
    elif tid == "T17":
        freed += force_delete(ep(r"%LOCALAPPDATA%\Microsoft\Teams\meeting-addin\Cache"), log_fn, reboot_flag, dry_run)
        recreate(ep(r"%LOCALAPPDATA%\Microsoft\Teams\meeting-addin\Cache"))
        log_fn("  ✅ Teams Meeting Add-in cache cleared", "success")
    elif tid in ("T18","T19"):
        freed += force_delete(ep(rp), log_fn, reboot_flag, dry_run)
        recreate(ep(rp))
        log_fn(f"  ✅ {task[2]} cleared", "success")
    # ── Adobe handlers ────────────────────────────────────────
    elif tid in ("A1","A2"):
        adobe_path = ep(rp)
        freed += force_delete(adobe_path, log_fn, reboot_flag, dry_run)
        recreate(adobe_path)
        log_fn(f"  ✅ {task[2]} cleared", "success")
    elif tid in ("A3","A4","A5","A6","A7","A8","A9","A10","A11","A12","A13"):
        freed += force_delete(ep(rp), log_fn, reboot_flag, dry_run)
        recreate(ep(rp))
        log_fn(f"  ✅ {task[2]} cleared", "success")
    elif tid in ("O10","O11"):
        freed += force_delete(ep(rp), log_fn, reboot_flag, dry_run)
        recreate(ep(rp))
        log_fn(f"  ✅ {task[2]} cleared", "success")
    elif tid in ("G1","G2","G3","G4","G5","G6","G7","G8","G9","G10","G11","G12"):
        freed += force_delete(ep(rp), log_fn, reboot_flag, dry_run)
        recreate(ep(rp))
        log_fn(f"  ✅ {task[2]} cleared", "success")
    elif tid in ("C1","C2","C3","C4"):
        run("taskkill /f /im Telegram.exe")
        run("taskkill /f /im Signal.exe")
        run("taskkill /f /im olk.exe")
        freed += force_delete(ep(rp), log_fn, reboot_flag, dry_run)
        recreate(ep(rp))
        log_fn(f"  ✅ {task[2]} cleared", "success")
    elif tid in ("M1","M2","M3","M4","M5","M6"):
        freed += force_delete(ep(rp), log_fn, reboot_flag, dry_run)
        recreate(ep(rp))
        log_fn(f"  ✅ {task[2]} cleared", "success")
    elif tid in ("V1","V2","V3","V4","V5"):
        freed += force_delete(ep(rp), log_fn, reboot_flag, dry_run)
        recreate(ep(rp))
        log_fn(f"  ✅ {task[2]} cleared", "success")
    else:
        freed += force_delete(rp, log_fn, reboot_flag, dry_run)
        if rp not in SKIP_RECREATE:
            recreate(rp)

    return freed
