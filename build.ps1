$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
$pyInstallerExe = Join-Path $projectRoot ".venv\Scripts\pyinstaller.exe"
$specFile = Join-Path $projectRoot "Forpus.spec"
$buildDir = Join-Path $projectRoot "build"
$distDir = Join-Path $projectRoot "dist"
$bundleDir = Join-Path $distDir "Forpus"
$zipFile = Join-Path $projectRoot "Forpus-win.zip"

if (-not (Test-Path $pythonExe)) {
    throw "Missing virtualenv Python at $pythonExe"
}

Push-Location $projectRoot
try {
    & $pythonExe -m pip install pyinstaller

    if (Test-Path $buildDir) {
        Remove-Item $buildDir -Recurse -Force
    }

    if (Test-Path $distDir) {
        Remove-Item $distDir -Recurse -Force
    }

    if (Test-Path $specFile) {
        Remove-Item $specFile -Force
    }

    if (Test-Path $zipFile) {
        Remove-Item $zipFile -Force
    }

    & $pyInstallerExe --clean --noconsole --name Forpus --onedir main.py

    if (-not (Test-Path $bundleDir)) {
        throw "Build did not produce $bundleDir"
    }

    Compress-Archive -Path (Join-Path $bundleDir "*") -DestinationPath $zipFile -Force

    Write-Host ""
    Write-Host "Build complete:"
    Write-Host "  App folder: $bundleDir"
    Write-Host "  Zip file:   $zipFile"
}
finally {
    Pop-Location
}
