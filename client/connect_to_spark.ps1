# Windows 11 Client - Connect to DGX SPARK Server

param(
    [string]$SparkIP = "SPARK_IP_HERE",
    [int]$Port = 8000,
    [string]$Question = ""
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

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

if ($SparkIP -eq "SPARK_IP_HERE") {
    Write-ColorOutput "[Error] Please configure SPARK_IP first!" "Red"
    Write-ColorOutput "Usage: .\connect_to_spark.ps1 -SparkIP 192.168.x.x" "Yellow"
    exit 1
}

$BaseURL = "http://${SparkIP}:${Port}"
$HealthURL = "${BaseURL}/health"
$QueryURL = "${BaseURL}/query"
$ModelsURL = "${BaseURL}/api/models"
$DocsURL = "${BaseURL}/docs"

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
            Write-ColorOutput "[Warning] Server is unhealthy - Ollama may not be running" "Yellow"
            Write-ColorOutput "   Database: $(if($response.database){'OK'}else{'FAIL'})" "White"
            Write-ColorOutput "   Ollama: $(if($response.ollama){'OK'}else{'FAIL'})" "White"
            Write-ColorOutput "   Model: $($response.model)" "White"
            return $false
        }
    }
    catch {
        Write-ColorOutput "[Error] Failed to connect to SPARK server" "Red"
        Write-ColorOutput "   Error: $($_.Exception.Message)" "Red"
        return $false
    }
}

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

function Start-InteractiveMode {
    Write-ColorOutput "`n[Interactive Mode] Started" "Cyan"
    Write-ColorOutput "Commands: exit to quit, models to see available models, help for examples" "Yellow"
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

function Show-DemoQueries {
    Write-ColorOutput "`n[Demo Queries]:" "Yellow"
    Write-ColorOutput "1. AED has stock?" "White"
    Write-ColorOutput "2. What wheelchair brands?" "White"
    Write-ColorOutput "3. What stretcher models?" "White"
    Write-ColorOutput "4. Equipment with stock less than 10?" "White"
    Write-ColorOutput "5. What equipment categories?" "White"
}

function Run-DemoQueries {
    $demoQueries = @(
        "AED has stock?",
        "What wheelchair brands?",
        "What stretcher models?",
        "Equipment with stock less than 10?",
        "What equipment categories?"
    )

    Write-ColorOutput "`n[Demo Mode] Select a query to run:" "Cyan"
    for ($i = 0; $i -lt $demoQueries.Count; $i++) {
        Write-ColorOutput "  $($i + 1). $($demoQueries[$i])" "White"
    }
    Write-ColorOutput "  6. Run all demos" "Yellow"
    Write-ColorOutput "  0. Cancel" "Gray"

    $choice = Read-Host "`nYour choice (0-6)"

    if ($choice -eq "0" -or [string]::IsNullOrWhiteSpace($choice)) {
        Write-ColorOutput "Cancelled" "Gray"
        return
    }

    if ($choice -eq "6") {
        Write-ColorOutput "`n[Running all demo queries...]" "Cyan"
        foreach ($query in $demoQueries) {
            Send-Query -QuestionText $query
            Write-ColorOutput "`n" "White"
        }
    } elseif ($choice -match "^[1-5]$") {
        $index = [int]$choice - 1
        Send-Query -QuestionText $demoQueries[$index]
    } else {
        Write-ColorOutput "[Error] Invalid choice" "Red"
    }
}

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

$connected = Test-SparkConnection

if ($Question) {
    if ($connected) {
        Send-Query -QuestionText $Question
    }
} else {
    Write-ColorOutput "`n[Menu] Choose an option:" "Cyan"
    Write-ColorOutput "1. Interactive mode" "White"
    Write-ColorOutput "2. Run demo queries" "White"
    Write-ColorOutput "3. Show available models" "White"
    Write-ColorOutput "4. Open API documentation" "White"
    Write-ColorOutput "5. Exit" "White"

    $choice = Read-Host "`nYour choice (1-5)"

    switch ($choice) {
        "1" { Start-InteractiveMode }
        "2" { Run-DemoQueries }
        "3" { Show-Models }
        "4" { Open-APIDocs }
        "5" { Write-ColorOutput "Goodbye!" "Green" }
        default { Write-ColorOutput "[Error] Invalid choice" "Red" }
    }
}

Write-ColorOutput "`n[Done] Script completed" "Green"
