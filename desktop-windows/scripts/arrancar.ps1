$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $project

# Python 3.15 es experimental y actualmente no es el objetivo de esta beta.
# Detectar Python compatible tanto con el launcher "py" como sin el launcher.
function Test-PythonCandidate([string]$Exe, [string[]]$ExtraArgs) {
  try {
    $command = Get-Command -Name $Exe -ErrorAction SilentlyContinue
    if (-not $command) { return $null }
    $version = & $Exe @ExtraArgs -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>$null
    if ($LASTEXITCODE -ne 0) { return $null }
    $version = "$version".Trim()
    if ($version -match '^3\.(11|12|13)$') {
      return @{ Exe=$Exe; Args=@($ExtraArgs); Version=$version }
    }
    if ($version) { Write-Host ("Omitiendo Python {0} ({1}); se requiere 3.11-3.13." -f $version, $Exe) -ForegroundColor Yellow }
  } catch {
    # Un comando puede existir como alias de Microsoft Store sin instalar Python.
  }
  return $null
}

function Get-UsablePython {
  # Primero intentar el Python Launcher, que permite coexistir con Python 3.15.
  foreach ($minor in @('3.13', '3.12', '3.11')) {
    $found = Test-PythonCandidate -Exe 'py' -ExtraArgs @("-$minor")
    if ($found) { return $found }
  }

  # Algunas instalaciones no incluyen "py" ni agregan python.exe al PATH.
  $roots = @(
    (Join-Path $env:LOCALAPPDATA 'Programs\Python'),
    $env:ProgramFiles,
    ${env:ProgramFiles(x86)}
  ) | Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Container) }
  foreach ($minor in @('313', '312', '311')) {
    foreach ($root in $roots) {
      foreach ($candidateExe in @(
        (Join-Path $root ("Python{0}\python.exe" -f $minor)),
        (Join-Path $root ("Python\Python{0}\python.exe" -f $minor))
      )) {
        $found = Test-PythonCandidate -Exe $candidateExe -ExtraArgs @()
        if ($found) { return $found }
      }
    }
  }
  foreach ($command in @('python', 'python3')) {
    $found = Test-PythonCandidate -Exe $command -ExtraArgs @()
    if ($found) { return $found }
  }

  Write-Host ''
  Write-Host 'No se encontro Python 3.11, 3.12 o 3.13.' -ForegroundColor Yellow
  Write-Host 'Comprueba las versiones instaladas:' -ForegroundColor Cyan
  Write-Host '  py -0p'
  Write-Host '  python --version'
  Write-Host 'Instala Python 3.12 sin desinstalar Python 3.15:' -ForegroundColor Cyan
  Write-Host '  winget install -e --id Python.Python.3.12'
  Write-Host 'Cierra y vuelve a abrir la consola; despues ejecuta INICIAR_APEX.cmd.'
  Write-Host 'Alternativa: descarga ApexDescargaDesktop.exe del workflow de GitHub; no requiere Python instalado.'
  throw 'No hay una version de Python compatible disponible para el codigo fuente.'
}

$venv = Join-Path $project '.venv'
$pythonExe = Join-Path $venv 'Scripts\python.exe'
if (Test-Path -LiteralPath $pythonExe -PathType Leaf) {
  $currentVenv = Test-PythonCandidate -Exe $pythonExe -ExtraArgs @()
  if (-not $currentVenv) {
    throw 'La carpeta .venv existe pero usa una version incompatible o no funciona. Renombrala como .venv_antiguo y vuelve a ejecutar INICIAR_APEX.cmd.'
  }
}

if (-not (Test-Path -LiteralPath $pythonExe -PathType Leaf)) {
  $py = Get-UsablePython
  Write-Host ("Preparando entorno aislado con Python {0}..." -f $py.Version) -ForegroundColor Cyan
  $pythonCommand = $py.Exe
  $pythonArgs = @($py.Args)
  & $pythonCommand @pythonArgs -m venv $venv
  if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear el entorno Python.' }
}

Write-Host 'Instalando dependencias y comprobando actualizaciones...' -ForegroundColor Cyan
& $pythonExe -m pip install --disable-pip-version-check -r (Join-Path $project 'requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron instalar dependencias. Revisa la conexion.' }
Write-Host 'Abriendo Apex Descarga Desktop...' -ForegroundColor Green
& $pythonExe (Join-Path $project 'main.py')
if ($LASTEXITCODE -ne 0) { throw 'Apex se cerro con un error.' }
