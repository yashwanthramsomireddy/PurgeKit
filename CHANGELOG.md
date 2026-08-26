# Changelog

All notable changes to PurgeKit will be documented here.

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
