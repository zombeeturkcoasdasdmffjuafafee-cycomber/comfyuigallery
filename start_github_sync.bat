@echo off
title ComfyUI GitHub Gallery Auto-Sync
cd /d "C:\Users\Donton\AppData\Local\ComfyUI_windows_portable\WEBSITE"

echo [1/3] Starting GitHub auto-sync watcher...
start cmd /k "python watch_github.py"

echo [2/3] Starting local preview server...
echo [3/3] Opening browser...
start http://localhost:8000

python -m http.server 8000