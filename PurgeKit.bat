@echo off
:: ============================================================
::  PurgeKit v1.1
::  License : MIT
::  Author  : TeamExyKings
::  GitHub  : https://github.com/TeamExyKings/PurgeKit
::
::  Cleans System + User temp folders, browser caches,
::  Windows Update, Delivery Optimization, Prefetch,
::  Activity History, and more.
::  Skips C:\Downloads entirely.
::  Uses 3-technique force-delete cascade.
:: ============================================================

:: ── Require Administrator ───────────────────────────────────
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo.
    echo  [ERROR] Please run this script as Administrator.
    echo  Right-click the file and select "Run as administrator".
    echo.
    pause
    exit /b 1
)

setlocal EnableDelayedExpansion
title PurgeKit v1.1 — TeamExyKings
color 0A

:: Log file on Desktop
set "LOG=%USERPROFILE%\Desktop\PurgeKit_Log.txt"
set "TIMESTAMP=%DATE% %TIME%"
set "REBOOT_NEEDED=0"
set "STEP=0"
set "TOTAL=23"
set "SKIPPED_FILES="

:: ── Empty folder for robocopy trick ─────────────────────────
set "EMPTY_DIR=%TEMP%\_purgekit_empty_"
if not exist "%EMPTY_DIR%" md "%EMPTY_DIR%" >nul 2>&1

:: ── Start Log ───────────────────────────────────────────────
(
echo ============================================================
echo   PurgeKit v1.1  ^|  MIT License  ^|  TeamExyKings
echo   GitHub   : https://github.com/TeamExyKings/PurgeKit
echo   Run Date : %TIMESTAMP%
echo   User     : %USERNAME%
echo   Machine  : %COMPUTERNAME%
echo ============================================================
echo.
) > "%LOG%"

:: ============================================================
call :PrintBanner
echo.
echo  This tool will clean your system in two phases:
echo    Phase 1 : System Level Temp ^& Cache
echo    Phase 2 : User Level Temp ^& Cache
echo.
echo  For each step you will be asked Y/N.
echo  Press ENTER after your choice.
echo.
echo  NOTE: C:\Downloads will NEVER be touched.
echo.
pause
echo.

:: ============================================================
::  PHASE 1 — SYSTEM LEVEL
:: ============================================================
call :PrintSection "PHASE 1 — SYSTEM LEVEL CLEANING"

:: ── S1: Windows System Temp ─────────────────────────────────
call :AskUser "S1" "Windows System Temp" "C:\Windows\Temp"
if "!ANSWER!"=="Y" (
    call :ForceDelete "C:\Windows\Temp"
    call :RecreateDir "C:\Windows\Temp"
)

:: ── S2: Windows Prefetch ────────────────────────────────────
call :AskUser "S2" "Prefetch Files" "C:\Windows\Prefetch"
if "!ANSWER!"=="Y" (
    call :ForceDelete "C:\Windows\Prefetch"
    call :RecreateDir "C:\Windows\Prefetch"
)

:: ── S3: Windows Update Cache ────────────────────────────────
call :AskUser "S3" "Windows Update Cache" "C:\Windows\SoftwareDistribution\Download"
if "!ANSWER!"=="Y" (
    call :Log "  Stopping wuauserv + bits..."
    net stop wuauserv >nul 2>&1
    net stop bits >nul 2>&1
    call :ForceDelete "C:\Windows\SoftwareDistribution\Download"
    call :RecreateDir "C:\Windows\SoftwareDistribution\Download"
    call :Log "  Restarting wuauserv + bits..."
    net start wuauserv >nul 2>&1
    net start bits >nul 2>&1
)

:: ── S4: Delivery Optimization ───────────────────────────────
call :AskUser "S4" "Delivery Optimization Files" "C:\Windows\SoftwareDistribution\DeliveryOptimization"
if "!ANSWER!"=="Y" (
    net stop DoSvc >nul 2>&1
    call :ForceDelete "C:\Windows\SoftwareDistribution\DeliveryOptimization"
    call :RecreateDir "C:\Windows\SoftwareDistribution\DeliveryOptimization"
    net start DoSvc >nul 2>&1
)

