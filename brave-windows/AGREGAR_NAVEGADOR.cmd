@echo off
setlocal
chcp 65001 >nul
echo Apex Descarga - agregar navegador Chromium (Brave/Chrome/Edge)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0windows\add-browser.ps1"
set "RESULT=%ERRORLEVEL%"
if not "%RESULT%"=="0" echo [ERROR] No se completo la autorizacion. Consulta GUIA_NAVEGADORES.md.
pause
exit /b %RESULT%
