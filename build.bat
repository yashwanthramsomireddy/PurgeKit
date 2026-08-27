@echo off
:: ============================================================
::  PurgeKit v3.1.5 — Build Script
::  Run from the PurgeKit folder in a normal CMD window
::  (Do NOT run as Administrator)
:: ============================================================

echo.
echo  [PurgeKit Build] Installing dependencies...
pip install customtkinter Pillow pystray winotify matplotlib pyinstaller --upgrade

echo.
echo  [PurgeKit Build] Generating icon...
python generate_icon.py

echo.
echo  [PurgeKit Build] Compiling to .exe ...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "PurgeKit" ^
    --uac-admin ^
    --icon "assets\icon.ico" ^
    --add-data "lang;lang" ^
    PurgeKit.py

echo.
echo  ============================================================
echo    Build complete!
echo    Your exe is at: dist\PurgeKit.exe
echo  ============================================================
echo.
pause
