# Changelog

All notable changes to PurgeKit will be documented here.

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
