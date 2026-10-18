$ErrorActionPreference = 'Stop'
$InstallDir = Join-Path $env:LOCALAPPDATA 'ApexVideoDownloader'
$SourceRoot = Split-Path -Parent $PSScriptRoot
$SourceWin = Join-Path $SourceRoot 'windows'
$SourceExt = Join-Path $SourceRoot 'extension'
$manifestLocal = Join-Path $InstallDir 'com.apex.video_downloader.json'
$hostLocal = Join-Path $InstallDir 'host.py'
$pythonFile = Join-Path $InstallDir 'python.path'
$backupPointer = Join-Path $InstallDir 'smart_merge_alpha_backup.json'
$requiredSource = @('windows\host.py','windows\smart_merge.py','extension\manifest.json',
                    'extension\popup.html','extension\popup.css','extension\popup.js',
                    'extension\smart_merge_ui.js','extension\background.js')
Write-Host '========================================================' -ForegroundColor Cyan
Write-Host ' APEX DESCARGA 2.0 - SMART MERGE ALPHA (PRUEBAS)' -ForegroundColor Cyan
Write-Host '========================================================' -ForegroundColor Cyan
Write-Host 'Esta Alpha cambia TEMPORALMENTE la instalacion 1.2.3 y crea respaldo restaurable.' -ForegroundColor Yellow
Write-Host 'Requiere 7-Zip instalado para reconstruccion RAR. NO lo instala automaticamente.' -ForegroundColor Yellow
Write-Host ''
foreach ($relative in $requiredSource) {
    if (-not (Test-Path -LiteralPath (Join-Path $SourceRoot $relative) -PathType Leaf)) {
        throw ('Paquete incompleto: ' + $relative)
    }
}
foreach ($file in @($manifestLocal, $hostLocal, $pythonFile, (Join-Path $InstallDir 'apex_host.exe'))) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
        throw ('Falta un componente estable: ' + $file)
    }
}
if (Test-Path -LiteralPath $backupPointer) {
    throw 'Ya existe un respaldo activo de Smart Merge. Primero restaura 1.2.3 o conserva la instalacion actual.'
}
$old = Get-Content -LiteralPath $manifestLocal -Raw | ConvertFrom-Json
if ($old.name -cne 'com.apex.video_downloader' -or $old.type -cne 'stdio') {
    throw 'No es el manifiesto Native Messaging de Apex. Se cancela.'
}
$python = (Get-Content -LiteralPath $pythonFile -Raw -Encoding UTF8).Trim().Trim('"')
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw 'Python configurado no encontrado.' }
& $python -m py_compile (Join-Path $SourceWin 'host.py') (Join-Path $SourceWin 'smart_merge.py')
if ($LASTEXITCODE -ne 0) { throw 'No paso la comprobacion de sintaxis Python.' }
Add-Type -AssemblyName System.Windows.Forms
$chooser = New-Object System.Windows.Forms.FolderBrowserDialog
$chooser.Description = 'Selecciona la carpeta extension ORIGINAL cargada en Brave (no la del paquete Alpha).'
$chooser.ShowNewFolderButton = $false
if ($chooser.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) { throw 'Cancelado por el usuario.' }
$target = [IO.Path]::GetFullPath($chooser.SelectedPath)
if ($target.TrimEnd('\') -ieq [IO.Path]::GetFullPath($SourceExt).TrimEnd('\')) {
    throw 'No puedes seleccionar la carpeta extension del propio paquete Alpha.'
}
$targetManifest = Join-Path $target 'manifest.json'
if (-not (Test-Path -LiteralPath $targetManifest -PathType Leaf)) { throw 'Falta manifest.json en la extension original.' }
$oldExt = Get-Content -LiteralPath $targetManifest -Raw | ConvertFrom-Json
if ($oldExt.name -cne 'Apex Descarga' -or $oldExt.version -cne '1.2.3') {
    throw 'Por seguridad, solo actualiza una extension Apex Descarga 1.2.3 original.'
}
$confirmation = Read-Host 'Brave debe estar cerrado. Escribe ALPHA para instalar y crear respaldo'
if ($confirmation -cne 'ALPHA') { throw 'Cancelado: no se modificaron archivos.' }
$backup = Join-Path $env:LOCALAPPDATA ('ApexSmartMergeBackup_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '_' + [guid]::NewGuid().ToString('N').Substring(0, 8))
$backupExt = Join-Path $backup 'extension'
$backupHost = Join-Path $backup 'host.py'
New-Item -ItemType Directory -Path $backupExt -Force | Out-Null
$extFiles = @('manifest.json','popup.html','popup.css','popup.js','background.js','smart_merge_ui.js')
foreach ($name in $extFiles) {
    $current = Join-Path $target $name
    if (Test-Path -LiteralPath $current -PathType Leaf) {
        Copy-Item -LiteralPath $current -Destination (Join-Path $backupExt $name) -Force
    }
}
Copy-Item -LiteralPath $hostLocal -Destination $backupHost -Force
try {
    foreach ($name in $extFiles) {
        $source = Join-Path $SourceExt $name
        if (Test-Path -LiteralPath $source -PathType Leaf) {
            Copy-Item -LiteralPath $source -Destination (Join-Path $target $name) -Force
        }
    }
    Copy-Item -LiteralPath (Join-Path $SourceWin 'host.py') -Destination $hostLocal -Force
    Copy-Item -LiteralPath (Join-Path $SourceWin 'smart_merge.py') -Destination (Join-Path $InstallDir 'smart_merge.py') -Force
    $new = Get-Content -LiteralPath $targetManifest -Raw | ConvertFrom-Json
    if ($new.version -cne '2.0.0' -or -not (Test-Path (Join-Path $InstallDir 'smart_merge.py'))) {
        throw 'La version Alpha no quedo instalada.'
    }
    $record = @{ backupRoot = $backup; extensionPath = $target; createdAt = (Get-Date).ToString('s') }
    $record | ConvertTo-Json | Set-Content -LiteralPath $backupPointer -Encoding UTF8
} catch {
    foreach ($name in $extFiles) {
        $original = Join-Path $backupExt $name
        $dest = Join-Path $target $name
        if (Test-Path -LiteralPath $original -PathType Leaf) {
            Copy-Item -LiteralPath $original -Destination $dest -Force
        } elseif ($name -eq 'smart_merge_ui.js' -and (Test-Path $dest)) {
            Remove-Item -LiteralPath $dest -Force
        }
    }
    Copy-Item -LiteralPath $backupHost -Destination $hostLocal -Force
    Remove-Item -LiteralPath (Join-Path $InstallDir 'smart_merge.py') -Force -ErrorAction SilentlyContinue
    throw ('Instalacion revertida: ' + $_.Exception.Message)
}
Write-Host ('Respaldo protegido: ' + $backup) -ForegroundColor Green
Write-Host 'ALPHA INSTALADA. El ID de Brave y el registro Native Messaging no se modificaron.' -ForegroundColor Green
Write-Host 'Abre Brave, recarga Apex en brave://extensions y comprueba Conectado.' -ForegroundColor Cyan
Write-Host 'Para volver a 1.2.3 cierra Brave y ejecuta RESTAURAR_APEX_1_2_3.cmd.' -ForegroundColor Yellow
