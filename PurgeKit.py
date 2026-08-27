"""
PurgeKit v3.1
MIT License — TeamExyKings
GitHub: https://github.com/yashwanthramsomireddy/PurgeKit
Built with love by Yashwanth Ram Somireddy, Chennai, India

Fixes in v3.1:
- Compact tab spacing fixed
- Spacious mode: sidebar navigation instead of missing tabs
- Theme applies on the fly (no restart needed)
- About tab: proper left-aligned two-column layout
- Startup tab: Enable/Disable per program, full path shown
- Scan tab: checkboxes + Clean Selected button
- Dry Run: visible topbar indicator, button text changes
- Taskbar/pinned icon uses PurgeKit icon correctly
"""

import sys
import os
import ctypes
import threading
import datetime
import platform
import tkinter as tk
from tkinter import messagebox, filedialog
import winreg
import tempfile

# ── Admin ─────────────────────────────────────────────────────
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def relaunch_as_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable,
        " ".join(f'"{a}"' for a in sys.argv), None, 1)
    sys.exit()

if platform.system() == "Windows" and not is_admin():
    relaunch_as_admin()

import customtkinter as ctk
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
from core.config       import (load_config, save_config, load_history, save_history,
                                load_whitelist, save_whitelist, verify_pin,
                                set_pin, clear_pin)
from core.cleaner      import (TASKS, DISK_CLEANUP_CATS, get_drives,
                                fmt_size, run, ep, run_task, recreate, folder_size)
from core.scanner      import scan_all, total_junk, SCAN_PATHS
from core.lang_manager import LANGUAGES, load_lang, t
from core.updater      import check_for_update
from core.scheduler    import create_schedule, remove_schedule, get_next_run, schedule_exists
from core.startup_manager import get_startup_programs, disable_startup, enable_startup
from core.log_manager  import write_log
from ui.themes         import get_theme

APP_VERSION  = "3.1.5"
GITHUB_URL   = "https://github.com/yashwanthramsomireddy/PurgeKit"
AUTHOR_NAME  = "Yashwanth Ram Somireddy"
AUTHOR_LOC   = "Chennai, India"
AUTHOR_BRAND = "TeamExyKings"
AUTOSTART_KEY = "PurgeKit"
AUTOSTART_REG = r"Software\Microsoft\Windows\CurrentVersion\Run"

# ── Icon ─────────────────────────────────────────────────────
def generate_icon(accent_color=(0, 230, 118)):
    size = 256
    img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    r, g, b = accent_color
    draw.ellipse([4,4,252,252], fill=(10,10,10,255), outline=(r,g,b,255), width=6)
    draw.ellipse([20,20,236,236], outline=(r,g,b,80), width=2)
    draw.line([(128,60),(128,160)], fill=(r,g,b), width=10)
    for i, offset in enumerate([-40,-25,-10,5,20,35,50]):
        draw.line([(128,160),(88+offset,210)],
                  fill=(r,g,b,max(60,255-i*28)), width=5)
    draw.ellipse([118,50,138,70], fill=(r,g,b,255))
    return img

def save_icon_file(accent_color=(0,230,118)):
    """Save .ico to temp and return path — used for taskbar/pinned icon."""
    try:
        img      = generate_icon(accent_color)
        ico_path = os.path.join(tempfile.gettempdir(), "purgekit_app.ico")
        img.save(ico_path, format="ICO",
                 sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])
        return ico_path
    except Exception:
        return ""

# ── Auto-start ────────────────────────────────────────────────
def get_autostart():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_REG, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, AUTOSTART_KEY)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False

def set_autostart(enable):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_REG, 0, winreg.KEY_SET_VALUE)
        if enable:
            val = (f'"{sys.executable}"' if getattr(sys,"frozen",False)
                   else f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"')
            winreg.SetValueEx(key, AUTOSTART_KEY, 0, winreg.REG_SZ, val)
        else:
            try:
                winreg.DeleteValue(key, AUTOSTART_KEY)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception:
        return False

# ══════════════════════════════════════════════════════════════
#  PIN SCREEN
# ══════════════════════════════════════════════════════════════
class PinScreen(ctk.CTkToplevel):
    MAX_ATTEMPTS = 3
    LOCKOUT_SECS = 30

    def __init__(self, parent, cfg, on_success, T):
        super().__init__(parent)
        self.cfg        = cfg
        self.on_success = on_success
        self.T          = T
        self.attempts   = cfg.get("pin_attempts", 0)
        th = get_theme(cfg.get("theme","Green"))
        self.title("PurgeKit — Locked")
        self.geometry("340x360")
        self.resizable(False, False)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
        self.configure(fg_color=th["bg_darkest"])
        self._th = th
        self._build(th)

    def _build(self, th):
        try:
            acc = tuple(int(th["accent"].lstrip("#")[i:i+2],16) for i in (0,2,4))
            li  = generate_icon(acc)
            lc  = ctk.CTkImage(light_image=li, dark_image=li, size=(56,56))
            ctk.CTkLabel(self, image=lc, text="").pack(pady=(24,4))
        except Exception:
            pass
        ctk.CTkLabel(self, text="PurgeKit",
                     font=ctk.CTkFont("Segoe UI",20,"bold"),
                     text_color=th["accent"]).pack()
        ctk.CTkLabel(self, text=t(self.T,"pin_enter"),
                     font=ctk.CTkFont("Segoe UI",13),
                     text_color=th["text_gray"]).pack(pady=(4,16))
        self.pin_var   = tk.StringVar()
        self.pin_entry = ctk.CTkEntry(self, textvariable=self.pin_var,
                                       show="●", width=200, height=44,
                                       font=ctk.CTkFont("Segoe UI",18),
                                       fg_color=th["bg_card"],
                                       text_color=th["text_white"],
                                       border_color=th["accent_dark"],
                                       justify="center")
        self.pin_entry.pack(pady=(0,4))
        self.pin_entry.bind("<Return>", lambda e: self._check())
        self.pin_entry.focus()
        self.msg_lbl = ctk.CTkLabel(self, text="",
                                     font=ctk.CTkFont("Segoe UI",11),
                                     text_color=th["error"])
        self.msg_lbl.pack(pady=(0,12))
        ctk.CTkButton(self, text=t(self.T,"pin_unlock"),
                      font=ctk.CTkFont("Segoe UI",13,"bold"),
                      height=38, corner_radius=8,
                      fg_color=th["accent_dark"], hover_color=th["accent_hover"],
                      text_color=th["accent"],
                      command=self._check).pack(padx=40, fill="x")

    def _check(self):
        pin = self.pin_var.get().strip()
        if verify_pin(pin, self.cfg.get("pin_hash","")):
            self.cfg["pin_attempts"] = 0
            save_config(self.cfg)
            self.destroy()
            self.on_success()
        else:
            self.attempts += 1
            self.cfg["pin_attempts"] = self.attempts
            save_config(self.cfg)
            self.pin_var.set("")
            remaining = self.MAX_ATTEMPTS - self.attempts
            if remaining <= 0:
                self.msg_lbl.configure(text=t(self.T,"pin_locked",seconds=self.LOCKOUT_SECS))
                self.pin_entry.configure(state="disabled")
                self.after(self.LOCKOUT_SECS*1000, self._reset_lockout)
            else:
                self.msg_lbl.configure(text=t(self.T,"pin_wrong",remaining=remaining))

    def _reset_lockout(self):
        self.attempts = 0
        self.cfg["pin_attempts"] = 0
        save_config(self.cfg)
        self.pin_entry.configure(state="normal")
        self.msg_lbl.configure(text="")
        self.pin_entry.focus()

# ══════════════════════════════════════════════════════════════
#  FIRST RUN WIZARD
# ══════════════════════════════════════════════════════════════
class FirstRunWizard(ctk.CTkToplevel):
    def __init__(self, parent, cfg, on_done):
        super().__init__(parent)
        self.cfg     = cfg
        self.on_done = on_done
        th = get_theme(cfg.get("theme","Green"))
        self.title("Welcome to PurgeKit")
        self.geometry("480x540")
        self.resizable(False, False)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._finish)
        self.configure(fg_color=th["bg_darkest"])
        self._th = th
        self._build_step0()

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    def _build_step0(self):
        self._clear()
        th = self._th
        try:
            acc = tuple(int(th["accent"].lstrip("#")[i:i+2],16) for i in (0,2,4))
            li  = generate_icon(acc)
            lc  = ctk.CTkImage(light_image=li, dark_image=li, size=(80,80))
            ctk.CTkLabel(self, image=lc, text="").pack(pady=(28,8))
        except Exception:
            pass
        ctk.CTkLabel(self, text="Welcome to PurgeKit",
                     font=ctk.CTkFont("Segoe UI",22,"bold"),
                     text_color=th["accent"]).pack()
        ctk.CTkLabel(self, text=f"v{APP_VERSION}  —  Windows Temp & Cache Cleaner",
                     font=ctk.CTkFont("Segoe UI",12),
                     text_color=th["text_gray"]).pack(pady=(2,12))
        ctk.CTkLabel(self,
                     text=(f"Built by {AUTHOR_NAME}\n"
                           f"{AUTHOR_LOC}  ({AUTHOR_BRAND})\n\n"
                           "Let's set up PurgeKit in 3 quick steps."),
                     font=ctk.CTkFont("Segoe UI",12),
                     text_color=th["text_white"], justify="center").pack(pady=(0,24))
        ctk.CTkButton(self, text="Next →",
                      font=ctk.CTkFont("Segoe UI",13,"bold"),
                      height=40, corner_radius=8,
                      fg_color=th["accent_dark"], hover_color=th["accent_hover"],
                      text_color=th["accent"],
                      command=self._build_step1).pack(padx=60, fill="x")

    def _build_step1(self):
        self._clear()
        th = self._th
        ctk.CTkLabel(self, text="Step 1 of 3 — Choose Language",
                     font=ctk.CTkFont("Segoe UI",16,"bold"),
                     text_color=th["accent"]).pack(pady=(28,12))
        self._lang_var = tk.StringVar(value=self.cfg.get("language","en"))
        scroll = ctk.CTkScrollableFrame(self, fg_color=th["bg_card"], corner_radius=8, height=320)
        scroll.pack(fill="x", padx=24, pady=(0,12))
        for code, name in LANGUAGES.items():
            ctk.CTkRadioButton(scroll, text=name, variable=self._lang_var, value=code,
                               font=ctk.CTkFont("Segoe UI",11),
                               text_color=th["text_white"],
                               fg_color=th["accent_dark"], hover_color=th["accent_dark"],
                               border_color=th["text_dim"]).pack(anchor="w", padx=12, pady=4)
        ctk.CTkButton(self, text="Next →",
                      font=ctk.CTkFont("Segoe UI",13,"bold"),
                      height=40, corner_radius=8,
                      fg_color=th["accent_dark"], hover_color=th["accent_hover"],
                      text_color=th["accent"],
                      command=self._save_step1).pack(padx=60, fill="x")

    def _save_step1(self):
        self.cfg["language"] = self._lang_var.get()
        self._build_step2()

    def _build_step2(self):
        self._clear()
        th = self._th
        ctk.CTkLabel(self, text="Step 2 of 3 — Choose Theme",
                     font=ctk.CTkFont("Segoe UI",16,"bold"),
                     text_color=th["accent"]).pack(pady=(28,16))
        self._theme_var = tk.StringVar(value=self.cfg.get("theme","Green"))
        for tname, color in [("Green","#00e676"),("Blue","#40c4ff"),("Purple","#ea80fc")]:
            row = ctk.CTkFrame(self, fg_color=th["bg_card"], corner_radius=8)
            row.pack(fill="x", padx=24, pady=6)
            ctk.CTkRadioButton(row, text=tname, variable=self._theme_var, value=tname,
                               font=ctk.CTkFont("Segoe UI",13,"bold"),
                               text_color=color,
                               fg_color=th["accent_dark"], hover_color=th["accent_dark"],
                               border_color=th["text_dim"]).pack(side="left", padx=14, pady=14)
            ctk.CTkLabel(row, text="●"*10, font=ctk.CTkFont("Segoe UI",14),
                         text_color=color).pack(side="right", padx=14)
        ctk.CTkFrame(self, fg_color="transparent", height=16).pack()
        ctk.CTkButton(self, text="Next →",
                      font=ctk.CTkFont("Segoe UI",13,"bold"),
                      height=40, corner_radius=8,
                      fg_color=th["accent_dark"], hover_color=th["accent_hover"],
                      text_color=th["accent"],
                      command=self._save_step2).pack(padx=60, fill="x")

    def _save_step2(self):
        self.cfg["theme"] = self._theme_var.get()
        self._build_step3()

    def _build_step3(self):
        self._clear()
        th = get_theme(self.cfg.get("theme","Green"))
        T  = load_lang(self.cfg.get("language","en"))
        self.configure(fg_color=th["bg_darkest"])
        ctk.CTkLabel(self, text="Step 3 of 3 — Quick Options",
                     font=ctk.CTkFont("Segoe UI",16,"bold"),
                     text_color=th["accent"]).pack(pady=(28,16))
        self._autostart_var = tk.BooleanVar(value=False)
        self._dryrun_var    = tk.BooleanVar(value=False)
        for var, label, note in [
            (self._autostart_var, t(T,"settings_autostart"), t(T,"settings_autostart_note")),
            (self._dryrun_var,    t(T,"settings_dry_run"),   "Preview what will be deleted before purging."),
        ]:
            row = ctk.CTkFrame(self, fg_color=th["bg_card"], corner_radius=8)
            row.pack(fill="x", padx=24, pady=6)
            ctk.CTkCheckBox(row, text=label, variable=var,
                            font=ctk.CTkFont("Segoe UI",12),
                            text_color=th["text_white"],
                            fg_color=th["accent_dark"], hover_color=th["accent_dark"],
                            checkmark_color=th["accent"],
                            border_color=th["text_dim"]).pack(anchor="w", padx=14, pady=(10,2))
            ctk.CTkLabel(row, text=f"  {note}",
                         font=ctk.CTkFont("Segoe UI",10),
                         text_color=th["text_gray"], anchor="w").pack(fill="x", padx=14, pady=(0,10))
        ctk.CTkFrame(self, fg_color="transparent", height=16).pack()
        ctk.CTkButton(self, text="✅  Finish Setup",
                      font=ctk.CTkFont("Segoe UI",13,"bold"),
                      height=40, corner_radius=8,
                      fg_color=th["accent_dark"], hover_color=th["accent_hover"],
                      text_color=th["accent"],
                      command=self._finish).pack(padx=60, fill="x")

    def _finish(self):
        try:
            self.cfg["autostart"] = self._autostart_var.get()
            self.cfg["dry_run"]   = self._dryrun_var.get()
            if self._autostart_var.get():
                set_autostart(True)
        except Exception:
            pass
        self.cfg["first_run"] = False
        save_config(self.cfg)
        self.destroy()
        self.on_done()

