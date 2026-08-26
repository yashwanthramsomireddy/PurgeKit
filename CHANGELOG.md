# Changelog

All notable changes to PurgeKit will be documented here.

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
