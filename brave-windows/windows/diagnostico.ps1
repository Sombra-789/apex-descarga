<#
  Apex Descarga Brave 1.2.3 - diagnostico y reparacion asistida.
  No descarga software, no solicita permisos de administrador y no modifica el
  registro de Windows. Solo cambia allowed_origins con consentimiento explicito.
#>
[CmdletBinding()]
param(
    [string]$ExtensionId = '',
    [string]$InstallDir = '',
    [switch]$Repair,
    [switch]$ConfirmRepair,
    [switch]$NonInteractive
)
$ErrorActionPreference = 'Stop'

function Say([string]$message, [string]$color = 'Gray') {
    Write-Host $message -ForegroundColor $color
}
function Check([string]$label, [bool]$ok, [string]$detail = '') {
    $state = if ($ok) { 'OK' } else { 'ATENCION' }
    $color = if ($ok) { 'Green' } else { 'Yellow' }
    Say ('[{0}] {1}{2}' -f $state, $label, $(if ($detail) { ' - ' + $detail } else { '' })) $color
}
function Is-ExtensionId([string]$value) {
    return $value -cmatch '^[a-p]{32}$'
}

try {
    if (-not $InstallDir) {
        $InstallDir = Join-Path $env:LOCALAPPDATA 'ApexVideoDownloader'
    }
    $InstallDir = [IO.Path]::GetFullPath($InstallDir)
    $manifestPath = Join-Path $InstallDir 'com.apex.video_downloader.json'
    $launcherPath = Join-Path $InstallDir 'apex_host.exe'
    $pythonFile = Join-Path $InstallDir 'python.path'

    Say ''
    Say '====================================================' 'Cyan'
    Say '  APEX DESCARGA 1.2.3 - DIAGNOSTICO BRAVE/WINDOWS' 'Cyan'
    Say '====================================================' 'Cyan'
    Say ('Directorio: ' + $InstallDir)

    if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        throw 'Falta el manifiesto Native Messaging. Instala primero el componente local de Apex.'
    }
    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($manifest.name -cne 'com.apex.video_downloader' -or $manifest.type -cne 'stdio') {
        throw 'El manifiesto no es el esperado para Apex. No se modifico.'
    }
    $origins = @($manifest.allowed_origins)
    if (-not $origins.Count -or @($origins | Where-Object { $_ -isnot [string] }).Count -gt 0) {
        throw 'La lista de origenes esta vacia o tiene un formato invalido.'
    }
    Check 'Manifiesto Native Messaging' $true $manifestPath
    $launcherOk = (Test-Path -LiteralPath $launcherPath -PathType Leaf) -and
                  ([IO.Path]::GetFullPath([string]$manifest.path) -ieq $launcherPath)
    Check 'Ejecutable local apex_host.exe' $launcherOk
    if (-not $launcherOk) {
        Say 'El ejecutable falta o la ruta del manifiesto es distinta. No se aplicaran reparaciones.' 'Red'
    }

    # Registro: solamente consulta. Brave puede heredar claves de Chromium/Chrome.
    $regKeys = @(
        'HKCU:\Software\BraveSoftware\Brave-Browser\NativeMessagingHosts\com.apex.video_downloader',
        'HKCU:\Software\Google\Chrome\NativeMessagingHosts\com.apex.video_downloader',
        'HKLM:\Software\BraveSoftware\Brave-Browser\NativeMessagingHosts\com.apex.video_downloader',
        'HKLM:\Software\Google\Chrome\NativeMessagingHosts\com.apex.video_downloader'
    )
    $registered = @()
    if ($IsWindows -or $env:OS -eq 'Windows_NT') {
        foreach ($key in $regKeys) {
            $item = Get-Item -LiteralPath $key -ErrorAction SilentlyContinue
            if ($null -ne $item) {
                $value = [string]$item.GetValue('')
                if ($value) {
                    $registered += [pscustomobject]@{ Key = $key; Path = $value }
                }
            }
        }
    }
    if ($registered.Count) {
        foreach ($entry in $registered) {
            Check ('Registro ' + $entry.Key) ($entry.Path -ieq $manifestPath) $entry.Path
        }
    } else {
        Say '[INFO] Sin registro en las ubicaciones habituales consultadas. Si Brave conecta, el registro puede estar en otra vista/ubicacion.' 'Yellow'
    }

    # Verificaciones informativas: no instalar ni actualizar dependencias automaticamente.
    $python = ''
    if (Test-Path -LiteralPath $pythonFile -PathType Leaf) {
        $python = (Get-Content -LiteralPath $pythonFile -Raw -Encoding UTF8).Trim().Trim('"')
    }
    $pythonOk = $python -and (Test-Path -LiteralPath $python -PathType Leaf)
    Check 'Python configurado' ([bool]$pythonOk) $python
    if ($pythonOk) {
        try {
            $yt = & $python -m yt_dlp --version 2>$null
            Check 'yt-dlp instalado' ($LASTEXITCODE -eq 0) ([string]($yt | Select-Object -First 1))
        } catch {
            Check 'yt-dlp instalado' $false 'No se pudo consultar'
        }
    } else {
        Check 'yt-dlp instalado' $false 'Requiere Python configurado'
    }
    Check 'FFmpeg en PATH' ([bool](Get-Command 'ffmpeg.exe' -ErrorAction SilentlyContinue))
    Check 'Deno en PATH (opcional segun sitio)' ([bool](Get-Command 'deno.exe' -ErrorAction SilentlyContinue))

    if (-not $ExtensionId -and -not $NonInteractive) {
        Say ''
        Say 'Copia el ID de Apex en brave://extensions (modo desarrollador).' 'Cyan'
        $ExtensionId = (Read-Host 'ID de la extension (Enter para salir sin cambios)').Trim()
    }
    if (-not $ExtensionId) {
        Say 'Diagnostico sin comparacion de ID. No se modifico nada.' 'Yellow'
        return
    }
    $ExtensionId = $ExtensionId.Trim()
    if (-not (Is-ExtensionId $ExtensionId)) {
        throw 'ID invalido. Debe tener exactamente 32 letras minusculas entre a y p.'
    }
    $expected = 'chrome-extension://' + $ExtensionId + '/'
    $matches = ($origins -ccontains $expected)
    Check 'Permiso para la extension actual' $matches $expected
    if ($matches) {
        Say 'Los permisos de Native Messaging ya coinciden. No es necesario reparar.' 'Green'
        return
    }
    Say ('Origenes anteriores: ' + ($origins -join ', ')) 'Yellow'
    Say 'El ID de Brave no coincide con allowed_origins. Esto causa el error de acceso prohibido.' 'Yellow'
    if (-not $Repair) {
        Say 'No se realizo ningun cambio. Abre REPARAR_APEX.cmd para reparar con confirmacion.' 'Cyan'
        return
    }
    if ($origins.Count -gt 1) {
        throw 'Hay varios navegadores autorizados. Para agregar un ID sin revocar otros, usa AGREGAR_NAVEGADOR.cmd; el reparador sencillo no sustituira todos los origenes.'
    }
    if (-not $launcherOk) {
        throw 'No se puede reparar: primero debe comprobarse la ruta de apex_host.exe.'
    }
    if ($registered.Count -and -not @($registered | Where-Object { $_.Path -ieq $manifestPath }).Count) {
        throw 'El registro apunta a otro manifiesto. No se cambio este archivo para evitar corregir una instalacion equivocada.'
    }
    if (-not $ConfirmRepair) {
        if ($NonInteractive) {
            throw 'Se requiere -ConfirmRepair para reparacion no interactiva.'
        }
        Say 'Esta reparacion revocara el ID anterior y autorizara SOLO el ID proporcionado.' 'Cyan'
        $confirmation = Read-Host 'Escribe REPARAR para confirmar (cualquier otra respuesta cancela)'
        if ($confirmation -cne 'REPARAR') {
            Say 'Cancelado. No se realizo ningun cambio.' 'Yellow'
            return
        }
    }

    $manifest.allowed_origins = @($expected)
    $json = $manifest | ConvertTo-Json -Depth 12
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    $stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $backup = $manifestPath + '.bak-' + $stamp
    $temp = $manifestPath + '.tmp-' + [guid]::NewGuid().ToString('N')
    try {
        [IO.File]::WriteAllText($temp, $json, $utf8)
        # File.Replace mantiene el manifiesto previo como copia de seguridad.
        [IO.File]::Replace($temp, $manifestPath, $backup, $false)
    } finally {
        if (Test-Path -LiteralPath $temp) {
            Remove-Item -LiteralPath $temp -Force
        }
    }
    $verify = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if (@($verify.allowed_origins).Count -ne 1 -or $verify.allowed_origins[0] -cne $expected) {
        throw 'No se pudo verificar el nuevo permiso. Revisa la copia de seguridad.'
    }
    Say ('Respaldo: ' + $backup) 'Cyan'
    Say ('Origen autorizado: ' + $expected) 'Green'
    Say 'REPARACION FINALIZADA. Cierra Brave por completo, abrelo y recarga Apex en brave://extensions.' 'Green'
} catch {
    Say ('[ERROR] ' + $_.Exception.Message) 'Red'
    exit 1
}