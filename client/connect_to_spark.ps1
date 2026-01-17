# Windows 11 Client - Connect to DGX SPARK Server
# 從 Windows 11 筆電連線到 SPARK 服務器

param(
    [string]$SparkIP = "SPARK_IP_HERE",  # 替換為實際的 SPARK IP
    [int]$Port = 8000,
    [string]$Question = ""
)

$ErrorActionPreference = "Stop"

# Colors
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

Write-ColorOutput "🚀 Ambulance Inventory Query Client - Windows 11" "Cyan"
Write-ColorOutput "Connecting to SPARK Server: $SparkIP:$Port" "Yellow"
Write-ColorOutput "=" * 60 "Gray"

# Check if SPARK IP is configured
if ($SparkIP -eq "SPARK_IP_HERE") {
    Write-ColorOutput "❌ Error: Please configure SPARK_IP first!" "Red"
    Write-ColorOutput "Edit this script and replace SPARK_IP_HERE with actual IP" "Yellow"
    exit 1
}

# API endpoints
$BaseURL = "http://${SparkIP}:${Port}"
$HealthURL = "${BaseURL}/health"
$QueryURL = "${BaseURL}/query"
$DocsURL = "${BaseURL}/docs"

# Function: Test connection
function Test-SparkConnection {
    Write-ColorOutput "`n🔍 Testing connection to SPARK server..." "Yellow"

    try {
        $response = Invoke-RestMethod -Uri $HealthURL -Method Get -TimeoutSec 5

        if ($response.status -eq "healthy") {
            Write-ColorOutput "✅ Connection successful!" "Green"
            Write-ColorOutput "   Database: $(if($response.database){'✅'}else{'❌'})" "White"
            Write-ColorOutput "   Ollama: $(if($response.ollama){'✅'}else{'❌'})" "White"
            Write-ColorOutput "   Model: $($response.model)" "White"
            Write-ColorOutput "   Version: $($response.version)" "White"
            return $true
        } else {
            Write-ColorOutput "⚠️  Server is unhealthy" "Yellow"
            return $false
        }
    }
    catch {
        Write-ColorOutput "❌ Failed to connect to SPARK server" "Red"
        Write-ColorOutput "   Error: $($_.Exception.Message)" "Red"
        Write-ColorOutput "`n💡 Troubleshooting:" "Yellow"
        Write-ColorOutput "   1. Check if SPARK IP is correct: $SparkIP" "White"
        Write-ColorOutput "   2. Ensure API server is running on SPARK" "White"
        Write-ColorOutput "   3. Check firewall allows port $Port" "White"
        Write-ColorOutput "   4. Test with: Test-NetConnection -ComputerName $SparkIP -Port $Port" "White"
        return $false
    }
}

# Function: Send query
function Send-Query {
    param([string]$QuestionText)

    Write-ColorOutput "`n💭 Question: $QuestionText" "Cyan"
    Write-ColorOutput "Sending to SPARK server..." "Yellow"

    try {
        $body = @{
            question = $QuestionText
        } | ConvertTo-Json

        $headers = @{
            "Content-Type" = "application/json"
        }

        $response = Invoke-RestMethod -Uri $QueryURL -Method Post -Body $body -Headers $headers -TimeoutSec 60

        if ($response.success) {
            Write-ColorOutput "`n✅ Query Successful!" "Green"
            Write-ColorOutput "=" * 60 "Gray"
            Write-ColorOutput "`n📊 SQL Query:" "Yellow"
            Write-ColorOutput $response.sql "White"
            Write-ColorOutput "`n💡 Answer:" "Yellow"
            Write-ColorOutput $response.answer "Green"
            Write-ColorOutput "=" * 60 "Gray"
        } else {
            Write-ColorOutput "`n❌ Query Failed" "Red"
            Write-ColorOutput "Error: $($response.error)" "Red"
        }
    }
    catch {
        Write-ColorOutput "`n❌ Failed to send query" "Red"
        Write-ColorOutput "Error: $($_.Exception.Message)" "Red"
    }
}

# Function: Interactive mode
function Start-InteractiveMode {
    Write-ColorOutput "`n🎮 Starting Interactive Mode" "Cyan"
    Write-ColorOutput "Type 'exit' or 'quit' to exit, 'help' for demo queries" "Yellow"
    Write-ColorOutput "=" * 60 "Gray"

    while ($true) {
        Write-Host "`n💭 Your question: " -ForegroundColor Cyan -NoNewline
        $userQuestion = Read-Host

        if ($userQuestion -in @("exit", "quit", "q")) {
            Write-ColorOutput "`n👋 Goodbye!" "Green"
            break
        }

        if ($userQuestion -in @("help", "h", "?")) {
            Show-DemoQueries
            continue
        }

        if ([string]::IsNullOrWhiteSpace($userQuestion)) {
            Write-ColorOutput "⚠️  Please enter a question" "Yellow"
            continue
        }

        Send-Query -QuestionText $userQuestion
    }
}

# Function: Show demo queries
function Show-DemoQueries {
    Write-ColorOutput "`n📚 Demo Queries:" "Yellow"
    Write-ColorOutput "1. 請問AED除顫器還有哪幾款有庫存？" "White"
    Write-ColorOutput "2. 請問輪椅有哪些品牌？" "White"
    Write-ColorOutput "3. 請問救護車擔架有哪些型號？" "White"
    Write-ColorOutput "4. 請問有哪些設備的庫存數量少於10件？" "White"
    Write-ColorOutput "5. 請問設備表中有哪些類別？" "White"
}

# Function: Open API documentation
function Open-APIDocs {
    Write-ColorOutput "`n📖 Opening API Documentation in browser..." "Yellow"
    Start-Process $DocsURL
}

# Main execution
Write-ColorOutput "`n🔧 Configuration:" "Yellow"
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
    Write-ColorOutput "`n📋 Choose an option:" "Cyan"
    Write-ColorOutput "1. Interactive mode (recommended)" "White"
    Write-ColorOutput "2. Show demo queries" "White"
    Write-ColorOutput "3. Open API documentation" "White"
    Write-ColorOutput "4. Exit" "White"

    $choice = Read-Host "`nYour choice (1-4)"

    switch ($choice) {
        "1" { Start-InteractiveMode }
        "2" { Show-DemoQueries }
        "3" { Open-APIDocs }
        "4" { Write-ColorOutput "👋 Goodbye!" "Green" }
        default { Write-ColorOutput "❌ Invalid choice" "Red" }
    }
}

Write-ColorOutput "`n✨ Script completed" "Green"