:: ── S5: Windows Error Reporting ─────────────────────────────
call :AskUser "S5" "Windows Error Reporting (WER)" "C:\ProgramData\Microsoft\Windows\WER"
if "!ANSWER!"=="Y" (
    call :ForceDelete "C:\ProgramData\Microsoft\Windows\WER\ReportQueue"
    call :ForceDelete "C:\ProgramData\Microsoft\Windows\WER\ReportArchive"
    call :RecreateDir "C:\ProgramData\Microsoft\Windows\WER\ReportQueue"
    call :RecreateDir "C:\ProgramData\Microsoft\Windows\WER\ReportArchive"
)

:: ── S6: CBS Logs ────────────────────────────────────────────
call :AskUser "S6" "Windows CBS Logs" "C:\Windows\Logs\CBS"
if "!ANSWER!"=="Y" (
    call :ForceDelete "C:\Windows\Logs\CBS"
    call :RecreateDir "C:\Windows\Logs\CBS"
)

:: ── S7: Crash Dumps ─────────────────────────────────────────
call :AskUser "S7" "Crash Dumps (Minidump + MEMORY.DMP)" "C:\Windows\Minidump"
if "!ANSWER!"=="Y" (
    call :ForceDelete "C:\Windows\Minidump"
    call :RecreateDir "C:\Windows\Minidump"
    if exist "C:\Windows\MEMORY.DMP" (
        call :ForceDeleteFile "C:\Windows\MEMORY.DMP"
    )
)

:: ── S8: Windows Font Cache ──────────────────────────────────
call :AskUser "S8" "Windows Font Cache" "C:\Windows\ServiceProfiles\LocalService\AppData\Local\FontCache"
if "!ANSWER!"=="Y" (
    net stop FontCache >nul 2>&1
    call :ForceDelete "C:\Windows\ServiceProfiles\LocalService\AppData\Local\FontCache"
    call :RecreateDir "C:\Windows\ServiceProfiles\LocalService\AppData\Local\FontCache"
    net start FontCache >nul 2>&1
)

:: ── S9: SoftwareDistribution DataStore Logs ─────────────────
call :AskUser "S9" "SoftwareDistribution DataStore Logs" "C:\Windows\SoftwareDistribution\DataStore\Logs"
if "!ANSWER!"=="Y" (
    net stop wuauserv >nul 2>&1
    call :ForceDelete "C:\Windows\SoftwareDistribution\DataStore\Logs"
    call :RecreateDir "C:\Windows\SoftwareDistribution\DataStore\Logs"
    net start wuauserv >nul 2>&1
)

:: ── S10: Windows Installer Patch Cache ──────────────────────
call :AskUser "S10" "Windows Installer Patch Cache" "C:\Windows\Installer\$PatchCache$"
if "!ANSWER!"=="Y" (
    call :ForceDelete "C:\Windows\Installer\$PatchCache$"
)

:: ── S11: DNS Cache ──────────────────────────────────────────
call :AskUser "S11" "DNS Cache (Flush)" "System DNS Resolver"
if "!ANSWER!"=="Y" (
    ipconfig /flushdns >nul 2>&1
    call :StepDone "S11" "DNS Cache flushed successfully"
)

:: ============================================================
::  PHASE 2 — USER LEVEL
:: ============================================================
call :PrintSection "PHASE 2 — USER LEVEL CLEANING"

:: ── U1: User Temp ───────────────────────────────────────────
call :AskUser "U1" "User Temp Folder" "%TEMP%"
if "!ANSWER!"=="Y" (
    call :ForceDelete "%TEMP%"
    call :RecreateDir "%TEMP%"
)

:: ── U2: Thumbnail Cache ─────────────────────────────────────
call :AskUser "U2" "Thumbnail Cache" "%LOCALAPPDATA%\Microsoft\Windows\Explorer"
if "!ANSWER!"=="Y" (
    taskkill /f /im explorer.exe >nul 2>&1
    del /f /s /q "%LOCALAPPDATA%\Microsoft\Windows\Explorer\thumbcache_*.db" >nul 2>&1
    start explorer.exe >nul 2>&1
    call :StepDone "U2" "Thumbnail cache cleared"
)

:: ── U3: Recent Files & Jump Lists ───────────────────────────
call :AskUser "U3" "Recent Files and Jump Lists" "%APPDATA%\Microsoft\Windows\Recent"
if "!ANSWER!"=="Y" (
    call :ForceDelete "%APPDATA%\Microsoft\Windows\Recent"
    call :RecreateDir "%APPDATA%\Microsoft\Windows\Recent"
)

