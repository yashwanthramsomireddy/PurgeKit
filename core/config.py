"""
PurgeKit v3.0 — Config Manager
MIT License — TeamExyKings
"""

import os
import json
import hashlib

# Paths
APP_DIR     = os.path.join(os.path.expanduser("~"), "AppData", "Local", "PurgeKit")
CONFIG_FILE = os.path.join(APP_DIR, "config.json")
HISTORY_FILE= os.path.join(APP_DIR, "history.json")
WHITE_FILE  = os.path.join(APP_DIR, "whitelist.json")
LOG_DIR     = os.path.join(os.path.expanduser("~"), "Downloads", "PurgeKit", "Logs")

DEFAULT_CONFIG = {
    "version":        "3.0",
    "theme":          "Green",
    "language":       "en",
    "compact_mode":   True,
    "autostart":      False,
    "first_run":      True,
    "pin_enabled":    False,
    "pin_hash":       "",
    "pin_attempts":   0,
    "scheduler":      {
        "enabled":    False,
        "frequency":  "weekly",
        "day":        "Sunday",
        "time":       "09:00",
    },
    "last_tasks":     {},
    "last_drives":    [],
    "activity_choice":"skip",
    "dry_run":        False,
}

def ensure_dirs():
    os.makedirs(APP_DIR,  exist_ok=True)
    os.makedirs(LOG_DIR,  exist_ok=True)

def load_config():
    ensure_dirs()
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            cfg = dict(DEFAULT_CONFIG)
            cfg.update(saved)
            # merge nested scheduler
            sched = dict(DEFAULT_CONFIG["scheduler"])
            sched.update(saved.get("scheduler", {}))
            cfg["scheduler"] = sched
            return cfg
    except Exception:
        pass
    return dict(DEFAULT_CONFIG)

def save_config(cfg):
    ensure_dirs()
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def load_history():
    ensure_dirs()
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []

def save_history(history):
    ensure_dirs()
    try:
        # keep last 50 runs
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history[-50:], f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def load_whitelist():
    ensure_dirs()
    try:
        if os.path.exists(WHITE_FILE):
            with open(WHITE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []

def save_whitelist(wl):
    ensure_dirs()
    try:
        with open(WHITE_FILE, "w", encoding="utf-8") as f:
            json.dump(wl, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

# ── PIN helpers ──────────────────────────────────────────────
def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()

def verify_pin(pin: str, stored_hash: str) -> bool:
    return hash_pin(pin) == stored_hash

def set_pin(cfg, pin: str):
    cfg["pin_enabled"] = True
    cfg["pin_hash"]    = hash_pin(pin)
    cfg["pin_attempts"] = 0
    save_config(cfg)

def clear_pin(cfg):
    cfg["pin_enabled"]  = False
    cfg["pin_hash"]     = ""
    cfg["pin_attempts"] = 0
    save_config(cfg)
