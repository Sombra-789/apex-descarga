$ErrorActionPreference = 'Stop'
$InstallDir = Join-Path $env:LOCALAPPDATA 'ApexVideoDownloader'
$SourceExtension = Join-Path (Split-Path -Parent $PSScriptRoot) 'extension'
$SourceHost = Join-Path $PSScriptRoot 'host.py'

Write-Host ''
Write-Host '=======================================================' -ForegroundColor Cyan
Write-Host '    APEX DESCARGA 1.2.2 - ACTUALIZADOR SEGURO' -ForegroundColor Cyan
Write-Host '=======================================================' -ForegroundColor Cyan
Write-Host 'Conserva la extension y el ID que ya funcionan en Brave.'
Write-Host 'Actualiza la interfaz, los iconos y host.py; conserva el registro y el EXE.'
Write-Host 'No necesita permisos de administrador.'
Write-Host ''

if (-not (Test-Path -LiteralPath $SourceHost -PathType Leaf)) { throw 'Paquete incompleto: falta windows\host.py.' }
$existingHost = Join-Path $InstallDir 'host.py'
$existingManifest = Join-Path $InstallDir 'com.apex.video_downloader.json'
$existingLauncher = Join-Path $InstallDir 'apex_host.exe'
$pythonPath = Join-Path $InstallDir 'python.path'
foreach ($f in @($existingHost, $existingManifest, $existingLauncher, $pythonPath)) {
    if (-not (Test-Path -LiteralPath $f -PathType Leaf)) {
        throw ('Falta el componente local: ' + $f + '. Instala primero Apex 1.0.2.')
    }
}
$manifestNative = Get-Content -LiteralPath $existingManifest -Raw -Encoding UTF8 | ConvertFrom-Json
if ($manifestNative.name -cne 'com.apex.video_downloader' -or @($manifestNative.allowed_origins).Count -ne 1) {
    throw 'El manifiesto Native Messaging no corresponde a Apex. Se detuvo para proteger tu conexion actual.'
}
Write-Host ('Componente local: ' + $InstallDir) -ForegroundColor Green
Write-Host ('Origen permitido: ' + @($manifestNative.allowed_origins)[0]) -ForegroundColor Green

# Select the exact unpacked extension folder already used by Brave. Updating
# THAT folder (instead of loading a copy) preserves the Chromium extension ID.
Write-Host ''
Write-Host 'Selecciona la carpeta EXTENSION que Brave ya usa para Apex.' -ForegroundColor Yellow
Write-Host 'No elijas la carpeta extension que viene dentro de este nuevo ZIP.' -ForegroundColor Yellow
Write-Host 'Si aparece un explorador de carpetas, navega a la instalacion ANTERIOR.'
$ExtensionTarget = ''
try {
    Add-Type -AssemblyName System.Windows.Forms
    $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
    $dialog.Description = 'Elige la carpeta extension ORIGINAL que esta cargada en Brave (no la nueva).'
    $dialog.ShowNewFolderButton = $false
    if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { $ExtensionTarget = $dialog.SelectedPath }
} catch {
    Write-Host 'No se pudo abrir la seleccion grafica; introduce la ruta manualmente.' -ForegroundColor Yellow
}
if ([string]::IsNullOrWhiteSpace($ExtensionTarget)) {
    $ExtensionTarget = Read-Host 'Ruta completa de la carpeta extension ORIGINAL (o Enter para cancelar)'
}
$ExtensionTarget = $ExtensionTarget.Trim().Trim('"')
if ([string]::IsNullOrWhiteSpace($ExtensionTarget)) { throw 'Cancelado: no se eligio la extension instalada.' }
$ExtensionTarget = [IO.Path]::GetFullPath($ExtensionTarget)
if (-not (Test-Path -LiteralPath $ExtensionTarget -PathType Container)) { throw 'La carpeta seleccionada no existe.' }
$sourceFull = [IO.Path]::GetFullPath($SourceExtension)
if ($ExtensionTarget.TrimEnd('\') -ieq $sourceFull.TrimEnd('\')) {
    throw 'Elegiste la extension NUEVA. Se requiere la carpeta anterior que Brave ya tiene cargada.'
}
$targetManifest = Join-Path $ExtensionTarget 'manifest.json'
if (-not (Test-Path -LiteralPath $targetManifest -PathType Leaf)) { throw 'La carpeta no contiene manifest.json.' }
$parsedManifest = Get-Content -LiteralPath $targetManifest -Raw -Encoding UTF8 | ConvertFrom-Json
if ((@('Apex Video Downloader','Apex Descarga') -notcontains [string]$parsedManifest.name) -or $parsedManifest.manifest_version -ne 3) {
    throw 'Esa carpeta no es nuestra extensión Apex Manifest V3.'
}
if (-not (Test-Path -LiteralPath (Join-Path $ExtensionTarget 'background.js') -PathType Leaf)) {
    throw 'La carpeta seleccionada no parece ser la extension original de Apex.'
}
Write-Host ('Extension seleccionada: ' + $ExtensionTarget) -ForegroundColor Green

$python = (Get-Content -LiteralPath $pythonPath -Raw -Encoding UTF8).Trim()
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw 'No se encontro el Python asociado a Apex.' }
& $python -m py_compile $SourceHost
if ($LASTEXITCODE -ne 0) { throw 'El nuevo host.py no pasa la comprobacion de sintaxis de Python.' }
Write-Host 'Python valido; actualizacion verificada.' -ForegroundColor Green

