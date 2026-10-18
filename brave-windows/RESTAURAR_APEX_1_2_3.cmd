@echo off
chcp 65001 >nul
title Restaurar Apex Descarga 1.2.3
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0windows\rollback_smart_merge.ps1"
if errorlevel 1 echo [ERROR] No fue posible completar la restauracion.
pause
