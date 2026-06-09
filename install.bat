@echo off
title AI Video Generator - Installer
color 0A
echo.
echo ================================================
echo    AI Video Generator - Auto Installer
echo    Created by Fiaz Shah
echo ================================================
echo.

echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found! Opening download page...
    start https://python.org/downloads
    echo Please install Python first, then run this again.
    pause
    exit
)
echo Python OK!

echo.
echo [2/5] Installing required libraries...
pip install moviepy edge-tts gtts requests pillow --quiet
echo Libraries installed!

echo.
echo [3/5] Installing FFmpeg...
winget install ffmpeg --silent >nul 2>&1
echo FFmpeg done!

echo.
echo [4/5] Creating output folder...
mkdir output >nul 2>&1
echo Output folder ready!

echo.
echo [5/5] Creating desktop shortcut...
set SCRIPT_DIR=%~dp0
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%USERPROFILE%\Desktop\AI Video Generator.lnk'); $s.TargetPath = 'python'; $s.Arguments = '%SCRIPT_DIR%gui.py'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.IconLocation = '%SCRIPT_DIR%AI_Video_Generator.exe'; $s.Save()"
echo Desktop shortcut created!

echo.
echo ================================================
echo    Installation Complete!
echo    Double click desktop shortcut to start!
echo ================================================
echo.
pause
