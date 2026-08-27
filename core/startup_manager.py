"""
PurgeKit v3.0 — Startup Programs Manager
MIT License — TeamExyKings
"""

import winreg

STARTUP_KEYS = [
    (winreg.HKEY_CURRENT_USER,  r"Software\Microsoft\Windows\CurrentVersion\Run",         "HKCU"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",         "HKLM"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run", "HKLM32"),
]

DISABLED_KEY  = r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"

def get_startup_programs():
    """Return list of (name, path, hive_label, enabled)."""
    programs = []
    for hive, key_path, label in STARTUP_KEYS:
        try:
            key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ)
            i = 0
            while True:
                try:
                    name, val, _ = winreg.EnumValue(key, i)
                    programs.append({
                        "name":    name,
                        "path":    val,
                        "hive":    hive,
                        "key":     key_path,
                        "label":   label,
                        "enabled": True,
                    })
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except Exception:
            pass
    return programs

def disable_startup(name, hive, key_path):
    try:
        key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ | winreg.KEY_WRITE)
        val, _ = winreg.QueryValueEx(key, name)
        # Move to disabled key under HKCU
        dis_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                  r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
                                  0, winreg.KEY_SET_VALUE)
        # Write 3-byte disabled flag
        import struct
        winreg.SetValueEx(dis_key, name, 0, winreg.REG_BINARY,
                          struct.pack("<I", 3) + b"\x00" * 8)
        winreg.CloseKey(dis_key)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False

def enable_startup(name):
    try:
        dis_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                  r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
                                  0, winreg.KEY_SET_VALUE)
        import struct
        winreg.SetValueEx(dis_key, name, 0, winreg.REG_BINARY,
                          struct.pack("<I", 2) + b"\x00" * 8)
        winreg.CloseKey(dis_key)
        return True
    except Exception:
        return False
