<#
.SYNOPSIS
    AI Workspace - Interactive Setup Wizard
.DESCRIPTION
    Automates the full first-time setup of the AI Workspace:
    - Prerequisite checks
    - Inference backend selection (Ollama / llama.cpp / LM Studio)
    - Secret generation
    - .env creation
    - Docker stack startup
    - Ollama model pulling
    - Service health verification
.NOTES
    Run from the repo root: .\setup.ps1
    Requires: Docker Desktop (WSL2), Python 3.12+, NVIDIA drivers
#>

[CmdletBinding()]
param(
    [switch]$SkipPrereqCheck,
    [switch]$InfraOnly   # Start infrastructure services only (no backend/frontend)
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ==============================================================================
# Helpers
# ==============================================================================

function Write-Banner {
    $banner = @"

  +------------------------------------------------------+
  |         AI Workspace - Setup Wizard                  |
  |         Privacy-first * Local-first * Modular        |
  +------------------------------------------------------+

"@
    Write-Host $banner -ForegroundColor Cyan
}

function Write-Step {
    param([string]$Number, [string]$Text)
    Write-Host "`n  [$Number] " -ForegroundColor Cyan -NoNewline
    Write-Host $Text -ForegroundColor White
}

function Write-Ok   { param([string]$Text); Write-Host "    [OK] $Text" -ForegroundColor Green }
function Write-Warn { param([string]$Text); Write-Host "    [!] $Text" -ForegroundColor Yellow }
function Write-Fail { param([string]$Text); Write-Host "    [X] $Text" -ForegroundColor Red }
function Write-Info { param([string]$Text); Write-Host "    -> $Text" -ForegroundColor Gray }

function Prompt-Value {
    param(
        [string]$Label,
        [string]$Default = "",
        [switch]$Secret,
        [switch]$Required
    )
    $display = if ($Default) { " [$Default]" } else { "" }
    Write-Host "    $Label$display : " -ForegroundColor White -NoNewline
    if ($Secret) {
        $secure = Read-Host -AsSecureString
        $value  = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
                      [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure))
    } else {
        $value = Read-Host
    }
    if (-not $value) { $value = $Default }
    if ($Required -and -not $value) {
        Write-Fail "$Label is required."
        exit 1
    }
    return $value
}

function Show-Menu {
    param([string]$Title, [string[]]$Options)
    Write-Host "`n    $Title" -ForegroundColor White
    for ($i = 0; $i -lt $Options.Count; $i++) {
        Write-Host "      [$($i+1)] $($Options[$i])" -ForegroundColor Cyan
    }
    do {
        Write-Host "    Choice: " -ForegroundColor White -NoNewline
        $input = Read-Host
        $idx   = [int]$input - 1
    } while ($idx -lt 0 -or $idx -ge $Options.Count)
    return $idx
}

function Generate-Secret {
    param([int]$Bytes = 32)
    return (python -c "import secrets; print(secrets.token_hex($Bytes))" 2>$null)
}

function Wait-Healthy {
    param([string]$Service, [int]$MaxSeconds = 60)
    Write-Info "Waiting for $Service to be healthy..."
    $elapsed = 0
    while ($elapsed -lt $MaxSeconds) {
        $status = docker inspect --format "{{.State.Health.Status}}" "ai-$Service" 2>$null
        if ($status -eq "healthy") {
            Write-Ok "$Service is healthy"
            return $true
        }
        Start-Sleep -Seconds 3
        $elapsed += 3
        Write-Host "." -NoNewline -ForegroundColor Gray
    }
    Write-Host ""
    Write-Warn "$Service did not become healthy within ${MaxSeconds}s - check: docker compose logs $Service"
    return $false
}

# ==============================================================================
# Script Entry
# ==============================================================================

Write-Banner

# Ensure we're in the repo root
if (-not (Test-Path "docker-compose.yml")) {
    Write-Fail "Run this script from the AI Workspace repo root (where docker-compose.yml lives)."
    exit 1
}

