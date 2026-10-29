# Agregar Brave, Chrome o Edge a una instalacion Apex Descarga ya existente.
# NO instala motores, NO toca otros hosts ni elimina permisos previos.
[CmdletBinding()]
param(
  [ValidateSet('Brave','Chrome','Edge')][string]$Browser = 'Brave',
  [string]$ExtensionId = '',
  [string]$InstallDir = '',
  [switch]$SkipRegistration
)
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Solo Windows.' }
if (-not $InstallDir) { $InstallDir = Join-Path $env:LOCALAPPDATA 'ApexVideoDownloader' }
$InstallDir = [IO.Path]::GetFullPath($InstallDir)
$manifestPath = Join-Path $InstallDir 'com.apex.video_downloader.json'
$exe = Join-Path $InstallDir 'apex_host.exe'
$map = @{
  Brave = @{ reg='HKCU:\Software\BraveSoftware\Brave-Browser\NativeMessagingHosts\com.apex.video_downloader'; page='brave://extensions' }
  Chrome = @{ reg='HKCU:\Software\Google\Chrome\NativeMessagingHosts\com.apex.video_downloader'; page='chrome://extensions' }
  Edge = @{ reg='HKCU:\Software\Microsoft\Edge\NativeMessagingHosts\com.apex.video_downloader'; page='edge://extensions' }
}
if (-not $PSBoundParameters.ContainsKey('Browser') -and -not $SkipRegistration) {
  Write-Host '1 Brave, 2 Google Chrome, 3 Microsoft Edge'
  switch ((Read-Host 'Navegador [1]').Trim()) { '2' {$Browser='Chrome'} '3' {$Browser='Edge'} default {$Browser='Brave'} }
}
$reg = $map[$Browser].reg
$page = $map[$Browser].page
foreach ($item in @($manifestPath,$exe)) {
  if (-not (Test-Path -LiteralPath $item -PathType Leaf)) { throw "Falta $item. Realiza primero una instalacion inicial." }
}
$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($manifest.name -cne 'com.apex.video_downloader' -or $manifest.type -cne 'stdio' -or [string]$manifest.path -ine $exe) {
  throw 'El manifiesto no pertenece a la instalacion Apex esperada.'
}
$origins = @($manifest.allowed_origins)
if (-not $origins.Count -or @($origins | Where-Object { $_ -cnotmatch '^chrome-extension://[a-p]{32}/$' }).Count) {
  throw 'El manifiesto tiene origenes invalidos; no se modifica.'
}
Write-Host ('En ' + $Browser + ': abre ' + $page + ' y carga la carpeta descomprimida:')
Write-Host (Join-Path $InstallDir 'extension')
if (-not $ExtensionId) { $ExtensionId = Read-Host 'ID exacto de la extension (32 letras a-p)' }
$ExtensionId = $ExtensionId.Trim()
if ($ExtensionId -cnotmatch '^[a-p]{32}$') { throw 'ID invalido; no se modifica nada.' }
if ((Test-Path -LiteralPath $reg) -and -not $SkipRegistration) {
  $present = [string](Get-Item -LiteralPath $reg).GetValue('')
  if ($present -and $present -ine $manifestPath) { throw ("El registro de " + $Browser + " usa otro host: " + $present + ". No se cambia.") }
}
$origin = 'chrome-extension://' + $ExtensionId + '/'
if ($origins -ccontains $origin) {
  Write-Host 'El ID ya estaba autorizado. Se verificara su registro sin modificar la lista.' -ForegroundColor Cyan
} else {
  $confirm = 'S'
  if (-not $SkipRegistration) { $confirm = (Read-Host "Agregar el ID al manifiesto de Apex para $Browser? [S/N]").Trim().ToUpperInvariant() }
  if ($confirm -ne 'S') { throw 'Cancelado sin cambios.' }
  $backup = $manifestPath + '.bak-' + (Get-Date -Format yyyyMMdd_HHmmss) + '-' + [guid]::NewGuid().ToString('N')
  $manifest.allowed_origins = @($origins + @($origin) | Select-Object -Unique)
  $json = $manifest | ConvertTo-Json -Depth 10
  $temp = $manifestPath + '.tmp-' + [guid]::NewGuid().ToString('N')
  try {
    [IO.File]::WriteAllText($temp, $json, (New-Object System.Text.UTF8Encoding $false))
    [IO.File]::Replace($temp, $manifestPath, $backup, $false)
  } finally {
    if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force }
  }
  Write-Host "Respaldo: $backup" -ForegroundColor Cyan
}
if (-not $SkipRegistration) {
  New-Item -Path $reg -Force | Out-Null
  Set-Item -LiteralPath $reg -Value $manifestPath
  $verify = [string](Get-Item -LiteralPath $reg).GetValue('')
  if ($verify -ine $manifestPath) { throw 'No se pudo registrar el host.' }
  Write-Host "Listo: cierra $Browser por completo, abrelo y recarga Apex en $page." -ForegroundColor Green
} else {
  Write-Host 'Modo CI: autorizado en el manifiesto sin registrar la clave.' -ForegroundColor Green
}
