$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
Set-Location $project

function Get-UsablePython {
  $candidates = @(
    @{Exe='py'; Args=@('-3.13')},
    @{Exe='py'; Args=@('-3.12')},
    @{Exe='py'; Args=@('-3.11')},
    @{Exe='python'; Args=@()}
  )
  foreach ($candidate in $candidates) {
    $exe = $candidate.Exe
    if (-not (Get-Command $exe -ErrorAction SilentlyContinue)) { continue }
    try {
      $argsForPython = @($candidate.Args)
      $v = & $exe @argsForPython -c 'import sys; print(sys.version_info.major, sys.version_info.minor)' 2>$null
      if ($LASTEXITCODE -ne 0) { continue }
      $numbers = "$v".Trim().Split(' ')
      if ($numbers[0] -eq '3' -and [int]$numbers[1] -ge 11 -and [int]$numbers[1] -le 13) {
        $choice = @($exe) + $argsForPython
        return ,$choice
      }
    } catch {}
  }
  throw 'Instala Python 3.12 o 3.13 desde python.org y activa Python Launcher (py). No utilizar Python 3.15 experimental.'
}

$venv = Join-Path $project '.venv'
$pythonExe = Join-Path $venv 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonExe)) {
  $py = Get-UsablePython
  Write-Host 'Preparando entorno aislado Python...' -ForegroundColor Cyan
  $pythonCommand = $py[0]
  $pythonArgs = @($py | Select-Object -Skip 1)
  & $pythonCommand @pythonArgs -m venv $venv
  if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear el entorno Python.' }
}
Write-Host 'Instalando dependencias y comprobando actualizaciones...' -ForegroundColor Cyan
& $pythonExe -m pip install --disable-pip-version-check -r (Join-Path $project 'requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron instalar dependencias. Revisa la conexión.' }
Write-Host 'Abriendo Apex Descarga Desktop...' -ForegroundColor Green
& $pythonExe (Join-Path $project 'main.py')
if ($LASTEXITCODE -ne 0) { throw 'Apex se cerró con un error.' }
