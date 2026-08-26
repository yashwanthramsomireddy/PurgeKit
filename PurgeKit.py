"""
PurgeKit v2.2
MIT License — TeamExyKings
GitHub: https://github.com/yashwanthramsomireddy/PurgeKit

Built with love by Yashwanth Ram Somireddy
Chennai, India (TeamExyKings)

Windows temp & cache cleaner with a modern GUI.
Requires: Python 3.11+, customtkinter, Pillow
"""

import sys
import os
import ctypes
import threading
import subprocess
import shutil
import datetime
import platform
import string
import winreg

# ── Admin check ─────────────────────────────────────────────
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def relaunch_as_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit()

if platform.system() == "Windows" and not is_admin():
    relaunch_as_admin()

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageDraw

# ── Theme ────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

BG_DARKEST  = "#0a0a0a"
BG_DARK     = "#111111"
BG_CARD     = "#181818"
BG_HOVER    = "#1e1e1e"
ACCENT      = "#00e676"
ACCENT_DIM  = "#00c853"
ACCENT_DARK = "#003916"
TEXT_WHITE  = "#f5f5f5"
TEXT_GRAY   = "#888888"
TEXT_DIM    = "#444444"
WARN        = "#ffab40"
ERROR       = "#ff5252"
SUCCESS     = "#00e676"

GITHUB_URL    = "https://github.com/yashwanthramsomireddy/PurgeKit"
AUTHOR_NAME   = "Yashwanth Ram Somireddy"
AUTHOR_LOC    = "Chennai, India"
AUTHOR_BRAND  = "TeamExyKings"
APP_VERSION   = "2.2"
AUTOSTART_KEY = "PurgeKit"

