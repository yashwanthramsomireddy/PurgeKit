# 🧹 PurgeKit

> A lightweight, open-source Windows temp and cache cleaner with a modern GUI.
> Built by [Yashwanth Ram Somireddy](https://github.com/yashwanthramsomireddy) — Chennai, India (TeamExyKings)

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%2F11-blue.svg)
![Version](https://img.shields.io/badge/Version-3.2-orange.svg)
![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)

---

## ✨ Features

- ✅ **Modern GUI** — pitch black dark theme with Green / Blue / Purple accent
- ✅ **29 Languages** — English, Tamil, Telugu, Hindi, and 25 more
- ✅ **Auto-update** — detects and installs new releases automatically
- ✅ **First run wizard** — pick language, theme, and options on first launch
- ✅ **PIN Lock** — 6-digit app lock with SHA-256 hash, 3-attempt lockout
- ✅ **Dry Run mode** — preview what will be deleted without deleting anything
- ✅ **Junk Scanner** — scans and ranks top junk folders by size, clean directly from results
- ✅ **Folder size per task** — shows size of each folder before cleaning
- ✅ **Total size counter** — shows total space that will be freed before purge
- ✅ **3-Technique force delete** — robocopy → takeown → reboot schedule
- ✅ **Per-drive Disk Cleanup** — select which drives to clean
- ✅ **Scheduler** — weekly/monthly auto-purge via Windows Task Scheduler
- ✅ **Whitelist** — exclude any folder from being cleaned
- ✅ **Remember last selection** — restores task choices on reopen
- ✅ **Windows toast notification** — shows space freed after purge
- ✅ **Log files** — saved to `Downloads\PurgeKit\Logs\` after every run
- ✅ **CLI silent mode** — `PurgeKit.exe --silent` for automation
- ✅ **Compact / Spacious** view toggle
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
| S5 | Windows Error Reporting | `C:\ProgramData\Microsoft\Windows\WER` |
| S6 | CBS Logs | `C:\Windows\Logs\CBS` |
| S7 | Crash Dumps | `C:\Windows\Minidump` + `MEMORY.DMP` |
| S8 | Windows Font Cache | `C:\Windows\ServiceProfiles\LocalService\AppData\Local\FontCache` |
| S9 | SoftwareDistribution Logs | `C:\Windows\SoftwareDistribution\DataStore\Logs` |
| S10 | Windows Installer Patch Cache | `C:\Windows\Installer\$PatchCache$` |
| S11 | DNS Cache | Flushed via `ipconfig /flushdns` |

### Phase 2 — User Level

| ID | Category | Path |
|---|---|---|
| U1 | User Temp Folder | `%TEMP%` |
| U1b | LocalAppData Temp | `%LOCALAPPDATA%\Temp` |
| U2 | Thumbnail Cache | `%LOCALAPPDATA%\Microsoft\Windows\Explorer` |
| U3 | Recent Files & Jump Lists | `%APPDATA%\Microsoft\Windows\Recent` |
| U4 | IE / Edge WebCache | `%LOCALAPPDATA%\Microsoft\Windows\WebCache` |
| U4b | IE / Legacy INetCache | `%LOCALAPPDATA%\Microsoft\Windows\INetCache` |
| U5 | DirectX Shader Cache | `%LOCALAPPDATA%\D3DSCache` |
| U5b | User Crash Dumps | `%LOCALAPPDATA%\CrashDumps` |
| U6 | Microsoft Teams Cache | `%APPDATA%\Microsoft\Teams\Cache` |
| U7 | VS Code Cache | `%APPDATA%\Code\Cache` |
| U8 | Microsoft Office Cache | `%LOCALAPPDATA%\Microsoft\Office\16.0\OfficeFileCache` |
| U9 | Spotify Cache | `%LOCALAPPDATA%\Spotify\Storage` |
| U10 | Icon Cache | `%LOCALAPPDATA%\IconCache.db` |
| U11 | Clipboard History | Windows Clipboard |
| U12 | Windows Store Cache | `wsreset.exe` |

### Phase 3 — Browser Level

| ID | Browser | What Is Cleared |
|---|---|---|
| B1 | Google Chrome | Cache, Code Cache, GPUCache |
| B1b | Google Chrome | Service Worker CacheStorage |
| B2 | Mozilla Firefox | cache2, startupCache, jumpListCache (all profiles) |
| B3 | Microsoft Edge | Cache, Code Cache, GPUCache |
| B3b | Microsoft Edge | Service Worker CacheStorage |

### Phase 4 — Developer Tools (unchecked by default)

| ID | Category | Path |
|---|---|---|
| D1 | npm Cache | `%APPDATA%\npm-cache` |
| D2 | pip Cache | `%LOCALAPPDATA%\pip\cache` |

### Phase 5 — Optional / Power User (unchecked by default)

| ID | Category | Note |
|---|---|---|
| O1 | Event Logs | App, System, Security logs |
| O2 | Recycle Bin | All drives |
| O3 | Windows Telemetry | `C:\ProgramData\Microsoft\Diagnosis` |
| O4 | Cortana / Search History | Windows Search cache |
| O5 | ARP Cache | Flushed via `arp -d *` |
| O6 | NetBIOS Cache | Flushed via `nbtstat -R` |
| O7 | Winsock Reset | ⚠ Requires reboot |
| O8 | Search Index Rebuild | ⚠ Search slow for hours after |
| O9 | Extra DNS Flush | Additional DNS pass |

---

## 🔄 Auto-Update

PurgeKit checks GitHub for new releases on every launch.

- If a newer version is found, an **Update Available** banner appears in the About tab
- Click **Download & Install** — a progress bar shows download status
- After download, the app closes, the new exe replaces the old one, and PurgeKit relaunches automatically
- Works only with the compiled `.exe` version

---

## 🔒 3-Technique Force Delete

PurgeKit uses a cascade of 3 techniques to handle locked files:

| Technique | Method | When Used |
|---|---|---|
| **T1** | `robocopy /MIR` empty folder mirror | First attempt — fastest |
| **T2** | `takeown` + `icacls` + force delete | If T1 fails |
| **T3** | Register pending delete on next reboot | If T2 fails — reboot notice shown |

---

## 🌐 Supported Languages (29)

English, Tamil, Hindi, Telugu, Kannada, Malayalam, Marathi, Bengali, Gujarati, Punjabi, Urdu, Spanish, French, German, Italian, Portuguese, Russian, Chinese (Simplified), Japanese, Korean, Arabic, Turkish, Dutch, Polish, Vietnamese, Thai, Indonesian, Malay, Swahili

---

## 🎨 Themes

| Theme | Accent Color |
|---|---|
| Green (default) | `#00e676` |
| Blue | `#40c4ff` |
| Purple | `#ea80fc` |

Theme applies instantly without restarting the app.

---

## 🚀 How to Use

### Requirements
- Windows 10 or Windows 11
- Administrator privileges

### Steps

1. Download `PurgeKit.exe` from [Releases](https://github.com/yashwanthramsomireddy/PurgeKit/releases)
2. Double-click → Allow UAC prompt
3. First launch opens the setup wizard (language, theme, options)
4. Select your tasks → **START PURGE**
5. Log is auto-saved to `Downloads\PurgeKit\Logs\` after every run

### CLI Silent Mode

Run a full purge silently (uses last saved task selection):

```bash
PurgeKit.exe --silent
```

---

## 📊 Log Files

Logs are saved to:

```
C:\Users\<YourName>\Downloads\PurgeKit\Logs\PurgeKit_YYYYMMDD_HHMMSS.txt
```

Each log includes machine name, username, OS version, space freed per step, technique used, and a summary at the end.

---

## 🛡️ Safety Notes

- Windows services are stopped before cleaning and restarted after
- Browsers are force-closed before cache cleaning to avoid file locks
- `C:\Downloads` and user documents are **never touched**
- Bookmarks, passwords, browser history, and extensions are **never deleted**
- Only cache and temp files are removed
- Dangerous system files (`System32`, `Installer` folder, driver cache, page file) are excluded entirely

---

## 🗺️ Roadmap

- [x] v1.0 — `.bat` script cleaner
- [x] v1.1 — Y/N per step, 3-technique force delete, activity history
- [x] v2.0 — Python GUI (CustomTkinter)
- [x] v2.1 — Per-drive cleanup, About tab, optional items
- [x] v2.2 — Compact default, new cache locations, npm/pip
- [x] v3.0 — 29 languages, themes, wizard, PIN lock, dry run, scanner, scheduler
- [x] v3.1 — Sidebar nav, tab fixes, scan clean, size per row, icon fix
- [x] v3.2 — Auto-update with download + install
- [ ] v3.3 — Inno Setup installer (proper Windows installer)
- [ ] v4.0 — Secure delete, PDF report export, disk health check

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
├── PurgeKit.py            # Main application
├── generate_icon.py       # Run before building to create icon
├── build.bat              # Build script (PyInstaller)
├── installer.iss          # Inno Setup installer config
├── requirements.txt       # Python dependencies
├── README.md
├── LICENSE
├── CHANGELOG.md
├── core/
│   ├── cleaner.py         # All cleaning logic + task definitions
│   ├── config.py          # Config, history, whitelist, PIN management
│   ├── lang_manager.py    # Language loader
│   ├── log_manager.py     # Log file writer
│   ├── scanner.py         # Junk folder scanner
│   ├── scheduler.py       # Windows Task Scheduler integration
│   ├── startup_manager.py # Startup programs reader
│   └── updater.py         # Auto-update checker + downloader
├── ui/
│   └── themes.py          # Green, Blue, Purple theme definitions
└── lang/
    ├── en.json            # English
    ├── ta.json            # Tamil
    ├── hi.json            # Hindi
    └── ... (29 total)
```

---

## 🔧 Building from Source

```bash
# Install dependencies
pip install customtkinter Pillow pystray winotify matplotlib pyinstaller

# Generate icon
python generate_icon.py

# Build exe
pyinstaller --onefile --windowed --name "PurgeKit" --uac-admin --icon "assets\icon.ico" --add-data "lang;lang" PurgeKit.py
```

Or just run `build.bat`.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## ⚠️ Disclaimer

PurgeKit deletes temporary and cache files only. It is provided **as-is** without warranty. Always ensure important data is backed up. The authors are not responsible for any unintended data loss.

---

## 👤 Author

**Yashwanth Ram Somireddy**
Chennai, India — TeamExyKings
GitHub: [@yashwanthramsomireddy](https://github.com/yashwanthramsomireddy)

---

*If PurgeKit helped you, give it a ⭐ on GitHub!*
