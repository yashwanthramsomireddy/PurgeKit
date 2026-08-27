"""
PurgeKit v3.0 — Log Manager
MIT License — TeamExyKings
Saves logs to: Downloads/PurgeKit/Logs/PurgeKit_YYYYMMDD_HHMMSS.txt
"""

import os
import datetime
import platform

GITHUB_URL   = "https://github.com/yashwanthramsomireddy/PurgeKit"
AUTHOR_NAME  = "Yashwanth Ram Somireddy"
AUTHOR_LOC   = "Chennai, India"
AUTHOR_BRAND = "TeamExyKings"
APP_VERSION  = "3.0"

def get_log_dir():
    log_dir = os.path.join(os.path.expanduser("~"), "Downloads", "PurgeKit", "Logs")
    os.makedirs(log_dir, exist_ok=True)
    return log_dir

def get_log_path():
    dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(get_log_dir(), f"PurgeKit_{dt}.txt")

def write_log(log_lines: list, extra_summary: str = ""):
    path = get_log_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write(f"  PurgeKit v{APP_VERSION}  |  MIT License  |  {AUTHOR_BRAND}\n")
            f.write(f"  Built with love by {AUTHOR_NAME}, {AUTHOR_LOC}\n")
            f.write(f"  GitHub  : {GITHUB_URL}\n")
            f.write(f"  Saved   : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"  User    : {os.environ.get('USERNAME', 'Unknown')}\n")
            f.write(f"  PC      : {platform.node()}\n")
            f.write(f"  OS      : {platform.platform()}\n")
            f.write("=" * 60 + "\n\n")
            if extra_summary:
                f.write(extra_summary + "\n\n")
                f.write("-" * 60 + "\n\n")
            for line in log_lines:
                f.write(line + "\n")
        return path
    except Exception as e:
        return None
