# Primera instalacion Apex Descarga 1.2.3; nunca reemplaza instalacion previa.
[CmdletBinding()]
param(
    [ValidateSet('Brave','Chrome','Edge')][string]$Browser = 'Brave',
    [string]$ExtensionId = '',
    [string]$InstallDir = '',
    [switch]$SkipRegistration
)
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Este instalador solo funciona en Windows.' }
if (-not $InstallDir) { $InstallDir = Join-Path $env:LOCALAPPDATA 'ApexVideoDownloader' }
$InstallDir = [IO.Path]::GetFullPath($InstallDir)
$sourceDir = Split-Path -Parent $PSScriptRoot
$sourceExtension = Join-Path $sourceDir 'extension'
$sourceHost = Join-Path $PSScriptRoot 'host.py'
$sourceLauncher = Join-Path $PSScriptRoot 'launcher.cs'
$manifestPath = Join-Path $InstallDir 'com.apex.video_downloader.json'
$launcherPath = Join-Path $InstallDir 'apex_host.exe'
$pythonPath = Join-Path $InstallDir 'python.path'
$extensionTarget = Join-Path $InstallDir 'extension'
if (-not $PSBoundParameters.ContainsKey('Browser') -and -not $SkipRegistration) {
    Write-Host 'Navegador: 1 Brave (recomendado), 2 Google Chrome (experimental), 3 Microsoft Edge (experimental).'
    $answer = (Read-Host 'Selecciona navegador [1]').Trim()
    switch ($answer) { '2' { $Browser='Chrome' } '3' { $Browser='Edge' } default { $Browser='Brave' } }
}
$browserSetup = @{
    Brave = @{ reg='HKCU:\Software\BraveSoftware\Brave-Browser\NativeMessagingHosts\com.apex.video_downloader'; page='brave://extensions' }
    Chrome = @{ reg='HKCU:\Software\Google\Chrome\NativeMessagingHosts\com.apex.video_downloader'; page='chrome://extensions' }
    Edge = @{ reg='HKCU:\Software\Microsoft\Edge\NativeMessagingHosts\com.apex.video_downloader'; page='edge://extensions' }
}
$regPath = $browserSetup[$Browser].reg
$extensionsPage = $browserSetup[$Browser].page
Write-Host ''
Write-Host ('APEX DESCARGA 1.2.3 - INSTALACION INICIAL WINDOWS / ' + $Browser) -ForegroundColor Cyan
Write-Host ('Apex Software Inc. / requiere Python 3.12 o 3.13 x64 y ' + $Browser + '.')
if ((Test-Path -LiteralPath $manifestPath) -or (Test-Path -LiteralPath $launcherPath)) {
    throw "Ya hay componentes Apex en $InstallDir. No se sobrescriben: usa ACTUALIZAR_APEX.cmd."
}
foreach ($needed in @($sourceHost, $sourceLauncher, (Join-Path $sourceExtension 'manifest.json'))) {
    if (-not (Test-Path -LiteralPath $needed -PathType Leaf)) { throw "Paquete incompleto: $needed" }
}
$extManifest = Get-Content (Join-Path $sourceExtension 'manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if ($extManifest.name -ne 'Apex Descarga' -or $extManifest.version -ne '1.2.3' -or $extManifest.manifest_version -ne 3) {
    throw 'La extension no corresponde a Apex Descarga 1.2.3 Manifest V3.'
}
$pythonCommand = $null
$pythonArgs = @()
foreach ($candidate in @(
    @{ cmd = 'py.exe'; args = @('-3.12') },
    @{ cmd = 'py.exe'; args = @('-3.13') },
    @{ cmd = 'python.exe'; args = @() }
)) {
    $found = Get-Command -Name ([string]$candidate['cmd']) -ErrorAction SilentlyContinue
    if (-not $found) { continue }
    $baseArgs = @($candidate['args'])
    $testArgs = $baseArgs + @('-c', 'import sys;sys.exit(0 if sys.version_info.major==3 and sys.version_info.minor in (12,13) and sys.maxsize>2**32 else 2)')
    try {
        Write-Host ("Comprobando Python: " + $found.Source + " " + ($baseArgs -join ' '))
        & $found.Source @testArgs 2>$null | Out-Null
        Write-Host ("Resultado: " + $LASTEXITCODE)
        if ($LASTEXITCODE -eq 0) {
            $pythonCommand = $found.Source
            $pythonArgs = $baseArgs
            break
        }
    } catch { }
}
if (-not $pythonCommand) { throw 'Instala Python 3.12/3.13 x64 desde python.org; luego abre otra consola.' }
Write-Host "Python compatible: $pythonCommand $($pythonArgs -join ' ')" -ForegroundColor Green
New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
$venvDir = Join-Path $InstallDir '.venv'
$venv = Join-Path $venvDir 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $venv -PathType Leaf)) {
    & $pythonCommand @pythonArgs -m venv $venvDir
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear el entorno Python local.' }
}
& $venv -m pip install --disable-pip-version-check --no-input yt-dlp
if ($LASTEXITCODE -ne 0) { throw 'No se pudo instalar yt-dlp; comprueba Internet y certificados.' }
& $venv -m yt_dlp --version
if ($LASTEXITCODE -ne 0) { throw 'yt-dlp no responde.' }
Copy-Item -LiteralPath $sourceHost -Destination (Join-Path $InstallDir 'host.py') -Force
Copy-Item -LiteralPath $sourceLauncher -Destination (Join-Path $InstallDir 'launcher.cs') -Force
& $venv -m py_compile (Join-Path $InstallDir 'host.py')
if ($LASTEXITCODE -ne 0) { throw 'host.py no pasa validacion.' }
Add-Type -Path (Join-Path $InstallDir 'launcher.cs') -OutputAssembly $launcherPath -OutputType ConsoleApplication -ErrorAction Stop
if (-not (Test-Path -LiteralPath $launcherPath -PathType Leaf)) { throw 'Fallo compilacion de puente.' }
[IO.File]::WriteAllText($pythonPath, $venv, (New-Object System.Text.UTF8Encoding $false))
if (-not (Test-Path -LiteralPath $extensionTarget -PathType Container)) {
    Copy-Item -LiteralPath $sourceExtension -Destination $extensionTarget -Recurse
}
Write-Host ''
Write-Host "Extension preparada: $extensionTarget" -ForegroundColor Cyan
Write-Host ("En " + $Browser + ": " + $extensionsPage + " > Modo desarrollador > Cargar descomprimida.")
Write-Host 'Selecciona la carpeta indicada, copia su ID de 32 letras y regresa aqui.'
if (-not $ExtensionId) { $ExtensionId = Read-Host 'ID de extension (32 letras a-p)' }
$ExtensionId = $ExtensionId.Trim()
if ($ExtensionId -cnotmatch '^[a-p]{32}$') { throw 'ID invalido. No se registro el host.' }
if ((Test-Path $regPath) -and (-not $SkipRegistration)) {
    $current = [string](Get-Item -LiteralPath $regPath).GetValue('')
    if ($current -and $current -ine $manifestPath) { throw "Hay un host previo en $current. No se sobrescribe." }
}
$manifest = @{
    name = 'com.apex.video_downloader'
    description = 'Apex Descarga 1.2.3 - host local'
    type = 'stdio'
    path = $launcherPath
    allowed_origins = @('chrome-extension://' + $ExtensionId + '/')
} | ConvertTo-Json -Depth 4
[IO.File]::WriteAllText($manifestPath, $manifest, (New-Object System.Text.UTF8Encoding $false))
if (-not $SkipRegistration) {
    New-Item -Path $regPath -Force | Out-Null
    Set-Item -LiteralPath $regPath -Value $manifestPath
    $registered = [string](Get-Item -LiteralPath $regPath).GetValue('')
    if ($registered -ine $manifestPath) { throw 'El registro Native Messaging no coincide.' }
}
Write-Host ''
Write-Host 'Instalacion inicial preparada.' -ForegroundColor Green
if ($SkipRegistration) { Write-Host 'Modo CI: registro omitido, no equivale a prueba de Brave real.' }
else {
    Write-Host ("Cierra " + $Browser + " COMPLETAMENTE, abrelo y recarga Apex en " + $extensionsPage + ".")
    Write-Host 'Comprueba CONECTADO / v1.2.3 en el icono de la extension; en Chrome/Edge es compatibilidad experimental.'
}
if (-not (Get-Command ffmpeg.exe -ErrorAction SilentlyContinue)) {
    Write-Host 'ATENCION: falta FFmpeg en PATH; MP3 y mezcla HD no funcionaran hasta instalarlo.' -ForegroundColor Yellow
}
if (-not (Get-Command deno.exe -ErrorAction SilentlyContinue)) {
    Write-Host 'Deno es opcional y algunos sitios pueden necesitarlo.' -ForegroundColor Yellow
}
