@echo off
:: ============================================================
::  PurgeKit v2.0 — Build Script
::  Compiles PurgeKit.py to a standalone .exe using PyInstaller
::  Run this once to generate dist\PurgeKit.exe
:: ============================================================

echo.
echo  [PurgeKit Build] Installing dependencies...
pip install customtkinter Pillow pyinstaller --upgrade

echo.
echo  [PurgeKit Build] Compiling to .exe ...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "PurgeKit" ^
    --uac-admin ^
    PurgeKit.py

echo.
echo  ============================================================
echo    Build complete!
echo    Your exe is at: dist\PurgeKit.exe
echo  ============================================================
echo.
pause
