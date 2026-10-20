$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
Write-Host '=========================================' -ForegroundColor Cyan
Write-Host '  APEX DESCARGA ANDROID - COMPILAR APK' -ForegroundColor Cyan
Write-Host '=========================================' -ForegroundColor Cyan
Write-Host 'Este script usa Gradle 8.9, JDK 17/21 y Android SDK 35.'
Write-Host 'No solicita permisos de administrador.'
Write-Host ''

function Read-JavaMajor([string]$exe) {
    try {
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $exe
        $psi.Arguments = '-version'
        $psi.UseShellExecute = $false
        $psi.CreateNoWindow = $true
        $psi.RedirectStandardError = $true
        $psi.RedirectStandardOutput = $true
        $p = New-Object System.Diagnostics.Process
        $p.StartInfo = $psi
        if (-not $p.Start()) { return 0 }
        $err = $p.StandardError.ReadToEnd()
        $stdout = $p.StandardOutput.ReadToEnd()
        if (-not $p.WaitForExit(10000)) { try { $p.Kill() } catch {}; return 0 }
        $text = $err + "`n" + $stdout
        if ($text -match '(?i)\bversion\s+"?((?:1\.)?\d+)') {
            $raw = $Matches[1]
            if ($raw -like '1.*') { return [int]($raw.Split('.')[1]) }
            return [int]($raw.Split('.')[0])
        }
        return 0
    } catch { return 0 }
}

# Prefer bundled Android Studio JDK; then JAVA_HOME; then installed JDKs; then PATH.
$candidates = New-Object 'System.Collections.Generic.List[string]'
$studioRoots = @(
    (Join-Path $env:ProgramFiles 'Android\Android Studio\jbr'),
    (Join-Path $env:ProgramFiles 'Android\Android Studio\jre'),
    (Join-Path $env:LOCALAPPDATA 'Programs\Android Studio\jbr')
)
foreach ($item in $studioRoots) { if ($item) { [void]$candidates.Add($item) } }
if ($env:JAVA_HOME) { [void]$candidates.Add($env:JAVA_HOME) }
$roots = @(
    (Join-Path $env:ProgramFiles 'Eclipse Adoptium'),
    (Join-Path $env:ProgramFiles 'Microsoft'),
    (Join-Path $env:ProgramFiles 'Java')
)
foreach ($root in $roots) {
    if (-not (Test-Path -LiteralPath $root -PathType Container)) { continue }
    foreach ($dir in @(Get-ChildItem -LiteralPath $root -Directory -ErrorAction SilentlyContinue)) {
        if ($dir.Name -match '(?i)jdk|temurin') { [void]$candidates.Add($dir.FullName) }
    }
}
$pathJava = Get-Command 'java.exe' -ErrorAction SilentlyContinue
if ($pathJava) { [void]$candidates.Add((Split-Path -Parent (Split-Path -Parent $pathJava.Source))) }

$chosen = $null
$major = 0
$seen = @{}
foreach ($candidateJdkHome in $candidates) {
    if ([string]::IsNullOrWhiteSpace($candidateJdkHome)) { continue }
    $candidateJdkHome = $candidateJdkHome.Trim().Trim('"')
    if ($seen.ContainsKey($candidateJdkHome.ToLowerInvariant())) { continue }
    $seen[$candidateJdkHome.ToLowerInvariant()] = $true
    $javaExe = Join-Path $candidateJdkHome 'bin\java.exe'
    $javacExe = Join-Path $candidateJdkHome 'bin\javac.exe'
    if (-not (Test-Path -LiteralPath $javaExe -PathType Leaf)) { continue }
    $found = Read-JavaMajor $javaExe
    Write-Host ('Java detectado: ' + $candidateJdkHome + ' (version ' + $found + ')')
    # Gradle 8.9 supports execution with Java 17-22. Need JDK, not merely JRE.
    if ($found -ge 17 -and $found -le 22 -and (Test-Path -LiteralPath $javacExe -PathType Leaf)) {
        $chosen = $candidateJdkHome
        $major = $found
        break
    }
}
if (-not $chosen) {
    Write-Host ''
    Write-Host 'No se encontro un JDK 17-22 compatible.' -ForegroundColor Yellow
    Write-Host 'Instala JDK 17 con: winget install --id EclipseAdoptium.Temurin.17.JDK -e' -ForegroundColor Cyan
    Write-Host 'Cierra la consola, abre otra y ejecuta GENERAR_APK_WINDOWS.cmd de nuevo.'
    throw 'No se puede compilar con Java 8. Apex requiere JDK 17 o 21.'
}
$env:JAVA_HOME = $chosen
$env:PATH = (Join-Path $chosen 'bin') + ';' + $env:PATH
Write-Host ('JDK seleccionado: ' + $chosen + ' (Java ' + $major + ')') -ForegroundColor Green

