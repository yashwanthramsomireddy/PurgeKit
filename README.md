# 🧹 PurgeKit

> A lightweight, open-source Windows temp and cache cleaner — no installation needed.  
> Built by [TeamExyKings](https://github.com/TeamExyKings)

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%2F11-blue.svg)
![Version](https://img.shields.io/badge/Version-1.1-orange.svg)
![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)

---

## ✨ Features

- ✅ **Y/N prompt for every step** — you choose what gets cleaned
- ✅ **3-Technique force-delete cascade** — handles locked files gracefully
- ✅ **System + User level** cleaning in order
- ✅ **Browser cache** — Chrome, Firefox, Edge
- ✅ **Windows Activity History** — delete only OR disable permanently
- ✅ **Disk Cleanup** fully automated (all categories)
- ✅ **Structured log file** saved to your Desktop after every run
- ✅ **Progress bar** shown during the run
- ✅ **Reboot notice** if pending deletes were scheduled
- ✅ `C:\Downloads` is **never touched**

---

## 📋 What It Cleans

### Phase 1 — System Level

| ID | Category | Path |
|---|---|---|
| S1 | Windows System Temp | `C:\Windows\Temp` |
| S2 | Prefetch Files | `C:\Windows\Prefetch` |
| S3 | Windows Update Cache | `C:\Windows\SoftwareDistribution\Download` |
| S4 | Delivery Optimization Files | `C:\Windows\SoftwareDistribution\DeliveryOptimization` |
| S5 | Windows Error Reporting | `C:\ProgramData\Microsoft\Windows\WER\ReportQueue/Archive` |
| S6 | CBS Logs | `C:\Windows\Logs\CBS` |
| S7 | Crash Dumps | `C:\Windows\Minidump` + `MEMORY.DMP` |
| S8 | Windows Font Cache | `C:\Windows\ServiceProfiles\LocalService\AppData\Local\FontCache` |
| S9 | SoftwareDistribution DataStore Logs | `C:\Windows\SoftwareDistribution\DataStore\Logs` |
| S10 | Windows Installer Patch Cache | `C:\Windows\Installer\$PatchCache$` |
| S11 | DNS Cache | Flushed via `ipconfig /flushdns` |

### Phase 2 — User Level

| ID | Category | Path |
|---|---|---|
| U1 | User Temp Folder | `%TEMP%` |
| U2 | Thumbnail Cache | `%LOCALAPPDATA%\Microsoft\Windows\Explorer\thumbcache_*.db` |
| U3 | Recent Files & Jump Lists | `%APPDATA%\Microsoft\Windows\Recent` |
| U4 | IE / Legacy Edge Cache | `%LOCALAPPDATA%\Microsoft\Windows\INetCache` |
| U5 | DirectX Shader Cache | `%LOCALAPPDATA%\D3DSCache` |
| U6 | Microsoft Teams Cache | `%APPDATA%\Microsoft\Teams\Cache + blob_storage` |
| U7 | Visual Studio Code Cache | `%APPDATA%\Code\Cache + CachedData` |
| U8 | Microsoft Office File Cache | `%LOCALAPPDATA%\Microsoft\Office\16.0\OfficeFileCache` |
| U9 | Spotify Cache | `%LOCALAPPDATA%\Spotify\Storage` |
| U10 | Windows Activity History | `ActivitiesCache.db` — Delete only OR Disable permanently |

### Phase 3 — Browsers

| ID | Browser | What Is Cleared |
|---|---|---|
| B1 | Google Chrome | Cache, Code Cache, GPUCache |
| B2 | Mozilla Firefox | cache2, startupCache, jumpListCache (all profiles) |
| B3 | Microsoft Edge | Cache, Code Cache, GPUCache |

### Phase 4 — Disk Cleanup

| ID | Action |
|---|---|
| DC | All Windows Disk Cleanup categories automated via `sageset 99` |

---

## 🔒 3-Technique Force Delete

PurgeKit uses a cascade of 3 techniques to handle locked files:

| Technique | Method | When Used |
|---|---|---|
| **T1** | `robocopy /MIR` empty folder mirror | First attempt — fastest |
| **T2** | `takeown` + `icacls` + force delete | If T1 fails |
| **T3** | Register pending delete on next Windows reboot | If T2 fails |

If T3 is used, PurgeKit will notify you at the end and ask you to restart your PC.

---

## 🕵️ Windows Activity History

By default, Windows stores your activity history locally in a hidden SQLite database:

```
%LOCALAPPDATA%\ConnectedDevicesPlatform\<profile>\ActivitiesCache.db
```

This file tracks: apps you opened, files you viewed, websites visited, and Timeline data.

PurgeKit gives you **3 options**:

| Choice | What Happens |
|---|---|
| `D` | Delete `ActivitiesCache.db` only (one-time clean) |
| `X` | Delete the file **AND** disable Activity History via registry permanently |
| `N` | Skip |

---

## 🚀 How to Use

### Requirements
- Windows 10 or Windows 11
- Administrator privileges

### Steps

1. Download `PurgeKit.bat` from [Releases](https://github.com/TeamExyKings/PurgeKit/releases)
2. Right-click the file
3. Select **"Run as administrator"**
4. Answer **Y** or **N** for each step
5. Watch the progress bar
6. Log file is saved to your **Desktop** when complete

---

## 📊 Log File

After every run, a structured log file is saved at:

```
C:\Users\<YourName>\Desktop\PurgeKit_Log.txt
```

### Sample Log Output

```
============================================================
  PurgeKit v1.1  |  MIT License  |  TeamExyKings
  Run Date : Wed 08/26/2026  10:45:00.00
  User     : Yash
  Machine  : STERLING-PC
============================================================

════════════════════════════════════════════════════════
  PHASE 1 — SYSTEM LEVEL CLEANING
════════════════════════════════════════════════════════

  STEP S1 : Windows System Temp
  Path     : C:\Windows\Temp
  User     : Y
  [T1-OK] Technique 1 (robocopy) succeeded

  STEP S3 : Windows Update Cache
  Path     : C:\Windows\SoftwareDistribution\Download
  User     : Y
  Stopping wuauserv + bits...
  Restarting wuauserv + bits...
  [T1-OK] Technique 1 (robocopy) succeeded

  STEP U10 : Windows Activity History
  Action   : Delete DB + Disable via Registry
  Status   : DONE

============================================================
  ALL TASKS COMPLETED
  End Time : Wed 08/26/2026  10:46:30.00
============================================================
```

---

## 🛡️ Safety Notes

- Windows services (`wuauserv`, `bits`, `DoSvc`, `FontCache`) are stopped before cleaning and restarted after
- Browsers (Chrome, Firefox, Edge) and apps (Teams, Spotify, VS Code) are force-closed before their cache is cleaned
- Explorer is briefly restarted to clear thumbnail cache locks
- `C:\Downloads` and user documents are **never touched**
- Bookmarks, passwords, browser history, and extensions are **never deleted**
- Only cache files are removed

---

## 🗺️ Roadmap

- [x] v1.0 — Initial `.bat` script with progress bar and log file
- [x] v1.1 — Y/N per step, 3-technique force delete, Activity History, all system+user folders, browser cache
- [ ] v2.0 — Python GUI (CustomTkinter) with checkboxes, progress bar UI, log viewer panel
- [ ] v2.1 — Packaged as `.exe` via PyInstaller
- [ ] v2.2 — Windows installer via Inno Setup
- [ ] v3.0 — Task Scheduler integration for automated cleaning

---

## 🤝 Contributing

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m "Add: description"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📁 Project Structure

```
PurgeKit/
│
├── PurgeKit.bat       # Main cleaner script
├── README.md          # This file
├── LICENSE            # MIT License
└── CHANGELOG.md       # Version history
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## ⚠️ Disclaimer

PurgeKit deletes temporary and cache files only. It is provided **as-is** without warranty. Always ensure important data is backed up before running any system maintenance tool. The authors are not responsible for any unintended data loss.

---

## 👤 Author

**TeamExyKings**  
GitHub: [@TeamExyKings](https://github.com/TeamExyKings)

---

*If PurgeKit helped you, give it a ⭐ on GitHub!*
