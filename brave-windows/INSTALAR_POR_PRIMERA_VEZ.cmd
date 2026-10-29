@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
echo Apex Descarga 1.2.3 - instalacion inicial Brave/Windows
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0windows\install-first.ps1"
set "EXITCODE=%ERRORLEVEL%"
echo.
if not "%EXITCODE%"=="0" echo [ERROR] Instalacion incompleta. Consulta README_PRIMERO.md.
pause
exit /b %EXITCODE%
