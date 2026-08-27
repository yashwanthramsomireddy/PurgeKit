"""
PurgeKit v3.0 — Junk Scanner
MIT License — TeamExyKings
"""

import os
from core.cleaner import ep, folder_size, fmt_size, TASKS

SCAN_PATHS = [
    (ep(r"%TEMP%"),                                                              "User Temp"),
    (ep(r"%LOCALAPPDATA%\Temp"),                                                 "LocalAppData Temp"),
    (r"C:\Windows\Temp",                                                         "Windows System Temp"),
    (r"C:\Windows\Prefetch",                                                     "Prefetch"),
    (r"C:\Windows\SoftwareDistribution\Download",                                "Windows Update Cache"),
    (r"C:\Windows\SoftwareDistribution\DeliveryOptimization",                    "Delivery Optimization"),
    (ep(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache"),                "Chrome Cache"),
    (ep(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Code Cache"),           "Chrome Code Cache"),
    (ep(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Service Worker\CacheStorage"), "Chrome SW Cache"),
    (ep(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache"),               "Edge Cache"),
    (ep(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Service Worker\CacheStorage"), "Edge SW Cache"),
    (ep(r"%LOCALAPPDATA%\Mozilla\Firefox\Profiles"),                             "Firefox Cache"),
    (ep(r"%LOCALAPPDATA%\Microsoft\Windows\WebCache"),                           "IE/Edge WebCache"),
    (ep(r"%LOCALAPPDATA%\Microsoft\Windows\INetCache"),                          "INetCache"),
    (ep(r"%APPDATA%\Microsoft\Teams\Cache"),                                     "Teams Cache"),
    (ep(r"%APPDATA%\Code\Cache"),                                                "VS Code Cache"),
    (ep(r"%LOCALAPPDATA%\Spotify\Storage"),                                      "Spotify Cache"),
    (ep(r"%APPDATA%\npm-cache"),                                                  "npm Cache"),
    (ep(r"%LOCALAPPDATA%\pip\cache"),                                             "pip Cache"),
    (ep(r"%LOCALAPPDATA%\D3DSCache"),                                             "DirectX Shader Cache"),
    (ep(r"%LOCALAPPDATA%\CrashDumps"),                                            "User Crash Dumps"),
    (r"C:\Windows\Minidump",                                                      "System Crash Dumps"),
    (r"C:\ProgramData\Microsoft\Windows\WER\ReportQueue",                         "WER Queue"),
    (r"C:\Windows\Logs\CBS",                                                      "CBS Logs"),
    (ep(r"%LOCALAPPDATA%\Microsoft\Office\16.0\OfficeFileCache"),                "Office Cache"),
    (ep(r"%APPDATA%\Microsoft\Windows\Recent"),                                   "Recent Files"),
]

def scan_all(progress_fn=None):
    """
    Scan all known junk paths.
    Returns sorted list of (label, path, size_bytes) descending by size.
    """
    results = []
    total   = len(SCAN_PATHS)
    for i, (path, label) in enumerate(SCAN_PATHS):
        if progress_fn:
            progress_fn(i / total, f"Scanning {label}...")
        if os.path.exists(path):
            size = folder_size(path)
            if size > 0:
                results.append((label, path, size))

    if progress_fn:
        progress_fn(1.0, "Scan complete.")

    results.sort(key=lambda x: x[2], reverse=True)
    return results

def total_junk(results):
    return sum(r[2] for r in results)
