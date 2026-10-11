@echo off
chcp 65001 >nul
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\generar_apk.ps1"
if errorlevel 1 (
    echo.
    echo [ERROR] No se genero la APK. Copia el error y compartelo para corregirlo.
)
pause