# ══════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════
class PurgeKitApp(ctk.CTk):

    COMPACT_W,  COMPACT_H  = 780, 740
    SPACIOUS_W, SPACIOUS_H = 1120, 860

    # Sidebar nav items: (key, icon, builder_method)
    NAV_ITEMS = [
        ("tab_tasks",   "🧹", "_panel_tasks"),
        ("tab_log",     "📄", "_panel_log"),
        ("tab_scan",    "🔍", "_panel_scan"),
        ("tab_settings","⚙",  "_panel_settings"),
        ("tab_about",   "ℹ",  "_panel_about"),
    ]

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.cfg       = load_config()
        self.history   = load_history()
        self.whitelist = load_whitelist()
        self.T         = load_lang(self.cfg.get("language","en"))
        self.th        = get_theme(self.cfg.get("theme","Green"))

        self.compact_mode  = tk.BooleanVar(value=self.cfg.get("compact_mode",True))
        self.task_vars     = {}
        self.drive_vars    = {}
        self.activity_var  = tk.StringVar(value=self.cfg.get("activity_choice","skip"))
        self.dry_run_var   = tk.BooleanVar(value=self.cfg.get("dry_run",False))
        self.autostart_var = tk.BooleanVar(value=get_autostart())
        self.running       = False
        self.reboot_needed = [False]
        self.log_lines     = []
        self._active_nav   = t(self.T,"tab_tasks")
        self._nav_btns     = {}
        self._scan_results = []
        self._scan_check_vars = {}

        self.title(f"PurgeKit v{APP_VERSION}  —  {AUTHOR_BRAND}")
        self.configure(fg_color=self.th["bg_darkest"])
        self.resizable(True, True)
        self.minsize(720, 580)

        # ── Taskbar/pinned icon ───────────────────────────────
        self._apply_icon()

        self._set_window_size()
        self._center_window()

        if self.cfg.get("first_run", True):
            self.withdraw()
            self.after(100, self._show_wizard)
        elif self.cfg.get("pin_enabled", False):
            self.withdraw()
            self.after(100, self._show_pin)
        else:
            self._init_ui()
            self._check_update()

    def _apply_icon(self):
        """Apply icon to window AND register with Windows for taskbar pinning."""
        try:
            th  = self.th
            acc = tuple(int(th["accent"].lstrip("#")[i:i+2],16) for i in (0,2,4))

            # Save icon to AppData so it persists for taskbar pinning
            app_dir  = os.path.join(os.environ.get("APPDATA",""), "PurgeKit")
            os.makedirs(app_dir, exist_ok=True)
            ico_path = os.path.join(app_dir, "purgekit.ico")

            img = generate_icon(acc)
            img.save(ico_path, format="ICO",
                     sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])

            if os.path.exists(ico_path):
                self.iconbitmap(default=ico_path)

            # Register App User Model ID so Windows taskbar uses our icon
            app_id = "TeamExyKings.PurgeKit"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        except Exception:
            pass

    def _set_window_size(self):
        w = self.COMPACT_W  if self.compact_mode.get() else self.SPACIOUS_W
        h = self.COMPACT_H  if self.compact_mode.get() else self.SPACIOUS_H
        self.geometry(f"{w}x{h}")

    def _center_window(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w  = self.COMPACT_W if self.compact_mode.get() else self.SPACIOUS_W
        h  = self.COMPACT_H if self.compact_mode.get() else self.SPACIOUS_H
        self.geometry(f"+{(sw-w)//2}+{(sh-h)//2}")

    def _show_wizard(self):
        FirstRunWizard(self, self.cfg, self._after_wizard).lift()

    def _after_wizard(self):
        self.cfg = load_config()
        self._reload_theme_lang()
        self.deiconify()
        self._init_ui()
        self._check_update()

    def _show_pin(self):
        PinScreen(self, self.cfg, self._after_pin, self.T)

    def _after_pin(self):
        self.deiconify()
        self._init_ui()
        self._check_update()

    def _reload_theme_lang(self):
        """Apply new theme/lang without restarting — rebuilds entire UI."""
        self.cfg = load_config()
        self.T   = load_lang(self.cfg.get("language","en"))
        self.th  = get_theme(self.cfg.get("theme","Green"))
        self.configure(fg_color=self.th["bg_darkest"])
        self._apply_icon()
        self._active_nav = t(self.T,"tab_tasks")
        self._init_ui()

    def _init_ui(self):
        for w in self.winfo_children():
            w.destroy()
        self._build_topbar()
        self.main_frame = ctk.CTkFrame(self, fg_color=self.th["bg_darkest"], corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)
        self._build_content()

    # ── Top bar ──────────────────────────────────────────────
    def _build_topbar(self):
        th  = self.th
        top = ctk.CTkFrame(self, fg_color=th["bg_dark"], height=54, corner_radius=0)
        top.pack(fill="x")
        top.pack_propagate(False)

        lf = ctk.CTkFrame(top, fg_color="transparent")
        lf.pack(side="left", padx=14, pady=8)
        try:
            acc = tuple(int(th["accent"].lstrip("#")[i:i+2],16) for i in (0,2,4))
            li  = generate_icon(acc)
            lc  = ctk.CTkImage(light_image=li, dark_image=li, size=(30,30))
            ctk.CTkLabel(lf, image=lc, text="").pack(side="left", padx=(0,8))
        except Exception:
            pass
        ctk.CTkLabel(lf, text="PurgeKit",
                     font=ctk.CTkFont("Segoe UI",20,"bold"),
                     text_color=th["accent"]).pack(side="left")
        ctk.CTkLabel(lf, text=f" v{APP_VERSION}",
                     font=ctk.CTkFont("Segoe UI",12),
                     text_color=th["text_gray"]).pack(side="left")

        rf = ctk.CTkFrame(top, fg_color="transparent")
        rf.pack(side="right", padx=14, pady=8)

        # Dry run indicator
        self.dryrun_lbl = ctk.CTkLabel(rf,
                                        text="🔍 DRY RUN ON" if self.dry_run_var.get() else "",
                                        font=ctk.CTkFont("Segoe UI",10,"bold"),
                                        text_color=th["warn"])
        self.dryrun_lbl.pack(side="left", padx=(0,8))

        ctk.CTkLabel(rf, text="Dry Run",
                     font=ctk.CTkFont("Segoe UI",10),
                     text_color=th["text_gray"]).pack(side="left", padx=(0,2))
        ctk.CTkSwitch(rf, text="", variable=self.dry_run_var,
                      command=self._on_dryrun_toggle,
                      width=40, height=20,
                      button_color=th["warn"], button_hover_color=th["warn"],
                      progress_color="#3a2000").pack(side="left", padx=(0,14))

        ctk.CTkLabel(rf, text=t(self.T,"compact_mode"),
                     font=ctk.CTkFont("Segoe UI",11),
                     text_color=th["text_gray"]).pack(side="left", padx=(0,4))
        ctk.CTkSwitch(rf, text="", variable=self.compact_mode,
                      command=self._toggle_compact,
                      width=44, height=22,
                      button_color=th["accent"], button_hover_color=th["accent_dim"],
                      progress_color=th["accent_dark"]).pack(side="left")

    def _on_dryrun_toggle(self):
        on = self.dry_run_var.get()
        try:
            self.dryrun_lbl.configure(text="🔍 DRY RUN ON" if on else "")
            if hasattr(self, "start_btn"):
                T  = self.T
                th = self.th
                if on:
                    self.start_btn.configure(text=t(T,"dry_run"),
                                              fg_color="#3a2000",
                                              text_color=th["warn"])
                else:
                    self.start_btn.configure(text=t(T,"start_purge"),
                                              fg_color=th["accent_dark"],
                                              text_color=th["accent"])
        except Exception:
            pass
        # Refresh sizes — dry run doesn't change sizes but updates total label color
        self.after(100, self._refresh_task_sizes)

    # ── Layout ───────────────────────────────────────────────
    def _build_content(self):
        for w in self.main_frame.winfo_children():
            w.destroy()
        if self.compact_mode.get():
            self._build_compact()
        else:
            self._build_spacious()

    # ── SPACIOUS: Sidebar + content area ─────────────────────
    def _build_spacious(self):
        th = self.th

        # Sidebar
        sidebar = ctk.CTkFrame(self.main_frame, fg_color=th["bg_dark"],
                               width=180, corner_radius=0)
        sidebar.pack(side="left", fill="y", padx=(0,1))
        sidebar.pack_propagate(False)

        ctk.CTkFrame(sidebar, fg_color="transparent", height=12).pack()

        self._nav_btns = {}
        for key, icon, method in self.NAV_ITEMS:
            label = f"  {icon}  {t(self.T, key)}"
            is_active = t(self.T, key) == self._active_nav
            btn = ctk.CTkButton(
                sidebar,
                text=label,
                font=ctk.CTkFont("Segoe UI", 12, "bold" if is_active else "normal"),
                height=40,
                corner_radius=8,
                anchor="w",
                fg_color=th["accent_dark"] if is_active else "transparent",
                hover_color=th["bg_hover"],
                text_color=th["accent"] if is_active else th["text_gray"],
                command=lambda k=key, m=method: self._nav_click_spacious(k, m)
            )
            btn.pack(fill="x", padx=8, pady=3)
            self._nav_btns[key] = btn

        # Content area
        self.content_area = ctk.CTkFrame(self.main_frame,
                                          fg_color=th["bg_darkest"], corner_radius=0)
        self.content_area.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        # Right log panel (always visible in spacious)
        right = ctk.CTkFrame(self.main_frame, fg_color=th["bg_dark"],
                              corner_radius=10, width=300)
        right.pack(side="right", fill="both", padx=(0,8), pady=8)
        right.pack_propagate(False)
        self._build_log_panel(right)

        self._show_spacious_panel(self._active_nav)

    def _nav_click_spacious(self, key, method):
        th = self.th
        self._active_nav = t(self.T, key)
        # Update button styles
        for k, btn in self._nav_btns.items():
            is_active = k == key
            btn.configure(
                fg_color=th["accent_dark"] if is_active else "transparent",
                text_color=th["accent"] if is_active else th["text_gray"],
                font=ctk.CTkFont("Segoe UI", 12, "bold" if is_active else "normal")
            )
        self._show_spacious_panel(t(self.T, key))

    def _show_spacious_panel(self, nav_label):
        for w in self.content_area.winfo_children():
            w.destroy()
        mapping = {
            t(self.T, "tab_tasks"):   self._panel_tasks,
            t(self.T, "tab_scan"):    self._panel_scan,
            t(self.T, "tab_settings"):self._panel_settings,
            t(self.T, "tab_about"):   self._panel_about,
        }
        builder = mapping.get(nav_label)
        if builder:
            builder(self.content_area)

    # ── COMPACT: CTkTabview with proper spacing ───────────────
    def _build_compact(self):
        th = self.th
        T  = self.T

        tabs = ctk.CTkTabview(
            self.main_frame,
            fg_color=th["bg_dark"],
            segmented_button_fg_color=th["bg_card"],
            segmented_button_selected_color=th["accent_dark"],
            segmented_button_selected_hover_color=th["accent_hover"],
            segmented_button_unselected_color=th["bg_card"],
            segmented_button_unselected_hover_color=th["bg_hover"],
            text_color=th["text_white"],
            text_color_disabled=th["text_dim"],
            border_color=th["text_dim"],
            border_width=1,
        )
        try:
            tabs._segmented_button.configure(font=ctk.CTkFont("Segoe UI", 11))
        except Exception:
            pass
        tabs.pack(fill="both", expand=True, padx=8, pady=8)

        tab_defs = [
            (t(T,"tab_tasks"),   self._panel_tasks),
            (t(T,"tab_log"),     self._panel_log),
            (t(T,"tab_scan"),    self._panel_scan),
            (t(T,"tab_settings"),self._panel_settings),
            (t(T,"tab_about"),   self._panel_about),
        ]
        for name, builder in tab_defs:
            tabs.add(name)

        for name, builder in tab_defs:
            tab = tabs.tab(name)
            # Add consistent inner padding
            inner = ctk.CTkFrame(tab, fg_color=th["bg_darkest"], corner_radius=0)
            inner.pack(fill="both", expand=True, padx=4, pady=4)
            builder(inner)

    # ══════════════════════════════════════════════════════════
    #  PANEL BUILDERS
    # ══════════════════════════════════════════════════════════

    # ── Background size scanner ──────────────────────────────
    def _compute_task_sizes(self, task_vars, callback):
        """Background scan of ALL task paths. Updates sizes live.
        total only counts checked tasks so dry run + select all shows correct total."""
        def _scan():
            sizes = {}
            total = 0
            for task in TASKS:
                tid    = task[0]
                path   = task[3]
                do_exp = task[4]
                rp     = ep(path) if do_exp else path
                sz     = 0
                try:
                    if os.path.exists(rp):
                        sz = folder_size(rp)
                except Exception:
                    pass
                sizes[tid] = sz
                # Only add to total if task is checked
                try:
                    if task_vars.get(tid) and task_vars[tid].get():
                        total += sz
                except Exception:
                    pass
                try:
                    self.after(0, lambda s=dict(sizes), tot=total: callback(s, tot, False))
                except Exception:
                    pass
            try:
                self.after(0, lambda: callback(dict(sizes), total, True))
            except Exception:
                pass
        threading.Thread(target=_scan, daemon=True).start()

    def _refresh_task_sizes(self):
        """Re-trigger size scan — call after select all / deselect all / dry run toggle."""
        try:
            th = self.th
            def _size_callback(sizes, total, done):
                try:
                    self.total_size_lbl.configure(
                        text=f"  💾  Total selected size: {fmt_size(total)}",
                        text_color=th["accent"] if done else th["text_gray"])
                    self.size_scan_lbl.configure(text="✅" if done else "⏳")
                    for tid, lbl in self._row_size_labels.items():
                        sz = sizes.get(tid, None)
                        if sz is not None:
                            var = self.task_vars.get(tid)
                            checked = var.get() if var else False
                            lbl.configure(
                                text=fmt_size(sz) if sz > 0 else "—",
                                text_color=th["accent"] if (sz > 0 and checked) else th["text_dim"])
                except Exception:
                    pass
            self.total_size_lbl.configure(
                text="  💾  Total selected size: scanning...",
                text_color=th["text_gray"])
            self._compute_task_sizes(self.task_vars, _size_callback)
        except Exception:
            pass

    # ── Tasks Panel ──────────────────────────────────────────
    def _panel_tasks(self, parent):
        th = self.th
        T  = self.T

        br = ctk.CTkFrame(parent, fg_color="transparent")
        br.pack(fill="x", pady=(4,6), padx=4)
        ctk.CTkButton(br, text=t(T,"select_all"), width=130, height=30,
                      fg_color=th["accent_dark"], hover_color=th["accent_hover"],
                      text_color=th["accent"],
                      font=ctk.CTkFont("Segoe UI",12), corner_radius=6,
                      command=self._select_all).pack(side="left", padx=(0,8))
        ctk.CTkButton(br, text=t(T,"deselect_all"), width=130, height=30,
                      fg_color=th["bg_card"], hover_color=th["bg_hover"],
                      text_color=th["text_gray"],
                      font=ctk.CTkFont("Segoe UI",12), corner_radius=6,
                      command=self._deselect_all).pack(side="left")

        # Total size row
        size_row = ctk.CTkFrame(parent, fg_color=th["bg_card"], corner_radius=6)
        size_row.pack(fill="x", padx=4, pady=(0,6))
        self.total_size_lbl = ctk.CTkLabel(size_row,
                                            text="  💾  Total selected size: scanning...",
                                            font=ctk.CTkFont("Segoe UI",11),
                                            text_color=th["text_gray"], anchor="w")
        self.total_size_lbl.pack(side="left", padx=8, pady=6)
        self.size_scan_lbl = ctk.CTkLabel(size_row, text="",
                                           font=ctk.CTkFont("Segoe UI",10),
                                           text_color=th["text_dim"])
        self.size_scan_lbl.pack(side="right", padx=8)
        self._row_size_labels = {}

        scroll = ctk.CTkScrollableFrame(parent, fg_color=th["bg_darkest"], corner_radius=8,
                                        scrollbar_button_color=th["accent_dark"],
                                        scrollbar_button_hover_color=th["accent"])
        scroll.pack(fill="both", expand=True, padx=2)

        last_tasks = self.cfg.get("last_tasks", {})
        phase_meta = {
            "System":    (th["phase_system"],  "⚙",  th["accent"], t(T,"phase_system")),
            "User":      (th["phase_user"],    "👤", th["accent"], t(T,"phase_user")),
            "Browser":   (th["phase_browser"], "🌐", th["accent"], t(T,"phase_browser")),
            "Developer": (th["phase_dev"],     "💻", th["accent"], t(T,"phase_developer")),
            "Optional":  (th["phase_opt"],     "⚠",  th["warn"],   t(T,"phase_optional")),
        }
        phases = {}
        for task in TASKS:
            phases.setdefault(task[1], []).append(task)

        for phase, tasks in phases.items():
            bg, icon, hdr_c, title = phase_meta.get(phase,(th["bg_card"],"•",th["accent"],phase))
            ph_f = ctk.CTkFrame(scroll, fg_color=bg, corner_radius=8)
            ph_f.pack(fill="x", pady=(8,2), padx=2)
            ctk.CTkLabel(ph_f, text=f"  {icon}  {title}",
                         font=ctk.CTkFont("Segoe UI",12,"bold"),
                         text_color=hdr_c, anchor="w").pack(fill="x", padx=12, pady=(6,4))

            for task in tasks:
                tid, ph, label, path, expand, default, warning = task
                saved   = last_tasks.get(tid)
                is_wl   = any(path in w or (expand and ep(path) in w) for w in self.whitelist)
                checked = (saved if saved is not None else default) and not is_wl
                var = tk.BooleanVar(value=checked)
                self.task_vars[tid] = var

                row = ctk.CTkFrame(scroll, fg_color=th["bg_card"], corner_radius=6)
                row.pack(fill="x", pady=2, padx=2)
                ctk.CTkCheckBox(row, text=label, variable=var,
                                font=ctk.CTkFont("Segoe UI",12),
                                text_color=th["text_dim"] if is_wl else th["text_white"],
                                fg_color=th["accent_dark"], hover_color=th["accent_dark"],
                                checkmark_color=th["accent"], border_color=th["text_dim"],
                                width=20, height=20).pack(side="left", padx=(10,6), pady=6)
                if is_wl:
                    ctk.CTkLabel(row, text="🚫",
                                 font=ctk.CTkFont("Segoe UI",10),
                                 text_color=th["text_dim"]).pack(side="left")
                if warning:
                    ctk.CTkLabel(row, text="⚠",
                                 font=ctk.CTkFont("Segoe UI",12),
                                 text_color=th["warn"]).pack(side="left", padx=(0,4))
                # Size label per row (updated after background scan)
                size_lbl = ctk.CTkLabel(row, text="—",
                                        font=ctk.CTkFont("Segoe UI",10,"bold"),
                                        text_color=th["accent"])
                size_lbl.pack(side="right", padx=(0,6))
                self._row_size_labels[tid] = size_lbl

                ctk.CTkLabel(row, text=path,
                             font=ctk.CTkFont("Segoe UI",10),
                             text_color=th["text_gray"]).pack(side="right", padx=(0,6))
                if warning:
                    wr = ctk.CTkFrame(scroll, fg_color="#110a00", corner_radius=4)
                    wr.pack(fill="x", padx=12, pady=(0,2))
                    ctk.CTkLabel(wr, text=f"  {warning}",
                                 font=ctk.CTkFont("Segoe UI",10),
                                 text_color=th["warn"], anchor="w").pack(fill="x", padx=8, pady=3)

        # Disk cleanup
        dc_f = ctk.CTkFrame(scroll, fg_color=th["phase_dc"], corner_radius=8)
        dc_f.pack(fill="x", pady=(10,2), padx=2)
        ctk.CTkLabel(dc_f, text=f"  🗑  {t(T,'phase_disk')}",
                     font=ctk.CTkFont("Segoe UI",12,"bold"),
                     text_color=th["accent"], anchor="w").pack(fill="x", padx=12, pady=(8,4))
        last_drives = self.cfg.get("last_drives",[])
        self.drive_vars = {}
        for drive_path, label, free, total in get_drives():
            var = tk.BooleanVar(value=(drive_path in last_drives) if last_drives else True)
            self.drive_vars[drive_path] = var
            row = ctk.CTkFrame(dc_f, fg_color=th["bg_card"], corner_radius=6)
            row.pack(fill="x", pady=2, padx=8)
            name = f"{drive_path}  {label}" if label else drive_path
            sz   = f"{fmt_size(free)} free / {fmt_size(total)}" if total>0 else ""
            ctk.CTkCheckBox(row, text=name, variable=var,
                            font=ctk.CTkFont("Segoe UI",12), text_color=th["text_white"],
                            fg_color=th["accent_dark"], hover_color=th["accent_dark"],
                            checkmark_color=th["accent"], border_color=th["text_dim"],
                            width=20, height=20).pack(side="left", padx=(10,6), pady=6)
            if sz:
                ctk.CTkLabel(row, text=sz, font=ctk.CTkFont("Segoe UI",10),
                             text_color=th["text_gray"]).pack(side="right", padx=(0,10))
        ctk.CTkFrame(dc_f, fg_color="transparent", height=6).pack()

        # Activity History
        ah_f = ctk.CTkFrame(scroll, fg_color=th["bg_card"], corner_radius=8)
        ah_f.pack(fill="x", pady=(10,2), padx=2)
        ctk.CTkLabel(ah_f, text=t(T,"activity_history"),
                     font=ctk.CTkFont("Segoe UI",12,"bold"),
                     text_color=th["warn"], anchor="w").pack(fill="x", padx=12, pady=(8,2))
        ctk.CTkLabel(ah_f, text=f"  {t(T,'activity_desc')}",
                     font=ctk.CTkFont("Segoe UI",10),
                     text_color=th["text_gray"], anchor="w").pack(fill="x", padx=12, pady=(0,6))
        for val, key in [("delete","activity_delete"),("disable","activity_disable"),("skip","activity_skip")]:
            ctk.CTkRadioButton(ah_f, text=t(T,key), variable=self.activity_var, value=val,
                               font=ctk.CTkFont("Segoe UI",11), text_color=th["text_white"],
                               fg_color=th["accent_dark"], hover_color=th["accent_dark"],
                               border_color=th["text_dim"]).pack(anchor="w", padx=20, pady=3)
        ctk.CTkFrame(ah_f, fg_color="transparent", height=8).pack()

        # Bottom bar
        bot = ctk.CTkFrame(parent, fg_color=th["bg_darkest"], corner_radius=0)
        bot.pack(fill="x", pady=(8,0), padx=4)
        self.progress_label = ctk.CTkLabel(bot, text=t(T,"ready"),
                                           font=ctk.CTkFont("Segoe UI",11),
                                           text_color=th["text_gray"], anchor="w")
        self.progress_label.pack(fill="x", pady=(0,4))
        self.progress_bar = ctk.CTkProgressBar(bot, height=10, fg_color=th["bg_card"],
                                               progress_color=th["accent"], corner_radius=5)
        self.progress_bar.pack(fill="x", pady=(0,8))
        self.progress_bar.set(0)

        # Trigger background size scan — slight delay so all widgets are ready
        def _size_callback(sizes, total, done):
            try:
                self.total_size_lbl.configure(
                    text=f"  💾  Total selected size: {fmt_size(total)}",
                    text_color=th["accent"] if done else th["text_gray"])
                self.size_scan_lbl.configure(text="✅" if done else "⏳")
                for tid, lbl in self._row_size_labels.items():
                    sz = sizes.get(tid, None)
                    if sz is not None:
                        var     = self.task_vars.get(tid)
                        checked = var.get() if var else False
                        lbl.configure(
                            text=fmt_size(sz) if sz > 0 else "—",
                            text_color=th["accent"] if (sz > 0 and checked) else th["text_dim"])
            except Exception:
                pass

        def _start_size_scan():
            self.total_size_lbl.configure(
                text="  💾  Total selected size: scanning...",
                text_color=th["text_gray"])
            self.size_scan_lbl.configure(text="⏳")
            self._compute_task_sizes(self.task_vars, _size_callback)

        self.after(300, _start_size_scan)

        btn_r = ctk.CTkFrame(bot, fg_color="transparent")
        btn_r.pack(fill="x")
        dry = self.dry_run_var.get()
        self.start_btn = ctk.CTkButton(
            btn_r,
            text=t(T,"dry_run") if dry else t(T,"start_purge"),
            font=ctk.CTkFont("Segoe UI",14,"bold"),
            height=42, corner_radius=8,
            fg_color="#3a2000" if dry else th["accent_dark"],
            hover_color=th["accent_hover"],
            text_color=th["warn"] if dry else th["accent"],
            command=self._start_purge)
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0,6))
        ctk.CTkButton(btn_r, text=t(T,"save_log"), height=42, width=80,
                      corner_radius=8, fg_color=th["bg_card"],
                      hover_color=th["bg_hover"], text_color=th["text_gray"],
                      font=ctk.CTkFont("Segoe UI",12),
                      command=self._save_log_manual).pack(side="left")

    # ── Log Panel ────────────────────────────────────────────
    def _panel_log(self, parent):
        self._build_log_panel(parent)

    def _build_log_panel(self, parent):
        th = self.th
        T  = self.T
        ctk.CTkLabel(parent, text=t(T,"tab_log"),
                     font=ctk.CTkFont("Segoe UI",13,"bold"),
                     text_color=th["accent"], anchor="w").pack(fill="x", padx=12, pady=(10,4))
        self.log_box = ctk.CTkTextbox(
            parent, fg_color=th["bg_darkest"], text_color=th["text_white"],
            font=ctk.CTkFont("Consolas",11), corner_radius=6,
            scrollbar_button_color=th["accent_dark"],
            scrollbar_button_hover_color=th["accent"],
            wrap="word", state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=8, pady=(0,8))
        for tag, color in [("success",th["success"]),("warn",th["warn"]),
                           ("error",th["error"]),("dim",th["text_gray"]),
                           ("accent",th["accent"]),("white",th["text_white"])]:
            self.log_box.tag_config(tag, foreground=color)
        self._log(f"PurgeKit v{APP_VERSION} ready.", "accent")
        self._log(t(T,"select_tasks"), "dim")

    # ── Scan Panel ───────────────────────────────────────────
    def _panel_scan(self, parent):
        th = self.th
        T  = self.T
        ctk.CTkLabel(parent, text=t(T,"scan_title"),
                     font=ctk.CTkFont("Segoe UI",14,"bold"),
                     text_color=th["accent"]).pack(pady=(12,2), padx=12, anchor="w")
        ctk.CTkLabel(parent, text=t(T,"scan_desc"),
                     font=ctk.CTkFont("Segoe UI",11),
                     text_color=th["text_gray"]).pack(padx=12, anchor="w", pady=(0,6))

        self.scan_progress_lbl = ctk.CTkLabel(parent, text="",
                                               font=ctk.CTkFont("Segoe UI",10),
                                               text_color=th["text_gray"])
        self.scan_progress_lbl.pack(padx=12, anchor="w")
        self.scan_progress_bar = ctk.CTkProgressBar(parent, height=8,
                                                     fg_color=th["bg_card"],
                                                     progress_color=th["accent"])
        self.scan_progress_bar.pack(fill="x", padx=12, pady=(2,6))
        self.scan_progress_bar.set(0)

        # Scan results scroll
        self.scan_scroll = ctk.CTkScrollableFrame(parent, fg_color=th["bg_darkest"],
                                                   corner_radius=8,
                                                   scrollbar_button_color=th["accent_dark"],
                                                   scrollbar_button_hover_color=th["accent"])
        self.scan_scroll.pack(fill="both", expand=True, padx=8, pady=(0,4))

        # Bottom button row
        btn_row = ctk.CTkFrame(parent, fg_color="transparent")
        btn_row.pack(fill="x", padx=12, pady=(4,4))
        ctk.CTkButton(btn_row, text=t(T,"scan_start"),
                      font=ctk.CTkFont("Segoe UI",13,"bold"),
                      height=38, corner_radius=8,
                      fg_color=th["accent_dark"], hover_color=th["accent_hover"],
                      text_color=th["accent"],
                      command=self._run_scan).pack(side="left", padx=(0,8))
        self.scan_clean_btn = ctk.CTkButton(btn_row, text="🧹  Clean Selected",
                                             font=ctk.CTkFont("Segoe UI",13,"bold"),
                                             height=38, corner_radius=8,
                                             fg_color="#1a1200", hover_color="#2a1e00",
                                             text_color=th["warn"],
                                             state="disabled",
                                             command=self._clean_scan_selected)
        self.scan_clean_btn.pack(side="left")

        # Clean progress bar (hidden until clean starts)
        self.scan_clean_progress_lbl = ctk.CTkLabel(parent, text="",
                                                     font=ctk.CTkFont("Segoe UI",10),
                                                     text_color=th["text_gray"])
        self.scan_clean_progress_lbl.pack(padx=12, anchor="w")
        self.scan_clean_bar = ctk.CTkProgressBar(parent, height=8,
                                                  fg_color=th["bg_card"],
                                                  progress_color=th["warn"],
                                                  corner_radius=5)
        self.scan_clean_bar.pack(fill="x", padx=12, pady=(2,8))
        self.scan_clean_bar.set(0)

    def _run_scan(self):
        th = self.th
        # Clear old results completely
        for w in self.scan_scroll.winfo_children():
            w.destroy()
        self._scan_check_vars = {}
        self._scan_results    = []
        self.scan_clean_btn.configure(state="disabled", text="🧹  Clean Selected")
        try:
            self.scan_clean_bar.set(0)
            self.scan_clean_progress_lbl.configure(text="")
        except Exception:
            pass

        def progress(pct, msg):
            try:
                self.after(0, lambda: (
                    self.scan_progress_bar.set(pct),
                    self.scan_progress_lbl.configure(text=msg)
                ))
            except Exception:
                pass

        def do_scan():
            results = scan_all(progress)
            self._scan_results = results
            total   = total_junk(results)

            def render():
                for w in self.scan_scroll.winfo_children():
                    w.destroy()

                # Total header
                hdr = ctk.CTkFrame(self.scan_scroll, fg_color=th["phase_dc"], corner_radius=8)
                hdr.pack(fill="x", pady=(0,6), padx=2)
                ctk.CTkLabel(hdr,
                             text=f"  Total junk found: {fmt_size(total)}  —  {len(results)} folders",
                             font=ctk.CTkFont("Segoe UI",13,"bold"),
                             text_color=th["accent"]).pack(side="left", padx=12, pady=8)

                # Select all / deselect for scan
                sr = ctk.CTkFrame(self.scan_scroll, fg_color="transparent")
                sr.pack(fill="x", padx=2, pady=(0,4))
                ctk.CTkButton(sr, text="✔ Select All", width=110, height=26,
                              fg_color=th["accent_dark"], hover_color=th["accent_hover"],
                              text_color=th["accent"],
                              font=ctk.CTkFont("Segoe UI",11), corner_radius=6,
                              command=lambda: [v.set(True) for v in self._scan_check_vars.values()]
                              ).pack(side="left", padx=(0,6))
                ctk.CTkButton(sr, text="✘ Deselect All", width=110, height=26,
                              fg_color=th["bg_card"], hover_color=th["bg_hover"],
                              text_color=th["text_gray"],
                              font=ctk.CTkFont("Segoe UI",11), corner_radius=6,
                              command=lambda: [v.set(False) for v in self._scan_check_vars.values()]
                              ).pack(side="left")

                for i, (label, path, size) in enumerate(results):
                    var = tk.BooleanVar(value=True)
                    self._scan_check_vars[path] = var

                    row = ctk.CTkFrame(self.scan_scroll, fg_color=th["bg_card"], corner_radius=6)
                    row.pack(fill="x", pady=2, padx=2)

                    ctk.CTkCheckBox(row, text="", variable=var,
                                    fg_color=th["accent_dark"], hover_color=th["accent_dark"],
                                    checkmark_color=th["accent"], border_color=th["text_dim"],
                                    width=20, height=20).pack(side="left", padx=(8,4), pady=8)

                    info = ctk.CTkFrame(row, fg_color="transparent")
                    info.pack(side="left", fill="x", expand=True, padx=(0,8), pady=6)
                    ctk.CTkLabel(info, text=f"#{i+1}  {label}",
                                 font=ctk.CTkFont("Segoe UI",12,"bold"),
                                 text_color=th["text_white"], anchor="w").pack(fill="x")
                    ctk.CTkLabel(info, text=path,
                                 font=ctk.CTkFont("Segoe UI",9),
                                 text_color=th["text_dim"], anchor="w").pack(fill="x")

                    ctk.CTkLabel(row, text=fmt_size(size),
                                 font=ctk.CTkFont("Segoe UI",12,"bold"),
                                 text_color=th["accent"]).pack(side="right", padx=12)

                self.scan_clean_btn.configure(state="normal")
            self.after(0, render)

        threading.Thread(target=do_scan, daemon=True).start()

    def _clean_scan_selected(self):
        selected_paths = [p for p, v in self._scan_check_vars.items() if v.get()]
        if not selected_paths:
            messagebox.showwarning("Nothing Selected", "Select at least one item to clean.")
            return
        confirm = messagebox.askyesno(
            "Confirm Clean",
            f"Delete {len(selected_paths)} selected folder(s) from scan results?\n\nThis cannot be undone."
        )
        if not confirm:
            return
        reboot = [False]
        total_count = len(selected_paths)

        def set_scan_clean_progress(pct, msg):
            try:
                self.after(0, lambda: (
                    self.scan_clean_bar.set(pct),
                    self.scan_clean_progress_lbl.configure(text=msg)
                ))
            except Exception:
                pass

        def do_clean():
            total_freed = 0
            self.after(0, lambda: self.scan_clean_btn.configure(
                state="disabled", text="⏳  Cleaning..."))
            for i, path in enumerate(selected_paths):
                pct = i / max(total_count, 1)
                set_scan_clean_progress(pct, f"[{i+1}/{total_count}] Cleaning: {os.path.basename(path)}...")
                self._log(f"\n── Scan Clean: {path}", "accent")
                if os.path.exists(path):
                    freed = folder_size(path)
                    from core.cleaner import force_delete
                    force_delete(path, self._log, reboot, self.dry_run_var.get())
                    recreate(path)
                    total_freed += freed
            set_scan_clean_progress(1.0, f"✅ Done — freed {fmt_size(total_freed)}")
            self._log(f"\n✅ Scan clean complete. Freed: {fmt_size(total_freed)}", "success")
            self.after(0, lambda: self.scan_clean_btn.configure(
                state="normal", text="🧹  Clean Selected"))
        threading.Thread(target=do_clean, daemon=True).start()

    # ── History Panel ────────────────────────────────────────
    def _panel_history(self, parent):
        th = self.th
        T  = self.T
        ctk.CTkLabel(parent, text=t(T,"history_title"),
                     font=ctk.CTkFont("Segoe UI",14,"bold"),
                     text_color=th["accent"]).pack(pady=(12,8), padx=12, anchor="w")

        if not self.history:
            ctk.CTkLabel(parent, text=t(T,"history_no_data"),
                         font=ctk.CTkFont("Segoe UI",12),
                         text_color=th["text_gray"]).pack(pady=40)
            return

        total_freed = sum(r.get("freed_bytes",0) for r in self.history)
        summary = ctk.CTkFrame(parent, fg_color=th["bg_card"], corner_radius=8)
        summary.pack(fill="x", padx=12, pady=(0,8))
        for lbl, val in [(t(T,"history_runs"), str(len(self.history))),
                         (t(T,"history_total"), fmt_size(total_freed))]:
            r = ctk.CTkFrame(summary, fg_color="transparent")
            r.pack(side="left", expand=True, pady=10)
            ctk.CTkLabel(r, text=val, font=ctk.CTkFont("Segoe UI",18,"bold"),
                         text_color=th["accent"]).pack()
            ctk.CTkLabel(r, text=lbl, font=ctk.CTkFont("Segoe UI",10),
                         text_color=th["text_gray"]).pack()

        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            recent = self.history[-12:]
            labels = [r.get("date","")[-5:] for r in recent]
            values = [r.get("freed_bytes",0)/(1<<20) for r in recent]
            fig, ax = plt.subplots(figsize=(5,2.2))
            fig.patch.set_facecolor(th["bg_darkest"])
            ax.set_facecolor(th["bg_card"])
            ax.bar(labels, values, color=th["accent"], width=0.6)
            ax.tick_params(colors=th["text_gray"], labelsize=7)
            ax.spines[:].set_color(th["text_dim"])
            ax.set_ylabel("MB freed", color=th["text_gray"], fontsize=8)
            plt.xticks(rotation=30, ha="right")
            plt.tight_layout(pad=0.4)
            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="x", padx=12, pady=(0,6))
            plt.close(fig)
        except Exception:
            pass

        scroll = ctk.CTkScrollableFrame(parent, fg_color=th["bg_darkest"], corner_radius=8,
                                         scrollbar_button_color=th["accent_dark"],
                                         scrollbar_button_hover_color=th["accent"])
        scroll.pack(fill="both", expand=True, padx=8, pady=(0,8))
        for run_data in reversed(self.history[-20:]):
            row = ctk.CTkFrame(scroll, fg_color=th["bg_card"], corner_radius=6)
            row.pack(fill="x", pady=2, padx=2)
            ctk.CTkLabel(row, text=run_data.get("date",""),
                         font=ctk.CTkFont("Segoe UI",11),
                         text_color=th["text_white"]).pack(side="left", padx=10, pady=6)
            ctk.CTkLabel(row, text=run_data.get("elapsed",""),
                         font=ctk.CTkFont("Segoe UI",10),
                         text_color=th["text_gray"]).pack(side="left", padx=6)
            ctk.CTkLabel(row, text=fmt_size(run_data.get("freed_bytes",0)),
                         font=ctk.CTkFont("Segoe UI",11,"bold"),
                         text_color=th["accent"]).pack(side="right", padx=10)

    # ── Startup Panel ────────────────────────────────────────
    def _panel_startup(self, parent):
        th = self.th
        T  = self.T
        ctk.CTkLabel(parent, text=t(T,"startup_title"),
                     font=ctk.CTkFont("Segoe UI",14,"bold"),
                     text_color=th["accent"]).pack(pady=(12,2), padx=12, anchor="w")
        ctk.CTkLabel(parent, text=t(T,"startup_desc"),
                     font=ctk.CTkFont("Segoe UI",11),
                     text_color=th["text_gray"]).pack(padx=12, anchor="w", pady=(0,6))

        self.startup_scroll = ctk.CTkScrollableFrame(parent, fg_color=th["bg_darkest"],
                                                      corner_radius=8,
                                                      scrollbar_button_color=th["accent_dark"],
                                                      scrollbar_button_hover_color=th["accent"])
        self.startup_scroll.pack(fill="both", expand=True, padx=8, pady=(0,4))
        ctk.CTkButton(parent, text=t(T,"startup_refresh"),
                      font=ctk.CTkFont("Segoe UI",12),
                      height=34, corner_radius=8,
                      fg_color=th["bg_card"], hover_color=th["bg_hover"],
                      text_color=th["text_gray"],
                      command=self._refresh_startup).pack(fill="x", padx=12, pady=(4,8))
        self._refresh_startup()

    def _refresh_startup(self):
        th = self.th
        for w in self.startup_scroll.winfo_children():
            w.destroy()
        try:
            programs = get_startup_programs()
            if not programs:
                ctk.CTkLabel(self.startup_scroll, text="No startup programs found.",
                             font=ctk.CTkFont("Segoe UI",11),
                             text_color=th["text_gray"]).pack(pady=20)
                return

            for prog in programs:
                # Card per program
                card = ctk.CTkFrame(self.startup_scroll, fg_color=th["bg_card"], corner_radius=8)
                card.pack(fill="x", pady=3, padx=2)

                top_row = ctk.CTkFrame(card, fg_color="transparent")
                top_row.pack(fill="x", padx=12, pady=(8,2))

                # Name + registry hive
                name_frame = ctk.CTkFrame(top_row, fg_color="transparent")
                name_frame.pack(side="left", fill="x", expand=True)
                ctk.CTkLabel(name_frame,
                             text=prog["name"],
                             font=ctk.CTkFont("Segoe UI",12,"bold"),
                             text_color=th["text_white"], anchor="w").pack(anchor="w")
                ctk.CTkLabel(name_frame,
                             text=f"Registry: {prog['label']}",
                             font=ctk.CTkFont("Segoe UI",9),
                             text_color=th["text_dim"], anchor="w").pack(anchor="w")

                # Enable / Disable button
                is_en = prog.get("enabled", True)
                btn_text  = "⏸ Disable" if is_en else "▶ Enable"
                btn_color = "#3a0000" if is_en else th["accent_dark"]
                btn_tc    = th["error"] if is_en else th["accent"]

                def make_toggle(p=prog, enabled=is_en):
                    def toggle():
                        try:
                            if enabled:
                                ok = disable_startup(p["name"], p["hive"], p["key"])
                            else:
                                ok = enable_startup(p["name"])
                            if ok:
                                # Small delay before refresh to let registry settle
                                self.after(400, self._refresh_startup)
                            else:
                                messagebox.showerror(
                                    "Error",
                                    f"Could not toggle '{p['name']}'.\n\n"
                                    "Some programs require elevated permissions to disable.")
                        except Exception as ex:
                            messagebox.showerror("Error", str(ex))
                    return toggle

                ctk.CTkButton(top_row,
                              text=btn_text, width=100, height=28,
                              fg_color=btn_color, hover_color=th["bg_hover"],
                              text_color=btn_tc,
                              font=ctk.CTkFont("Segoe UI",11), corner_radius=6,
                              command=make_toggle()).pack(side="right", padx=(8,0))

                # Full path — wrapping label
                ctk.CTkLabel(card,
                             text=prog["path"],
                             font=ctk.CTkFont("Segoe UI",9),
                             text_color=th["text_gray"],
                             anchor="w", wraplength=600, justify="left"
                             ).pack(fill="x", padx=12, pady=(2,8))

        except Exception as e:
            ctk.CTkLabel(self.startup_scroll,
                         text=f"Could not load startup programs:\n{e}",
                         font=ctk.CTkFont("Segoe UI",10),
                         text_color=th["error"]).pack(pady=20, padx=12)

    # ── Settings Panel ───────────────────────────────────────
    def _panel_settings(self, parent):
        th = self.th
        T  = self.T

        scroll = ctk.CTkScrollableFrame(parent, fg_color=th["bg_darkest"], corner_radius=0,
                                        scrollbar_button_color=th["accent_dark"],
                                        scrollbar_button_hover_color=th["accent"])
        scroll.pack(fill="both", expand=True, padx=4, pady=4)

        def section(title, color=None):
            ctk.CTkLabel(scroll, text=title,
                         font=ctk.CTkFont("Segoe UI",13,"bold"),
                         text_color=color or th["accent"],
                         anchor="w").pack(fill="x", padx=4, pady=(14,4))

        def card():
            f = ctk.CTkFrame(scroll, fg_color=th["bg_card"], corner_radius=8)
            f.pack(fill="x", pady=3, padx=2)
            return f

        def row_in(parent, pady=10):
            r = ctk.CTkFrame(parent, fg_color="transparent")
            r.pack(fill="x", padx=14, pady=pady)
            return r

        # Language
        section(f"🌐  {t(T,'settings_language')}")
        lf = card()
        r  = row_in(lf)
        ctk.CTkLabel(r, text=t(T,"settings_language"),
                     font=ctk.CTkFont("Segoe UI",12),
                     text_color=th["text_white"], width=140, anchor="w").pack(side="left")
        cur_lang_name = LANGUAGES.get(self.cfg.get("language","en"),"English")
        ctk.CTkOptionMenu(r,
                          values=list(LANGUAGES.values()),
                          variable=tk.StringVar(value=cur_lang_name),
                          fg_color=th["bg_card"],
                          button_color=th["accent_dark"],
                          button_hover_color=th["accent_hover"],
                          text_color=th["text_white"],
                          font=ctk.CTkFont("Segoe UI",11),
                          command=self._on_lang_change,
                          width=220).pack(side="right")

        # Theme
        section(f"🎨  {t(T,'settings_theme')}")
        tf = card()
        r  = row_in(tf)
        ctk.CTkLabel(r, text=t(T,"settings_theme"),
                     font=ctk.CTkFont("Segoe UI",12),
                     text_color=th["text_white"], width=140, anchor="w").pack(side="left")
        self._theme_var_s = tk.StringVar(value=self.cfg.get("theme","Green"))
        ctk.CTkSegmentedButton(r, values=["Green","Blue","Purple"],
                               variable=self._theme_var_s,
                               fg_color=th["bg_darkest"],
                               selected_color=th["accent_dark"],
                               selected_hover_color=th["accent_hover"],
                               unselected_color=th["bg_hover"],
                               unselected_hover_color=th["bg_card"],
                               text_color=th["text_white"],
                               font=ctk.CTkFont("Segoe UI",12),
                               command=self._on_theme_change).pack(side="right")

        # Dry Run
        section("🔍  Dry Run Mode")
        dr = card()
        r  = row_in(dr)
        ctk.CTkLabel(r, text=t(T,"settings_dry_run"),
                     font=ctk.CTkFont("Segoe UI",12),
                     text_color=th["text_white"],
                     wraplength=380, justify="left").pack(side="left", fill="x", expand=True)
        ctk.CTkSwitch(r, text="", variable=self.dry_run_var,
                      command=self._on_dryrun_toggle,
                      width=44, height=22,
                      button_color=th["warn"], button_hover_color=th["warn"],
                      progress_color="#3a2000").pack(side="right")

        # Auto-start
        section(f"🚀  {t(T,'settings_autostart')}")
        asf = card()
        r   = row_in(asf)
        ctk.CTkLabel(r, text=t(T,"settings_autostart"),
                     font=ctk.CTkFont("Segoe UI",12),
                     text_color=th["text_white"]).pack(side="left", fill="x", expand=True)
        ctk.CTkSwitch(r, text="", variable=self.autostart_var,
                      command=self._toggle_autostart,
                      width=44, height=22,
                      button_color=th["accent"], button_hover_color=th["accent_dim"],
                      progress_color=th["accent_dark"]).pack(side="right")
        ctk.CTkLabel(asf, text=f"  {t(T,'settings_autostart_note')}",
                     font=ctk.CTkFont("Segoe UI",10),
                     text_color=th["text_gray"], anchor="w").pack(fill="x", padx=14, pady=(0,10))

        # PIN Lock
        section(f"🔐  {t(T,'settings_pin')}", color=th["warn"])
        pf = card()
        r  = row_in(pf)
        pin_enabled = self.cfg.get("pin_enabled", False)
        self._pin_sw_var = tk.BooleanVar(value=pin_enabled)
        ctk.CTkLabel(r, text=t(T,"settings_pin_enable"),
                     font=ctk.CTkFont("Segoe UI",12),
                     text_color=th["text_white"]).pack(side="left")
        ctk.CTkSwitch(r, text="", variable=self._pin_sw_var,
                      command=self._toggle_pin,
                      width=44, height=22,
                      button_color=th["warn"], button_hover_color=th["warn"],
                      progress_color="#3a2000").pack(side="right")
        r2 = row_in(pf, pady=4)
        ctk.CTkButton(r2, text=t(T,"settings_pin_set"), width=130, height=30,
                      fg_color=th["bg_darkest"], hover_color=th["bg_hover"],
                      text_color=th["warn"],
                      font=ctk.CTkFont("Segoe UI",12), corner_radius=6,
                      command=self._set_pin_dialog).pack(side="left", padx=(0,8))
        ctk.CTkButton(r2, text=t(T,"settings_pin_disable"), width=130, height=30,
                      fg_color=th["bg_darkest"], hover_color=th["bg_hover"],
                      text_color=th["text_gray"],
                      font=ctk.CTkFont("Segoe UI",12), corner_radius=6,
                      command=self._disable_pin).pack(side="left")

        # Scheduler
        section(f"🗓  {t(T,'settings_scheduler')}")
        sf = card()
        self._sched_var = tk.BooleanVar(value=schedule_exists())
        r  = row_in(sf)
        ctk.CTkLabel(r, text=t(T,"settings_scheduler_enable"),
                     font=ctk.CTkFont("Segoe UI",12),
                     text_color=th["text_white"]).pack(side="left")
        ctk.CTkSwitch(r, text="", variable=self._sched_var,
                      command=self._toggle_scheduler,
                      width=44, height=22,
                      button_color=th["accent"], button_hover_color=th["accent_dim"],
                      progress_color=th["accent_dark"]).pack(side="right")
        r2 = row_in(sf, pady=4)
        self._freq_var = tk.StringVar(value=self.cfg["scheduler"].get("frequency","weekly").capitalize())
        ctk.CTkLabel(r2, text=t(T,"settings_frequency"),
                     font=ctk.CTkFont("Segoe UI",11),
                     text_color=th["text_gray"]).pack(side="left", padx=(0,8))
        ctk.CTkSegmentedButton(r2,
                               values=[t(T,"settings_weekly"), t(T,"settings_monthly")],
                               variable=self._freq_var,
                               fg_color=th["bg_darkest"],
                               selected_color=th["accent_dark"],
                               unselected_color=th["bg_hover"],
                               text_color=th["text_white"],
                               font=ctk.CTkFont("Segoe UI",11),
                               width=200).pack(side="left")
        next_run = get_next_run()
        ctk.CTkLabel(sf, text=f"  Next run: {next_run}",
                     font=ctk.CTkFont("Segoe UI",10),
                     text_color=th["text_gray"], anchor="w").pack(fill="x", padx=14, pady=(0,10))

        # Whitelist
        section(f"🚫  {t(T,'settings_whitelist')}")
        wf = card()
        self.wl_box = ctk.CTkTextbox(wf, height=80,
                                      fg_color=th["bg_darkest"],
                                      text_color=th["text_white"],
                                      font=ctk.CTkFont("Consolas",11))
        self.wl_box.pack(fill="x", padx=10, pady=(10,4))
        self.wl_box.insert("end", "\n".join(self.whitelist))
        r2 = row_in(wf, pady=6)
        ctk.CTkButton(r2, text=t(T,"settings_add_path"), width=130, height=28,
                      fg_color=th["accent_dark"], hover_color=th["accent_hover"],
                      text_color=th["accent"],
                      font=ctk.CTkFont("Segoe UI",11), corner_radius=6,
                      command=self._add_whitelist).pack(side="left", padx=(0,8))
        ctk.CTkButton(r2, text=t(T,"settings_remove_path"), width=140, height=28,
                      fg_color=th["bg_darkest"], hover_color=th["bg_hover"],
                      text_color=th["text_gray"],
                      font=ctk.CTkFont("Segoe UI",11), corner_radius=6,
                      command=self._clear_whitelist).pack(side="left")

        # Save
        ctk.CTkFrame(scroll, fg_color="transparent", height=8).pack()
        ctk.CTkButton(scroll, text=t(T,"settings_save"),
                      font=ctk.CTkFont("Segoe UI",13,"bold"),
                      height=40, corner_radius=8,
                      fg_color=th["accent_dark"], hover_color=th["accent_hover"],
                      text_color=th["accent"],
                      command=self._save_settings).pack(fill="x", padx=4, pady=(0,8))

    # ── About Panel ──────────────────────────────────────────
    def _panel_about(self, parent):
        th = self.th
        T  = self.T

        scroll = ctk.CTkScrollableFrame(parent, fg_color=th["bg_darkest"], corner_radius=0,
                                        scrollbar_button_color=th["accent_dark"],
                                        scrollbar_button_hover_color=th["accent"])
        scroll.pack(fill="both", expand=True, padx=4, pady=4)

        try:
            acc = tuple(int(th["accent"].lstrip("#")[i:i+2],16) for i in (0,2,4))
            li  = generate_icon(acc)
            lc  = ctk.CTkImage(light_image=li, dark_image=li, size=(72,72))
            ctk.CTkLabel(scroll, image=lc, text="").pack(pady=(16,8))
        except Exception:
            pass

        ctk.CTkLabel(scroll, text="PurgeKit",
                     font=ctk.CTkFont("Segoe UI",26,"bold"),
                     text_color=th["accent"]).pack()
        ctk.CTkLabel(scroll, text=f"v{APP_VERSION}  —  {t(T,'app_subtitle')}",
                     font=ctk.CTkFont("Segoe UI",12),
                     text_color=th["text_gray"]).pack(pady=(2,16))

        # Info card — properly aligned two columns
        info_f = ctk.CTkFrame(scroll, fg_color=th["bg_card"], corner_radius=10)
        info_f.pack(fill="x", padx=16, pady=(0,12))

        rows = [
            (f"Built by",  AUTHOR_NAME),
            ("Location",             AUTHOR_LOC),
            ("Brand",                AUTHOR_BRAND),
            ("License",              "MIT — Free & Open Source"),
            ("Platform",             "Windows 10 / 11"),
            (t(T,"about_version"),   APP_VERSION),
        ]
        for lbl, val in rows:
            r = ctk.CTkFrame(info_f, fg_color="transparent")
            r.pack(fill="x", padx=16, pady=5)
            # Fixed width left column — right aligned label
            ctk.CTkLabel(r, text=lbl,
                         font=ctk.CTkFont("Segoe UI",11),
                         text_color=th["text_gray"],
                         width=140, anchor="w").pack(side="left")
            ctk.CTkLabel(r, text=val,
                         font=ctk.CTkFont("Segoe UI",11,"bold"),
                         text_color=th["text_white"],
                         anchor="w").pack(side="left", padx=(8,0))

        # GitHub
        ctk.CTkLabel(scroll, text=t(T,"about_github"),
                     font=ctk.CTkFont("Segoe UI",11),
                     text_color=th["text_gray"]).pack(pady=(10,4))
        ctk.CTkButton(scroll, text=GITHUB_URL,
                      font=ctk.CTkFont("Segoe UI",11,"bold"),
                      fg_color=th["accent_dark"], hover_color=th["accent_hover"],
                      text_color=th["accent"], height=34, corner_radius=8,
                      command=self._open_github).pack(padx=16, pady=(0,10), fill="x")

        # Update checker label
        self.update_lbl = ctk.CTkLabel(scroll, text=t(T,"update_check"),
                                        font=ctk.CTkFont("Segoe UI",11),
                                        text_color=th["text_gray"])
        self.update_lbl.pack(pady=(0,10))

        ctk.CTkLabel(scroll, text=t(T,"about_desc"),
                     font=ctk.CTkFont("Segoe UI",10),
                     text_color=th["text_dim"], justify="center").pack(pady=(0,12))

    # ── Helpers ──────────────────────────────────────────────
    def _log(self, text, tag="white"):
        ts   = datetime.datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {text}"
        self.log_lines.append(line)
        def _ins():
            try:
                self.log_box.configure(state="normal")
                self.log_box.insert("end", line + "\n", tag)
                self.log_box.see("end")
                self.log_box.configure(state="disabled")
            except Exception:
                pass
        try:
            self.after(0, _ins)
        except Exception:
            pass

    def _set_progress(self, value, label):
        try:
            self.after(0, lambda: (
                self.progress_bar.set(value),
                self.progress_label.configure(text=label)
            ))
        except Exception:
            pass

    def _select_all(self):
        for v in self.task_vars.values():  v.set(True)
        for v in self.drive_vars.values(): v.set(True)
        self.after(100, self._refresh_task_sizes)

    def _deselect_all(self):
        for v in self.task_vars.values():  v.set(False)
        for v in self.drive_vars.values(): v.set(False)
        self.after(100, self._refresh_task_sizes)

    def _toggle_compact(self):
        self.cfg["compact_mode"] = self.compact_mode.get()
        save_config(self.cfg)
        self._set_window_size()
        self._build_content()

    def _toggle_autostart(self):
        ok = set_autostart(self.autostart_var.get())
        if not ok:
            messagebox.showerror("Error", "Could not update startup registry.")
            self.autostart_var.set(not self.autostart_var.get())
        else:
            self.cfg["autostart"] = self.autostart_var.get()
            save_config(self.cfg)

    def _toggle_pin(self):
        if self._pin_sw_var.get():
            self._set_pin_dialog()
        else:
            self._disable_pin()

    def _set_pin_dialog(self):
        th = self.th
        T  = self.T
        win = ctk.CTkToplevel(self)
        win.title(t(T,"pin_set_title"))
        win.geometry("320x300")
        win.configure(fg_color=th["bg_darkest"])
        win.resizable(False, False)
        win.grab_set()
        ctk.CTkLabel(win, text=t(T,"pin_set_title"),
                     font=ctk.CTkFont("Segoe UI",16,"bold"),
                     text_color=th["accent"]).pack(pady=(20,12))
        pin1 = tk.StringVar()
        pin2 = tk.StringVar()
        msg_v = tk.StringVar()
        for var, placeholder in [(pin1,t(T,"pin_enter_new")),(pin2,t(T,"pin_confirm"))]:
            ctk.CTkLabel(win, text=placeholder,
                         font=ctk.CTkFont("Segoe UI",11),
                         text_color=th["text_gray"]).pack(pady=(4,0))
            ctk.CTkEntry(win, textvariable=var, show="●",
                         width=200, height=36,
                         font=ctk.CTkFont("Segoe UI",16),
                         fg_color=th["bg_card"],
                         text_color=th["text_white"],
                         justify="center").pack(pady=(2,4))
        ctk.CTkLabel(win, textvariable=msg_v,
                     font=ctk.CTkFont("Segoe UI",11),
                     text_color=th["error"]).pack()
        def save_pin():
            p1 = pin1.get().strip()
            p2 = pin2.get().strip()
            if len(p1) != 6 or not p1.isdigit():
                msg_v.set(t(T,"pin_too_short")); return
            if p1 != p2:
                msg_v.set(t(T,"pin_mismatch")); return
            set_pin(self.cfg, p1)
            self._pin_sw_var.set(True)
            win.destroy()
            messagebox.showinfo("PIN", t(T,"pin_set_success"))
        ctk.CTkButton(win, text=t(T,"settings_pin_set"),
                      font=ctk.CTkFont("Segoe UI",12,"bold"),
                      height=36, corner_radius=8,
                      fg_color=th["accent_dark"], hover_color=th["accent_hover"],
                      text_color=th["accent"],
                      command=save_pin).pack(padx=40, fill="x", pady=(10,0))

    def _disable_pin(self):
        clear_pin(self.cfg)
        self._pin_sw_var.set(False)
        messagebox.showinfo("PIN", t(self.T,"pin_disabled"))

    def _toggle_scheduler(self):
        if self._sched_var.get():
            freq = "weekly" if "weekly" in self._freq_var.get().lower() else "monthly"
            create_schedule(frequency=freq)
            self.cfg["scheduler"]["enabled"]   = True
            self.cfg["scheduler"]["frequency"] = freq
        else:
            remove_schedule()
            self.cfg["scheduler"]["enabled"] = False
        save_config(self.cfg)

    def _add_whitelist(self):
        path = filedialog.askdirectory(title="Select folder to exclude")
        if path:
            self.whitelist.append(path)
            self.wl_box.insert("end", "\n" + path)

    def _clear_whitelist(self):
        self.whitelist = []
        self.wl_box.delete("1.0","end")

    def _on_lang_change(self, selection):
        code = next((c for c,n in LANGUAGES.items() if n==selection), "en")
        self.cfg["language"] = code
        save_config(self.cfg)
        self._reload_theme_lang()

    def _on_theme_change(self, selection):
        self.cfg["theme"] = selection
        save_config(self.cfg)
        self._reload_theme_lang()

    def _save_settings(self):
        wl_text = self.wl_box.get("1.0","end").strip()
        self.whitelist = [p.strip() for p in wl_text.splitlines() if p.strip()]
        save_whitelist(self.whitelist)
        self.cfg["dry_run"] = self.dry_run_var.get()
        save_config(self.cfg)
        messagebox.showinfo("Settings", "Settings saved successfully.")

    def _open_github(self):
        import webbrowser
        webbrowser.open(GITHUB_URL)

    def _save_log_manual(self):
        path = write_log(self.log_lines)
        if path:
            messagebox.showinfo(t(self.T,"log_saved"),
                                t(self.T,"log_saved_to", path=path))
        else:
            messagebox.showerror("Error", "Could not save log.")

    def _check_update(self):
        def _do():
            result, ver, url = check_for_update()
            def _show():
                try:
                    T  = self.T
                    th = self.th
                    if result is True:
                        msg = t(T,"update_available",version=ver)
                        color = th["warn"]
                    elif result is False:
                        msg = t(T,"update_latest")
                        color = th["text_gray"]
                    else:
                        msg = t(T,"update_error")
                        color = th["text_dim"]
                    self.update_lbl.configure(text=msg, text_color=color)
                except Exception:
                    pass
            self.after(0, _show)
        threading.Thread(target=_do, daemon=True).start()

    # ── Purge Engine ─────────────────────────────────────────
    def _start_purge(self):
        if self.running:
            return
        selected   = [tid for tid,v in self.task_vars.items() if v.get()]
        sel_drives = [d   for d,  v in self.drive_vars.items() if v.get()]
        if not selected and not sel_drives and self.activity_var.get()=="skip":
            messagebox.showwarning(t(self.T,"nothing_selected"), t(self.T,"select_one"))
            return
        self.running = True
        dry = self.dry_run_var.get()
        self.start_btn.configure(text=t(self.T,"running"), state="disabled",
                                  fg_color="#002510", text_color=self.th["text_gray"])
        self.reboot_needed = [False]
        threading.Thread(target=self._purge_thread,
                         args=(selected, sel_drives, dry), daemon=True).start()

    def _purge_thread(self, selected, sel_drives, dry_run):
        T   = self.T
        th  = self.th
        act = self.activity_var.get()
        total       = len(selected) + len(sel_drives) + (0 if act=="skip" else 1)
        done        = 0
        total_freed = 0
        start_time  = datetime.datetime.now()

        self._log("", "dim")
        self._log("═"*50, "accent")
        self._log(f"  {t(T,'purge_started')}" + (" [DRY RUN]" if dry_run else ""), "accent")
        self._log("═"*50, "accent")

        for task in TASKS:
            tid = task[0]
            if tid not in selected:
                continue
            path   = task[3]
            do_exp = task[4]
            rp     = ep(path) if do_exp else path
            if any(wl in rp or rp in wl for wl in self.whitelist):
                self._log(t(T,"whitelist_skip",path=rp), "dim")
                continue
            done += 1
            self._set_progress(done/max(total,1), f"[{done}/{total}] {task[2]}...")
            self._log(f"\n── {tid}: {task[2]}", "accent")
            freed = run_task(tid, self._log, self.reboot_needed, dry_run)
            total_freed += freed

        for drv in sel_drives:
            done += 1
            self._set_progress(done/max(total,1), f"[{done}/{total}] Disk Cleanup {drv}...")
            self._log(f"\n── Disk Cleanup: {drv}", "accent")
            if not dry_run:
                for cat in DISK_CLEANUP_CATS:
                    run(f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VolumeCaches\\{cat}" '
                        f'/v StateFlags0099 /t REG_DWORD /d 2 /f')
                run(f"cleanmgr /sagerun:99 /d {drv[0]}", timeout=300)
            else:
                self._log(f"  [DRY RUN] Would run Disk Cleanup on {drv}", "warn")
            self._log(f"  ✅ Disk Cleanup done: {drv}", "success")

        if act != "skip":
            done += 1
            self._set_progress(done/max(total,1), "Windows Activity History...")
            self._log("\n── Activity History", "accent")
            cdp = ep(r"%LOCALAPPDATA%\ConnectedDevicesPlatform")
            if not dry_run:
                run("taskkill /f /im explorer.exe")
            if os.path.exists(cdp):
                for profile in os.listdir(cdp):
                    db = os.path.join(cdp, profile, "ActivitiesCache.db")
                    if os.path.exists(db):
                        if dry_run:
                            sz = os.path.getsize(db)
                            self._log(f"  [DRY RUN] Would delete: {db} ({fmt_size(sz)})", "warn")
                            total_freed += sz
                        else:
                            try:
                                sz = os.path.getsize(db)
                                os.remove(db)
                                total_freed += sz
                                self._log(f"  ✅ Deleted: {db}", "success")
                            except Exception:
                                run(f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager" '
                                    f'/v PendingFileRenameOperations /t REG_MULTI_SZ /d "\\??\\{db}\\0" /f')
                                self.reboot_needed[0] = True
            if not dry_run:
                run("start explorer.exe")
                if act == "disable":
                    for v in ["EnableActivityFeed","PublishUserActivities","UploadUserActivities"]:
                        run(f'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" '
                            f'/v {v} /t REG_DWORD /d 0 /f')
                    self._log("  ✅ Activity History disabled", "success")

        elapsed     = datetime.datetime.now() - start_time
        elapsed_str = str(elapsed).split(".")[0]
        freed_str   = fmt_size(total_freed)
        summary     = (f"{'='*60}\n"
                       f"  {t(T,'space_freed')}: {freed_str}\n"
                       f"  {t(T,'time_taken')}:  {elapsed_str}\n"
                       f"{'='*60}")

        if not dry_run:
            self.history.append({
                "date":        datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "freed_bytes": total_freed,
                "elapsed":     elapsed_str,
                "dry_run":     False,
            })
            save_history(self.history)

        self.cfg["last_tasks"]     = {tid: v.get() for tid,v in self.task_vars.items()}
        self.cfg["last_drives"]    = [d for d,v in self.drive_vars.items() if v.get()]
        self.cfg["activity_choice"]= act
        save_config(self.cfg)

        log_path = write_log(self.log_lines, summary)

        if not dry_run:
            try:
                from winotify import Notification
                Notification(app_id="PurgeKit",
                             title=t(T,"notification_title"),
                             msg=t(T,"notification_body",
                                   size=freed_str, time=elapsed_str, files="—"),
                             duration="short").show()
            except Exception:
                pass

        self._set_progress(1.0, "✅ All done!")
        self._log("", "dim")
        self._log("═"*50, "accent")
        complete_key = "dry_run_complete" if dry_run else "purge_complete"
        self._log(f"  {t(T,complete_key)}", "success")
        self._log(f"  {t(T,'space_freed')}: {freed_str}", "success")
        self._log(f"  {t(T,'time_taken')}: {elapsed_str}", "dim")
        if log_path:
            self._log(f"  Log: {log_path}", "dim")
        if self.reboot_needed[0]:
            self._log(f"  ⚠ {t(T,'reboot_required')}", "warn")
            self.after(0, lambda: messagebox.showwarning(
                t(T,"reboot_required"), t(T,"reboot_msg")))
        self._log("═"*50, "accent")

        def _re():
            dry = self.dry_run_var.get()
            self.start_btn.configure(
                text=t(T,"dry_run") if dry else t(T,"start_purge"),
                state="normal",
                fg_color="#3a2000" if dry else th["accent_dark"],
                text_color=th["warn"] if dry else th["accent"])
            self.running = False
        self.after(0, _re)


