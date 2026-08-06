$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$py = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path $py)) {
    Write-Error "No se encontro .venv\Scripts\python.exe. Crea el entorno e instala requirements.txt."
}

& $py -m pip install pyinstaller --quiet

& $py -m PyInstaller --noconfirm --clean "SoftRelief.spec"

if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller fallo."
}

if (Test-Path "dist\.env") {
    Remove-Item "dist\.env" -Force
}

Write-Output "Build listo: dist\SoftRelief.exe (one-file, con .env incluido dentro del exe)"
