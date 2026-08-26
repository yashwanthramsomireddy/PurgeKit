# 🧹 PurgeKit v1.0

> A lightweight, open-source Windows temp and cache cleaner — no installation needed.  
> Built by [TeamExyKings](https://github.com/TeamExyKings)

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%2F11-blue.svg)
![Version](https://img.shields.io/badge/Version-1.0-orange.svg)
![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)

---

## 📋 What It Cleans

| # | Category | Path Cleaned |
|---|---|---|
| 1 | User Temp Folder | `%TEMP%` |
| 2 | Windows System Temp | `C:\Windows\Temp` |
| 3 | Prefetch Files | `C:\Windows\Prefetch` |
| 4 | Windows Update Cache | `C:\Windows\SoftwareDistribution\Download` |
| 5 | Delivery Optimization Files | `C:\Windows\SoftwareDistribution\DeliveryOptimization` |
| 6 | Thumbnail Cache | `%LOCALAPPDATA%\Microsoft\Windows\Explorer\thumbcache_*.db` |
| 7 | Recent Files & Jump Lists | `%APPDATA%\Microsoft\Windows\Recent` |
| 8 | DNS Cache | System DNS Resolver (flushed via `ipconfig /flushdns`) |
| 9 | Google Chrome Cache | Cache, Code Cache, GPUCache |
| 10 | Mozilla Firefox Cache | cache2, startupCache, jumpListCache (all profiles) |
| 11 | Microsoft Edge Cache | Cache, Code Cache, GPUCache |
| 12 | Disk Cleanup (All Categories) | All standard Windows Disk Cleanup items automated |

> ✅ **C:\Downloads is never touched.**

---

## 🚀 How to Use

### Requirements
- Windows 10 or Windows 11
- Administrator privileges (the script will prompt if not elevated)

### Steps

1. Download `PurgeKit.bat` from [Releases](https://github.com/TeamExyKings/PurgeKit/releases)
2. Right-click the file
3. Select **"Run as administrator"**
4. Watch the progress bar — all steps run automatically
5. A detailed log file is saved to your **Desktop** when complete

---

## 📊 Log File

After every run, a structured log file is created at:

```
C:\Users\<YourName>\Desktop\PurgeKit_Log.txt
```

### Sample Log Output

```
============================================================
  PurgeKit v1.0  |  MIT License
  Run Date : Wed 08/26/2026  10:45:00.00
  User     : Yash
  Machine  : STERLING-PC
============================================================

  STEP 1/12 : User Temp Folder
  Path        : C:\Users\Yash\AppData\Local\Temp
  Status      : DONE

  STEP 2/12 : Windows System Temp
  Path        : C:\Windows\Temp
  Status      : DONE

  ...

============================================================
  ALL TASKS COMPLETED SUCCESSFULLY
  End Time : Wed 08/26/2026  10:46:12.00
============================================================
```

---

## 🛡️ Safety Notes

- **Windows Update service** (`wuauserv`) and **BITS** are stopped before cleaning the update cache and automatically restarted after
- **Delivery Optimization service** (`DoSvc`) is handled the same way
- **Browsers** (Chrome, Firefox, Edge) are force-closed before their cache is cleaned to avoid file-lock errors
- **Explorer** is briefly restarted to clear thumbnail cache locks
- The script **does not** touch `C:\Downloads` or any user documents
- The script **does not** delete browser history, passwords, or bookmarks — only cache files

---

## 🔧 What Happens to Each Browser

| Browser | What Is Cleared | What Is Kept |
|---|---|---|
| Chrome | Cache, Code Cache, GPUCache, Cookies | Bookmarks, Passwords, History, Extensions |
| Firefox | cache2, startupCache, jumpListCache | Bookmarks, Passwords, History, Add-ons |
| Edge | Cache, Code Cache, GPUCache | Bookmarks, Passwords, History, Extensions |

---

## 🗺️ Roadmap

- [x] v1.0 — `.bat` script with progress bar and log file
- [ ] v2.0 — Python GUI app (CustomTkinter) with checkbox per step, progress bar UI, log viewer
- [ ] v2.1 — Packaged as `.exe` via PyInstaller
- [ ] v2.2 — Windows installer via Inno Setup
- [ ] v3.0 — Schedule automatic cleaning (Task Scheduler integration)

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Commit: `git commit -m "Add: your feature description"`
5. Push: `git push origin feature/your-feature-name`
6. Open a Pull Request

Please follow the existing code style and add comments for any new steps.

---

## 📁 Project Structure

```
PurgeKit/
│
├── PurgeKit.bat     # Main cleaner script (v1.0)
├── README.md              # This file
├── LICENSE                # MIT License
└── CHANGELOG.md           # Version history
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

You are free to use, modify, distribute, and include this in your own projects — personal or commercial — with attribution.

---

## ⚠️ Disclaimer

This tool deletes temporary and cache files only. It is provided **as-is** without warranty of any kind. Always ensure you have backups of important data before running any system maintenance tool. The authors are not responsible for any unintended data loss.

---

## 👤 Author

**TeamExyKings**  
GitHub: [@TeamExyKings](https://github.com/TeamExyKings)

---

*If this tool helped you, consider giving it a ⭐ on GitHub!*
