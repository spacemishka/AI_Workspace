<#
.SYNOPSIS
    AI Workspace - Common development commands
.DESCRIPTION
    Run with: .\scripts\dev.ps1 <command>
    Commands: start, stop, restart, logs, status, models, migrate, clean
#>

param([string]$Command = "help")

function Write-Header { param([string]$Text)
    Write-Host "`n  $Text" -ForegroundColor Cyan
}

switch ($Command) {

    "start" {
        Write-Header "Starting infrastructure..."
        docker compose up -d postgres redis qdrant ollama langfuse prometheus grafana
        Write-Host "  Done. Run 'dev.ps1 status' to check." -ForegroundColor Green
    }

    "start-all" {
        Write-Header "Starting full stack..."
        docker compose up -d
    }

    "stop" {
        Write-Header "Stopping all services..."
        docker compose down
    }

    "restart" {
        param([string]$Service)
        if ($args[0]) {
            Write-Header "Restarting $($args[0])..."
            docker compose restart $args[0]
        } else {
            Write-Header "Restarting all services..."
            docker compose restart
        }
    }

    "logs" {
        $svc = if ($args[0]) { $args[0] } else { "backend" }
        Write-Header "Tailing logs: $svc"
        docker compose logs -f $svc
    }

    "status" {
        Write-Header "Service status"
        docker compose ps
    }

    "models" {
        Write-Header "Ollama - loaded models and VRAM"
        docker exec ai-ollama ollama ps
        Write-Header "Ollama - all downloaded models"
        docker exec ai-ollama ollama list
    }

    "pull" {
        $model = $args[0]
        if (-not $model) { Write-Host "Usage: dev.ps1 pull <model-name>" -ForegroundColor Red; exit 1 }
        Write-Header "Pulling Ollama model: $model"
        docker exec ai-ollama ollama pull $model
    }

    "migrate" {
        Write-Header "Running database migrations..."
        docker compose run --rm backend alembic upgrade head
        Write-Host "  Migrations complete." -ForegroundColor Green
    }

    "clean" {
        Write-Host "`n  WARNING: This will remove all Docker volumes (data loss!)" -ForegroundColor Red
        Write-Host "  Continue? [y/N]: " -ForegroundColor Red -NoNewline
        if ((Read-Host) -match "^[Yy]$") {
            docker compose down -v
            Write-Host "  All volumes removed." -ForegroundColor Yellow
        }
    }

    "urls" {
        Write-Host @"

  Service URLs:
    Backend API   ->  http://localhost:8000
    API Docs      ->  http://localhost:8000/docs
    Frontend      ->  http://localhost:5173
    Langfuse      ->  http://localhost:3001
    Grafana       ->  http://localhost:3002
    Prometheus    ->  http://localhost:9090
    Qdrant        ->  http://localhost:6333/dashboard
    Ollama        ->  http://localhost:11434
    llama.cpp     ->  http://localhost:8080
    LM Studio     ->  http://localhost:1234

"@ -ForegroundColor Cyan
    }

    default {
        Write-Host @"

  AI Workspace - Dev Commands
  Usage: .\scripts\dev.ps1 <command>

  Commands:
    start        Start infrastructure services (postgres, redis, qdrant, ollama, etc.)
    start-all    Start everything including backend and frontend
    stop         Stop all services
    logs [svc]   Tail logs for a service (default: backend)
    status       Show all service status
    models       Show Ollama loaded models and VRAM usage
    pull <name>  Pull an Ollama model
    migrate      Run Alembic database migrations
    clean        Remove all Docker volumes (DESTRUCTIVE)
    urls         Print all service URLs

"@ -ForegroundColor White
    }
}