$sdk = @($env:ANDROID_HOME, $env:ANDROID_SDK_ROOT,
    (Join-Path $env:LOCALAPPDATA 'Android\Sdk')) |
    Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Container) } |
    Select-Object -First 1
if (-not $sdk) { throw 'No se encontro Android SDK. Instala Android Studio y SDK Platform 35.' }
$platform = Join-Path $sdk 'platforms\android-35\android.jar'
if (-not (Test-Path -LiteralPath $platform -PathType Leaf)) {
    throw 'Falta SDK Platform 35. Instalala desde Android Studio > SDK Manager.'
}
$env:ANDROID_HOME = $sdk

$toolRoot = Join-Path $env:LOCALAPPDATA 'ApexDescargaBuild'
$gradleExe = Join-Path $toolRoot 'gradle-8.9\bin\gradle.bat'
if (-not (Test-Path -LiteralPath $gradleExe -PathType Leaf)) {
    New-Item -ItemType Directory -Force -Path $toolRoot | Out-Null
    $zip = Join-Path $toolRoot 'gradle-8.9-bin.zip'
    $hashFile = Join-Path $toolRoot 'gradle-8.9-bin.zip.sha256'
    Write-Host 'Descargando Gradle 8.9 desde distribucion oficial...' -ForegroundColor Cyan
    Invoke-WebRequest -Uri 'https://services.gradle.org/distributions/gradle-8.9-bin.zip' -OutFile $zip
    Invoke-WebRequest -Uri 'https://services.gradle.org/distributions/gradle-8.9-bin.zip.sha256' -OutFile $hashFile
    $expectedHash = ((Get-Content -LiteralPath $hashFile -Raw).Trim() -split '\s+')[0].ToUpperInvariant()
    $actualHash = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToUpperInvariant()
    if ($actualHash -cne $expectedHash) { throw 'Checksum incorrecto de Gradle. Se detuvo por seguridad.' }
    Write-Host 'Checksum SHA256 verificado; descomprimiendo Gradle.' -ForegroundColor Green
    Expand-Archive -LiteralPath $zip -DestinationPath $toolRoot -Force
}
if (-not (Test-Path -LiteralPath $gradleExe -PathType Leaf)) { throw 'Gradle no quedo instalado correctamente.' }

Push-Location $project
try {
    Write-Host 'Compilando APK. La primera vez puede tardar varios minutos.' -ForegroundColor Cyan
    & $gradleExe --no-daemon :app:assembleDebug
    if ($LASTEXITCODE -ne 0) { throw 'Gradle no pudo compilar. Revisa el error completo.' }
} finally {
    Pop-Location
}
$apk = Join-Path $project 'app\build\outputs\apk\debug\app-debug.apk'
if (-not (Test-Path -LiteralPath $apk -PathType Leaf)) { throw 'Gradle termino pero no se encontro la APK.' }
$dest = Join-Path $project 'APEX_DESCARGA_ANDROID_1.0.1_DEBUG.apk'
Copy-Item -LiteralPath $apk -Destination $dest -Force
Write-Host 'APK GENERADA CON EXITO:' -ForegroundColor Green
Write-Host $dest -ForegroundColor Cyan
Write-Host 'Es una APK de desarrollo. No la publiques como version final sin probar y firmar.'
