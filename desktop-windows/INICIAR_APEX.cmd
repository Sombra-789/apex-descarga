@echo off
setlocal
chcp 65001 >nul
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\arrancar.ps1"
if errorlevel 1 (
  echo.
  echo [ERROR] No se pudo iniciar. Copia el mensaje para diagnosticarlo.
)
pause