:: ── U4: IE / Legacy Edge Cache ──────────────────────────────
call :AskUser "U4" "IE / Legacy Edge Cache" "%LOCALAPPDATA%\Microsoft\Windows\INetCache"
if "!ANSWER!"=="Y" (
    call :ForceDelete "%LOCALAPPDATA%\Microsoft\Windows\INetCache"
    call :RecreateDir "%LOCALAPPDATA%\Microsoft\Windows\INetCache"
)

:: ── U5: DirectX Shader Cache ────────────────────────────────
call :AskUser "U5" "DirectX Shader Cache (D3DSCache)" "%LOCALAPPDATA%\D3DSCache"
if "!ANSWER!"=="Y" (
    call :ForceDelete "%LOCALAPPDATA%\D3DSCache"
    call :RecreateDir "%LOCALAPPDATA%\D3DSCache"
)

:: ── U6: Teams Cache ─────────────────────────────────────────
call :AskUser "U6" "Microsoft Teams Cache" "%APPDATA%\Microsoft\Teams\Cache"
if "!ANSWER!"=="Y" (
    taskkill /f /im Teams.exe >nul 2>&1
    call :ForceDelete "%APPDATA%\Microsoft\Teams\Cache"
    call :ForceDelete "%APPDATA%\Microsoft\Teams\blob_storage"
    call :RecreateDir "%APPDATA%\Microsoft\Teams\Cache"
    call :RecreateDir "%APPDATA%\Microsoft\Teams\blob_storage"
)

:: ── U7: VS Code Cache ───────────────────────────────────────
call :AskUser "U7" "Visual Studio Code Cache" "%APPDATA%\Code\Cache"
if "!ANSWER!"=="Y" (
    taskkill /f /im Code.exe >nul 2>&1
    call :ForceDelete "%APPDATA%\Code\Cache"
    call :ForceDelete "%APPDATA%\Code\CachedData"
    call :RecreateDir "%APPDATA%\Code\Cache"
    call :RecreateDir "%APPDATA%\Code\CachedData"
)

:: ── U8: Office Cache ────────────────────────────────────────
call :AskUser "U8" "Microsoft Office File Cache" "%LOCALAPPDATA%\Microsoft\Office\16.0\OfficeFileCache"
if "!ANSWER!"=="Y" (
    call :ForceDelete "%LOCALAPPDATA%\Microsoft\Office\16.0\OfficeFileCache"
    call :RecreateDir "%LOCALAPPDATA%\Microsoft\Office\16.0\OfficeFileCache"
)

:: ── U9: Spotify Cache ───────────────────────────────────────
call :AskUser "U9" "Spotify Cache" "%LOCALAPPDATA%\Spotify\Storage"
if "!ANSWER!"=="Y" (
    taskkill /f /im Spotify.exe >nul 2>&1
    call :ForceDelete "%LOCALAPPDATA%\Spotify\Storage"
    call :RecreateDir "%LOCALAPPDATA%\Spotify\Storage"
)

