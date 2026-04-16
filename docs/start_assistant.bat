@echo off
setlocal
title JARVIS FULL STACK

pushd "D:\JARVIS AI\AI Assistant"

REM Prevent double-run using lock file
if exist jarvis.lock (
  echo Already running (jarvis.lock exists).
  echo Run STOP_ALL.bat to close everything.
  popd
  pause
  exit /b
)
echo running> jarvis.lock

REM Kill any old ngrok
taskkill /f /im ngrok.exe >nul 2>&1

REM Start Flask + ngrok + Voice
start "JARVIS API" cmd /k "cd /d "D:\JARVIS AI\AI Assistant" && python web_server.py"
timeout /t 2 >nul
start "ngrok" cmd /k "cd /d "D:\JARVIS AI\AI Assistant" && ngrok http 5000"
timeout /t 2 >nul
start "JARVIS Voice" cmd /k "cd /d "D:\AI Assistant" && python ""JARVIS V0.01.py"""

echo Full stack launched.
popd
exit /b