"""
PurgeKit v3.5.1 — Software Updater
MIT License — TeamExyKings
GitHub: https://github.com/yashwanthramsomireddy/PurgeKit

Downloads installers directly from official vendor URLs (via winget manifest).
User installs manually — we never execute anything silently.
100% legal, no Defender issues, official sources only.
"""

import subprocess
import threading
import os
import re
import urllib.request
import urllib.error
import glob


# ── winget availability ──────────────────────────────────────
def is_winget_available() -> bool:
    try:
        r = subprocess.run(["winget", "--version"],
                           capture_output=True, text=True, timeout=10)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


# ── Parse winget table output ────────────────────────────────
def _parse_winget_table(output: str) -> list:
    lines = output.splitlines()
    hdr_idx = None
    for i, line in enumerate(lines):
        if "Name" in line and "Id" in line and "Version" in line:
            hdr_idx = i
            break
    if hdr_idx is None:
        return []

    header        = lines[hdr_idx]
    col_id        = header.index("Id")        if "Id"        in header else 30
    col_version   = header.index("Version")   if "Version"   in header else 55
    col_available = header.index("Available") if "Available" in header else 70
    col_source    = header.index("Source")    if "Source"    in header else 85

    apps = []
    for line in lines[hdr_idx + 2:]:
        if not line.strip() or line.startswith("-"):
            continue
        if "upgrades available" in line.lower():
            break
        try:
            name      = line[0:col_id].strip()
            app_id    = line[col_id:col_version].strip()
            version   = line[col_version:col_available].strip()
            available = line[col_available:col_source].strip() if col_available < len(line) else ""
            source    = line[col_source:].strip() if col_source < len(line) else ""
            if name and app_id and available:
                apps.append({
                    "name":      name,
                    "id":        app_id,
                    "version":   version,
                    "available": available,
                    "source":    source,
                    "status":    "Pending",
                })
        except Exception:
            continue
    return apps


# ── Get upgradeable apps ─────────────────────────────────────
def get_upgradeable_apps(progress_fn=None) -> list:
    try:
        if progress_fn:
            progress_fn(0.1, "Checking for updates via winget...")
        result = subprocess.run(
            ["winget", "upgrade",
             "--accept-source-agreements",
             "--include-unknown"],
            capture_output=True, text=True, timeout=90,
            encoding="utf-8", errors="replace"
        )
        if progress_fn:
            progress_fn(0.8, "Parsing results...")
        apps = _parse_winget_table(result.stdout)
        if progress_fn:
            progress_fn(1.0, f"Found {len(apps)} update(s) available.")
        return apps
    except subprocess.TimeoutExpired:
        if progress_fn:
            progress_fn(1.0, "Timeout — winget took too long.")
        return []
    except Exception as e:
        if progress_fn:
            progress_fn(1.0, f"Error: {e}")
        return []


# ── Get official URL via winget show ─────────────────────────
def get_official_url(app_id: str) -> tuple:
    """
    Uses winget show to extract the official installer URL.
    Returns (url, filename) or ("", "") if not found.
    """
    try:
        result = subprocess.run(
            ["winget", "show", "--id", app_id,
             "--accept-source-agreements"],
            capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="replace"
        )
        output = result.stdout

        # Extract installer URL from winget show output
        url_patterns = [
            r'Installer Url\s*:\s*(https?://\S+)',
            r'InstallerUrl\s*:\s*(https?://\S+)',
            r'Download Url\s*:\s*(https?://\S+)',
            r'Url\s*:\s*(https?://[^\s]+\.(?:exe|msi|msix|appx))',
        ]
        for pattern in url_patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                url      = match.group(1).strip()
                # Resolve redirect to get the real filename
                real_url = _resolve_redirect(url)
                filename = _url_to_filename(real_url or url, app_id)
                return (real_url or url), filename

        return "", ""
    except Exception:
        return "", ""


def _resolve_redirect(url: str, max_hops: int = 5) -> str:
    """
    Follow HTTP redirects (e.g. GitHub → CDN) and return the final URL.
    GitHub release links redirect to objects.githubusercontent.com or similar.
    """
    current = url
    for _ in range(max_hops):
        try:
            req = urllib.request.Request(current, method="HEAD",
                headers={"User-Agent": _ua()})
            # Don't auto-follow — we want to capture each hop
            opener = urllib.request.build_opener(
                urllib.request.HTTPRedirectHandler())
            with opener.open(req, timeout=10) as resp:
                final = resp.geturl()
                if final and final != current:
                    current = final
                    continue
                return current
        except urllib.error.HTTPError as e:
            if e.code in (301, 302, 303, 307, 308):
                loc = e.headers.get("Location", "")
                if loc:
                    current = loc
                    continue
            return current
        except Exception:
            return current
    return current


def _url_to_filename(url: str, fallback_id: str) -> str:
    """Extract a clean filename from a URL."""
    part = url.split("?")[0].split("#")[0]
    name = part.split("/")[-1]
    if name and "." in name and len(name) > 4:
        return name
    return f"{_safe_name(fallback_id)}_installer.exe"


