$ErrorActionPreference='Stop'
$root = Join-Path $env:TEMP ('ApexNativeTest_' + [guid]::NewGuid().ToString('N'))
$folder=Join-Path $root 'ApexVideoDownloader'
New-Item -ItemType Directory -Path $folder -Force | Out-Null
try {
    $exe = Join-Path $folder 'apex_host.exe'
    [IO.File]::WriteAllBytes($exe, [byte[]]@(0))
    $manifest = Join-Path $folder 'com.apex.video_downloader.json'
    $prior='chrome-extension://ogibajeopkkcgjlnjdpkdppdicbcodlm/'
    $next='chrome-extension://codeljnkpoahdegaopkiabplpcagpljl/'
    $inputManifest=@{name='com.apex.video_downloader';path=$exe;type='stdio';description='Test';allowed_origins=@($prior)} | ConvertTo-Json
    [IO.File]::WriteAllText($manifest, $inputManifest)
    $script=Join-Path $PSScriptRoot '..\windows\diagnostico.ps1'

    & $script -InstallDir $folder -ExtensionId 'codeljnkpoahdegaopkiabplpcagpljl' -NonInteractive
    if ((Get-Content $manifest -Raw | ConvertFrom-Json).allowed_origins[0] -cne $prior) {
        throw 'El diagnostico modifico la autorizacion sin permiso.'
    }

    & $script -InstallDir $folder -ExtensionId 'codeljnkpoahdegaopkiabplpcagpljl' -Repair -ConfirmRepair -NonInteractive
    if ((Get-Content $manifest -Raw | ConvertFrom-Json).allowed_origins[0] -cne $next) {
        throw 'No se actualizo el ID.'
    }
    $backup=Get-ChildItem -LiteralPath $folder -Filter '*.bak-*'
    if (-not $backup -or ((Get-Content $backup[0].FullName -Raw | ConvertFrom-Json).allowed_origins[0] -cne $prior)) {
        throw 'No se conservo el manifiesto original.'
    }

    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $script -InstallDir $folder -ExtensionId 'INVALID' -Repair -ConfirmRepair -NonInteractive
    if ($LASTEXITCODE -eq 0) { throw 'Se acepto un ID invalido.' }
    if ((Get-Content $manifest -Raw | ConvertFrom-Json).allowed_origins[0] -cne $next) {
        throw 'Un ID invalido modifico el manifiesto.'
    }
    # El caso negativo anterior devolvio 1 como se esperaba. Limpiar ese codigo
    # evita que GitHub Actions marque como fallida una prueba que paso.
    $global:LASTEXITCODE = 0
    Write-Host 'PASS: diagnostico de solo lectura, reparacion consentida, respaldo, rechazo ID invalido.' -ForegroundColor Green
} finally {
    Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
}