:: ── U10: Windows Activity History (ActivitiesCache.db) ──────
echo.
echo  ┌─────────────────────────────────────────────────────┐
echo  │  PRIVACY : Windows Activity History                  │
echo  │                                                       │
echo  │  Windows secretly stores your activity history in:   │
echo  │  %%LOCALAPPDATA%%\ConnectedDevicesPlatform\           │
echo  │  inside a hidden SQLite file: ActivitiesCache.db     │
echo  │                                                       │
echo  │  This tracks: apps you opened, files you viewed,     │
echo  │  websites visited, timeline data.                     │
echo  │                                                       │
echo  │  Options:                                             │
echo  │    D = Delete the database file only (one-time clean) │
echo  │    X = Disable Activity History via registry too      │
echo  │    N = Skip this step                                 │
echo  └─────────────────────────────────────────────────────┘
echo.
set /p "ACT_CHOICE=  Your choice [D/X/N]: "
set "ACT_CHOICE=!ACT_CHOICE: =!"
if /i "!ACT_CHOICE!"=="D" (
    call :Log ""
    call :Log "  STEP U10 : Windows Activity History"
    call :Log "  Action   : Delete ActivitiesCache.db only"
    taskkill /f /im explorer.exe >nul 2>&1
    for /d %%P in ("%LOCALAPPDATA%\ConnectedDevicesPlatform\*") do (
        call :ForceDeleteFile "%%P\ActivitiesCache.db"
    )
    start explorer.exe >nul 2>&1
    call :StepDone "U10" "ActivitiesCache.db deleted"
)
if /i "!ACT_CHOICE!"=="X" (
    call :Log ""
    call :Log "  STEP U10 : Windows Activity History"
    call :Log "  Action   : Delete DB + Disable via Registry"
    taskkill /f /im explorer.exe >nul 2>&1
    for /d %%P in ("%LOCALAPPDATA%\ConnectedDevicesPlatform\*") do (
        call :ForceDeleteFile "%%P\ActivitiesCache.db"
    )
    start explorer.exe >nul 2>&1
    reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v "EnableActivityFeed" /t REG_DWORD /d 0 /f >nul 2>&1
    reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v "PublishUserActivities" /t REG_DWORD /d 0 /f >nul 2>&1
    reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v "UploadUserActivities" /t REG_DWORD /d 0 /f >nul 2>&1
    call :StepDone "U10" "ActivitiesCache.db deleted + Activity History disabled in registry"
)
if /i "!ACT_CHOICE!"=="N" (
    call :Log ""
    call :Log "  STEP U10 : Windows Activity History -- SKIPPED by user"
    echo   [SKIPPED] Windows Activity History
)

:: ============================================================
::  PHASE 3 — BROWSERS
:: ============================================================
call :PrintSection "PHASE 3 — BROWSER CACHE CLEANING"

:: ── B1: Google Chrome ───────────────────────────────────────
call :AskUser "B1" "Google Chrome Cache" "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache"
if "!ANSWER!"=="Y" (
    taskkill /f /im chrome.exe >nul 2>&1
    call :ForceDelete "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache"
    call :ForceDelete "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Code Cache"
    call :ForceDelete "%LOCALAPPDATA%\Google\Chrome\User Data\Default\GPUCache"
    call :RecreateDir "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache"
    call :RecreateDir "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Code Cache"
    call :RecreateDir "%LOCALAPPDATA%\Google\Chrome\User Data\Default\GPUCache"
)

:: ── B2: Mozilla Firefox ─────────────────────────────────────
call :AskUser "B2" "Mozilla Firefox Cache (All Profiles)" "%LOCALAPPDATA%\Mozilla\Firefox\Profiles"
if "!ANSWER!"=="Y" (
    taskkill /f /im firefox.exe >nul 2>&1
    for /d %%P in ("%LOCALAPPDATA%\Mozilla\Firefox\Profiles\*") do (
        call :ForceDelete "%%P\cache2"
        call :ForceDelete "%%P\startupCache"
        call :ForceDelete "%%P\jumpListCache"
        call :RecreateDir "%%P\cache2"
        call :RecreateDir "%%P\startupCache"
    )
    call :StepDone "B2" "Firefox cache cleared across all profiles"
)

:: ── B3: Microsoft Edge ──────────────────────────────────────
call :AskUser "B3" "Microsoft Edge Cache" "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache"
if "!ANSWER!"=="Y" (
    taskkill /f /im msedge.exe >nul 2>&1
    call :ForceDelete "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache"
    call :ForceDelete "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Code Cache"
    call :ForceDelete "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\GPUCache"
    call :RecreateDir "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache"
    call :RecreateDir "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Code Cache"
    call :RecreateDir "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\GPUCache"
)

:: ============================================================
::  PHASE 4 — DISK CLEANUP
:: ============================================================
call :PrintSection "PHASE 4 — WINDOWS DISK CLEANUP"

