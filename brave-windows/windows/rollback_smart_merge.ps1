$ErrorActionPreference = 'Stop'
$install = Join-Path $env:LOCALAPPDATA 'ApexVideoDownloader'
$pointer = Join-Path $install 'smart_merge_alpha_backup.json'
if (-not (Test-Path -LiteralPath $pointer -PathType Leaf)) {
    throw 'No se encontro respaldo registrado de Smart Merge Alpha.'
}
$record = Get-Content -LiteralPath $pointer -Raw -Encoding UTF8 | ConvertFrom-Json
$backup = [IO.Path]::GetFullPath([string]$record.backupRoot)
$target = [IO.Path]::GetFullPath([string]$record.extensionPath)
$root = Join-Path $backup 'extension'
$manifest = Join-Path $root 'manifest.json'
$host = Join-Path $backup 'host.py'
if (-not (Test-Path -LiteralPath $manifest -PathType Leaf) -or
    -not (Test-Path -LiteralPath $host -PathType Leaf)) {
    throw 'El respaldo no esta completo. No se realizo ninguna modificacion.'
}
$oldVersion = (Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json).version
if ($oldVersion -cne '1.2.3') { throw 'El respaldo no corresponde a Apex 1.2.3.' }
$current = Join-Path $target 'manifest.json'
if (-not (Test-Path -LiteralPath $current -PathType Leaf) -or
    (Get-Content -LiteralPath $current -Raw | ConvertFrom-Json).version -cne '2.0.0') {
    throw 'La extension activa no parece la Alpha 2.0. Restauracion detenida.'
}
Write-Host ('Se restaurara Apex Descarga 1.2.3 desde ' + $backup) -ForegroundColor Yellow
Write-Host 'No se borraran tus descargas ni el historial del navegador.'
$confirmation = Read-Host 'Cierra Brave y escribe RESTAURAR para confirmar'
if ($confirmation -cne 'RESTAURAR') { throw 'Cancelado sin cambios.' }
foreach ($name in @('manifest.json','popup.html','popup.css','popup.js','background.js')) {
    $original = Join-Path $root $name
    if (-not (Test-Path -LiteralPath $original -PathType Leaf)) { throw ('Falta respaldo: ' + $name) }
}
foreach ($name in @('manifest.json','popup.html','popup.css','popup.js','background.js')) {
    Copy-Item -LiteralPath (Join-Path $root $name) -Destination (Join-Path $target $name) -Force
}
Copy-Item -LiteralPath $host -Destination (Join-Path $install 'host.py') -Force
if (-not (Test-Path -LiteralPath (Join-Path $root 'smart_merge_ui.js'))) {
    Remove-Item -LiteralPath (Join-Path $target 'smart_merge_ui.js') -Force -ErrorAction SilentlyContinue
}
Remove-Item -LiteralPath (Join-Path $install 'smart_merge.py') -Force -ErrorAction SilentlyContinue
if ((Get-Content -LiteralPath (Join-Path $target 'manifest.json') -Raw | ConvertFrom-Json).version -cne '1.2.3') {
    throw 'Fallo la comprobacion de la version restaurada.'
}
Remove-Item -LiteralPath $pointer -Force
Write-Host 'Apex Descarga 1.2.3 restaurada. Abre Brave y recarga la extension.' -ForegroundColor Green
Write-Host ('El respaldo original permanece en: ' + $backup)