# ==============================================================================
# Step 1 - Prerequisites
# ==============================================================================

Write-Step "1" "Checking prerequisites..."

if (-not $SkipPrereqCheck) {

    # Docker
    try {
        $dockerVer = (docker --version) -replace "Docker version ", ""
        Write-Ok "Docker: $dockerVer"
    } catch {
        Write-Fail "Docker not found. Install Docker Desktop from https://www.docker.com/products/docker-desktop"
        exit 1
    }

    # Docker running
    $null = docker info --format '{{.ServerVersion}}' 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Ok "Docker daemon is running"
    } else {
        Write-Fail "Docker daemon is not running. Start Docker Desktop and try again."
        exit 1
    }

    # Python
    try {
        $pyVer = (python --version) -replace "Python ", ""
        $major, $minor = $pyVer.Split(".")[0..1] | ForEach-Object { [int]$_ }
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 12)) {
            Write-Warn "Python $pyVer found - 3.12+ recommended."
        } else {
            Write-Ok "Python: $pyVer"
        }
    } catch {
        Write-Warn "Python not found - secret generation will use fallback method."
    }

    # NVIDIA driver
    try {
        $smi = nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>$null
        if ($smi) {
            Write-Ok "NVIDIA GPU: $($smi.Trim())"
        }
    } catch {
        Write-Warn "nvidia-smi not found - GPU acceleration will not work. Install NVIDIA drivers."
    }

    # Git
    try {
        $gitVer = git --version
        Write-Ok "Git: $gitVer"
    } catch {
        Write-Warn "Git not found."
    }

} else {
    Write-Warn "Prerequisite check skipped."
}

# ==============================================================================
# Step 2 - Inference Backend Selection
# ==============================================================================

Write-Step "2" "Select local inference backend"
Write-Info "All backends expose an OpenAI-compatible API - switching later is a config change only."

$backendOptions = @(
    "Ollama          (recommended - Docker, multi-model, GPU-accelerated)",
    "llama.cpp       (Docker, single GGUF model, maximum control)",
    "LM Studio       (native Windows app - must be installed separately)"
)
$backendIdx = Show-Menu -Title "Inference Backend:" -Options $backendOptions

$backend = @("ollama", "llamacpp", "lmstudio")[$backendIdx]
Write-Ok "Selected: $($backendOptions[$backendIdx].Split(" ")[0])"

# ==============================================================================
# Step 3 - .env Configuration
# ==============================================================================

Write-Step "3" "Environment configuration"

$skipEnv = $false
if (Test-Path ".env") {
    Write-Warn ".env already exists."
    Write-Host "    Overwrite it? [y/N] : " -ForegroundColor Yellow -NoNewline
    $overwrite = Read-Host
    if ($overwrite -notmatch "^[Yy]$") {
        Write-Info "Keeping existing .env - skipping configuration."
        $skipEnv = $true
    }
}

