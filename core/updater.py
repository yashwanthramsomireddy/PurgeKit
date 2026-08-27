"""
PurgeKit v3.0 — Auto Update Checker
MIT License — TeamExyKings
"""

import urllib.request
import json

GITHUB_API = "https://api.github.com/repos/yashwanthramsomireddy/PurgeKit/releases/latest"
CURRENT_VERSION = "3.0"

def check_for_update(timeout=5):
    """
    Returns (is_available: bool, latest_version: str, url: str)
    """
    try:
        req = urllib.request.Request(
            GITHUB_API,
            headers={"User-Agent": "PurgeKit-Updater/3.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
        tag     = data.get("tag_name", "").lstrip("v")
        url     = data.get("html_url", "https://github.com/yashwanthramsomireddy/PurgeKit/releases")
        if tag and _version_gt(tag, CURRENT_VERSION):
            return True, tag, url
        return False, CURRENT_VERSION, url
    except Exception:
        return None, CURRENT_VERSION, ""

def _version_gt(a, b):
    """Return True if version string a > b."""
    try:
        av = [int(x) for x in a.split(".")]
        bv = [int(x) for x in b.split(".")]
        return av > bv
    except Exception:
        return False
