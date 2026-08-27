# Changelog

All notable changes to PurgeKit will be documented here.

---

## [3.2.0] - 2026-08-27

### Added
- **Auto-update system** — full download and install from GitHub releases:
  - On launch, checks GitHub API for newer version
  - About tab shows update status: ✅ up to date / 🟡 update available / ⚠ check failed
  - "Download & Install" button appears when update found
  - Progress bar shows download % and MB downloaded / total MB
  - After download, a batch script replaces the exe, relaunches new version, and cleans up automatically
  - Works only for compiled `.exe` — running via `python PurgeKit.py` shows a link to GitHub instead
  - Retry button shown if download fails
  - If no direct download URL found in release assets, falls back to opening GitHub releases page

### Changed
- `updater.py` now returns `(is_available, version, download_url, release_url)` — 4 values
- `check_for_update` searches release assets for `PurgeKit.exe` download URL
- `CURRENT_VERSION` synced to `3.2` in updater.py
- `APP_VERSION` updated to `3.2`

---

## [3.1.6] - 2026-08-27

### Fixed
- **App icon** — icon now saves to `%APPDATA%\PurgeKit\purgekit.ico` and uses `iconbitmap(default=...)` which works correctly for compiled exe; exe file icon fixed via `--icon assets\icon.ico` PyInstaller flag
- **Update checker showing false positive** — `CURRENT_VERSION` in updater.py was stuck at `3.0`, now correctly set to `3.1.5` so it won't falsely report an update
- **generate_icon.py** — new helper script that creates `assets/icon.ico` before building
- **build.bat** — updated to run `generate_icon.py` first and pass `--icon assets\icon.ico` to PyInstaller

---

## [3.1.5] - 2026-08-27

### Changed
- **About tab** — removed ❤️ icon from "Built by", removed 📍 icon from Location
- **First run wizard** — removed 📍 icon from location line

---

## [3.1.4] - 2026-08-27

### Removed
- **History tab** — removed entirely from compact and spacious modes (history still saved in background for future use)

---

## [3.1.3] - 2026-08-27

### Removed
- **Startup Programs tab** — removed entirely from both compact and spacious modes

### Fixed
- **Tasks tab — sizes now work correctly**:
  - All task rows show their folder size (not just checked ones)
  - Total only counts checked tasks — so Select All shows full system total
  - Dry Run toggle, Select All, and Deselect All all trigger a size refresh
  - Unchecked rows show size in dim color; checked rows show in accent color
- **Dry Run + Select All** — pressing Select All then toggling Dry Run now correctly updates total size label

---

## [3.1.2] - 2026-08-27

### Fixed
- **Scan tab** — pressing Scan Now clears previous results, resets clean progress bar and button before showing fresh results
- **Tasks tab sizes** — added 300ms delay before starting background size scan so all row widgets exist first; size labels now reliably update
- **Startup tab disable/enable** — replaced immediate refresh with 400ms delayed refresh to let registry settle; improved error message when toggle fails

---

## [3.1.1] - 2026-08-27

### Added
- **Scan tab — Clean progress bar**: pressing "Clean Selected" now shows a progress bar and per-item status label below the buttons; button changes to "⏳ Cleaning..." while running and restores when done
- **Tasks tab — Total size header**: a size bar below Select/Deselect shows total size of all checked tasks (live updated as background scan runs)
- **Tasks tab — Per-row size**: each task row now shows its folder size on the right (background scan, shows "—" then updates to actual size)

---

## [3.1.0] - 2026-08-27

### Fixed
- **Compact mode tab spacing** — removed unsupported `tab_length` arg, fixed via segmented button font config and inner padding per tab
- **Spacious mode navigation** — replaced missing tabview with a proper left sidebar nav with active highlight
- **Theme applies on the fly** — changing theme/language in Settings instantly rebuilds UI, no restart needed
- **About tab alignment** — fixed-width left column (140px), both columns left-aligned, consistent spacing
- **Startup tab** — each program now shows Enable/Disable button, full path wraps properly (no truncation)
- **Scan tab** — added checkboxes per result, Select All / Deselect All, and Clean Selected button
- **Dry Run mode** — topbar shows "🔍 DRY RUN ON" indicator, START PURGE button turns orange with "DRY RUN" text, toggle in both topbar and settings in sync
- **Taskbar / pinned icon** — uses PurgeKit icon via `SetCurrentProcessExplicitAppUserModelID` so pinned taskbar shortcut shows correct icon

### Changed
- Spacious mode now uses sidebar navigation (Tasks, Log, Scan, History, Startup, Settings, About) instead of missing tabs
- Scan Clean Selected runs force_delete on selected paths directly
- Log panel always visible on right side in spacious mode

---

## [3.0.0] - 2026-08-26

