@echo off
chcp 65001 >nul
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0windows\upgrade.ps1"
if errorlevel 1 echo [ERROR] La actualizacion no se completo. Revisa el mensaje anterior.
pause
