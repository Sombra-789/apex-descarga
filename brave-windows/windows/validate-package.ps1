$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$manifest = Get-Content -LiteralPath (Join-Path $root 'extension/manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$version = [string]$manifest.version
$hostSource = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'host.py') -Raw -Encoding UTF8
if ($version -ne '1.2.4' -or $manifest.action.default_title -ne "Apex Descarga $version" -or
    $hostSource -notmatch "(?m)^VERSION = '$([regex]::Escape($version))'\r?$" ) {
    throw 'Paquete inconsistente: las versiones de la extension y del componente local no coinciden.'
}
foreach ($file in @('site-policy.js', 'background.js', 'popup.js', 'popup.html', 'popup.css')) {
    if (-not (Test-Path -LiteralPath (Join-Path $root "extension/$file") -PathType Leaf)) { throw "Paquete incompleto: falta $file" }
}
