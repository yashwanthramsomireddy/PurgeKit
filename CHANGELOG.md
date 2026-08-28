# Changelog

All notable changes to PurgeKit will be documented here.

---

## [3.6.0] - 2026-08-28

### Added
- **3rd Party Apps tab** — separate tab with 6 categories, all unchecked by default:
  - 🎮 Games & Launchers: Steam, Epic Games, GOG Galaxy, Riot, Battle.net, Overwolf, Origin, Ubisoft Connect
  - 💬 Communication: Telegram, Signal, Outlook offline cache
  - 📦 Other 3rd Party: Slack, Postman, Skype, Google Drive, Dropbox, Figma, WebEx, Brave, Vivaldi, Opera, Chrome Canary, NVIDIA, AMD, Teams add-in, Spotify UWP, CrashRpt
  - 🎨 Adobe: All Adobe apps (Media Cache, Acrobat, Premiere, After Effects, Illustrator, InDesign, XD, Lightroom, Bridge, Creative Cloud)
  - 🎬 Media: OBS Studio, DaVinci Resolve, HandBrake, VLC
  - 🔧 Dev Tools: JetBrains IDEs, Visual Studio, Electron Builder
  - Per-category ✔ / ✘ buttons on each section header
  - Own progress bar and Purge button
  - Total selected size display
- **Per-category Select All / Deselect All in Tasks tab** — ✔ / ✘ buttons on every phase header row
- **Donate tab — location-aware**:
  - Detects country via IP (ipapi.co)
  - India: Razorpay primary (₹) + PayPal secondary
  - International: PayPal primary ($) + Razorpay secondary
- **New task paths**: Games (G1-G12), Communication (C1-C4), Media (M1-M6), DevTools (V1-V5)
- **Total tasks: 104+ across 9 phases**

### Changed
- `APP_VERSION` → `3.6`, `CURRENT_VERSION` → `3.6`
- ThirdParty and Adobe phases remain in Tasks tab for now (also in 3rd Party tab)

---

## [3.5.3] - 2026-08-28

### Added
- **3rd Party Apps phase** (19 items, all unchecked by default):
  Slack, Postman, Skype, Google Drive, Dropbox, Figma, WebEx,
  Brave, Vivaldi, Opera, Chrome Canary, NVIDIA DXCache/GLCache/Temp,
  AMD DxCache, Teams Meeting Add-in, Spotify UWP, CrashRpt
- **Adobe Apps phase** (12 items, all unchecked by default):
  Media Cache, Media Cache Files, Acrobat DC, Premiere Pro,
  After Effects, Illustrator, InDesign, XD, Lightroom,
  Bridge, Creative Cloud Desktop Logs, CoreSync Cache
- **Developer phase additions** (D6-D11, all unchecked):
  NuGet HTTP Cache, NuGet Packages Store, Yarn, pnpm, Cargo, Android Studio
- **User phase additions** (U24-U34, checked by default):
  DISM Logs, MeasuredBoot Logs, Windows Diagnostics, LocalService Temp,
  NetworkService Temp, Jump List AutoDest, Jump List CustomDest,
  Temp Low Integrity, CrashRpt, Chrome Extension Storage, Edge Extension Storage
- **Optional additions**: Skype Media Cache Full (O10), Adobe Common Full (O11)
- Total tasks: 104 across 7 phases

### Changed
- `APP_VERSION` → `3.5.3`, `CURRENT_VERSION` → `3.5.3`

---

## [3.5.2] - 2026-08-28

### Added
- **New cleaning paths**:
  - U21: Downloaded Installations Cache (`%LOCALAPPDATA%\Downloaded Installations`)
  - U22: Squirrel Temp (`%LOCALAPPDATA%\SquirrelTemp`) — app installer temp files
  - U23: iTunes Cache (`%LOCALAPPDATA%\Apple Computer\iTunes`)

### Fixed
- **Activity History radio buttons** — larger, clearly visible selection indicator; bold text; accent color border; descriptive subtitle under each option; reordered to Skip / Delete / Disable
- **Disk Cleanup label** — added clear description: "Runs Windows Disk Cleanup tool on selected drives. Only removes temp files, system logs, update backups, and recycle bin — never your personal files or apps."
- **Windows Defender scan history (U19)** — changed to target only `History\Store` subfolder instead of entire `History` tree; reduces scan time from 5+ min to seconds
- **Software Updater scroll bg** — force-sets `_parent_canvas` bg color on render to prevent white background showing on dynamic theme change; fixed without requiring re-scan

---

## [3.5.1] - 2026-08-28

### Fixed
- **GitHub download redirect** — GitHub release URLs redirect to CDN (objects.githubusercontent.com); now using a proper redirect-following opener so all GitHub-hosted installers download correctly
- **YAML files cleaned up** — winget leaves `.yaml` manifest files in the download folder; these are now automatically deleted after download, keeping the folder clean with only the installer
- **File size validation** — incomplete downloads (< 10 KB) are deleted and reported as failed instead of silently left

---

## [3.5.0] - 2026-08-28

### Added
- **White Theme** — clean light mode with green accents; switches CustomTkinter to light appearance mode automatically; selectable in Settings and First Run Wizard

