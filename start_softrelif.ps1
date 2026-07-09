# ================================
# Launcher de SoftRelif + MariaDB
# ================================

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Cambia estos datos por los de tu servidor Termux
$SshUser = "u0_a753"
$SshHost = "100.104.42.92"
$SshPort = "8022"

# Túnel: Windows 3307 -> Android/Termux 3306
$LocalDbPort = "3307"
$RemoteDbHost = "127.0.0.1"
$RemoteDbPort = "3306"

$Forward = "${LocalDbPort}:${RemoteDbHost}:${RemoteDbPort}"

# Variables para la app
$env:SOFTRELIF_DB_HOST = "127.0.0.1"
$env:SOFTRELIF_DB_PORT = $LocalDbPort
$env:SOFTRELIF_DB_USER = "softrelif_app"
$env:SOFTRELIF_DB_PASSWORD = "SoftRelif_1234!"
$env:SOFTRELIF_DB_NAME = "softrelif_db"

Write-Host "Iniciando túnel SSH hacia MariaDB..."
Write-Host "127.0.0.1:${LocalDbPort} -> ${SshHost}:${RemoteDbPort}"

$tunnel = Start-Process `
    -FilePath "ssh" `
    -ArgumentList "-N", "-L", $Forward, "$SshUser@$SshHost", "-p", $SshPort `
    -PassThru

Start-Sleep -Seconds 3

try {
    Write-Host "Iniciando SoftRelif..."

    $PythonExe = Join-Path $ProjectDir ".venv\Scripts\python.exe"
    $MainPy = Join-Path $ProjectDir "main.py"

    if (Test-Path $PythonExe) {
        & $PythonExe $MainPy
    }
    else {
        python $MainPy
    }
}
finally {
    Write-Host "Cerrando túnel SSH..."

    if ($tunnel -and !$tunnel.HasExited) {
        Stop-Process -Id $tunnel.Id -Force
    }
}