def _ua() -> str:
    return ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36")


# ── Download from URL with real progress ─────────────────────
def download_from_url(url: str, dest_path: str,
                       progress_fn=None) -> bool:
    """
    Downloads from the official URL with byte-level progress reporting.
    Follows redirects properly (critical for GitHub releases).
    """
    try:
        req = urllib.request.Request(url, headers={"User-Agent": _ua()})

        # Use a redirect-following opener
        opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(),
            urllib.request.HTTPRedirectHandler()
        )
        with opener.open(req, timeout=120) as resp:
            total      = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 65536  # 64 KB chunks

            with open(dest_path, "wb") as f:
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_fn and total > 0:
                        pct    = downloaded / total
                        dl_mb  = downloaded / (1 << 20)
                        tot_mb = total / (1 << 20)
                        progress_fn(pct,
                                    f"Downloading: {dl_mb:.1f} MB / {tot_mb:.1f} MB  "
                                    f"({int(pct * 100)}%)")
                    elif progress_fn:
                        dl_mb = downloaded / (1 << 20)
                        progress_fn(0.5, f"Downloading: {dl_mb:.1f} MB...")

        return True

    except Exception as e:
        if progress_fn:
            progress_fn(0.0, f"Download error: {e}")
        return False


# ── Clean up YAML files winget leaves behind ─────────────────
def _cleanup_yaml(directory: str):
    """Remove winget YAML manifest files — not needed by user."""
    for f in glob.glob(os.path.join(directory, "**", "*.yaml"), recursive=True):
        try:
            os.remove(f)
        except Exception:
            pass
    # Remove empty subdirectories
    for root, dirs, files in os.walk(directory, topdown=False):
        for d in dirs:
            dp = os.path.join(root, d)
            try:
                if not os.listdir(dp):
                    os.rmdir(dp)
            except Exception:
                pass


# ── Main download entry point ─────────────────────────────────
def download_installer(app_id: str, app_name: str,
                        progress_fn=None, done_fn=None):
    """
    1. Gets official installer URL via winget show
    2. Resolves any redirects (e.g. GitHub → CDN)
    3. Downloads with real byte progress
    4. Removes YAML files left by winget
    5. Calls done_fn(success, message, file_path)
    We NEVER execute the installer.
    """
    def _worker():
        try:
            # Step 1: Get URL
            if progress_fn:
                progress_fn(0.03, f"Looking up official URL for {app_name}...")

            url, filename = get_official_url(app_id)

            if not url:
                if done_fn:
                    done_fn(False,
                            f"Could not find official download URL for {app_name}.\n"
                            f"Please download from the app's official website.",
                            "")
                return

            # Step 2: Prepare destination
            dl_dir = os.path.join(
                os.path.expanduser("~"), "Downloads",
                "PurgeKit", "Installers", _safe_name(app_name)
            )
            os.makedirs(dl_dir, exist_ok=True)
            dest = os.path.join(dl_dir, filename)

            if progress_fn:
                progress_fn(0.08, f"Source: {url[:70]}...")

            # Step 3: Download
            ok = download_from_url(url, dest, progress_fn)

            # Step 4: Remove YAML leftovers
            _cleanup_yaml(dl_dir)

            # Step 5: Verify and report
            if ok and os.path.exists(dest) and os.path.getsize(dest) > 10240:
                size_mb = os.path.getsize(dest) / (1 << 20)
                if progress_fn:
                    progress_fn(1.0,
                                f"✅ {filename}  ({size_mb:.1f} MB) — ready to install")
                if done_fn:
                    done_fn(True, dest, dest)
            else:
                # Clean up incomplete file
                if os.path.exists(dest):
                    os.remove(dest)
                if done_fn:
                    done_fn(False,
                            f"Download failed or file too small.\nURL: {url}",
                            "")

        except Exception as e:
            if progress_fn:
                progress_fn(0.0, f"Error: {e}")
            if done_fn:
                done_fn(False, str(e), "")

    threading.Thread(target=_worker, daemon=True).start()


# ── Open helpers ─────────────────────────────────────────────
def open_installer(file_path: str) -> bool:
    """Open the downloaded installer. User installs manually."""
    try:
        os.startfile(file_path)
        return True
    except Exception:
        try:
            import subprocess
            subprocess.Popen(["explorer", os.path.dirname(file_path)])
            return True
        except Exception:
            return False


def open_in_folder(file_path: str):
    """Reveal file in File Explorer."""
    try:
        import subprocess
        subprocess.Popen(["explorer", "/select,", file_path])
    except Exception:
        try:
            import subprocess
            subprocess.Popen(["explorer", os.path.dirname(file_path)])
        except Exception:
            pass


def _safe_name(name: str) -> str:
    safe = "".join(c for c in name if c.isalnum() or c in " -_.")
    return safe.strip()[:40] or "installer"