### Changed
- **Software Updater — Official URL download**:
  - Uses `winget show --id <app>` to extract the official installer URL from the app manifest
  - Downloads **directly from the vendor's official URL** (same as downloading from the app website)
  - Real byte-level progress bar: `12.4 MB / 38.1 MB  (32%)`
  - Saves to `Downloads\PurgeKit\Installers\<AppName>\`
  - No YAML manifests, no portable packages — just the official installer
  - Zero Defender issues — file comes from the vendor, not winget CDN
  - User opens installer manually — we never execute anything
  - File Explorer opens at download location after download completes
- `CURRENT_VERSION` → `3.5` in updater.py
- `APP_VERSION` → `3.5`

---

## [3.4.2] - 2026-08-28

### Changed
- **Software Updater — Download & Open approach**:
  - Removed silent background installation entirely
  - Each app now has its own **⬇ Download** button
  - Download uses `winget download` to save installer to `Downloads\PurgeKit\Installers\<AppName>\`
  - After download, button changes to **▶ Open Installer** — user runs it themselves
  - File Explorer opens at the download location automatically
  - **One app at a time** — all other Download buttons disabled while one is in progress
  - No silent execution — PurgeKit never runs the installer, only downloads it
  - This approach has zero Defender issues and zero legal concerns

### Removed
- Select All / Deselect All buttons (not needed — each app has its own button)
- `update_selected_apps()` function — replaced by `download_installer()` + `open_installer()`

---

## [3.4.1] - 2026-08-28

### Fixed
- **Software Updater row height** — rows were too tall due to `pack_propagate(False)` frames; switched to `grid` layout so rows are compact and clean
- **Software Updater header** — switched to grid to match data rows alignment
- **"None" button renamed** to "Deselect All", "All" renamed to "Select All" for clarity

### Info
- winget updates download and install **silently in background** — no setup wizard appears
- Windows Defender may scan the downloaded installer briefly — this is normal, click Allow
- Progress and results appear in the Log tab and progress bar

---

## [3.4.0] - 2026-08-28

### Added
- **Software Updater tab** — powered by Microsoft winget (Windows Package Manager)
  - Scans all installed apps and shows updates available
  - Table: App Name | Current Version | Latest | Source | Status
  - Checkbox per app — select exactly what to update
  - "Update Selected" button with per-app status + progress bar
  - Select All / Deselect All for update list
  - Graceful fallback with link to install winget if not present
  - 100% free, no third-party databases, uses official Microsoft tooling
- **Social Media Kit** (HTML tool — PurgeKit_SocialKit.html):
  - Social Card: Instagram/TikTok Reel (1080×1920), Square (1080×1080), OG/Twitter (1200×630), Pinterest (1000×1500), WhatsApp (800×800), Icon (512×512)
  - Social Media Kit: brand colors, ready-to-post captions for Twitter/Instagram/LinkedIn/Pinterest, hashtag sets, platform specs table
  - YouTube Assets: Channel Banner (2560×1440), Thumbnail A — Release (1280×720), Thumbnail B — Tutorial (1280×720), Watermark (200×200)
  - All assets downloadable as PNG from the browser
- **Project Documentation** (PurgeKit_ProjectDoc.md) — full markdown docs
- **Word Document** (PurgeKit_ProjectDoc.docx) — professional formatted doc with all sections
- **Excel Workbook** (PurgeKit_ProjectWorkbook.xlsx) — 5 sheets:
  - Tech Stack, Feature Tracker, Issue Tracker, GitHub, Donation

### Changed
- `core/software_updater.py` — new module (winget wrapper)
- `lang/*.json` — added `tab_updater` key to all 29 language files
- `APP_VERSION` → `3.4`, `CURRENT_VERSION` → `3.4`

---

## [3.3.1] - 2026-08-27

### Added
- **SysInfo tab** — renamed from lowercase `tab_sysinfo` to **💻 SysInfo** across all 29 language files
- **Donate button** in About tab — PayPal link (paypal.me/yash92duster) with blue PayPal button styling

### Fixed
- **Inno Setup** — `runascurrentuser` flag fix confirmed working, installs to `C:\Program Files (x86)\PurgeKit\`

---

## [3.3.0] - 2026-08-27

### Added
- **System Info tab** — shows OS, Windows build, machine name, uptime, RAM usage with progress bar, disk usage per drive with progress bar, processor info; auto-loads on open with Refresh button
- **New cleaning paths (User phase)**:
  - U13: Zoom Cache (`%APPDATA%\Zoom\data`)
  - U14: Zoom Logs (`%APPDATA%\Zoom\logs`)
  - U15: Discord Cache (`%APPDATA%\discord\Cache`)
  - U15b: Discord Code Cache (`%APPDATA%\discord\Code Cache`)
  - U16: WhatsApp Desktop Cache (`%APPDATA%\WhatsApp\Cache`)
  - U17: OneDrive Logs (`%LOCALAPPDATA%\Microsoft\OneDrive\logs`)
  - U18: Teams 2.0 Cache (new MS Teams package)
  - U19: Windows Defender Scan History
  - U20: Windows Update Logs (`C:\Windows\Logs\WindowsUpdate`)
- **New cleaning paths (Developer phase, unchecked by default)**:
  - D3: Maven Cache (`%USERPROFILE%\.m2\repository`)
  - D4: Gradle Cache (`%USERPROFILE%\.gradle\caches`)
  - D5: Docker Logs (`%LOCALAPPDATA%\Docker\log`)

### Fixed
- **Default checkboxes** — Optional and Developer phases now always start unchecked regardless of last saved selection
- **Inno Setup installer** — added `runascurrentuser` flag to [Run] section, fixes `code 740 elevation` error after install completes
- **installer.iss** — updated to v3.3, removed startup registry entry from installer (handled inside app instead)

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