### Added
- Full project restructure into modules: core/, ui/, lang/
- **29 languages**: English, Tamil, Hindi, Telugu, Kannada, Malayalam, Marathi, Bengali, Gujarati, Punjabi, Urdu, Spanish, French, German, Italian, Portuguese, Russian, Chinese, Japanese, Korean, Arabic, Turkish, Dutch, Polish, Vietnamese, Thai, Indonesian, Malay, Swahili
- **Theme selector**: Green, Blue, Purple — applied across entire UI including icon
- **First run wizard**: Language, theme, and quick options on first launch
- **PIN Lock**: 6-digit PIN with SHA-256 hash storage, 3-attempt lockout, 30-second cooldown
- **Dry Run mode**: Preview what would be deleted without deleting anything
- **Junk Scanner tab**: Scans and ranks top junk folders by size
- **Space saved history**: Bar chart + per-run history (last 50 runs)
- **Startup Programs Manager**: View programs that run at Windows startup
- **Settings tab**: Language, theme, dry run, autostart, PIN, scheduler, whitelist — all in one place
- **Scheduler**: Weekly/monthly auto-purge via Windows Task Scheduler
- **Auto-update checker**: Checks GitHub API for new releases on startup
- **Windows toast notification**: Shows space freed after purge
- **Whitelist / Exclude paths**: Add folders to never-delete list
- **Remember last selection**: Saves and restores task selections between runs
- **CLI silent mode**: `PurgeKit.exe --silent` for automation
- **Inno Setup installer**: Professional Windows installer with Start Menu + Desktop shortcuts
- **Logs now saved to**: `Downloads\PurgeKit\Logs\PurgeKit_YYYYMMDD_HHMMSS.txt`
- **Tab spacing fixed**: No overlap or spacing issues in compact/spacious modes
- **Per-step space freed**: Shows bytes freed per task in log
- **Summary block**: Total space freed, time taken, shown at end of each run

---

## [2.2.0] - 2026-08-26

### Added
- **Default compact mode** — app opens compact by default
- **Drive detection fixed** — detects all drives by checking actual disk space (not drive type), so D:\, E:\ etc. all appear correctly
- **New temp/cache locations:**
  - U1b: LocalAppData Temp (`%LOCALAPPDATA%\Temp`)
  - U4: IE/Edge WebCache (`%LOCALAPPDATA%\Microsoft\Windows\WebCache`)
  - U5b: User Crash Dumps (`%LOCALAPPDATA%\CrashDumps`)
  - B1b: Chrome Service Worker CacheStorage
  - B3b: Edge Service Worker CacheStorage
  - D1: npm cache (`%APPDATA%\npm-cache`) — Developer, unchecked
  - D2: pip cache (`%LOCALAPPDATA%\pip\cache`) — Developer, unchecked
  - O9: Extra DNS flush — Optional, unchecked
- **Developer Tools phase** — npm + pip cache, unchecked by default
- **Auto-start toggle** in About panel — enable/disable PurgeKit on Windows startup via registry
- **Updated author credit** — "Built with ❤️ by Yashwanth Ram Somireddy, 📍 Chennai, India (TeamExyKings)"
- Browser cache handlers now log per-browser success message

---

## [2.1.0] - 2026-08-26

### Added
- **About tab / popup** with GitHub link, TeamExyKings credit, version info
- **Per-drive Disk Cleanup** — auto-detects all drives, shows label + free/total space, checkbox per drive
- **Icon Cache** cleaner (U10) — restarts Explorer automatically
- **Clipboard History** clear (U11)
- **Windows Store Cache** reset via wsreset (U12)
- **Optional / Power User section** (unchecked by default):
  - O1: Event Logs (Application + System + Security)
  - O2: Recycle Bin on all drives
  - O3: Windows Telemetry Data
  - O4: Cortana / Windows Search History
  - O5: ARP Cache flush
  - O6: NetBIOS Cache flush
  - O7: Winsock Reset (warns reboot required)
  - O8: Windows Search Index rebuild
- Warning label shown under each optional item explaining the risk
- `⚠` icon next to optional checkboxes
- About popup in spacious mode, About tab in compact mode
- GitHub button opens browser directly

### Removed
- Hibernation file, Old Restore Points, Windows Installer cache — excluded for safety

---

## [2.0.0] - 2026-08-26

### Added
- Full Python GUI using CustomTkinter
- Pitch black dark mode by default, green accent
- Compact / Spacious toggle switch in top bar
- Checkbox per cleaning task — full control
- Select All / Deselect All buttons
- Windows Activity History step with radio options (Delete / Disable / Skip)
- Live log panel with colour-coded output (success/warn/error/dim)
- Progress bar with current step label
- Log auto-saved to Downloads as `PurgeKit_YYYYMMDD_HHMMSS.txt` after every run
- Manual Save Log button
- Reboot warning dialog if T3 (pending delete) was triggered
- Generated unique PurgeKit icon (broom + green glow)
- UAC admin auto-relaunch on startup
- `requirements.txt` for easy dependency install
- `build.bat` to compile to standalone `.exe` via PyInstaller

---

## [1.1.0] - 2026-08-26

### Added
- Renamed project from WinTempCleaner to **PurgeKit**
- Y/N prompt for every individual cleaning step
- **Phase 1 — System Level** (in order): Windows System Temp, Prefetch, Windows Update Cache, Delivery Optimization, WER, CBS Logs, Crash Dumps, Font Cache, DataStore Logs, Installer Patch Cache, DNS Cache
- **Phase 2 — User Level** (in order): User Temp, Thumbnail Cache, Recent Files, INetCache, D3DSCache, Teams Cache, VS Code Cache, Office Cache, Spotify Cache
- **Windows Activity History** step with 3 options: Delete only (D), Delete + Disable via registry (X), Skip (N)
- **3-Technique force-delete cascade**: T1 robocopy mirror → T2 takeown+icacls → T3 pending reboot delete
- Reboot notice shown at end if T3 was triggered
- Phase 3 — Browser cache (Chrome, Firefox, Edge) with Y/N
- Phase 4 — Disk Cleanup (all categories automated)
- ASCII banner on startup
- Section headers per phase
- Structured log with technique outcome per step

### Changed
- All folder recreations after deletion to prevent app errors
- Services stopped/restarted properly per step

---

## [1.0.0] - 2026-08-26

### Added
- Initial release as WinTempCleaner
- Basic temp, cache, browser, update, prefetch, DNS, disk cleanup
- Progress bar and desktop log file
- Admin privilege check
- MIT License