if (-not $skipEnv) {

    Write-Info "Generating secrets..."
    $jwtSecret           = Generate-Secret 32
    $langfuseNextauth    = Generate-Secret 32
    $langfuseSalt        = Generate-Secret 16

    if (-not $jwtSecret) {
        # Fallback if Python unavailable
        $jwtSecret        = [System.Guid]::NewGuid().ToString("N") + [System.Guid]::NewGuid().ToString("N")
        $langfuseNextauth = [System.Guid]::NewGuid().ToString("N") + [System.Guid]::NewGuid().ToString("N")
        $langfuseSalt     = [System.Guid]::NewGuid().ToString("N")
        Write-Warn "Python unavailable - secrets generated with GUID fallback (less entropy)."
    } else {
        Write-Ok "Secrets generated"
    }

    Write-Host ""
    Write-Info "Enter values (press Enter to accept defaults shown in [brackets]):"
    Write-Host ""

    $postgresPassword   = Prompt-Value "PostgreSQL password" -Secret -Required
    $redisPassword      = Prompt-Value "Redis password"      -Secret -Required
    $grafanaPassword    = Prompt-Value "Grafana admin password" -Secret -Required
    $openrouterKey      = Prompt-Value "OpenRouter API key (sk-or-... or leave empty)" -Default ""
    $openrouterModel    = Prompt-Value "OpenRouter default model" -Default "anthropic/claude-3.5-sonnet"
    $postgresUser       = Prompt-Value "PostgreSQL username" -Default "aiworkspace"
    $postgresDb         = Prompt-Value "PostgreSQL database"  -Default "aiworkspace"
    $ollamaDefault      = Prompt-Value "Ollama default chat model" -Default "llama3.1:8b"
    $ollamaEmbed        = Prompt-Value "Ollama embedding model"    -Default "nomic-embed-text"

    # Backend-specific inference URL
    $inferenceUrl = switch ($backend) {
        "ollama"   { "http://ollama:11434/v1" }
        "llamacpp" { "http://llamacpp:8080/v1" }
        "lmstudio" { "http://host.docker.internal:1234/v1" }
    }

    # Write .env
    $envContent = @"
# =============================================================================
# AI Workspace - Environment Variables
# Generated by setup.ps1 on $(Get-Date -Format "yyyy-MM-dd HH:mm")
# NEVER commit this file to version control.
# =============================================================================

# -- Environment ---------------------------------------------------------------
ENVIRONMENT=development

# -- PostgreSQL ----------------------------------------------------------------
POSTGRES_USER=$postgresUser
POSTGRES_PASSWORD=$postgresPassword
POSTGRES_DB=$postgresDb

# -- Redis ---------------------------------------------------------------------
REDIS_PASSWORD=$redisPassword

# -- Qdrant --------------------------------------------------------------------
QDRANT_API_KEY=

# -- Local Inference - Backend: $backend ----------------------------------------
LOCAL_INFERENCE_BASE_URL=$inferenceUrl
OLLAMA_DEFAULT_MODEL=$ollamaDefault
OLLAMA_EMBED_MODEL=$ollamaEmbed

# -- Cloud Provider (OpenRouter - pluggable) -----------------------------------
CLOUD_PROVIDER=openrouter
OPENROUTER_API_KEY=$openrouterKey
OPENROUTER_DEFAULT_MODEL=$openrouterModel

# -- Security ------------------------------------------------------------------
JWT_SECRET_KEY=$jwtSecret
JWT_EXPIRE_MINUTES=60

# -- Langfuse (LLM Tracing) ----------------------------------------------------
LANGFUSE_NEXTAUTH_SECRET=$langfuseNextauth
LANGFUSE_SALT=$langfuseSalt
# Fill these in after first Langfuse login (Settings > API Keys)
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=

# -- Grafana -------------------------------------------------------------------
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=$grafanaPassword

# -- Frontend ------------------------------------------------------------------
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
"@

    Set-Content -Path ".env" -Value $envContent -Encoding UTF8
    Write-Ok ".env created"
}

# ==============================================================================
# Step 4 - LM Studio instructions (if selected)
# ==============================================================================

if ($backend -eq "lmstudio") {
    Write-Step "4" "LM Studio setup"
    Write-Host @"

    LM Studio runs natively on Windows - NOT in Docker.

    Before continuing:
      1. Download LM Studio from https://lmstudio.ai
      2. Install and launch it
      3. Go to the Search tab and download a model (recommended: Q4_K_M of any 7B model)
      4. Go to the Local Server tab
      5. Select your model, enable CORS, set GPU layers to max
      6. Click Start Server - confirm it shows "listening on port 1234"

"@ -ForegroundColor Yellow

    Write-Host "    Press Enter once LM Studio server is running... " -ForegroundColor Cyan -NoNewline
    Read-Host | Out-Null

    # Verify LM Studio is reachable
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:1234/v1/models" -TimeoutSec 5 -UseBasicParsing
        Write-Ok "LM Studio is reachable at http://localhost:1234"
    } catch {
        Write-Warn "LM Studio did not respond at localhost:1234 - ensure the server is started."
        Write-Host "    Continue anyway? [y/N] : " -ForegroundColor Yellow -NoNewline
        if ((Read-Host) -notmatch "^[Yy]$") { exit 1 }
    }
}

