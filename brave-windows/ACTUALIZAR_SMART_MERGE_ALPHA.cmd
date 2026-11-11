@echo off
chcp 65001 >nul
title Apex Descarga 2.0 Alpha - Instalador con respaldo
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0windows\upgrade_smart_merge.ps1"
if errorlevel 1 echo [ERROR] La version Alpha no se instalo. Lee el mensaje superior.
pause