# ── Task definitions ─────────────────────────────────────────
# (id, phase, label, path_display, env_expand, default_checked, warning)
TASKS = [
    # ── System Level
    ("S1",  "System",   "Windows System Temp",              r"C:\Windows\Temp",                                                False, True,  None),
    ("S2",  "System",   "Prefetch Files",                   r"C:\Windows\Prefetch",                                            False, True,  None),
    ("S3",  "System",   "Windows Update Cache",             r"C:\Windows\SoftwareDistribution\Download",                       False, True,  None),
    ("S4",  "System",   "Delivery Optimization Files",      r"C:\Windows\SoftwareDistribution\DeliveryOptimization",           False, True,  None),
    ("S5",  "System",   "Windows Error Reporting",          r"C:\ProgramData\Microsoft\Windows\WER",                           False, True,  None),
    ("S6",  "System",   "CBS Logs",                         r"C:\Windows\Logs\CBS",                                            False, True,  None),
    ("S7",  "System",   "Crash Dumps",                      r"C:\Windows\Minidump",                                            False, True,  None),
    ("S8",  "System",   "Windows Font Cache",               r"C:\Windows\ServiceProfiles\LocalService\AppData\Local\FontCache", False, True,  None),
    ("S9",  "System",   "SoftwareDistribution Logs",        r"C:\Windows\SoftwareDistribution\DataStore\Logs",                 False, True,  None),
    ("S10", "System",   "Windows Installer Patch Cache",    r"C:\Windows\Installer\$PatchCache$",                              False, True,  None),
    ("S11", "System",   "DNS Cache (Flush)",                "System DNS Resolver",                                             False, True,  None),
    # ── User Level
    ("U1",  "User",     "User Temp Folder (%TEMP%)",        "%TEMP%",                                                          True,  True,  None),
    ("U1b", "User",     "LocalAppData Temp",                r"%LOCALAPPDATA%\Temp",                                            True,  True,  None),
    ("U2",  "User",     "Thumbnail Cache",                  r"%LOCALAPPDATA%\Microsoft\Windows\Explorer",                      True,  True,  None),
    ("U3",  "User",     "Recent Files & Jump Lists",        r"%APPDATA%\Microsoft\Windows\Recent",                             True,  True,  None),
    ("U4",  "User",     "IE / Legacy Edge WebCache",        r"%LOCALAPPDATA%\Microsoft\Windows\WebCache",                      True,  True,  None),
    ("U4b", "User",     "IE / Legacy INetCache",            r"%LOCALAPPDATA%\Microsoft\Windows\INetCache",                     True,  True,  None),
    ("U5",  "User",     "DirectX Shader Cache",             r"%LOCALAPPDATA%\D3DSCache",                                       True,  True,  None),
    ("U5b", "User",     "User Crash Dumps",                 r"%LOCALAPPDATA%\CrashDumps",                                      True,  True,  None),
    ("U6",  "User",     "Microsoft Teams Cache",            r"%APPDATA%\Microsoft\Teams\Cache",                                True,  True,  None),
    ("U7",  "User",     "VS Code Cache",                    r"%APPDATA%\Code\Cache",                                           True,  True,  None),
    ("U8",  "User",     "Microsoft Office Cache",           r"%LOCALAPPDATA%\Microsoft\Office\16.0\OfficeFileCache",           True,  True,  None),
    ("U9",  "User",     "Spotify Cache",                    r"%LOCALAPPDATA%\Spotify\Storage",                                 True,  True,  None),
    ("U10", "User",     "Icon Cache",                       r"%LOCALAPPDATA%\IconCache.db",                                    True,  True,  None),
    ("U11", "User",     "Clipboard History",                "Windows Clipboard",                                               False, True,  None),
    ("U12", "User",     "Windows Store Cache (wsreset)",    "Microsoft Store",                                                 False, True,  None),
    # ── Browser Level
    ("B1",  "Browser",  "Chrome — Cache + Code + GPU",      r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache",           True,  True,  None),
    ("B1b", "Browser",  "Chrome — Service Worker Cache",    r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Service Worker",  True,  True,  None),
    ("B2",  "Browser",  "Firefox — Cache (All Profiles)",   r"%LOCALAPPDATA%\Mozilla\Firefox\Profiles",                        True,  True,  None),
    ("B3",  "Browser",  "Edge — Cache + Code + GPU",        r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache",          True,  True,  None),
    ("B3b", "Browser",  "Edge — Service Worker Cache",      r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Service Worker", True,  True,  None),
    # ── Developer Tools (optional, unchecked)
    ("D1",  "Developer","npm Cache",                        r"%APPDATA%\npm-cache",                                            True,  False, "Clears npm package cache. Safe — packages re-download when needed."),
    ("D2",  "Developer","pip Cache",                        r"%LOCALAPPDATA%\pip\cache",                                       True,  False, "Clears pip package cache. Safe — packages re-download when needed."),
    # ── Optional / Power User (unchecked by default)
    ("O1",  "Optional", "Event Logs (App + System)",        "Windows Event Viewer Logs",                                       False, False, "Clears Application, System and Security event logs. Diagnostic history will be lost."),
    ("O2",  "Optional", "Recycle Bin (All Drives)",         "All Drive Recycle Bins",                                          False, False, "Permanently deletes all items in the Recycle Bin across all drives."),
    ("O3",  "Optional", "Windows Telemetry Data",           r"C:\ProgramData\Microsoft\Diagnosis",                             False, False, "Removes telemetry data sent to Microsoft. Safe but disables some diagnostics."),
    ("O4",  "Optional", "Cortana / Search History",         r"%LOCALAPPDATA%\Packages\Microsoft.Windows.Search*",              True,  False, "Clears Cortana and Windows Search history."),
    ("O5",  "Optional", "ARP Cache (Flush)",                "Network ARP Table",                                               False, False, "Flushes ARP table. Network may rebuild briefly."),
    ("O6",  "Optional", "NetBIOS Cache (Flush)",            "NetBIOS Name Cache",                                              False, False, "Flushes NetBIOS name cache. Safe on modern networks."),
    ("O7",  "Optional", "Winsock Reset",                    "Windows Network Stack",                                           False, False, "⚠ REQUIRES REBOOT. Resets network stack. Use only for network issues."),
    ("O8",  "Optional", "Windows Search Index Rebuild",     "Windows Search Index",                                            False, False, "⚠ Search will be slow for several hours while index rebuilds."),
    ("O9",  "Optional", "DNS Cache (Flush) — Extra",        "System DNS Resolver",                                             False, False, "Additional DNS flush pass. Useful after network changes or VPN issues."),
]

ACTIVITY_OPTIONS = [
    ("delete",  "Delete ActivitiesCache.db (one-time clean)"),
    ("disable", "Delete + Disable Activity History permanently"),
    ("skip",    "Skip"),
]

SKIP_PATHS = {
    "System DNS Resolver", "Windows Clipboard", "Microsoft Store",
    "Network ARP Table", "NetBIOS Name Cache", "Windows Network Stack",
    "Windows Search Index", "All Drive Recycle Bins", "Windows Event Viewer Logs",
}

# ── Helpers ──────────────────────────────────────────────────
def ep(path):
    return os.path.expandvars(path)

def run(cmd, timeout=120):
    try:
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=timeout)
    except Exception:
        pass

def get_drives():
    """Detect all accessible drives regardless of type."""
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
                    vol_buf = ctypes.create_unicode_buffer(261)
                    ctypes.windll.kernel32.GetVolumeInformationW(
                        path, vol_buf, 261, None, None, None, None, 0)
                    label = vol_buf.value
                except Exception:
                    pass
                if total > 0:  # only real drives with actual space
                    drives.append((path, label, free, total))
            except Exception:
                pass
    return drives if drives else [("C:\\", "System", 0, 0)]

def fmt_size(b):
    if b >= 1 << 30:
        return f"{b / (1 << 30):.1f} GB"
    if b >= 1 << 20:
        return f"{b / (1 << 20):.1f} MB"
    return f"{b / (1 << 10):.1f} KB"

def force_delete(path, log_fn, reboot_flag):
    if not os.path.exists(path):
        log_fn(f"  [SKIP] Not found: {path}", "dim")
        return
    empty = os.path.join(os.environ.get("TEMP", r"C:\Windows\Temp"), "_purgekit_empty_")
    os.makedirs(empty, exist_ok=True)
    run(f'robocopy "{empty}" "{path}" /MIR /NFL /NDL /NJH /NJS /nc /ns /np')
    try:
        shutil.rmtree(path, ignore_errors=True)
    except Exception:
        pass
    if not os.path.exists(path):
        log_fn(f"  ✅ T1 (robocopy) — {path}", "success")
        return
    log_fn("  ⚠ T1 failed, trying T2 (takeown)...", "warn")
    run(f'takeown /f "{path}" /r /d y')
    run(f'icacls "{path}" /grant administrators:F /t /q')
    try:
        shutil.rmtree(path, ignore_errors=True)
    except Exception:
        pass
    if not os.path.exists(path):
        log_fn(f"  ✅ T2 (takeown+icacls) — {path}", "success")
        return
    log_fn("  ⚠ T2 failed, scheduling on reboot (T3)...", "warn")
    for root_dir, dirs, files in os.walk(path):
        for f in files:
            full = os.path.join(root_dir, f)
            run(f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager" '
                f'/v PendingFileRenameOperations /t REG_MULTI_SZ /d "\\??\\{full}\\0" /f')
    reboot_flag[0] = True
    log_fn(f"  🔁 T3 — scheduled for reboot: {path}", "warn")

def recreate(path):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        pass

# ── Auto-start helpers ───────────────────────────────────────
AUTOSTART_REG = r"Software\Microsoft\Windows\CurrentVersion\Run"

def get_autostart_state():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_REG, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, AUTOSTART_KEY)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False

def set_autostart(enable: bool):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_REG, 0, winreg.KEY_SET_VALUE)
        if enable:
            exe_path = sys.executable if getattr(sys, "frozen", False) else sys.executable
            script   = os.path.abspath(sys.argv[0])
            value    = f'"{exe_path}" "{script}"' if not getattr(sys, "frozen", False) else f'"{exe_path}"'
            winreg.SetValueEx(key, AUTOSTART_KEY, 0, winreg.REG_SZ, value)
        else:
            try:
                winreg.DeleteValue(key, AUTOSTART_KEY)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception:
        return False

# ── Icon generator ───────────────────────────────────────────
def generate_icon():
    size = 256
    img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, 252, 252], fill=(10, 10, 10, 255), outline=(0, 230, 118, 255), width=6)
    draw.ellipse([20, 20, 236, 236], outline=(0, 200, 100, 80), width=2)
    draw.line([(128, 60), (128, 160)], fill=(0, 230, 118), width=10)
    for i, offset in enumerate([-40, -25, -10, 5, 20, 35, 50]):
        draw.line([(128, 160), (88 + offset, 210)],
                  fill=(0, 230, 118, max(60, 255 - i * 28)), width=5)
    draw.ellipse([118, 50, 138, 70], fill=(0, 230, 118, 255))
    return img