# ==============================================================================
# Step 5 - Start Docker Stack
# ==============================================================================

Write-Step "5" "Starting Docker infrastructure"

$coreServices = "postgres redis qdrant langfuse prometheus grafana"

$inferenceService = switch ($backend) {
    "ollama"   { "ollama" }
    "llamacpp" { "llamacpp" }
    "lmstudio" { "" }  # runs outside Docker
}

$servicesToStart = if ($inferenceService) { "$coreServices $inferenceService" } else { $coreServices }

Write-Info "Starting: $servicesToStart"
docker compose up -d $servicesToStart.Split(" ")

if ($LASTEXITCODE -ne 0) {
    Write-Fail "docker compose up failed. Check the output above."
    exit 1
}

Write-Ok "Services started"

# ==============================================================================
# Step 6 - Wait for Core Services
# ==============================================================================

Write-Step "6" "Waiting for services to become healthy"

Wait-Healthy "postgres" 60 | Out-Null
Wait-Healthy "redis"    30 | Out-Null
Wait-Healthy "qdrant"   30 | Out-Null

# ==============================================================================
# Step 7 - Pull Ollama Models
# ==============================================================================

if ($backend -eq "ollama") {
    Write-Step "7" "Pulling Ollama models"

    Write-Info "Waiting for Ollama to start..."
    Start-Sleep -Seconds 5

    # Read model names from .env
    $dotenv = Get-Content ".env" | Where-Object { $_ -match "^OLLAMA_" }
    $embedModel   = ($dotenv | Where-Object { $_ -match "^OLLAMA_EMBED_MODEL=" }) -replace "^OLLAMA_EMBED_MODEL=", ""
    $defaultModel = ($dotenv | Where-Object { $_ -match "^OLLAMA_DEFAULT_MODEL=" }) -replace "^OLLAMA_DEFAULT_MODEL=", ""

    $modelsToPull = @($embedModel, $defaultModel) | Where-Object { $_ }

    Write-Host ""
    Write-Info "Models to pull: $($modelsToPull -join ', ')"
    Write-Info "(You can add more later with: docker exec ai-ollama ollama pull [model])"
    Write-Host ""

    foreach ($model in $modelsToPull) {
        Write-Info "Pulling $model ..."
        docker exec ai-ollama ollama pull $model
        if ($LASTEXITCODE -eq 0) {
            Write-Ok "Pulled: $model"
        } else {
            Write-Warn "Failed to pull $model - you can retry with: docker exec ai-ollama ollama pull $model"
        }
    }

    Write-Host ""
    Write-Info "Additional recommended models (optional):"
    Write-Info "  docker exec ai-ollama ollama pull qwen2.5-coder:7b  # coding"
    Write-Info "  docker exec ai-ollama ollama pull mistral:7b         # fast reasoning"
}

# ==============================================================================
# Step 8 - Start App Services (unless --InfraOnly)
# ==============================================================================

if (-not $InfraOnly) {
    if ((Test-Path "backend/Dockerfile") -and (Test-Path "frontend/Dockerfile")) {
        Write-Step "8" "Starting application services"
        docker compose up -d backend worker frontend
        Write-Ok "Application services started"
    } else {
        Write-Step "8" "Application services"
        Write-Warn "backend/Dockerfile or frontend/Dockerfile not found - skipping."
        Write-Info "Run backend and frontend locally during development."
    }
}

# ==============================================================================
# Step 9 - Verification Summary
# ==============================================================================

Write-Step "9" "Verification"
Write-Host ""

