# Changelog

All notable changes to WinTempCleaner will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] - 2026-08-26

### Added
- Initial release of WinTempCleaner as a `.bat` script
- Cleans User Temp, Windows System Temp, Prefetch
- Cleans Windows Update Cache (with service stop/start handling)
- Cleans Delivery Optimization Files (with service stop/start handling)
- Cleans Thumbnail Cache (with Explorer restart)
- Cleans Recent Files and Jump Lists
- Flushes DNS Cache
- Cleans Google Chrome cache (Cache, Code Cache, GPUCache)
- Cleans Mozilla Firefox cache (all profiles: cache2, startupCache, jumpListCache)
- Cleans Microsoft Edge cache (Cache, Code Cache, GPUCache)
- Automates Windows Disk Cleanup with all categories enabled (sageset 99)
- Progress bar displayed during each step
- Structured log file saved to Desktop after every run
- Admin privilege check on startup
- C:\Downloads is explicitly excluded from all operations
- MIT License
