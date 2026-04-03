@echo off
setlocal enabledelayedexpansion
title JARVIS BACKEND DEBUG

set "PROJ=D:\JARVIS AI\AI_Assistant"

echo =====================================
echo  JARVIS BACKEND DEBUG LAUNCHER
echo =====================================
echo Project folder: "%PROJ%"
echo.

if not exist "%PROJ%\" (
  echo ERROR: Project folder NOT found.
  echo Check the PROJ path in this .bat
  echo.
  pause
  exit /b 1
)

pushd "%PROJ%"
echo OK: Now in: %CD%
echo.

if exist "web_server.py" (
  echo OK: web_server.py found
) else (
  echo ERROR: web_server.py NOT found in this folder
  dir
  echo.
  pause
  exit /b 1
)

if exist "jarvis.lock" (
  echo NOTE: jarvis.lock exists (this means START thinks it is already running)
  echo Deleting jarvis.lock now...
  del /q "jarvis.lock" >nul 2>&1
)

echo Writing lock...
echo running> "jarvis.lock"

echo.
echo Checking Python...
python --version
if errorlevel 1 (
  echo ERROR: "python" not found in PATH.
  echo Try installing / or use "py" instead of "python" in the bat.
  pause
  exit /b 1
)

echo.
echo Checking ngrok...
ngrok version
if errorlevel 1 (
  echo ERROR: "ngrok" not found in PATH.
  echo Put ngrok.exe in this folder OR add it to PATH.
  pause
  exit /b 1
)

echo.
echo Killing old ngrok...
taskkill /f /im ngrok.exe >nul 2>&1

echo.
echo Starting Flask API window...
start "JARVIS API" cmd /k "cd /d ""%PROJ%"" && python web_server.py"

timeout /t 2 >nul

echo Starting ngrok window...
start "ngrok" cmd /k "cd /d ""%PROJ%"" && ngrok http 5000"

echo.
echo DONE. You should now see 2 windows (API + ngrok).
echo If you don't, tell me what you see above.
echo.
popd
pause