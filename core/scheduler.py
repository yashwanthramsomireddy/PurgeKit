"""
PurgeKit v3.0 — Scheduler
MIT License — TeamExyKings
"""

import subprocess
import sys
import os

TASK_NAME = "PurgeKit_AutoPurge"

def _exe_path():
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    return f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}" --silent'

def create_schedule(frequency="weekly", day="Sunday", time_str="09:00"):
    """Create or update a Windows scheduled task for PurgeKit."""
    remove_schedule()
    exe = _exe_path()
    if frequency == "weekly":
        sched = f'/SC WEEKLY /D {day.upper()[:3]} /ST {time_str}'
    else:
        sched = f'/SC MONTHLY /D 1 /ST {time_str}'
    cmd = (f'schtasks /Create /TN "{TASK_NAME}" /TR {exe} '
           f'{sched} /RL HIGHEST /F')
    try:
        subprocess.run(cmd, shell=True, capture_output=True, timeout=15)
        return True
    except Exception:
        return False

def remove_schedule():
    try:
        subprocess.run(f'schtasks /Delete /TN "{TASK_NAME}" /F',
                       shell=True, capture_output=True, timeout=10)
    except Exception:
        pass

def get_next_run():
    try:
        result = subprocess.run(
            f'schtasks /Query /TN "{TASK_NAME}" /FO LIST',
            shell=True, capture_output=True, text=True, timeout=10)
        for line in result.stdout.splitlines():
            if "Next Run Time" in line or "next run" in line.lower():
                return line.split(":", 1)[-1].strip()
    except Exception:
        pass
    return "Not scheduled"

def schedule_exists():
    try:
        result = subprocess.run(
            f'schtasks /Query /TN "{TASK_NAME}"',
            shell=True, capture_output=True, timeout=10)
        return result.returncode == 0
    except Exception:
        return False
