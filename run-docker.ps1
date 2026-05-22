# ============================================================
# InsightFlow AI — Docker Run Script
# Usage: .\run-docker.ps1
#        .\run-docker.ps1 -Detach        (run in background)
#        .\run-docker.ps1 -Down          (stop all containers)
#        .\run-docker.ps1 -Logs service  (tail logs for a service)
# ============================================================

param(
    [switch]$Detach,
    [switch]$Down,
    [string]$Logs = ""
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

function Write-Step($msg) {
    Write-Host "`n>>> $msg" -ForegroundColor Cyan
}

function Check-Docker {
    try {
        docker info | Out-Null
    } catch {
        Write-Host "ERROR: Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
        exit 1
    }
}

# ── Stop containers ─────────────────────────────────────────
if ($Down) {
    Write-Step "Stopping all InsightFlow containers..."
    Set-Location $ProjectRoot
    docker compose down
    Write-Host "Done." -ForegroundColor Green
    exit 0
}

# ── Tail logs ───────────────────────────────────────────────
if ($Logs -ne "") {
    Set-Location $ProjectRoot
    docker compose logs -f $Logs
    exit 0
}

# ── Build & Run ─────────────────────────────────────────────
Check-Docker

Write-Step "Building and starting InsightFlow AI..."
Write-Host "  Services: MongoDB, Redis, Zookeeper, Kafka" -ForegroundColor Gray
Write-Host "  Services: auth, dataset, analytics, notification, api-gateway" -ForegroundColor Gray
Write-Host "  Services: ai-service (Python/FastAPI)" -ForegroundColor Gray
Write-Host "  Services: frontend (React/Vite → nginx)" -ForegroundColor Gray
Write-Host ""
Write-Host "  NOTE: First build downloads Maven/Node dependencies." -ForegroundColor Yellow
Write-Host "        This may take 5-10 minutes on first run." -ForegroundColor Yellow

Set-Location $ProjectRoot

if ($Detach) {
    docker compose up --build -d
    Write-Host ""
    Write-Host "All containers started in background." -ForegroundColor Green
    Write-Host ""
    Write-Host "  Frontend:     http://localhost:5173" -ForegroundColor White
    Write-Host "  API Gateway:  http://localhost:4000/api" -ForegroundColor White
    Write-Host "  AI Service:   http://localhost:8000/docs" -ForegroundColor White
    Write-Host "  Auth Service: http://localhost:8081" -ForegroundColor White
    Write-Host ""
    Write-Host "  Tip: Run '.\run-docker.ps1 -Logs <service>' to tail logs." -ForegroundColor Gray
    Write-Host "  Tip: Run '.\run-docker.ps1 -Down' to stop everything." -ForegroundColor Gray
} else {
    docker compose up --build
}