# Parse credentials from .env for verification checks
$pgUser = "aiworkspace"
$pgDb = "aiworkspace"
$redisPass = ""
if (Test-Path ".env") {
    $envLines = Get-Content ".env"
    foreach ($line in $envLines) {
        if ($line -match "^POSTGRES_USER=(.*)$") { $pgUser = $matches[1].Trim() }
        if ($line -match "^POSTGRES_DB=(.*)$")   { $pgDb   = $matches[1].Trim() }
        if ($line -match "^REDIS_PASSWORD=(.*)$") { $redisPass = $matches[1].Trim() }
    }
}

$checks = @(
    @{ Name = "PostgreSQL"; Cmd = { docker exec ai-postgres pg_isready -U $pgUser -d $pgDb -q } },
    @{ Name = "Redis";      Cmd = { docker exec ai-redis redis-cli -a $redisPass ping 2>$null | Select-String "PONG" } },
    @{ Name = "Qdrant";     Cmd = { (Invoke-WebRequest "http://localhost:6333/healthz" -UseBasicParsing -TimeoutSec 5).StatusCode -eq 200 } },
    @{ Name = "Langfuse";   Cmd = { (Invoke-WebRequest "http://localhost:3001/api/public/health" -UseBasicParsing -TimeoutSec 5).StatusCode -eq 200 } },
    @{ Name = "Grafana";    Cmd = { (Invoke-WebRequest "http://localhost:3002/api/health" -UseBasicParsing -TimeoutSec 5).StatusCode -eq 200 } },
    @{ Name = "Prometheus"; Cmd = { (Invoke-WebRequest "http://localhost:9090/-/healthy" -UseBasicParsing -TimeoutSec 5).StatusCode -eq 200 } }
)

if ($backend -eq "ollama") {
    $checks += @{ Name = "Ollama"; Cmd = { (Invoke-WebRequest "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 5).StatusCode -eq 200 } }
}
if ($backend -eq "llamacpp") {
    $hasGguf = (Test-Path "models") -and (Get-ChildItem "models" -Filter "*.gguf" -ErrorAction SilentlyContinue).Count -gt 0
    if (-not $hasGguf) {
        Write-Warn "No .gguf model file found in ./models/ directory for llama.cpp."
        Write-Info "Download a .gguf model (e.g. Llama 3.1 8B Q4_K_M) into ./models/ and restart llamacpp."
    }
    $checks += @{ Name = "llama.cpp"; Cmd = { (Invoke-WebRequest "http://localhost:8080/health" -UseBasicParsing -TimeoutSec 5).StatusCode -eq 200 } }
}
if ($backend -eq "lmstudio") {
    $checks += @{ Name = "LM Studio"; Cmd = { (Invoke-WebRequest "http://localhost:1234/v1/models" -UseBasicParsing -TimeoutSec 5).StatusCode -eq 200 } }
}

foreach ($check in $checks) {
    try {
        $result = & $check.Cmd
        if ($result) { Write-Ok $check.Name } else { Write-Warn "$($check.Name) - unexpected response" }
    } catch {
        Write-Warn "$($check.Name) - not reachable yet (may still be starting)"
    }
}

# ==============================================================================
# Done - Print Service URLs
# ==============================================================================

Write-Host @"

  +------------------------------------------------------+
  |  Setup complete! Service URLs:                       |
  +------------------------------------------------------+
  |  Backend API   ->  http://localhost:8000              |
  |  API Docs      ->  http://localhost:8000/docs         |
  |  Frontend      ->  http://localhost:5173              |
  |  Langfuse      ->  http://localhost:3001              |
  |  Grafana       ->  http://localhost:3002              |
  |  Prometheus    ->  http://localhost:9090              |
  |  Qdrant        ->  http://localhost:6333/dashboard    |
  +------------------------------------------------------+

  Next step: Open Langfuse at http://localhost:3001
  Sign up, create an API key, then add it to .env:
    LANGFUSE_PUBLIC_KEY=pk-lf-...
    LANGFUSE_SECRET_KEY=sk-lf-...

  Useful commands:
    docker compose ps                    # service status
    docker compose logs -f [service]     # tail logs
    docker compose restart [service]     # restart a service
    docker compose down                  # stop everything

"@ -ForegroundColor Cyan
