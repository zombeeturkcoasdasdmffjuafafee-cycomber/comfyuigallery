@echo off
title ComfyUI Local Gallery Manager
cd /d "C:\Users\Donton\AppData\Local\ComfyUI_windows_portable\WEBSITE"

echo [1/3] Starting background image watcher script...
start cmd /k "python watch_local.py"

echo [2/3] Starting local web server on port 8000...
echo [3/3] Opening gallery in your browser...
start http://localhost:8000

:: Keeps the server window open and running
python -m http.server 8000