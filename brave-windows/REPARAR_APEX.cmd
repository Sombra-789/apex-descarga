@echo off
chcp 65001 >nul
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0windows\diagnostico.ps1" -Repair
if errorlevel 1 echo [ERROR] La reparacion no se completo. Revisa el diagnostico.
pause
