# ============================================
# 救護車庫存查詢系統 - Ollama 本地端版本 (PowerShell)
# ============================================

$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Ambulance Inventory Query System" -ForegroundColor Cyan
Write-Host "  Using Local Ollama LLM" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker
Write-Host "Checking Docker..." -ForegroundColor Yellow
$dockerRunning = docker info 2>$null
if (-not $dockerRunning) {
    Write-Host "X Docker is not running" -ForegroundColor Red
    Write-Host "Please start Docker Desktop first" -ForegroundColor Yellow
    exit 1
}
Write-Host "OK Docker is running" -ForegroundColor Green
Write-Host ""

# Check Ollama
Write-Host "Checking Ollama..." -ForegroundColor Yellow
try {
    $ollamaTest = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "OK Ollama is running" -ForegroundColor Green
    
    $models = ($ollamaTest.Content | ConvertFrom-Json).models
    $modelNames = $models | ForEach-Object { $_.name }
    
    if ($modelNames -contains "qwen3:30b") {
        Write-Host "OK Model qwen3:30b is ready" -ForegroundColor Green
    } else {
        Write-Host "! Model qwen3:30b not found" -ForegroundColor Yellow
        Write-Host "  Available models: $($modelNames -join ', ')" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Download qwen3:30b? (y/n)" -ForegroundColor Yellow
        $download = Read-Host
        if ($download -eq 'y') {
            Write-Host "Downloading model (about 19GB)..." -ForegroundColor Yellow
            ollama pull qwen3:30b
        } else {
            Write-Host "Please download manually: ollama pull qwen3:30b" -ForegroundColor Yellow
            exit 1
        }
    }
} catch {
    Write-Host "X Ollama is not running or cannot connect" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check:" -ForegroundColor Yellow
    Write-Host "  1. Ollama is installed" -ForegroundColor White
    Write-Host "  2. Ollama is running" -ForegroundColor White
    Write-Host "  3. Allow external access (set OLLAMA_HOST=0.0.0.0)" -ForegroundColor White
    Write-Host ""
    Write-Host "Setup (PowerShell Admin):" -ForegroundColor Yellow
    Write-Host '  [Environment]::SetEnvironmentVariable("OLLAMA_HOST", "0.0.0.0", "User")' -ForegroundColor Gray
    Write-Host "  Then restart Ollama" -ForegroundColor Gray
    exit 1
}
Write-Host ""

# Menu
Write-Host "Please select an option:" -ForegroundColor Yellow
Write-Host "  1. Start system (database + app)" -ForegroundColor White
Write-Host "  2. System check (test all components)" -ForegroundColor White
Write-Host "  3. Run demo queries" -ForegroundColor White
Write-Host "  4. Interactive mode" -ForegroundColor White
Write-Host "  5. Start pgAdmin (database management)" -ForegroundColor White
Write-Host "  6. View logs" -ForegroundColor White
Write-Host "  7. Stop system" -ForegroundColor White
Write-Host "  8. Clean all (including data)" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter option (1-8)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Starting system..." -ForegroundColor Yellow
        docker-compose -f docker-compose.ollama.yml up -d
        Write-Host ""
        Write-Host "OK System started!" -ForegroundColor Green
        Write-Host ""
        Write-Host "System Info:" -ForegroundColor Cyan
        Write-Host "  Database: localhost:5432" -ForegroundColor White
        Write-Host "  LLM: Local Ollama (qwen3:30b)" -ForegroundColor White
        Write-Host "  GPU: RTX 5070" -ForegroundColor White
        Write-Host ""
        Write-Host "Next step:" -ForegroundColor Yellow
        Write-Host "  .\run-ollama.ps1  (select 2 for system check)" -ForegroundColor White
    }
    "2" {
        Write-Host ""
        Write-Host "Running system check..." -ForegroundColor Yellow
        Write-Host ""
        docker-compose -f docker-compose.ollama.yml run --rm query-app-ollama python test_llm_query_ollama.py --check
    }
    "3" {
        Write-Host ""
        Write-Host "Running demo queries..." -ForegroundColor Yellow
        Write-Host "(Using local Ollama, completely free!)" -ForegroundColor Green
        Write-Host ""
        docker-compose -f docker-compose.ollama.yml run --rm query-app-ollama python test_llm_query_ollama.py --demo
    }
    "4" {
        Write-Host ""
        Write-Host "Entering interactive mode..." -ForegroundColor Yellow
        Write-Host "(Type 'exit' or 'quit' to leave)" -ForegroundColor Gray
        Write-Host ""
        docker-compose -f docker-compose.ollama.yml run --rm query-app-ollama python test_llm_query_ollama.py --interactive
    }
    "5" {
        Write-Host ""
        Write-Host "Starting pgAdmin..." -ForegroundColor Yellow
        docker-compose -f docker-compose.ollama.yml --profile tools up -d pgadmin
        Start-Sleep -Seconds 3
        Write-Host ""
        Write-Host "OK pgAdmin started!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Open in browser: http://localhost:5050" -ForegroundColor Cyan
        Write-Host "Login:" -ForegroundColor Yellow
        Write-Host "  Email: admin@example.com" -ForegroundColor White
        Write-Host "  Password: admin123" -ForegroundColor White
        
        Start-Process "http://localhost:5050"
    }
    "6" {
        Write-Host ""
        Write-Host "Viewing logs (Ctrl+C to exit):" -ForegroundColor Yellow
        Write-Host ""
        docker-compose -f docker-compose.ollama.yml logs -f
    }
    "7" {
        Write-Host ""
        Write-Host "Stopping system..." -ForegroundColor Yellow
        docker-compose -f docker-compose.ollama.yml down
        Write-Host ""
        Write-Host "OK System stopped" -ForegroundColor Green
        Write-Host "(Data preserved, Ollama model still available)" -ForegroundColor Gray
    }
    "8" {
        Write-Host ""
        Write-Host "WARNING: This will delete all data!" -ForegroundColor Red
        Write-Host "(Ollama model will not be deleted)" -ForegroundColor Gray
        $confirm = Read-Host "Continue? (yes/no)"
        if ($confirm -eq "yes") {
            Write-Host ""
            Write-Host "Cleaning system and data..." -ForegroundColor Yellow
            docker-compose -f docker-compose.ollama.yml down -v
            Write-Host ""
            Write-Host "OK System cleaned" -ForegroundColor Green
        } else {
            Write-Host "Cancelled" -ForegroundColor Yellow
        }
    }
    default {
        Write-Host ""
        Write-Host "X Invalid option" -ForegroundColor Red
    }
}

Write-Host ""