# ── CLI silent mode ───────────────────────────────────────────
def run_silent():
    from core.cleaner import TASKS, get_drives, DISK_CLEANUP_CATS, run_task, run, fmt_size
    from core.log_manager import write_log
    cfg    = load_config()
    reboot = [False]
    log    = []
    freed  = 0
    log_fn = lambda msg, tag: log.append(msg)
    print(f"PurgeKit v{APP_VERSION} — Silent Mode")
    for task in TASKS:
        if cfg.get("last_tasks",{}).get(task[0], task[5]):
            print(f"  Cleaning: {task[2]}")
            freed += run_task(task[0], log_fn, reboot, False)
    for drv, _, _, _ in get_drives():
        for cat in DISK_CLEANUP_CATS:
            run(f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VolumeCaches\\{cat}" '
                f'/v StateFlags0099 /t REG_DWORD /d 2 /f')
        run(f"cleanmgr /sagerun:99 /d {drv[0]}", timeout=300)
    path = write_log(log, f"Silent run — freed {fmt_size(freed)}")
    print(f"Done. Freed {fmt_size(freed)}. Log: {path}")
    if reboot[0]:
        print("REBOOT REQUIRED.")


if __name__ == "__main__":
    if "--silent" in sys.argv:
        run_silent()
    else:
        app = PurgeKitApp()
        app.mainloop()
