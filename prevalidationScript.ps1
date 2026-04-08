Param(
    [Parameter(Mandatory = $true)]
    [string]$PingUrl,
    [string]$RepoDir = "."
)

$ErrorActionPreference = "Stop"

function StepPass([string]$msg) { Write-Host "PASSED -- $msg" -ForegroundColor Green }
function StepFail([string]$msg) { Write-Host "FAILED -- $msg" -ForegroundColor Red }

$RepoDir = (Resolve-Path $RepoDir).Path
$PingUrl = $PingUrl.TrimEnd('/')

Write-Host "OpenEnv Submission Validator (PowerShell)" -ForegroundColor Cyan
Write-Host "Repo: $RepoDir"
Write-Host "Ping URL: $PingUrl"

# Step 1: Ping space reset
try {
    $resp = Invoke-WebRequest -Uri "$PingUrl/reset" -Method Post -ContentType "application/json" -Body "{}" -TimeoutSec 30
    if ($resp.StatusCode -eq 200) { StepPass "HF Space responds to /reset" } else { throw "HTTP $($resp.StatusCode)" }
}
catch {
    StepFail "HF Space /reset check failed: $_"
    exit 1
}

# Step 2: Docker build
try {
    docker version | Out-Null
}
catch {
    StepFail "Docker is not available. Start Docker Desktop first."
    exit 1
}

$dockerfilePath = Join-Path $RepoDir "Dockerfile"
if (-not (Test-Path $dockerfilePath)) {
    $dockerfilePath = Join-Path $RepoDir "server/Dockerfile"
}
if (-not (Test-Path $dockerfilePath)) {
    StepFail "No Dockerfile found in root or server/"
    exit 1
}

try {
    docker build -t seo-analyzer-env -f $dockerfilePath $RepoDir
    if ($LASTEXITCODE -ne 0) { throw "docker build exit code $LASTEXITCODE" }
    StepPass "Docker build succeeded"
}
catch {
    StepFail "Docker build failed: $_"
    exit 1
}

# Step 3: openenv validate
try {
    Push-Location $RepoDir
    openenv validate
    if ($LASTEXITCODE -ne 0) { throw "openenv validate exit code $LASTEXITCODE" }
    Pop-Location
    StepPass "openenv validate passed"
}
catch {
    Pop-Location
    StepFail "openenv validate failed: $_"
    exit 1
}

Write-Host "All checks passed. Submission is ready." -ForegroundColor Green