call :AskUser "DC" "Windows Disk Cleanup (All Categories Automated)" "cleanmgr /sageset:99"
if "!ANSWER!"=="Y" (
    call :Log "  Registering all Disk Cleanup categories (sageset 99)..."
    for %%K in (
        "Active Setup Temp Folders"
        "BranchCache"
        "Content Indexer Cleaner"
        "D3D Shader Cache"
        "Delivery Optimization Files"
        "Device Driver Packages"
        "Diagnostic Data Viewer database files"
        "Downloaded Program Files"
        "Internet Cache Files"
        "Memory Dump Files"
        "Offline Pages Files"
        "Old ChkDsk Files"
        "Previous Installations"
        "Recycle Bin"
        "Service Pack Cleanup"
        "Setup Log Files"
        "System error memory dump files"
        "System error minidump files"
        "Temporary Files"
        "Temporary Setup Files"
        "Thumbnail Cache"
        "Update Cleanup"
        "Upgrade Discarded Files"
        "Windows Defender"
        "Windows Error Reporting Archive Files"
        "Windows Error Reporting Files"
        "Windows Error Reporting Queue Files"
        "Windows Error Reporting System Archive Files"
        "Windows Error Reporting System Queue Files"
        "Windows ESD installation files"
        "Windows Upgrade Log Files"
    ) do (
        reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\%%~K" /v StateFlags0099 /t REG_DWORD /d 2 /f >nul 2>&1
    )
    call :Log "  Running cleanmgr /sagerun:99 ..."
    cleanmgr /sagerun:99 >nul 2>&1
    call :StepDone "DC" "Windows Disk Cleanup completed"
)

:: ── Cleanup empty dir ────────────────────────────────────────
rd /s /q "%EMPTY_DIR%" >nul 2>&1

:: ============================================================
::  REBOOT NOTICE
:: ============================================================
if "!REBOOT_NEEDED!"=="1" (
    echo.
    echo  ┌─────────────────────────────────────────────────────┐
    echo  │  REBOOT REQUIRED                                      │
    echo  │                                                       │
    echo  │  Some files were registered for deletion on next      │
    echo  │  Windows startup (Technique 3 was used).              │
    echo  │  Please restart your PC to complete the cleanup.      │
    echo  └─────────────────────────────────────────────────────┘
    call :Log ""
    call :Log "  REBOOT REQUIRED : Pending file deletions registered."
    call :Log "  Restart your PC to complete the cleanup."
)

:: ============================================================
::  DONE
:: ============================================================
echo.
echo  ============================================================
echo    PurgeKit v1.1 — ALL TASKS COMPLETED
echo  ============================================================
echo    Log saved to : %LOG%
echo  ============================================================
echo.

call :Log ""
call :Log "============================================================"
call :Log "  ALL TASKS COMPLETED"
call :Log "  End Time : %DATE% %TIME%"
call :Log "============================================================"

pause
exit /b 0


:: ============================================================
::  SUBROUTINES
:: ============================================================

:: ── Print Banner ─────────────────────────────────────────────
:PrintBanner
cls
echo.
echo  ██████╗ ██╗   ██╗██████╗  ██████╗ ███████╗██╗  ██╗██╗████████╗
echo  ██╔══██╗██║   ██║██╔══██╗██╔════╝ ██╔════╝██║ ██╔╝██║╚══██╔══╝
echo  ██████╔╝██║   ██║██████╔╝██║  ███╗█████╗  █████╔╝ ██║   ██║
echo  ██╔═══╝ ██║   ██║██╔══██╗██║   ██║██╔══╝  ██╔═██╗ ██║   ██║
echo  ██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗██║  ██╗██║   ██║
echo  ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝
echo.
echo                  v1.1  ^|  MIT License  ^|  TeamExyKings
echo            https://github.com/TeamExyKings/PurgeKit
echo.
goto :eof

:: ── Print Section Header ─────────────────────────────────────
:PrintSection
echo.
echo  ════════════════════════════════════════════════════════
echo    %~1
echo  ════════════════════════════════════════════════════════
echo.
call :Log ""
call :Log "════════════════════════════════════════════════════════"
call :Log "  %~1"
call :Log "════════════════════════════════════════════════════════"
goto :eof

:: ── Ask User Y/N ─────────────────────────────────────────────
:AskUser
set /a STEP+=1
set /a PCT=STEP*100/TOTAL
set "STEPID=%~1"
set "STEPNAME=%~2"
set "STEPPATH=%~3"
call :ProgressBar %PCT%
echo   [%STEPID%] %STEPNAME%
echo        Path : %STEPPATH%
set /p "ANSWER=       Clean this? [Y/N]: "
set "ANSWER=!ANSWER: =!"
if /i "!ANSWER!"=="Y" set "ANSWER=Y"
if /i "!ANSWER!"=="N" set "ANSWER=N"
if "!ANSWER!"=="" set "ANSWER=N"
call :Log ""
call :Log "  STEP %STEPID% : %STEPNAME%"
call :Log "  Path     : %STEPPATH%"
call :Log "  User     : !ANSWER!"
goto :eof