$confirmation = Read-Host 'Cerraste Brave completamente y confirmas esta carpeta? [S/N]'
if ($confirmation.Trim().ToUpperInvariant() -ne 'S') { throw 'Cancelado por el usuario; no se ha modificado ningun archivo.' }

# Keep backup OUTSIDE the extension folder (Brave only reads its root) and a
# second backup of host.py. Never delete user data or reinstall dependencies.
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$backupRoot = Join-Path $env:LOCALAPPDATA ('ApexVideoDownloader_backup_' + $stamp)
$backupExt = Join-Path $backupRoot 'extension_anterior'
New-Item -ItemType Directory -Path $backupExt -Force | Out-Null
foreach ($name in @('manifest.json', 'popup.html', 'popup.css', 'popup.js', 'background.js')) {
    $file = Join-Path $ExtensionTarget $name
    if (Test-Path -LiteralPath $file -PathType Leaf) { Copy-Item -LiteralPath $file -Destination (Join-Path $backupExt $name) -Force }
}
Copy-Item -LiteralPath $existingHost -Destination (Join-Path $backupRoot 'host_anterior.py') -Force
$sourceIcons = Join-Path $SourceExtension 'icons'
$targetIcons = Join-Path $ExtensionTarget 'icons'
$backupIcons = Join-Path $backupRoot 'icons_anteriores'
if (Test-Path -LiteralPath $targetIcons -PathType Container) {
    Copy-Item -LiteralPath $targetIcons -Destination $backupIcons -Recurse -Force
}
Write-Host ('Respaldo: ' + $backupRoot) -ForegroundColor Cyan
try {
    foreach ($name in @('manifest.json', 'popup.html', 'popup.css', 'popup.js', 'background.js')) {
        Copy-Item -LiteralPath (Join-Path $SourceExtension $name) -Destination (Join-Path $ExtensionTarget $name) -Force
    }
    if (-not (Test-Path -LiteralPath $sourceIcons -PathType Container)) { throw 'Falta carpeta icons del paquete.' }
    if (-not (Test-Path -LiteralPath $targetIcons -PathType Container)) { New-Item -ItemType Directory -Path $targetIcons -Force | Out-Null }
    foreach ($icon in @('brand.png', '16.png', '48.png', '128.png')) {
        Copy-Item -LiteralPath (Join-Path $sourceIcons $icon) -Destination (Join-Path $targetIcons $icon) -Force
    }
    Copy-Item -LiteralPath $SourceHost -Destination $existingHost -Force
    $applied = Get-Content -LiteralPath $targetManifest -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($applied.version -cne '1.2.2') { throw 'No se pudo actualizar el manifiesto de la extensión.' }
} catch {
    foreach ($name in @('manifest.json', 'popup.html', 'popup.css', 'popup.js', 'background.js')) {
        $old = Join-Path $backupExt $name
        if (Test-Path -LiteralPath $old) { Copy-Item -LiteralPath $old -Destination (Join-Path $ExtensionTarget $name) -Force }
    }
    Copy-Item -LiteralPath (Join-Path $backupRoot 'host_anterior.py') -Destination $existingHost -Force
    if (Test-Path -LiteralPath $backupIcons -PathType Container) {
        foreach ($icon in @('brand.png', '16.png', '48.png', '128.png')) {
            $prior = Join-Path $backupIcons $icon
            if (Test-Path -LiteralPath $prior -PathType Leaf) { Copy-Item -LiteralPath $prior -Destination (Join-Path $targetIcons $icon) -Force }
        }
    }
    throw ('Actualizacion revertida desde copia de seguridad: ' + $_.Exception.Message)
}
Write-Host ''
Write-Host 'ACTUALIZACION 1.2.2 APLICADA.' -ForegroundColor Green
Write-Host 'Tu ID, el registro Native Messaging y los archivos descargados siguen intactos.' -ForegroundColor Green
Write-Host 'En brave://extensions, pulsa ACTUALIZAR (o la flecha recargar de Apex).' -ForegroundColor Cyan
Write-Host 'Abre el icono de Apex y comprueba Conectado y V1.2.2.'
Write-Host ('Respaldo de seguridad: ' + $backupRoot)
Write-Host ''