# ══════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════
class PurgeKitApp(ctk.CTk):

    COMPACT_W,  COMPACT_H  = 740, 700
    SPACIOUS_W, SPACIOUS_H = 1080, 840

    def __init__(self):
        super().__init__()
        self.title(f"PurgeKit v{APP_VERSION}  —  {AUTHOR_BRAND}")
        self.configure(fg_color=BG_DARKEST)
        self.resizable(True, True)
        self.minsize(680, 580)

        # Default compact ON
        self.compact_mode  = tk.BooleanVar(value=True)
        self.task_vars     = {}
        self.drive_vars    = {}
        self.activity_var  = tk.StringVar(value="skip")
        self.autostart_var = tk.BooleanVar(value=get_autostart_state())
        self.running       = False
        self.reboot_needed = [False]
        self.log_lines     = []

        try:
            icon_img = generate_icon()
            ico_path = os.path.join(os.environ.get("TEMP", ""), "purgekit_icon.ico")
            icon_img.save(ico_path, format="ICO", sizes=[(256, 256), (64, 64), (32, 32)])
            self.iconbitmap(ico_path)
        except Exception:
            pass

        self._set_window_size()
        self._center_window()
        self._build_ui()

    def _set_window_size(self):
        if self.compact_mode.get():
            self.geometry(f"{self.COMPACT_W}x{self.COMPACT_H}")
        else:
            self.geometry(f"{self.SPACIOUS_W}x{self.SPACIOUS_H}")

    def _center_window(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w  = self.COMPACT_W  if self.compact_mode.get() else self.SPACIOUS_W
        h  = self.COMPACT_H  if self.compact_mode.get() else self.SPACIOUS_H
        self.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    # ── Top bar ──────────────────────────────────────────────
    def _build_ui(self):
        top = ctk.CTkFrame(self, fg_color=BG_DARK, height=54, corner_radius=0)
        top.pack(fill="x", side="top")
        top.pack_propagate(False)

        lf = ctk.CTkFrame(top, fg_color="transparent")
        lf.pack(side="left", padx=14, pady=8)
        try:
            li = generate_icon()
            lc = ctk.CTkImage(light_image=li, dark_image=li, size=(30, 30))
            ctk.CTkLabel(lf, image=lc, text="").pack(side="left", padx=(0, 8))
        except Exception:
            pass
        ctk.CTkLabel(lf, text="PurgeKit",
                     font=ctk.CTkFont("Segoe UI", 20, "bold"),
                     text_color=ACCENT).pack(side="left")
        ctk.CTkLabel(lf, text=f" v{APP_VERSION}",
                     font=ctk.CTkFont("Segoe UI", 12),
                     text_color=TEXT_GRAY).pack(side="left")

        rf = ctk.CTkFrame(top, fg_color="transparent")
        rf.pack(side="right", padx=14, pady=8)
        ctk.CTkLabel(rf, text="Compact",
                     font=ctk.CTkFont("Segoe UI", 11),
                     text_color=TEXT_GRAY).pack(side="left", padx=(0, 4))
        ctk.CTkSwitch(rf, text="", variable=self.compact_mode,
                      command=self._toggle_compact,
                      width=44, height=22,
                      button_color=ACCENT, button_hover_color=ACCENT_DIM,
                      progress_color=ACCENT_DARK).pack(side="left")

        self.main_frame = ctk.CTkFrame(self, fg_color=BG_DARKEST, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)
        self._build_content()

    def _build_content(self):
        for w in self.main_frame.winfo_children():
            w.destroy()
        if self.compact_mode.get():
            self._build_compact_layout()
        else:
            self._build_spacious_layout()

    def _build_spacious_layout(self):
        left = ctk.CTkFrame(self.main_frame, fg_color=BG_DARKEST, corner_radius=0)
        left.pack(side="left", fill="both", expand=True, padx=(12, 6), pady=12)
        right = ctk.CTkFrame(self.main_frame, fg_color=BG_DARK, corner_radius=10, width=330)
        right.pack(side="right", fill="both", padx=(0, 12), pady=12)
        right.pack_propagate(False)
        self._build_task_panel(left)
        self._build_log_panel(right)

    def _build_compact_layout(self):
        self.tabs = ctk.CTkTabview(
            self.main_frame, fg_color=BG_DARK,
            segmented_button_fg_color=BG_CARD,
            segmented_button_selected_color=ACCENT_DARK,
            segmented_button_selected_hover_color=ACCENT_DARK,
            segmented_button_unselected_color=BG_CARD,
            text_color=TEXT_WHITE,
            border_color=TEXT_DIM, border_width=1
        )
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)
        for tab in ["🧹 Tasks", "📄 Log", "ℹ About"]:
            self.tabs.add(tab)
        self._build_task_panel(self.tabs.tab("🧹 Tasks"))
        self._build_log_panel(self.tabs.tab("📄 Log"))
        self._build_about_panel(self.tabs.tab("ℹ About"))

    # ── Task Panel ───────────────────────────────────────────
    def _build_task_panel(self, parent):
        # Select/Deselect row
        br = ctk.CTkFrame(parent, fg_color="transparent")
        br.pack(fill="x", pady=(0, 6))
        for txt, cmd, fg, tc in [
            ("✔ Select All",   self._select_all,   ACCENT_DARK, ACCENT),
            ("✘ Deselect All", self._deselect_all, "#1a1a1a",   TEXT_GRAY),
        ]:
            ctk.CTkButton(br, text=txt, width=120, height=28,
                          fg_color=fg, hover_color="#004d20" if fg == ACCENT_DARK else "#222222",
                          text_color=tc, font=ctk.CTkFont("Segoe UI", 12),
                          corner_radius=6, command=cmd).pack(side="left", padx=(0, 8))

        scroll = ctk.CTkScrollableFrame(parent, fg_color=BG_DARKEST, corner_radius=8,
                                        scrollbar_button_color=ACCENT_DARK,
                                        scrollbar_button_hover_color=ACCENT)
        scroll.pack(fill="both", expand=True)

        phase_meta = {
            "System":    ("#003916", "⚙",  ACCENT, "System Level"),
            "User":      ("#003020", "👤", ACCENT, "User Level"),
            "Browser":   ("#002818", "🌐", ACCENT, "Browser Level"),
            "Developer": ("#0a1a00", "💻", ACCENT, "Developer Tools  (unchecked by default)"),
            "Optional":  ("#1a1200", "⚠",  WARN,   "Optional / Power User  (unchecked by default)"),
        }

        phases = {}
        for task in TASKS:
            phases.setdefault(task[1], []).append(task)

        for phase, tasks in phases.items():
            bg, icon, hdr_color, title = phase_meta.get(phase, (BG_CARD, "•", ACCENT, phase))
            ph_f = ctk.CTkFrame(scroll, fg_color=bg, corner_radius=8)
            ph_f.pack(fill="x", pady=(8, 2), padx=2)
            ctk.CTkLabel(ph_f, text=f"  {icon}  {title}",
                         font=ctk.CTkFont("Segoe UI", 12, "bold"),
                         text_color=hdr_color, anchor="w").pack(fill="x", padx=12, pady=(6, 4))

            for task in tasks:
                tid, ph, label, path, expand, default, warning = task
                var = tk.BooleanVar(value=default)
                self.task_vars[tid] = var

                row = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=6)
                row.pack(fill="x", pady=2, padx=2)

                ctk.CTkCheckBox(row, text=label, variable=var,
                                font=ctk.CTkFont("Segoe UI", 12),
                                text_color=TEXT_WHITE, fg_color=ACCENT_DARK,
                                hover_color=ACCENT_DARK, checkmark_color=ACCENT,
                                border_color=TEXT_DIM, width=20, height=20
                                ).pack(side="left", padx=(10, 6), pady=6)

                if warning:
                    ctk.CTkLabel(row, text="⚠",
                                 font=ctk.CTkFont("Segoe UI", 12),
                                 text_color=WARN).pack(side="left", padx=(0, 4))

                ctk.CTkLabel(row, text=path,
                             font=ctk.CTkFont("Segoe UI", 10),
                             text_color=TEXT_GRAY, anchor="w").pack(side="right", padx=(0, 10))

                if warning:
                    wr = ctk.CTkFrame(scroll, fg_color="#110a00", corner_radius=4)
                    wr.pack(fill="x", padx=12, pady=(0, 2))
                    ctk.CTkLabel(wr, text=f"  {warning}",
                                 font=ctk.CTkFont("Segoe UI", 10),
                                 text_color=WARN, anchor="w").pack(fill="x", padx=8, pady=3)

        # ── Disk Cleanup per drive
        dc_f = ctk.CTkFrame(scroll, fg_color="#001a10", corner_radius=8)
        dc_f.pack(fill="x", pady=(10, 2), padx=2)
        ctk.CTkLabel(dc_f, text="  🗑  Disk Cleanup — Per Drive",
                     font=ctk.CTkFont("Segoe UI", 12, "bold"),
                     text_color=ACCENT, anchor="w").pack(fill="x", padx=12, pady=(8, 4))

        drives = get_drives()
        self.drive_vars = {}
        for drive_path, label, free, total in drives:
            var = tk.BooleanVar(value=True)
            self.drive_vars[drive_path] = var
            row = ctk.CTkFrame(dc_f, fg_color=BG_CARD, corner_radius=6)
            row.pack(fill="x", pady=2, padx=8)
            name = f"{drive_path}  {label}" if label else drive_path
            sz   = f"{fmt_size(free)} free / {fmt_size(total)}" if total > 0 else ""
            ctk.CTkCheckBox(row, text=name, variable=var,
                            font=ctk.CTkFont("Segoe UI", 12), text_color=TEXT_WHITE,
                            fg_color=ACCENT_DARK, hover_color=ACCENT_DARK,
                            checkmark_color=ACCENT, border_color=TEXT_DIM,
                            width=20, height=20).pack(side="left", padx=(10, 6), pady=6)
            if sz:
                ctk.CTkLabel(row, text=sz, font=ctk.CTkFont("Segoe UI", 10),
                             text_color=TEXT_GRAY).pack(side="right", padx=(0, 10))
        ctk.CTkFrame(dc_f, fg_color="transparent", height=6).pack()

        # ── Activity History
        ah_f = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=8)
        ah_f.pack(fill="x", pady=(10, 2), padx=2)
        ctk.CTkLabel(ah_f, text="  🔒  Privacy — Windows Activity History",
                     font=ctk.CTkFont("Segoe UI", 12, "bold"),
                     text_color=WARN, anchor="w").pack(fill="x", padx=12, pady=(8, 2))
        ctk.CTkLabel(ah_f, text="  Tracks apps, files, and websites visited (ActivitiesCache.db)",
                     font=ctk.CTkFont("Segoe UI", 10),
                     text_color=TEXT_GRAY, anchor="w").pack(fill="x", padx=12, pady=(0, 6))
        for val, txt in ACTIVITY_OPTIONS:
            ctk.CTkRadioButton(ah_f, text=txt, variable=self.activity_var, value=val,
                               font=ctk.CTkFont("Segoe UI", 11), text_color=TEXT_WHITE,
                               fg_color=ACCENT_DARK, hover_color=ACCENT_DARK,
                               border_color=TEXT_DIM).pack(anchor="w", padx=20, pady=3)
        ctk.CTkFrame(ah_f, fg_color="transparent", height=8).pack()

        # ── Bottom bar
        bot = ctk.CTkFrame(parent, fg_color=BG_DARKEST, corner_radius=0)
        bot.pack(fill="x", pady=(8, 0))

        self.progress_label = ctk.CTkLabel(bot, text="Ready to purge.",
                                           font=ctk.CTkFont("Segoe UI", 11),
                                           text_color=TEXT_GRAY, anchor="w")
        self.progress_label.pack(fill="x", padx=2, pady=(0, 4))

        self.progress_bar = ctk.CTkProgressBar(bot, height=10, fg_color=BG_CARD,
                                               progress_color=ACCENT, corner_radius=5)
        self.progress_bar.pack(fill="x", padx=2, pady=(0, 8))
        self.progress_bar.set(0)

        btn_r = ctk.CTkFrame(bot, fg_color="transparent")
        btn_r.pack(fill="x")
        self.start_btn = ctk.CTkButton(
            btn_r, text="🧹  START PURGE",
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
            height=42, corner_radius=8,
            fg_color=ACCENT_DARK, hover_color="#005c20", text_color=ACCENT,
            command=self._start_purge)
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(btn_r, text="📄 Log", height=42, width=80, corner_radius=8,
                      fg_color=BG_CARD, hover_color=BG_HOVER, text_color=TEXT_GRAY,
                      font=ctk.CTkFont("Segoe UI", 12),
                      command=self._save_log).pack(side="left", padx=(0, 6))
        if not self.compact_mode.get():
            ctk.CTkButton(btn_r, text="ℹ About", height=42, width=90, corner_radius=8,
                          fg_color=BG_CARD, hover_color=BG_HOVER, text_color=TEXT_GRAY,
                          font=ctk.CTkFont("Segoe UI", 12),
                          command=self._show_about).pack(side="right")

    # ── Log Panel ────────────────────────────────────────────
    def _build_log_panel(self, parent):
        ctk.CTkLabel(parent, text="📋  Run Log",
                     font=ctk.CTkFont("Segoe UI", 13, "bold"),
                     text_color=ACCENT, anchor="w").pack(fill="x", padx=12, pady=(10, 4))
        self.log_box = ctk.CTkTextbox(
            parent, fg_color=BG_DARKEST, text_color=TEXT_WHITE,
            font=ctk.CTkFont("Consolas", 11), corner_radius=6,
            scrollbar_button_color=ACCENT_DARK,
            scrollbar_button_hover_color=ACCENT,
            wrap="word", state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        for tag, color in [("success", SUCCESS), ("warn", WARN), ("error", ERROR),
                           ("dim", TEXT_GRAY), ("accent", ACCENT), ("white", TEXT_WHITE)]:
            self.log_box.tag_config(tag, foreground=color)
        self._log(f"PurgeKit v{APP_VERSION} ready.", "accent")
        self._log("Select tasks and press START PURGE.", "dim")

    # ── About Panel ──────────────────────────────────────────
    def _build_about_panel(self, parent):
        frame = ctk.CTkScrollableFrame(parent, fg_color=BG_DARKEST, corner_radius=0,
                                       scrollbar_button_color=ACCENT_DARK,
                                       scrollbar_button_hover_color=ACCENT)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        try:
            li = generate_icon()
            lc = ctk.CTkImage(light_image=li, dark_image=li, size=(72, 72))
            ctk.CTkLabel(frame, image=lc, text="").pack(pady=(16, 8))
        except Exception:
            pass

        ctk.CTkLabel(frame, text="PurgeKit",
                     font=ctk.CTkFont("Segoe UI", 26, "bold"),
                     text_color=ACCENT).pack()
        ctk.CTkLabel(frame, text=f"v{APP_VERSION}  —  Windows Temp & Cache Cleaner",
                     font=ctk.CTkFont("Segoe UI", 12),
                     text_color=TEXT_GRAY).pack(pady=(2, 16))

        # Info card
        info_f = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=10)
        info_f.pack(fill="x", padx=8, pady=(0, 12))
        for lbl, val in [
            ("Built with ❤️ by", AUTHOR_NAME),
            ("Location",         f"📍 {AUTHOR_LOC}"),
            ("Brand",            AUTHOR_BRAND),
            ("License",          "MIT — Free & Open Source"),
            ("Platform",         "Windows 10 / 11"),
            ("Version",          APP_VERSION),
        ]:
            r = ctk.CTkFrame(info_f, fg_color="transparent")
            r.pack(fill="x", padx=14, pady=5)
            ctk.CTkLabel(r, text=lbl, font=ctk.CTkFont("Segoe UI", 11),
                         text_color=TEXT_GRAY, width=110, anchor="w").pack(side="left")
            ctk.CTkLabel(r, text=val, font=ctk.CTkFont("Segoe UI", 11, "bold"),
                         text_color=TEXT_WHITE, anchor="w").pack(side="left")

        # GitHub button
        ctk.CTkLabel(frame, text="GitHub Repository",
                     font=ctk.CTkFont("Segoe UI", 11), text_color=TEXT_GRAY).pack(pady=(8, 4))
        ctk.CTkButton(frame, text=GITHUB_URL,
                      font=ctk.CTkFont("Segoe UI", 11, "bold"),
                      fg_color=ACCENT_DARK, hover_color="#005c20",
                      text_color=ACCENT, height=34, corner_radius=8,
                      command=self._open_github).pack(padx=8, pady=(0, 14), fill="x")

        # Auto-start toggle
        as_f = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=10)
        as_f.pack(fill="x", padx=8, pady=(0, 12))
        as_r = ctk.CTkFrame(as_f, fg_color="transparent")
        as_r.pack(fill="x", padx=14, pady=12)
        ctk.CTkLabel(as_r, text="🚀  Launch PurgeKit on Windows startup",
                     font=ctk.CTkFont("Segoe UI", 12),
                     text_color=TEXT_WHITE, anchor="w").pack(side="left", fill="x", expand=True)
        ctk.CTkSwitch(as_r, text="", variable=self.autostart_var,
                      command=self._toggle_autostart,
                      width=44, height=22,
                      button_color=ACCENT, button_hover_color=ACCENT_DIM,
                      progress_color=ACCENT_DARK).pack(side="right")
        ctk.CTkLabel(as_f,
                     text="  Note: Auto-start works best with the compiled .exe version.",
                     font=ctk.CTkFont("Segoe UI", 10),
                     text_color=TEXT_GRAY, anchor="w").pack(fill="x", padx=14, pady=(0, 10))

        ctk.CTkLabel(frame,
                     text="PurgeKit is 100% open source under the MIT License.\nFree to use, modify, and distribute.",
                     font=ctk.CTkFont("Segoe UI", 10),
                     text_color=TEXT_DIM, justify="center").pack(pady=(4, 12))

    def _show_about(self):
        win = ctk.CTkToplevel(self)
        win.title("About PurgeKit")
        win.geometry("480x560")
        win.configure(fg_color=BG_DARKEST)
        win.resizable(False, False)
        win.grab_set()
        self._build_about_panel(win)

    def _open_github(self):
        import webbrowser
        webbrowser.open(GITHUB_URL)

    def _toggle_autostart(self):
        ok = set_autostart(self.autostart_var.get())
        if not ok:
            messagebox.showerror("Auto-start Error",
                                 "Could not update startup registry.\nTry running as Administrator.")
            self.autostart_var.set(not self.autostart_var.get())

    # ── Helpers ──────────────────────────────────────────────
    def _log(self, text, tag="white"):
        ts   = datetime.datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {text}"
        self.log_lines.append(line)
        def _ins():
            self.log_box.configure(state="normal")
            self.log_box.insert("end", line + "\n", tag)
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        try:
            self.after(0, _ins)
        except Exception:
            pass

    def _set_progress(self, value, label):
        try:
            self.after(0, lambda: (self.progress_bar.set(value),
                                   self.progress_label.configure(text=label)))
        except Exception:
            pass

    def _select_all(self):
        for v in self.task_vars.values():
            v.set(True)
        for v in self.drive_vars.values():
            v.set(True)

    def _deselect_all(self):
        for v in self.task_vars.values():
            v.set(False)
        for v in self.drive_vars.values():
            v.set(False)

    def _toggle_compact(self):
        self._set_window_size()
        self._build_content()

    def _save_log(self, auto=False):
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        os.makedirs(downloads, exist_ok=True)
        dt  = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        lp  = os.path.join(downloads, f"PurgeKit_{dt}.txt")
        hdr = (f"{'=' * 60}\n"
               f"  PurgeKit v{APP_VERSION}  |  MIT License  |  {AUTHOR_BRAND}\n"
               f"  Built with love by {AUTHOR_NAME}, {AUTHOR_LOC}\n"
               f"  GitHub : {GITHUB_URL}\n"
               f"  Saved  : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
               f"  User   : {os.environ.get('USERNAME', 'Unknown')}\n"
               f"  PC     : {platform.node()}\n"
               f"{'=' * 60}\n\n")
        try:
            with open(lp, "w", encoding="utf-8") as f:
                f.write(hdr)
                for line in self.log_lines:
                    f.write(line + "\n")
            if auto:
                self._log(f"  Log saved: {lp}", "dim")
            else:
                messagebox.showinfo("Log Saved", f"Log saved to:\n{lp}")
        except Exception as e:
            if not auto:
                messagebox.showerror("Error", f"Could not save log:\n{e}")

    # ── Purge engine ─────────────────────────────────────────
    def _start_purge(self):
        if self.running:
            return
        selected   = [tid for tid, v in self.task_vars.items() if v.get()]
        sel_drives = [d   for d,   v in self.drive_vars.items() if v.get()]
        if not selected and not sel_drives and self.activity_var.get() == "skip":
            messagebox.showwarning("Nothing Selected", "Select at least one task.")
            return
        self.running = True
        self.start_btn.configure(text="⏳  Running...", state="disabled",
                                  fg_color="#002510", text_color=TEXT_GRAY)
        self.reboot_needed = [False]
        threading.Thread(target=self._purge_thread,
                         args=(selected, sel_drives), daemon=True).start()

    def _purge_thread(self, selected, sel_drives):
        act   = self.activity_var.get()
        total = len(selected) + len(sel_drives) + (0 if act == "skip" else 1)
        done  = 0

        self._log("", "dim")
        self._log("═" * 50, "accent")
        self._log("  PURGE STARTED", "accent")
        self._log("═" * 50, "accent")

        for task in TASKS:
            tid, phase, label, path, do_exp, default, warning = task
            if tid not in selected:
                continue
            done += 1
            self._set_progress(done / max(total, 1), f"[{done}/{total}] {label}...")
            self._log(f"\n── {tid}: {label}", "accent")
            rp = ep(path) if do_exp else path

            # ── System handlers
            if tid == "S3":
                run("net stop wuauserv"); run("net stop bits")
                force_delete(rp, self._log, self.reboot_needed); recreate(rp)
                run("net start wuauserv"); run("net start bits")
            elif tid == "S4":
                run("net stop DoSvc")
                force_delete(rp, self._log, self.reboot_needed); recreate(rp)
                run("net start DoSvc")
            elif tid == "S8":
                run("net stop FontCache")
                force_delete(rp, self._log, self.reboot_needed); recreate(rp)
                run("net start FontCache")
            elif tid == "S9":
                run("net stop wuauserv")
                force_delete(rp, self._log, self.reboot_needed); recreate(rp)
                run("net start wuauserv")
            elif tid in ("S11", "O9"):
                run("ipconfig /flushdns")
                self._log("  ✅ DNS cache flushed", "success")
            # ── User handlers
            elif tid == "U1b":
                p = ep(r"%LOCALAPPDATA%\Temp")
                force_delete(p, self._log, self.reboot_needed); recreate(p)
            elif tid == "U2":
                run("taskkill /f /im explorer.exe")
                thumbs = ep(r"%LOCALAPPDATA%\Microsoft\Windows\Explorer")
                if os.path.exists(thumbs):
                    for f in os.listdir(thumbs):
                        if f.startswith("thumbcache_") and f.endswith(".db"):
                            try:
                                os.remove(os.path.join(thumbs, f))
                            except Exception:
                                pass
                run("start explorer.exe")
                self._log("  ✅ Thumbnail cache cleared", "success")
            elif tid == "U4":
                force_delete(ep(r"%LOCALAPPDATA%\Microsoft\Windows\WebCache"),
                             self._log, self.reboot_needed)
                recreate(ep(r"%LOCALAPPDATA%\Microsoft\Windows\WebCache"))
            elif tid == "U5b":
                force_delete(ep(r"%LOCALAPPDATA%\CrashDumps"), self._log, self.reboot_needed)
                recreate(ep(r"%LOCALAPPDATA%\CrashDumps"))
            elif tid == "U6":
                run("taskkill /f /im Teams.exe")
                for sub in [r"%APPDATA%\Microsoft\Teams\Cache",
                             r"%APPDATA%\Microsoft\Teams\blob_storage"]:
                    p = ep(sub)
                    force_delete(p, self._log, self.reboot_needed); recreate(p)
            elif tid == "U7":
                run("taskkill /f /im Code.exe")
                for sub in [r"%APPDATA%\Code\Cache", r"%APPDATA%\Code\CachedData"]:
                    p = ep(sub)
                    force_delete(p, self._log, self.reboot_needed); recreate(p)
            elif tid == "U9":
                run("taskkill /f /im Spotify.exe")
                force_delete(rp, self._log, self.reboot_needed); recreate(rp)
            elif tid == "U10":
                run("taskkill /f /im explorer.exe")
                ic = ep(r"%LOCALAPPDATA%\IconCache.db")
                if os.path.exists(ic):
                    try:
                        os.remove(ic)
                        self._log("  ✅ IconCache.db deleted", "success")
                    except Exception:
                        run(f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager" '
                            f'/v PendingFileRenameOperations /t REG_MULTI_SZ /d "\\??\\{ic}\\0" /f')
                        self.reboot_needed[0] = True
                run("start explorer.exe")
            elif tid == "U11":
                run("cmd /c echo. | clip")
                self._log("  ✅ Clipboard cleared", "success")
            elif tid == "U12":
                run("wsreset.exe")
                self._log("  ✅ Windows Store cache reset", "success")
            # ── Browser handlers
            elif tid == "B1":
                run("taskkill /f /im chrome.exe")
                base = ep(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default")
                for sub in ["Cache", "Code Cache", "GPUCache"]:
                    p = os.path.join(base, sub)
                    force_delete(p, self._log, self.reboot_needed); recreate(p)
                self._log("  ✅ Chrome cache cleared", "success")
            elif tid == "B1b":
                run("taskkill /f /im chrome.exe")
                sw = ep(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Service Worker\CacheStorage")
                force_delete(sw, self._log, self.reboot_needed); recreate(sw)
                self._log("  ✅ Chrome Service Worker cache cleared", "success")
            elif tid == "B2":
                run("taskkill /f /im firefox.exe")
                profiles = ep(r"%LOCALAPPDATA%\Mozilla\Firefox\Profiles")
                if os.path.exists(profiles):
                    for prof in os.listdir(profiles):
                        for sub in ["cache2", "startupCache", "jumpListCache"]:
                            p = os.path.join(profiles, prof, sub)
                            force_delete(p, self._log, self.reboot_needed); recreate(p)
                self._log("  ✅ Firefox cache cleared", "success")
            elif tid == "B3":
                run("taskkill /f /im msedge.exe")
                base = ep(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default")
                for sub in ["Cache", "Code Cache", "GPUCache"]:
                    p = os.path.join(base, sub)
                    force_delete(p, self._log, self.reboot_needed); recreate(p)
                self._log("  ✅ Edge cache cleared", "success")
            elif tid == "B3b":
                run("taskkill /f /im msedge.exe")
                sw = ep(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Service Worker\CacheStorage")
                force_delete(sw, self._log, self.reboot_needed); recreate(sw)
                self._log("  ✅ Edge Service Worker cache cleared", "success")
            # ── Developer handlers
            elif tid == "D1":
                npm = ep(r"%APPDATA%\npm-cache")
                force_delete(npm, self._log, self.reboot_needed); recreate(npm)
                self._log("  ✅ npm cache cleared", "success")
            elif tid == "D2":
                pip = ep(r"%LOCALAPPDATA%\pip\cache")
                force_delete(pip, self._log, self.reboot_needed); recreate(pip)
                self._log("  ✅ pip cache cleared", "success")
            # ── System special
            elif tid == "S5":
                for sub in ["ReportQueue", "ReportArchive"]:
                    p = rf"C:\ProgramData\Microsoft\Windows\WER\{sub}"
                    force_delete(p, self._log, self.reboot_needed); recreate(p)
            elif tid == "S7":
                force_delete(r"C:\Windows\Minidump", self._log, self.reboot_needed)
                recreate(r"C:\Windows\Minidump")
                if os.path.exists(r"C:\Windows\MEMORY.DMP"):
                    try:
                        os.remove(r"C:\Windows\MEMORY.DMP")
                        self._log("  ✅ MEMORY.DMP deleted", "success")
                    except Exception:
                        run('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager" '
                            '/v PendingFileRenameOperations /t REG_MULTI_SZ '
                            '/d "\\??\\C:\\Windows\\MEMORY.DMP\\0" /f')
                        self.reboot_needed[0] = True
            # ── Optional handlers
            elif tid == "O1":
                for lg in ["Application", "System", "Security"]:
                    run(f'wevtutil cl "{lg}"')
                self._log("  ✅ Event logs cleared", "success")
            elif tid == "O2":
                for drv, _, _, _ in get_drives():
                    run(f'rd /s /q "{drv}$Recycle.Bin"')
                self._log("  ✅ Recycle Bin emptied on all drives", "success")
            elif tid == "O3":
                force_delete(r"C:\ProgramData\Microsoft\Diagnosis", self._log, self.reboot_needed)
                self._log("  ✅ Telemetry data removed", "success")
            elif tid == "O4":
                pkg = ep(r"%LOCALAPPDATA%\Packages")
                if os.path.exists(pkg):
                    for p in os.listdir(pkg):
                        if "Microsoft.Windows.Search" in p:
                            dc = os.path.join(pkg, p, "LocalState", "DeviceSearchCache")
                            force_delete(dc, self._log, self.reboot_needed)
                self._log("  ✅ Cortana search history cleared", "success")
            elif tid == "O5":
                run("arp -d *")
                self._log("  ✅ ARP cache flushed", "success")
            elif tid == "O6":
                run("nbtstat -R")
                self._log("  ✅ NetBIOS cache flushed", "success")
            elif tid == "O7":
                run("netsh winsock reset")
                self.reboot_needed[0] = True
                self._log("  ✅ Winsock reset — REBOOT REQUIRED", "warn")
            elif tid == "O8":
                run("sc config WSearch start= disabled")
                run("net stop WSearch")
                run("sc config WSearch start= auto")
                run("net start WSearch")
                self._log("  ✅ Search index rebuild triggered", "success")
            else:
                # Generic
                force_delete(rp, self._log, self.reboot_needed)
                if rp not in SKIP_PATHS:
                    recreate(rp)

        # ── Disk Cleanup per drive
        disk_cats = [
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
        for drv in sel_drives:
            done += 1
            self._set_progress(done / max(total, 1), f"[{done}/{total}] Disk Cleanup {drv}...")
            self._log(f"\n── Disk Cleanup: {drv}", "accent")
            for cat in disk_cats:
                run(f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VolumeCaches\\{cat}" '
                    f'/v StateFlags0099 /t REG_DWORD /d 2 /f')
            run(f"cleanmgr /sagerun:99 /d {drv[0]}", timeout=300)
            self._log(f"  ✅ Disk Cleanup done: {drv}", "success")

        # ── Activity History
        if act != "skip":
            done += 1
            self._set_progress(done / max(total, 1), "Windows Activity History...")
            self._log("\n── Activity History", "accent")
            cdp = ep(r"%LOCALAPPDATA%\ConnectedDevicesPlatform")
            run("taskkill /f /im explorer.exe")
            if os.path.exists(cdp):
                for profile in os.listdir(cdp):
                    db = os.path.join(cdp, profile, "ActivitiesCache.db")
                    if os.path.exists(db):
                        try:
                            os.remove(db)
                            self._log(f"  ✅ Deleted: {db}", "success")
                        except Exception:
                            run(f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager" '
                                f'/v PendingFileRenameOperations /t REG_MULTI_SZ /d "\\??\\{db}\\0" /f')
                            self.reboot_needed[0] = True
            run("start explorer.exe")
            if act == "disable":
                for v in ["EnableActivityFeed", "PublishUserActivities", "UploadUserActivities"]:
                    run(f'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" '
                        f'/v {v} /t REG_DWORD /d 0 /f')
                self._log("  ✅ Activity History disabled in registry", "success")

        # ── Finish
        self._save_log(auto=True)
        self._set_progress(1.0, "✅ All done!")
        self._log("", "dim")
        self._log("═" * 50, "accent")
        self._log("  PURGE COMPLETE ✅", "success")
        if self.reboot_needed[0]:
            self._log("  ⚠ REBOOT REQUIRED", "warn")
            self.after(0, lambda: messagebox.showwarning(
                "Reboot Required",
                "Some files are scheduled for deletion on next startup.\n"
                "Please restart your PC to complete the cleanup."))
        else:
            self._log("  No reboot needed.", "dim")
        self._log("═" * 50, "accent")
        self._log("  Log auto-saved to Downloads.", "dim")

        def _re():
            self.start_btn.configure(text="🧹  START PURGE", state="normal",
                                      fg_color=ACCENT_DARK, text_color=ACCENT)
            self.running = False
        self.after(0, _re)


if __name__ == "__main__":
    app = PurgeKitApp()
    app.mainloop()
