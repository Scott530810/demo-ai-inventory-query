# Windows 11 Client - Connect to DGX SPARK Server

param(
    [string]$SparkIP = "SPARK_IP_HERE",
    [int]$Port = 8000,
    [string]$Question = ""
)

$ErrorActionPreference = "Stop"

# Fix UTF-8 encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
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
    Write-ColorOutput "`n[Check] Testing connection..." "Yellow"
    try {
        $response = Invoke-RestMethod -Uri $HealthURL -Method Get -TimeoutSec 10
        if ($response.status -eq "healthy") {
            Write-ColorOutput "[OK] Connection successful!" "Green"
        } else {
            Write-ColorOutput "[Warning] Server unhealthy - Ollama may not be running" "Yellow"
        }
        Write-ColorOutput "   Database: $(if($response.database){'OK'}else{'FAIL'})" "White"
        Write-ColorOutput "   Ollama: $(if($response.ollama){'OK'}else{'FAIL'})" "White"
        Write-ColorOutput "   Model: $($response.model)" "White"
        return $true
    }
    catch {
        Write-ColorOutput "[Error] Failed to connect: $($_.Exception.Message)" "Red"
        return $false
    }
}

function Send-Query {
    param([string]$QuestionText)
    Write-ColorOutput "`n[Question] $QuestionText" "Cyan"
    Write-ColorOutput "Sending to SPARK server..." "Yellow"

    try {
        $body = @{ question = $QuestionText } | ConvertTo-Json -Depth 10
        $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($body)

        $webRequest = [System.Net.HttpWebRequest]::Create($QueryURL)
        $webRequest.Method = "POST"
        $webRequest.ContentType = "application/json; charset=utf-8"
        $webRequest.Timeout = 120000

        $requestStream = $webRequest.GetRequestStream()
        $requestStream.Write($bodyBytes, 0, $bodyBytes.Length)
        $requestStream.Close()

        $webResponse = $webRequest.GetResponse()
        $responseStream = $webResponse.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($responseStream, [System.Text.Encoding]::UTF8)
        $responseText = $reader.ReadToEnd()
        $reader.Close()
        $responseStream.Close()
        $webResponse.Close()

        $response = $responseText | ConvertFrom-Json

        if ($response.success) {
            Write-ColorOutput "`n[OK] Query Successful!" "Green"
            Write-ColorOutput ("=" * 60) "Gray"
            Write-ColorOutput "`n[SQL]:" "Yellow"
            Write-ColorOutput $response.sql "White"
            Write-ColorOutput "`n[Answer]:" "Yellow"
            Write-ColorOutput $response.answer "Green"
            Write-ColorOutput ("=" * 60) "Gray"
        } else {
            Write-ColorOutput "`n[Error] Query Failed: $($response.error)" "Red"
        }
    }
    catch {
        Write-ColorOutput "`n[Error] $($_.Exception.Message)" "Red"
    }
}

function Show-Models {
    Write-ColorOutput "`n[Models] Getting available models..." "Yellow"
    try {
        $response = Invoke-RestMethod -Uri $ModelsURL -Method Get -TimeoutSec 10
        Write-ColorOutput "Current: $($response.current)" "Green"
        Write-ColorOutput "Available:" "White"
        foreach ($model in $response.models) {
            $marker = if ($model -eq $response.current) { " <-- current" } else { "" }
            Write-ColorOutput "  - ${model}${marker}" "White"
        }
    }
    catch {
        Write-ColorOutput "[Error] $($_.Exception.Message)" "Red"
    }
}

function Start-InteractiveMode {
    Write-ColorOutput "`n[Interactive Mode] Started" "Cyan"
    Write-ColorOutput "Commands: exit, models, help" "Yellow"
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
    Write-ColorOutput "4. Equipment with stock < 10?" "White"
    Write-ColorOutput "5. What categories?" "White"
}

function Invoke-DemoQueries {
    Write-ColorOutput "`n[Demo Mode] Select:" "Cyan"
    Write-ColorOutput "  1. AED has stock?" "White"
    Write-ColorOutput "  2. What wheelchair brands?" "White"
    Write-ColorOutput "  3. What stretcher models?" "White"
    Write-ColorOutput "  4. Equipment with stock < 10?" "White"
    Write-ColorOutput "  5. What categories?" "White"
    Write-ColorOutput "  6. Run all" "Yellow"
    Write-ColorOutput "  0. Cancel" "Gray"

    $choice = Read-Host "`nChoice (0-6)"

    $queries = @(
        "AED has stock?",
        "What wheelchair brands?",
        "What stretcher models?",
        "Equipment with stock less than 10?",
        "What categories?"
    )

    if ($choice -eq "0" -or [string]::IsNullOrWhiteSpace($choice)) {
        return
    }
    if ($choice -eq "6") {
        foreach ($q in $queries) {
            Send-Query -QuestionText $q
        }
    }
    elseif ($choice -match "^[1-5]$") {
        Send-Query -QuestionText $queries[[int]$choice - 1]
    }
}

function Open-APIDocs {
    Write-ColorOutput "`n[Browser] Opening API docs..." "Yellow"
    Start-Process $DocsURL
}

# Main
Write-ColorOutput "`n[Config]:" "Yellow"
Write-ColorOutput "   SPARK IP: $SparkIP" "White"
Write-ColorOutput "   Port: $Port" "White"

$connected = Test-SparkConnection
if (-not $connected) { exit 1 }

if ($Question) {
    Send-Query -QuestionText $Question
}
else {
    Write-ColorOutput "`n[Menu]:" "Cyan"
    Write-ColorOutput "1. Interactive mode" "White"
    Write-ColorOutput "2. Demo queries" "White"
    Write-ColorOutput "3. Show models" "White"
    Write-ColorOutput "4. API docs" "White"
    Write-ColorOutput "5. Exit" "White"

    $choice = Read-Host "`nChoice (1-5)"

    switch ($choice) {
        "1" { Start-InteractiveMode }
        "2" { Invoke-DemoQueries }
        "3" { Show-Models }
        "4" { Open-APIDocs }
        "5" { Write-ColorOutput "Goodbye!" "Green" }
        default { Write-ColorOutput "[Error] Invalid" "Red" }
    }
}

Write-ColorOutput "`n[Done]" "Green"
