# Windows 11 Client - Connect to DGX SPARK Server
# 從 Windows 11 筆電連線到 SPARK 服務器

param(
    [string]$SparkIP = "SPARK_IP_HERE",  # 替換為實際的 SPARK IP
    [int]$Port = 8000,
    [string]$Question = ""
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Colors
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

Write-ColorOutput "[Client] Ambulance Inventory Query - Windows 11" "Cyan"
Write-ColorOutput "Connecting to SPARK Server: ${SparkIP}:${Port}" "Yellow"
Write-ColorOutput ("=" * 60) "Gray"

# Check if SPARK IP is configured
if ($SparkIP -eq "SPARK_IP_HERE") {
    Write-ColorOutput "[Error] Please configure SPARK_IP first!" "Red"
    Write-ColorOutput "Usage: .\connect_to_spark.ps1 -SparkIP 192.168.x.x" "Yellow"
    exit 1
}

# API endpoints
$BaseURL = "http://${SparkIP}:${Port}"
$HealthURL = "${BaseURL}/health"
$QueryURL = "${BaseURL}/query"
$ModelsURL = "${BaseURL}/api/models"
$DocsURL = "${BaseURL}/docs"

# Function: Test connection
function Test-SparkConnection {
    Write-ColorOutput "`n[Check] Testing connection to SPARK server..." "Yellow"

    try {
        $response = Invoke-RestMethod -Uri $HealthURL -Method Get -TimeoutSec 10

        if ($response.status -eq "healthy") {
            Write-ColorOutput "[OK] Connection successful!" "Green"
            Write-ColorOutput "   Database: $(if($response.database){'OK'}else{'FAIL'})" "White"
            Write-ColorOutput "   Ollama: $(if($response.ollama){'OK'}else{'FAIL'})" "White"
            Write-ColorOutput "   Model: $($response.model)" "White"
            Write-ColorOutput "   Version: $($response.version)" "White"
            return $true
        } else {
            Write-ColorOutput "[Warning] Server is unhealthy" "Yellow"
            return $false
        }
    }
    catch {
        Write-ColorOutput "[Error] Failed to connect to SPARK server" "Red"
        Write-ColorOutput "   Error: $($_.Exception.Message)" "Red"
        Write-ColorOutput "`n[Troubleshooting]:" "Yellow"
        Write-ColorOutput "   1. Check if SPARK IP is correct: $SparkIP" "White"
        Write-ColorOutput "   2. Ensure API server is running on SPARK" "White"
        Write-ColorOutput "   3. Check firewall allows port $Port" "White"
        Write-ColorOutput "   4. Test: Test-NetConnection -ComputerName $SparkIP -Port $Port" "White"
        return $false
    }
}

# Function: Send query
function Send-Query {
    param([string]$QuestionText)

    Write-ColorOutput "`n[Question] $QuestionText" "Cyan"
    Write-ColorOutput "Sending to SPARK server..." "Yellow"

    try {
        $body = @{
            question = $QuestionText
        } | ConvertTo-Json -Depth 10

        $headers = @{
            "Content-Type" = "application/json; charset=utf-8"
        }

        $response = Invoke-RestMethod -Uri $QueryURL -Method Post -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) -Headers $headers -TimeoutSec 120

        if ($response.success) {
            Write-ColorOutput "`n[OK] Query Successful!" "Green"
            Write-ColorOutput ("=" * 60) "Gray"
            Write-ColorOutput "`n[SQL Query]:" "Yellow"
            Write-ColorOutput $response.sql "White"
            Write-ColorOutput "`n[Answer]:" "Yellow"
            Write-ColorOutput $response.answer "Green"
            Write-ColorOutput ("=" * 60) "Gray"
        } else {
            Write-ColorOutput "`n[Error] Query Failed" "Red"
            Write-ColorOutput "Error: $($response.error)" "Red"
        }
    }
    catch {
        Write-ColorOutput "`n[Error] Failed to send query" "Red"
        Write-ColorOutput "Error: $($_.Exception.Message)" "Red"
    }
}

