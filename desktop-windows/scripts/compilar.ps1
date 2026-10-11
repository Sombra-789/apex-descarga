$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
Set-Location $project
$venvPython = Join-Path $project '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $venvPython)) {
  Write-Host 'Primero ejecuta INICIAR_APEX.cmd para crear el entorno Python.' -ForegroundColor Yellow
  throw 'Entorno Python no disponible.'
}
Write-Host 'Preparando PyInstaller en el entorno aislado...' -ForegroundColor Cyan
& $venvPython -m pip install --disable-pip-version-check -r (Join-Path $project 'requirements-build.txt')
if ($LASTEXITCODE -ne 0) { throw 'Fallo al instalar PyInstaller.' }
Write-Host 'Generando aplicación .exe de Windows (sin Brave)...' -ForegroundColor Cyan
& $venvPython -m PyInstaller --noconfirm --clean --onefile --windowed --name 'ApexDescargaDesktop' --icon (Join-Path $project 'assets\apex_icon.ico') --add-data 'assets\apex_icon.png;assets' --collect-all 'yt_dlp' (Join-Path $project 'main.py')
if ($LASTEXITCODE -ne 0) { throw 'Fallo PyInstaller. Revisa el error de compilación.' }
$exe = Join-Path $project 'dist\ApexDescargaDesktop.exe'
if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw 'No se encontró el archivo .exe esperado.' }
Write-Host 'LISTO: ' $exe -ForegroundColor Green
Write-Host 'FFmpeg debe estar en PATH o en dist\bin\ffmpeg.exe para crear MP3 y combinar video HD.'
Write-Host 'El ejecutable está destinado a pruebas: comprobar firma y licencias antes de distribución.'
