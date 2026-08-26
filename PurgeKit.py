"""
PurgeKit v2.0
MIT License — TeamExyKings
GitHub: https://github.com/yashwanthramsomireddy/PurgeKit

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

# ── Admin check (Windows only) ──────────────────────────────
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
from PIL import Image, ImageDraw, ImageFont
import io
import base64

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

# ── Cleaning Tasks Definition ────────────────────────────────
TASKS = [
    # (id, phase, label, path_display, env_expand)
    # Phase 1 — System
    ("S1",  "System",   "Windows System Temp",              r"C:\Windows\Temp",                                          False),
    ("S2",  "System",   "Prefetch Files",                   r"C:\Windows\Prefetch",                                      False),
    ("S3",  "System",   "Windows Update Cache",             r"C:\Windows\SoftwareDistribution\Download",                 False),
    ("S4",  "System",   "Delivery Optimization Files",      r"C:\Windows\SoftwareDistribution\DeliveryOptimization",     False),
    ("S5",  "System",   "Windows Error Reporting",          r"C:\ProgramData\Microsoft\Windows\WER",                     False),
    ("S6",  "System",   "CBS Logs",                         r"C:\Windows\Logs\CBS",                                      False),
    ("S7",  "System",   "Crash Dumps",                      r"C:\Windows\Minidump",                                      False),
    ("S8",  "System",   "Windows Font Cache",               r"C:\Windows\ServiceProfiles\LocalService\AppData\Local\FontCache", False),
    ("S9",  "System",   "SoftwareDistribution Logs",        r"C:\Windows\SoftwareDistribution\DataStore\Logs",           False),
    ("S10", "System",   "Windows Installer Patch Cache",    r"C:\Windows\Installer\$PatchCache$",                        False),
    ("S11", "System",   "DNS Cache (Flush)",                "System DNS Resolver",                                       False),
    # Phase 2 — User
    ("U1",  "User",     "User Temp Folder",                 "%TEMP%",                                                    True),
    ("U2",  "User",     "Thumbnail Cache",                  r"%LOCALAPPDATA%\Microsoft\Windows\Explorer",                True),
    ("U3",  "User",     "Recent Files & Jump Lists",        r"%APPDATA%\Microsoft\Windows\Recent",                       True),
    ("U4",  "User",     "IE / Legacy Edge Cache",           r"%LOCALAPPDATA%\Microsoft\Windows\INetCache",               True),
    ("U5",  "User",     "DirectX Shader Cache",             r"%LOCALAPPDATA%\D3DSCache",                                 True),
    ("U6",  "User",     "Microsoft Teams Cache",            r"%APPDATA%\Microsoft\Teams\Cache",                          True),
    ("U7",  "User",     "VS Code Cache",                    r"%APPDATA%\Code\Cache",                                     True),
    ("U8",  "User",     "Microsoft Office Cache",           r"%LOCALAPPDATA%\Microsoft\Office\16.0\OfficeFileCache",     True),
    ("U9",  "User",     "Spotify Cache",                    r"%LOCALAPPDATA%\Spotify\Storage",                           True),
    # Phase 3 — Browsers
    ("B1",  "Browser",  "Google Chrome Cache",              r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache",     True),
    ("B2",  "Browser",  "Mozilla Firefox Cache",            r"%LOCALAPPDATA%\Mozilla\Firefox\Profiles",                  True),
    ("B3",  "Browser",  "Microsoft Edge Cache",             r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache",    True),
    # Phase 4 — Disk Cleanup
    ("DC",  "Cleanup",  "Windows Disk Cleanup (All)",       "cleanmgr /sageset:99",                                      False),
]

ACTIVITY_OPTIONS = [
    ("delete",   "Delete ActivitiesCache.db (one-time clean)"),
    ("disable",  "Delete + Disable Activity History permanently"),
    ("skip",     "Skip"),
]

# ── Helper: expand env vars ──────────────────────────────────
def ep(path):
    return os.path.expandvars(path)

# ── Helper: run command silently ─────────────────────────────
def run(cmd):
    try:
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=60)
    except Exception:
        pass

# ── Helper: force delete with 3-technique cascade ────────────
def force_delete(path, log_fn, reboot_flag):
    if not os.path.exists(path):
        log_fn(f"  [SKIP] Not found: {path}", "dim")
        return

    # T1 — robocopy mirror
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

    # T2 — takeown + icacls
    log_fn(f"  ⚠ T1 failed, trying T2 (takeown)...", "warn")
    run(f'takeown /f "{path}" /r /d y')
    run(f'icacls "{path}" /grant administrators:F /t /q')
    try:
        shutil.rmtree(path, ignore_errors=True)
    except Exception:
        pass

    if not os.path.exists(path):
        log_fn(f"  ✅ T2 (takeown+icacls) — {path}", "success")
        return

    # T3 — schedule on reboot
    log_fn(f"  ⚠ T2 failed, scheduling on reboot (T3)...", "warn")
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

# ── Generate Icon ─────────────────────────────────────────────
def generate_icon():
    """Generate a unique PurgeKit broom/vortex icon."""
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background circle — deep black
    draw.ellipse([4, 4, 252, 252], fill=(10, 10, 10, 255), outline=(0, 230, 118, 255), width=6)

    # Inner glow ring
    draw.ellipse([20, 20, 236, 236], outline=(0, 200, 100, 80), width=2)

    # Draw stylized "P" broom shape using green lines
    # Broom handle
    draw.line([(128, 60), (128, 160)], fill=(0, 230, 118), width=10)
    # Broom head — sweep lines
    for i, offset in enumerate([-40, -25, -10, 5, 20, 35, 50]):
        alpha = 255 - i * 20
        x = 88 + offset
        draw.line([(128, 160), (x, 210)], fill=(0, 230, 118, alpha), width=5)
    # Top accent dot
    draw.ellipse([118, 50, 138, 70], fill=(0, 230, 118, 255))

    return img

# ══════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════
class PurgeKitApp(ctk.CTk):

    COMPACT_W, COMPACT_H = 720, 640
    SPACIOUS_W, SPACIOUS_H = 1000, 780

    def __init__(self):
        super().__init__()

        self.title("PurgeKit v2.0  —  TeamExyKings")
        self.configure(fg_color=BG_DARKEST)
        self.resizable(True, True)
        self.minsize(680, 580)

        # State
        self.compact_mode = tk.BooleanVar(value=False)
        self.task_vars = {}
        self.activity_var = tk.StringVar(value="skip")
        self.running = False
        self.reboot_needed = [False]
        self.log_lines = []

        # Icon
        try:
            icon_img = generate_icon()
            icon_tk = ctk.CTkImage(light_image=icon_img, dark_image=icon_img, size=(32, 32))
            self._icon_ctk = icon_tk
            # Set taskbar icon
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
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"+{x}+{y}")

    # ── Build UI ─────────────────────────────────────────────
    def _build_ui(self):
        # ── Top bar
        top = ctk.CTkFrame(self, fg_color=BG_DARK, height=56, corner_radius=0)
        top.pack(fill="x", side="top")
        top.pack_propagate(False)

        # Logo + title
        title_frame = ctk.CTkFrame(top, fg_color="transparent")
        title_frame.pack(side="left", padx=16, pady=8)

        try:
            logo_img = generate_icon()
            logo_ctk = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(32, 32))
            logo_label = ctk.CTkLabel(title_frame, image=logo_ctk, text="")
            logo_label.pack(side="left", padx=(0, 8))
        except Exception:
            pass

        ctk.CTkLabel(
            title_frame, text="PurgeKit", font=ctk.CTkFont("Segoe UI", 20, "bold"),
            text_color=ACCENT
        ).pack(side="left")
        ctk.CTkLabel(
            title_frame, text=" v2.0", font=ctk.CTkFont("Segoe UI", 13),
            text_color=TEXT_GRAY
        ).pack(side="left")

        # Right controls
        right = ctk.CTkFrame(top, fg_color="transparent")
        right.pack(side="right", padx=16, pady=8)

        ctk.CTkLabel(right, text="Compact", font=ctk.CTkFont("Segoe UI", 12),
                     text_color=TEXT_GRAY).pack(side="left", padx=(0, 4))
        ctk.CTkSwitch(
            right, text="", variable=self.compact_mode,
            command=self._toggle_compact,
            width=44, height=22,
            button_color=ACCENT, button_hover_color=ACCENT_DIM,
            progress_color=ACCENT_DARK
        ).pack(side="left")

        # ── Main content
        self.main_frame = ctk.CTkFrame(self, fg_color=BG_DARKEST, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        self._build_content()

    def _build_content(self):
        # Clear existing content
        for w in self.main_frame.winfo_children():
            w.destroy()

        compact = self.compact_mode.get()

        if compact:
            self._build_compact_layout()
        else:
            self._build_spacious_layout()

    def _build_spacious_layout(self):
        # Left panel — tasks
        left = ctk.CTkFrame(self.main_frame, fg_color=BG_DARKEST, corner_radius=0)
        left.pack(side="left", fill="both", expand=True, padx=(12, 6), pady=12)

        # Right panel — log
        right = ctk.CTkFrame(self.main_frame, fg_color=BG_DARK, corner_radius=10, width=300)
        right.pack(side="right", fill="both", padx=(0, 12), pady=12)
        right.pack_propagate(False)

        self._build_task_panel(left)
        self._build_log_panel(right)

    def _build_compact_layout(self):
        # Notebook-style tabs
        self.tabs = ctk.CTkTabview(
            self.main_frame, fg_color=BG_DARK,
            segmented_button_fg_color=BG_CARD,
            segmented_button_selected_color=ACCENT_DARK,
            segmented_button_selected_hover_color=ACCENT_DARK,
            segmented_button_unselected_color=BG_CARD,
            text_color=TEXT_WHITE,
            border_color=TEXT_DIM, border_width=1
        )
        self.tabs.pack(fill="both", expand=True, padx=12, pady=12)
        self.tabs.add("🧹 Tasks")
        self.tabs.add("📄 Log")

        self._build_task_panel(self.tabs.tab("🧹 Tasks"))
        self._build_log_panel(self.tabs.tab("📄 Log"))

    # ── Task Panel ───────────────────────────────────────────
    def _build_task_panel(self, parent):
        # Select All / Deselect All
        btn_row = ctk.CTkFrame(parent, fg_color="transparent")
        btn_row.pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            btn_row, text="✔ Select All", width=120, height=28,
            fg_color=ACCENT_DARK, hover_color="#004d20", text_color=ACCENT,
            font=ctk.CTkFont("Segoe UI", 12), corner_radius=6,
            command=self._select_all
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row, text="✘ Deselect All", width=120, height=28,
            fg_color="#1a1a1a", hover_color="#222222", text_color=TEXT_GRAY,
            font=ctk.CTkFont("Segoe UI", 12), corner_radius=6,
            command=self._deselect_all
        ).pack(side="left")

        # Scrollable task list
        scroll = ctk.CTkScrollableFrame(
            parent, fg_color=BG_DARKEST, corner_radius=8,
            scrollbar_button_color=ACCENT_DARK,
            scrollbar_button_hover_color=ACCENT
        )
        scroll.pack(fill="both", expand=True)

        # Group by phase
        phases = {}
        for task in TASKS:
            tid, phase, label, path, _ = task
            phases.setdefault(phase, []).append(task)

        phase_colors = {
            "System":  "#003916",
            "User":    "#003020",
            "Browser": "#002818",
            "Cleanup": "#001a10",
        }
        phase_icons = {
            "System": "⚙",
            "User": "👤",
            "Browser": "🌐",
            "Cleanup": "🗑",
        }

        for phase, tasks in phases.items():
            # Phase header
            ph_frame = ctk.CTkFrame(
                scroll, fg_color=phase_colors.get(phase, BG_CARD),
                corner_radius=8
            )
            ph_frame.pack(fill="x", pady=(8, 2), padx=2)

            ctk.CTkLabel(
                ph_frame,
                text=f"  {phase_icons.get(phase, '•')}  {phase} Level",
                font=ctk.CTkFont("Segoe UI", 12, "bold"),
                text_color=ACCENT, anchor="w"
            ).pack(fill="x", padx=12, pady=(6, 4))

            for task in tasks:
                tid, ph, label, path, _ = task
                var = tk.BooleanVar(value=True)
                self.task_vars[tid] = var

                row = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=6)
                row.pack(fill="x", pady=2, padx=2)

                ctk.CTkCheckBox(
                    row, text=label,
                    variable=var,
                    font=ctk.CTkFont("Segoe UI", 12),
                    text_color=TEXT_WHITE,
                    fg_color=ACCENT_DARK,
                    hover_color=ACCENT_DARK,
                    checkmark_color=ACCENT,
                    border_color=TEXT_DIM,
                    width=20, height=20
                ).pack(side="left", padx=(10, 6), pady=6)

                ctk.CTkLabel(
                    row, text=path,
                    font=ctk.CTkFont("Segoe UI", 10),
                    text_color=TEXT_GRAY, anchor="w"
                ).pack(side="right", padx=(0, 10), pady=6)

        # ── Activity History
        act_frame = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=8)
        act_frame.pack(fill="x", pady=(12, 2), padx=2)

        ctk.CTkLabel(
            act_frame,
            text="  🔒  Privacy — Windows Activity History",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=WARN, anchor="w"
        ).pack(fill="x", padx=12, pady=(8, 2))

        ctk.CTkLabel(
            act_frame,
            text="  Tracks apps opened, files viewed, websites visited (ActivitiesCache.db)",
            font=ctk.CTkFont("Segoe UI", 10),
            text_color=TEXT_GRAY, anchor="w"
        ).pack(fill="x", padx=12, pady=(0, 6))

        for val, txt in ACTIVITY_OPTIONS:
            ctk.CTkRadioButton(
                act_frame, text=txt,
                variable=self.activity_var, value=val,
                font=ctk.CTkFont("Segoe UI", 11),
                text_color=TEXT_WHITE,
                fg_color=ACCENT_DARK,
                hover_color=ACCENT_DARK,
                border_color=TEXT_DIM
            ).pack(anchor="w", padx=20, pady=3)

        ctk.CTkFrame(act_frame, fg_color="transparent", height=8).pack()

        # ── Bottom controls
        bottom = ctk.CTkFrame(parent, fg_color=BG_DARKEST, corner_radius=0)
        bottom.pack(fill="x", pady=(10, 0))

        # Progress bar
        self.progress_label = ctk.CTkLabel(
            bottom, text="Ready to purge.",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=TEXT_GRAY, anchor="w"
        )
        self.progress_label.pack(fill="x", padx=2, pady=(0, 4))

        self.progress_bar = ctk.CTkProgressBar(
            bottom, height=10,
            fg_color=BG_CARD,
            progress_color=ACCENT,
            corner_radius=5
        )
        self.progress_bar.pack(fill="x", padx=2, pady=(0, 8))
        self.progress_bar.set(0)

        btn_row2 = ctk.CTkFrame(bottom, fg_color="transparent")
        btn_row2.pack(fill="x")

        self.start_btn = ctk.CTkButton(
            btn_row2, text="🧹  START PURGE",
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
            height=42, corner_radius=8,
            fg_color=ACCENT_DARK, hover_color="#005c20",
            text_color=ACCENT,
            command=self._start_purge
        )
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(
            btn_row2, text="📄  Save Log",
            font=ctk.CTkFont("Segoe UI", 12),
            height=42, width=110, corner_radius=8,
            fg_color=BG_CARD, hover_color=BG_HOVER,
            text_color=TEXT_GRAY,
            command=self._save_log
        ).pack(side="right")

    # ── Log Panel ────────────────────────────────────────────
    def _build_log_panel(self, parent):
        ctk.CTkLabel(
            parent, text="📋  Run Log",
            font=ctk.CTkFont("Segoe UI", 13, "bold"),
            text_color=ACCENT, anchor="w"
        ).pack(fill="x", padx=12, pady=(10, 4))

        self.log_box = ctk.CTkTextbox(
            parent,
            fg_color=BG_DARKEST,
            text_color=TEXT_WHITE,
            font=ctk.CTkFont("Consolas", 11),
            corner_radius=6,
            scrollbar_button_color=ACCENT_DARK,
            scrollbar_button_hover_color=ACCENT,
            wrap="word",
            state="disabled"
        )
        self.log_box.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Color tags (configure after creation)
        self.log_box.tag_config("success", foreground=SUCCESS)
        self.log_box.tag_config("warn", foreground=WARN)
        self.log_box.tag_config("error", foreground=ERROR)
        self.log_box.tag_config("dim", foreground=TEXT_GRAY)
        self.log_box.tag_config("accent", foreground=ACCENT)
        self.log_box.tag_config("white", foreground=TEXT_WHITE)

        self._log("PurgeKit v2.0 ready.", "accent")
        self._log("Select tasks and press START PURGE.", "dim")

    # ── Log helpers ──────────────────────────────────────────
    def _log(self, text, tag="white"):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {text}"
        self.log_lines.append(line)

        def _insert():
            self.log_box.configure(state="normal")
            self.log_box.insert("end", line + "\n", tag)
            self.log_box.see("end")
            self.log_box.configure(state="disabled")

        try:
            self.after(0, _insert)
        except Exception:
            pass

    def _set_progress(self, value, label):
        def _upd():
            self.progress_bar.set(value)
            self.progress_label.configure(text=label)
        try:
            self.after(0, _upd)
        except Exception:
            pass

    # ── Select / Deselect ────────────────────────────────────
    def _select_all(self):
        for var in self.task_vars.values():
            var.set(True)

    def _deselect_all(self):
        for var in self.task_vars.values():
            var.set(False)

    # ── Toggle Compact ───────────────────────────────────────
    def _toggle_compact(self):
        self._set_window_size()
        self._build_content()

    # ── Save Log ─────────────────────────────────────────────
    def _save_log(self):
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        os.makedirs(downloads, exist_ok=True)
        dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(downloads, f"PurgeKit_{dt}.txt")
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("=" * 60 + "\n")
                f.write("  PurgeKit v2.0  |  MIT License  |  TeamExyKings\n")
                f.write(f"  GitHub: https://github.com/yashwanthramsomireddy/PurgeKit\n")
                f.write(f"  Saved : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"  User  : {os.environ.get('USERNAME', 'Unknown')}\n")
                f.write(f"  PC    : {platform.node()}\n")
                f.write("=" * 60 + "\n\n")
                for line in self.log_lines:
                    f.write(line + "\n")
            messagebox.showinfo("Log Saved", f"Log saved to:\n{log_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save log:\n{e}")

    # ── Purge Engine ─────────────────────────────────────────
    def _start_purge(self):
        if self.running:
            return
        selected = [tid for tid, var in self.task_vars.items() if var.get()]
        if not selected and self.activity_var.get() == "skip":
            messagebox.showwarning("Nothing Selected", "Please select at least one task.")
            return

        self.running = True
        self.start_btn.configure(text="⏳  Running...", state="disabled",
                                  fg_color="#002510", text_color=TEXT_GRAY)
        self.reboot_needed = [False]

        thread = threading.Thread(target=self._purge_thread, args=(selected,), daemon=True)
        thread.start()

    def _purge_thread(self, selected):
        total = len(selected) + (1 if self.activity_var.get() != "skip" else 0)
        done = 0

        self._log("", "dim")
        self._log("═" * 50, "accent")
        self._log("  PURGE STARTED", "accent")
        self._log("═" * 50, "accent")

        for task in TASKS:
            tid, phase, label, path, do_expand = task
            if tid not in selected:
                continue

            done += 1
            pct = done / max(total, 1)
            self._set_progress(pct, f"[{done}/{total}] {label}...")
            self._log(f"\n── {tid}: {label}", "accent")

            real_path = ep(path) if do_expand else path

            # ── Special handlers
            if tid == "S3":
                run("net stop wuauserv")
                run("net stop bits")
                force_delete(real_path, self._log, self.reboot_needed)
                recreate(real_path)
                run("net start wuauserv")
                run("net start bits")

            elif tid == "S4":
                run("net stop DoSvc")
                force_delete(real_path, self._log, self.reboot_needed)
                recreate(real_path)
                run("net start DoSvc")

            elif tid == "S8":
                run("net stop FontCache")
                force_delete(real_path, self._log, self.reboot_needed)
                recreate(real_path)
                run("net start FontCache")

            elif tid == "S9":
                run("net stop wuauserv")
                force_delete(real_path, self._log, self.reboot_needed)
                recreate(real_path)
                run("net start wuauserv")

            elif tid == "S11":
                run("ipconfig /flushdns")
                self._log("  ✅ DNS cache flushed", "success")

            elif tid == "U2":
                run("taskkill /f /im explorer.exe")
                thumbs = ep(r"%LOCALAPPDATA%\Microsoft\Windows\Explorer")
                for f in os.listdir(thumbs) if os.path.exists(thumbs) else []:
                    if f.startswith("thumbcache_") and f.endswith(".db"):
                        try:
                            os.remove(os.path.join(thumbs, f))
                        except Exception:
                            pass
                run("start explorer.exe")
                self._log("  ✅ Thumbnail cache cleared", "success")

            elif tid == "U6":
                run("taskkill /f /im Teams.exe")
                force_delete(ep(r"%APPDATA%\Microsoft\Teams\Cache"), self._log, self.reboot_needed)
                force_delete(ep(r"%APPDATA%\Microsoft\Teams\blob_storage"), self._log, self.reboot_needed)
                recreate(ep(r"%APPDATA%\Microsoft\Teams\Cache"))
                recreate(ep(r"%APPDATA%\Microsoft\Teams\blob_storage"))

            elif tid == "U7":
                run("taskkill /f /im Code.exe")
                force_delete(ep(r"%APPDATA%\Code\Cache"), self._log, self.reboot_needed)
                force_delete(ep(r"%APPDATA%\Code\CachedData"), self._log, self.reboot_needed)
                recreate(ep(r"%APPDATA%\Code\Cache"))
                recreate(ep(r"%APPDATA%\Code\CachedData"))

            elif tid == "U9":
                run("taskkill /f /im Spotify.exe")
                force_delete(real_path, self._log, self.reboot_needed)
                recreate(real_path)

            elif tid == "B1":
                run("taskkill /f /im chrome.exe")
                base = ep(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default")
                for sub in ["Cache", "Code Cache", "GPUCache"]:
                    p = os.path.join(base, sub)
                    force_delete(p, self._log, self.reboot_needed)
                    recreate(p)

            elif tid == "B2":
                run("taskkill /f /im firefox.exe")
                profiles = ep(r"%LOCALAPPDATA%\Mozilla\Firefox\Profiles")
                if os.path.exists(profiles):
                    for prof in os.listdir(profiles):
                        for sub in ["cache2", "startupCache", "jumpListCache"]:
                            p = os.path.join(profiles, prof, sub)
                            force_delete(p, self._log, self.reboot_needed)
                            recreate(p)

            elif tid == "B3":
                run("taskkill /f /im msedge.exe")
                base = ep(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default")
                for sub in ["Cache", "Code Cache", "GPUCache"]:
                    p = os.path.join(base, sub)
                    force_delete(p, self._log, self.reboot_needed)
                    recreate(p)

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

            elif tid == "S5":
                for sub in ["ReportQueue", "ReportArchive"]:
                    p = rf"C:\ProgramData\Microsoft\Windows\WER\{sub}"
                    force_delete(p, self._log, self.reboot_needed)
                    recreate(p)

            elif tid == "DC":
                self._log("  Registering Disk Cleanup categories...", "dim")
                categories = [
                    "Active Setup Temp Folders", "BranchCache", "Content Indexer Cleaner",
                    "D3D Shader Cache", "Delivery Optimization Files", "Device Driver Packages",
                    "Downloaded Program Files", "Internet Cache Files", "Memory Dump Files",
                    "Offline Pages Files", "Old ChkDsk Files", "Previous Installations",
                    "Recycle Bin", "Service Pack Cleanup", "Setup Log Files",
                    "System error memory dump files", "System error minidump files",
                    "Temporary Files", "Temporary Setup Files", "Thumbnail Cache",
                    "Update Cleanup", "Upgrade Discarded Files", "Windows Defender",
                    "Windows Error Reporting Archive Files", "Windows Error Reporting Files",
                    "Windows Error Reporting Queue Files", "Windows ESD installation files",
                    "Windows Upgrade Log Files",
                ]
                for cat in categories:
                    run(f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VolumeCaches\\{cat}" '
                        f'/v StateFlags0099 /t REG_DWORD /d 2 /f')
                run("cleanmgr /sagerun:99")
                self._log("  ✅ Disk Cleanup completed", "success")

            else:
                # Generic delete + recreate
                force_delete(real_path, self._log, self.reboot_needed)
                if os.path.dirname(real_path) and real_path not in [
                    "System DNS Resolver", r"C:\Windows\Installer\$PatchCache$"
                ]:
                    recreate(real_path)

        # ── Activity History
        act = self.activity_var.get()
        if act != "skip":
            done += 1
            pct = done / max(total, 1)
            self._set_progress(pct, "Windows Activity History...")
            self._log("\n── U10: Windows Activity History", "accent")

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
                            self._log(f"  🔁 Scheduled on reboot: {db}", "warn")
            run("start explorer.exe")

            if act == "disable":
                run('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" '
                    '/v EnableActivityFeed /t REG_DWORD /d 0 /f')
                run('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" '
                    '/v PublishUserActivities /t REG_DWORD /d 0 /f')
                run('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" '
                    '/v UploadUserActivities /t REG_DWORD /d 0 /f')
                self._log("  ✅ Activity History disabled in registry", "success")

        # ── Auto-save log
        self._save_log_auto()

        # ── Done
        self._set_progress(1.0, "✅ All done!")
        self._log("", "dim")
        self._log("═" * 50, "accent")
        self._log("  PURGE COMPLETE ✅", "success")

        if self.reboot_needed[0]:
            self._log("  ⚠ REBOOT REQUIRED — some files scheduled for deletion on next startup.", "warn")
            self.after(0, lambda: messagebox.showwarning(
                "Reboot Required",
                "Some files could not be deleted while Windows was running.\n\n"
                "They have been scheduled for deletion on next startup.\n\n"
                "Please restart your PC to complete the cleanup."
            ))
        else:
            self._log("  No reboot needed.", "dim")

        self._log("═" * 50, "accent")
        self._log("  Log auto-saved to Downloads folder.", "dim")

        def _re_enable():
            self.start_btn.configure(
                text="🧹  START PURGE", state="normal",
                fg_color=ACCENT_DARK, text_color=ACCENT
            )
            self.running = False
        self.after(0, _re_enable)

    def _save_log_auto(self):
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        os.makedirs(downloads, exist_ok=True)
        dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(downloads, f"PurgeKit_{dt}.txt")
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("=" * 60 + "\n")
                f.write("  PurgeKit v2.0  |  MIT License  |  TeamExyKings\n")
                f.write(f"  GitHub: https://github.com/yashwanthramsomireddy/PurgeKit\n")
                f.write(f"  Saved : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"  User  : {os.environ.get('USERNAME', 'Unknown')}\n")
                f.write(f"  PC    : {platform.node()}\n")
                f.write("=" * 60 + "\n\n")
                for line in self.log_lines:
                    f.write(line + "\n")
            self._log(f"  Log: {log_path}", "dim")
        except Exception as e:
            self._log(f"  [WARN] Could not auto-save log: {e}", "warn")


# ── Entry Point ──────────────────────────────────────────────
if __name__ == "__main__":
    app = PurgeKitApp()
    app.mainloop()
