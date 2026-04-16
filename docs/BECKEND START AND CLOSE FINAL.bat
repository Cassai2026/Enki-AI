@echo off
setlocal
title JARVIS BACKEND (ONE WINDOW + CLEAN SHUTDOWN)

set "PROJ=D:\JARVIS AI\AI_Assistant"

REM ---- Go to project folder ----
pushd "%PROJ%" >nul 2>&1
if errorlevel 1 (
  echo ERROR: Folder not found: "%PROJ%"
  pause
  exit /b 1
)

REM ---- Prevent duplicate runs ----
if exist jarvis.lock (
  echo Already running (jarvis.lock exists).
  echo Run STOP_ALL.bat if it is stuck.
  popd
  pause
  exit /b
)
echo running> jarvis.lock

REM ---- Make sure old ngrok is dead ----
taskkill /f /im ngrok.exe >nul 2>&1

echo =====================================
echo   Starting JARVIS Backend Services
echo   Folder: %CD%
echo =====================================
echo.

REM ---- Start Flask (background) ----
echo Starting Flask API...
start "" /b python web_server.py

timeout /t 2 >nul

REM ---- Start ngrok (background) ----
echo Starting ngrok...
start "" /b ngrok http 5000

echo.
echo =====================================
echo   BACKEND RUNNING
echo   - Flask: http://127.0.0.1:5000/health
echo   - ngrok: check your ngrok dashboard/output
echo.
echo   Press any key to STOP everything cleanly.
echo =====================================
echo.

pause >nul

:cleanup
echo.
echo Stopping ngrok...
taskkill /f /im ngrok.exe >nul 2>&1

echo Stopping Flask (web_server.py)...
powershell -NoProfile -Command ^
  "Get-CimInstance Win32_Process | ? { $_.Name -eq 'python.exe' -and $_.CommandLine -match 'web_server\.py' } | % { Stop-Process -Id $_.ProcessId -Force }" ^
  >nul 2>&1

del /q jarvis.lock >nul 2>&1

echo Done.
popd >nul 2>&1
exit /b