$ErrorActionPreference = "Stop"

function Write-Info($msg) {
    Write-Host "[INFO] $msg" -ForegroundColor Cyan
}

function Write-WarnMsg($msg) {
    Write-Host "[WARN] $msg" -ForegroundColor Yellow
}

function Write-Ok($msg) {
    Write-Host "[OK] $msg" -ForegroundColor Green
}

function Is-PortListening([int]$port) {
    $conn = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue
    return $null -ne $conn
}

function Start-BackgroundPowerShell($workingDir, $command, $logPath) {
    $script = "Set-Location '$workingDir'; $command *> '$logPath'"
    return Start-Process `
        -FilePath "powershell.exe" `
        -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $script) `
        -WindowStyle Hidden `
        -PassThru
}

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$logsDir = Join-Path $root "logs"
$frontendDir = Join-Path $root "frontend"
$aiDir = Join-Path $root "ai-service"
$aiVenvPython = Join-Path $aiDir ".venv\Scripts\python.exe"
$aiPythonCommand = "python"

if (Test-Path $aiVenvPython) {
    $venvReady = $false
    try {
        & $aiVenvPython -c "import flask, flask_cors, flask_sqlalchemy, requests, openai, sentence_transformers, psycopg2" *> $null
        $venvReady = ($LASTEXITCODE -eq 0)
    } catch {
        $venvReady = $false
    }

    if ($venvReady) {
        $aiPythonCommand = "& '$aiVenvPython'"
        Write-Info "Using ai-service virtualenv Python."
    } else {
        Write-WarnMsg "ai-service virtualenv is missing required packages. Falling back to system Python."
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Risk Control Platform - One Click Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Info "Checking Docker availability..."
docker ps *> $null
Write-Ok "Docker is available."

if (-not (Test-Path (Join-Path $root ".env"))) {
    Write-Info "Creating .env from .env.example ..."
    Copy-Item (Join-Path $root ".env.example") (Join-Path $root ".env")
}

if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
}

Write-Info "Starting infrastructure containers (docker-compose up -d)..."
Set-Location $root
docker-compose up -d
Write-Ok "Infrastructure started."

Write-Info "Waiting 8 seconds for DB/Redis warm-up..."
Start-Sleep -Seconds 8

$started = @{}

if (Is-PortListening 8080) {
    Write-WarnMsg "Backend port 8080 is already in use. Skipping backend start."
} else {
    Write-Info "Starting Java backend..."
    $backendLog = Join-Path $logsDir "backend.out.log"
    $p = Start-BackgroundPowerShell $root "mvn spring-boot:run" $backendLog
    $started["backend"] = $p.Id
    Write-Ok "Backend start command sent (PID=$($p.Id))."
}

if (Is-PortListening 5000) {
    Write-WarnMsg "AI service port 5000 is already in use. Skipping AI service start."
} else {
    Write-Info "Starting AI service..."
    $aiLog = Join-Path $logsDir "ai.out.log"
    $aiCommand = "$aiPythonCommand app.py"
    $p = Start-BackgroundPowerShell $aiDir $aiCommand $aiLog
    $started["ai-service"] = $p.Id
    Write-Ok "AI service start command sent (PID=$($p.Id))."
}

if ((Is-PortListening 3000) -or (Is-PortListening 5173)) {
    Write-WarnMsg "Frontend port 3000 or 5173 is already in use. Skipping frontend start."
} else {
    Write-Info "Starting frontend..."
    $frontendLog = Join-Path $logsDir "frontend.out.log"
    $p = Start-BackgroundPowerShell $frontendDir "npm run dev" $frontendLog
    $started["frontend"] = $p.Id
    Write-Ok "Frontend start command sent (PID=$($p.Id))."
}

Write-Host ""
Write-Host "--------------------" -ForegroundColor DarkCyan
Write-Host "Start Summary" -ForegroundColor DarkCyan
Write-Host "--------------------" -ForegroundColor DarkCyan
Write-Host "Backend  : http://localhost:8080"
Write-Host "AI       : http://localhost:5000/health"
Write-Host "Frontend : http://localhost:3000 (or Vite printed URL)"
Write-Host "Swagger  : http://localhost:8080/swagger-ui.html"
Write-Host ""
Write-Host "Logs:"
Write-Host "  $logsDir\backend.out.log"
Write-Host "  $logsDir\ai.out.log"
Write-Host "  $logsDir\frontend.out.log"
Write-Host ""

if ($started.Count -gt 0) {
    Write-Host "Spawned process IDs:"
    $started.GetEnumerator() | ForEach-Object { Write-Host ("  {0}: {1}" -f $_.Key, $_.Value) }
} else {
    Write-WarnMsg "No new service process was started by this script."
}

Write-Host ""
Write-Ok "Done."