:: ── Step Done ────────────────────────────────────────────────
:StepDone
echo        Status: DONE — %~2
call :Log "  Status   : DONE — %~2"
echo.
goto :eof

:: ── Progress Bar ─────────────────────────────────────────────
:ProgressBar
set /a "FILLED=%~1/5"
set /a "EMPTY=20-FILLED"
set "BAR=["
for /l %%i in (1,1,%FILLED%) do set "BAR=!BAR!█"
for /l %%i in (1,1,%EMPTY%) do set "BAR=!BAR!░"
set "BAR=!BAR!] %~1%%"
echo.
echo   Progress : !BAR!
goto :eof

:: ── Force Delete (3-Technique Cascade) ───────────────────────
:ForceDelete
set "TARGET=%~1"
if not exist "!TARGET!" (
    call :Log "  [SKIP] Path not found: !TARGET!"
    goto :eof
)

call :Log "  Deleting: !TARGET!"

:: — Technique 1: robocopy empty folder mirror ────────────────
if not exist "%EMPTY_DIR%" md "%EMPTY_DIR%" >nul 2>&1
robocopy "%EMPTY_DIR%" "!TARGET!" /MIR /NFL /NDL /NJH /NJS /nc /ns /np >nul 2>&1
rd /s /q "!TARGET!" >nul 2>&1

if not exist "!TARGET!" (
    call :Log "  [T1-OK] Technique 1 (robocopy) succeeded: !TARGET!"
    call :StepDone "" "Cleaned via Technique 1 (robocopy)"
    goto :eof
)

call :Log "  [T1-FAIL] Technique 1 failed, trying Technique 2..."
echo        [T1 Failed] Trying Technique 2 (takeown + icacls)...

:: — Technique 2: takeown + icacls + force delete ─────────────
takeown /f "!TARGET!" /r /d y >nul 2>&1
icacls "!TARGET!" /grant administrators:F /t /q >nul 2>&1
rd /s /q "!TARGET!" >nul 2>&1
del /f /s /q "!TARGET!\*.*" >nul 2>&1

if not exist "!TARGET!" (
    call :Log "  [T2-OK] Technique 2 (takeown+icacls) succeeded: !TARGET!"
    call :StepDone "" "Cleaned via Technique 2 (takeown+icacls)"
    goto :eof
)

call :Log "  [T2-FAIL] Technique 2 failed, trying Technique 3..."
echo        [T2 Failed] Trying Technique 3 (schedule on reboot)...

:: — Technique 3: Register pending delete on next reboot ───────
for /r "!TARGET!" %%F in (*) do (
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager" /v PendingFileRenameOperations /t REG_MULTI_SZ /d "\??\%%F\0" /f >nul 2>&1
)
set "REBOOT_NEEDED=1"
call :Log "  [T3-SCHED] Files scheduled for deletion on next reboot: !TARGET!"
echo        [T3] Files scheduled for deletion on next reboot.
echo.
goto :eof

:: ── Force Delete Single File ─────────────────────────────────
:ForceDeleteFile
set "FTARGET=%~1"
if not exist "!FTARGET!" goto :eof
call :Log "  Deleting file: !FTARGET!"
del /f /q "!FTARGET!" >nul 2>&1
if not exist "!FTARGET!" (
    call :Log "  [OK] Deleted: !FTARGET!"
    goto :eof
)
takeown /f "!FTARGET!" >nul 2>&1
icacls "!FTARGET!" /grant administrators:F /q >nul 2>&1
del /f /q "!FTARGET!" >nul 2>&1
if not exist "!FTARGET!" (
    call :Log "  [T2-OK] Deleted with takeown: !FTARGET!"
    goto :eof
)
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager" /v PendingFileRenameOperations /t REG_MULTI_SZ /d "\??\!FTARGET!\0" /f >nul 2>&1
set "REBOOT_NEEDED=1"
call :Log "  [T3-SCHED] Scheduled on reboot: !FTARGET!"
goto :eof

:: ── Recreate Directory ───────────────────────────────────────
:RecreateDir
if not exist "%~1" md "%~1" >nul 2>&1
goto :eof

:: ── Write to Log ─────────────────────────────────────────────
:Log
echo %~1 >> "%LOG%"
goto :eof
