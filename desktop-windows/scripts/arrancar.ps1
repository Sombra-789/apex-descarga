$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $project

function Test-ApexPython([string]$Exe, [string[]]$ExtraArgs) {
    try {
        if (-not (Get-Command -Name $Exe -ErrorAction SilentlyContinue)) { return $null }
        $v = & $Exe @ExtraArgs -c 'import sys; print(str(sys.version_info.major) + "." + str(sys.version_info.minor))' 2>$null
        if ($LASTEXITCODE -ne 0) { return $null }
        $v = "$v".Trim()
        if ($v -match '^3\.(11|12|13)$') {
            return @{ Exe=$Exe; Args=@($ExtraArgs); Version=$v }
        }
    } catch { }
    return $null
}

function Find-ApexPython {
    foreach ($minor in @('3.13','3.12','3.11')) {
        $candidate = Test-ApexPython -Exe 'py' -ExtraArgs @("-$minor")
        if ($candidate) { return $candidate }
    }
    foreach ($root in @((Join-Path $env:LOCALAPPDATA 'Programs\Python'),$env:ProgramFiles,${env:ProgramFiles(x86)})) {
        if (-not $root -or -not (Test-Path -LiteralPath $root -PathType Container)) { continue }
        foreach ($minor in @('313','312','311')) {
            foreach ($path in @(
                (Join-Path $root "Python$minor\python.exe"),
                (Join-Path $root "Python\Python$minor\python.exe")
            )) {
                $candidate=Test-ApexPython -Exe $path -ExtraArgs @()
                if ($candidate) { return $candidate }
            }
        }
    }
    foreach ($command in @('python','python3')) {
        $candidate=Test-ApexPython -Exe $command -ExtraArgs @()
        if ($candidate) { return $candidate }
    }
    Write-Host 'Apex necesita Python 3.11, 3.12 o 3.13 para ejecutar el codigo fuente.' -ForegroundColor Yellow
    Write-Host 'Puedes tener Python 3.15 instalado al mismo tiempo. Instala 3.12 con:'
    Write-Host 'winget install -e --id Python.Python.3.12' -ForegroundColor Cyan
    Write-Host 'O descarga el archivo ApexDescargaDesktop.exe desde las Actions de GitHub; no necesita Python externo.'
    throw 'Python compatible no encontrado.'
}

$venv = Join-Path $project '.venv'
$pythonExe = Join-Path $venv 'Scripts\python.exe'
if (Test-Path -LiteralPath $pythonExe -PathType Leaf) {
    if (-not (Test-ApexPython -Exe $pythonExe -ExtraArgs @())) {
        throw 'La carpeta .venv existente usa Python incompatible. Renombrala a .venv_antiguo y vuelve a ejecutar.'
    }
} else {
    $python = Find-ApexPython
    $exe=$python.Exe
    $arguments=@($python.Args)
    Write-Host "Creando entorno aislado con Python $($python.Version)..." -ForegroundColor Cyan
    & $exe @arguments -m venv $venv
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear el entorno virtual.' }
}
Write-Host 'Instalando dependencias verificadas de Apex Desktop...' -ForegroundColor Cyan
& $pythonExe -m pip install --disable-pip-version-check -r (Join-Path $project 'requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'Error instalando dependencias. Comprueba tu conexion.' }
Write-Host 'Abriendo Apex Descarga Desktop 0.2 UI Pro...' -ForegroundColor Green
& $pythonExe (Join-Path $project 'main.py')
if ($LASTEXITCODE -ne 0) { throw 'Apex Descarga se cerro con un error.' }