# Function: Show available models
function Show-Models {
    Write-ColorOutput "`n[Models] Getting available models..." "Yellow"

    try {
        $response = Invoke-RestMethod -Uri $ModelsURL -Method Get -TimeoutSec 10
        Write-ColorOutput "Current model: $($response.current)" "Green"
        Write-ColorOutput "Available models:" "White"
        foreach ($model in $response.models) {
            $marker = if ($model -eq $response.current) { " <-- current" } else { "" }
            Write-ColorOutput "  - ${model}${marker}" "White"
        }
    }
    catch {
        Write-ColorOutput "[Error] Failed to get models: $($_.Exception.Message)" "Red"
    }
}

# Function: Interactive mode
function Start-InteractiveMode {
    Write-ColorOutput "`n[Interactive Mode] Started" "Cyan"
    Write-ColorOutput "Commands: 'exit' to quit, 'models' to see available models" "Yellow"
    Write-ColorOutput ("=" * 60) "Gray"

    while ($true) {
        Write-Host "`nYour question: " -ForegroundColor Cyan -NoNewline
        $userQuestion = Read-Host

        if ($userQuestion -in @("exit", "quit", "q")) {
            Write-ColorOutput "`nGoodbye!" "Green"
            break
        }

        if ($userQuestion -in @("models", "model")) {
            Show-Models
            continue
        }

        if ($userQuestion -in @("help", "h", "?")) {
            Show-DemoQueries
            continue
        }

        if ([string]::IsNullOrWhiteSpace($userQuestion)) {
            Write-ColorOutput "[Warning] Please enter a question" "Yellow"
            continue
        }

        Send-Query -QuestionText $userQuestion
    }
}

# Function: Show demo queries
function Show-DemoQueries {
    Write-ColorOutput "`n[Demo Queries]:" "Yellow"
    Write-ColorOutput "1. AED除顫器有庫存嗎" "White"
    Write-ColorOutput "2. 輪椅有哪些品牌" "White"
    Write-ColorOutput "3. 擔架有哪些型號" "White"
    Write-ColorOutput "4. 哪些設備庫存少於10件" "White"
    Write-ColorOutput "5. 設備有哪些類別" "White"
}

# Function: Open API documentation
function Open-APIDocs {
    Write-ColorOutput "`n[Browser] Opening API Documentation..." "Yellow"
    Start-Process $DocsURL
}

# Main execution
Write-ColorOutput "`n[Configuration]:" "Yellow"
Write-ColorOutput "   SPARK IP: $SparkIP" "White"
Write-ColorOutput "   Port: $Port" "White"
Write-ColorOutput "   Health Check: $HealthURL" "White"
Write-ColorOutput "   API Docs: $DocsURL" "White"

# Test connection first
if (-not (Test-SparkConnection)) {
    exit 1
}

# If question provided via parameter, use it
if ($Question) {
    Send-Query -QuestionText $Question
} else {
    # Show menu
    Write-ColorOutput "`n[Menu] Choose an option:" "Cyan"
    Write-ColorOutput "1. Interactive mode (recommended)" "White"
    Write-ColorOutput "2. Show demo queries" "White"
    Write-ColorOutput "3. Show available models" "White"
    Write-ColorOutput "4. Open API documentation" "White"
    Write-ColorOutput "5. Exit" "White"

    $choice = Read-Host "`nYour choice (1-5)"

    switch ($choice) {
        "1" { Start-InteractiveMode }
        "2" { Show-DemoQueries }
        "3" { Show-Models }
        "4" { Open-APIDocs }
        "5" { Write-ColorOutput "Goodbye!" "Green" }
        default { Write-ColorOutput "[Error] Invalid choice" "Red" }
    }
}

Write-ColorOutput "`n[Done] Script completed" "Green"
