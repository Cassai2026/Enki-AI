@echo off
setlocal
title JARVIS BACKEND (SINGLE WINDOW)

set "PROJ=D:\JARVIS AI\AI_Assistant"
pushd "%PROJ%"

REM Kill old ngrok
taskkill /f /im ngrok.exe >nul 2>&1

echo Starting Flask in background...
start /b python web_server.py

timeout /t 2 >nul

echo Starting ngrok in background...
start /b ngrok http 5000

echo.
echo Backend running in this window.
echo Close this window to stop everything.
echo.

pause