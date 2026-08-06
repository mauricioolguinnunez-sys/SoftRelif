$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$py = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path $py)) {
    Write-Error "No se encontro .venv\Scripts\python.exe. Crea el entorno e instala requirements.txt."
}

& $py -m pip install pyinstaller --quiet

& $py -m PyInstaller --noconfirm --clean --onefile --windowed --name SoftRelief --add-data "assets;assets" --add-data "games;games" main.py

if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller fallo."
}

Copy-Item ".env" "dist\.env" -Force

Write-Output "Build listo: dist\SoftRelief.exe"