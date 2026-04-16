@echo off
title STOPPING JARVIS

set "PROJ=D:\JARVIS AI\AI_Assistant"
pushd "%PROJ%" >nul 2>&1

taskkill /f /im ngrok.exe >nul 2>&1

powershell -NoProfile -Command ^
  "Get-CimInstance Win32_Process | ? { $_.Name -eq 'python.exe' -and $_.CommandLine -match 'web_server\.py' } | % { Stop-Process -Id $_.ProcessId -Force }" ^
  >nul 2>&1

powershell -NoProfile -Command ^
  "Get-CimInstance Win32_Process | ? { $_.Name -eq 'python.exe' -and $_.CommandLine -match 'JARVIS V0\.01\.py' } | % { Stop-Process -Id $_.ProcessId -Force }" ^
  >nul 2>&1

del /q jarvis.lock >nul 2>&1

popd >nul 2>&1
echo Done.
pause