# encoding: utf-8
# Windows 11 Client - Connect to DGX SPARK Server (Chinese Version)

param(
    [string]$SparkIP = "SPARK_IP_HERE",
    [int]$Port = 8000,
    [string]$Question = ""
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

# Chinese demo queries stored as array
$script:DemoQueries = @(
    "AED除顫器有庫存嗎",
    "輪椅有哪些品牌",
    "擔架有哪些型號",
    "庫存少於10件的設備",
    "設備有哪些類別"
)

function Write-Color([string]$Msg, [string]$Color = "White") {
    Write-Host $Msg -ForegroundColor $Color
}

Write-Color "[Client] Ambulance Inventory Query" "Cyan"
Write-Color "Server: ${SparkIP}:${Port}" "Yellow"
Write-Color ("=" * 50) "Gray"

if ($SparkIP -eq "SPARK_IP_HERE") {
    Write-Color "[Error] Set SPARK_IP first" "Red"
    exit 1
}

$BaseURL = "http://${SparkIP}:${Port}"

function Test-Connection {
    Write-Color "`n[Check] Testing..." "Yellow"
    try {
        $r = Invoke-RestMethod -Uri "$BaseURL/health" -Method Get -TimeoutSec 10
        Write-Color "  DB: $(if($r.database){'OK'}else{'FAIL'})" "White"
        Write-Color "  Ollama: $(if($r.ollama){'OK'}else{'FAIL'})" "White"
        Write-Color "  Model: $($r.model)" "White"
        return $true
    } catch {
        Write-Color "[Error] $($_.Exception.Message)" "Red"
        return $false
    }
}

function Send-Query([string]$Q) {
    Write-Color "`n[Q] $Q" "Cyan"
    try {
        $body = @{question=$Q} | ConvertTo-Json
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
        $req = [System.Net.HttpWebRequest]::Create("$BaseURL/query")
        $req.Method = "POST"
        $req.ContentType = "application/json; charset=utf-8"
        $req.Timeout = 120000
        $s = $req.GetRequestStream()
        $s.Write($bytes,0,$bytes.Length)
        $s.Close()
        $res = $req.GetResponse()
        $rd = New-Object System.IO.StreamReader($res.GetResponseStream(),[System.Text.Encoding]::UTF8)
        $txt = $rd.ReadToEnd()
        $rd.Close()
        $res.Close()
        $r = $txt | ConvertFrom-Json
        if ($r.success) {
            Write-Color "`n[SQL]" "Yellow"
            Write-Color $r.sql "White"
            Write-Color "`n[Answer]" "Yellow"
            Write-Color $r.answer "Green"
        } else {
            Write-Color "[Error] $($r.error)" "Red"
        }
    } catch {
        Write-Color "[Error] $($_.Exception.Message)" "Red"
    }
}

function Show-Models {
    try {
        $r = Invoke-RestMethod -Uri "$BaseURL/api/models" -TimeoutSec 10
        Write-Color "Current: $($r.current)" "Green"
        $r.models | ForEach-Object { Write-Color "  - $_" "White" }
    } catch {
        Write-Color "[Error] $($_.Exception.Message)" "Red"
    }
}

function Start-Interactive {
    Write-Color "`n[Interactive] exit=quit, models, help" "Cyan"
    while ($true) {
        Write-Host "`nQuestion: " -NoNewline -ForegroundColor Cyan
        $q = Read-Host
        if ($q -in @("exit","quit","q")) { Write-Color "Bye!" "Green"; break }
        if ($q -eq "models") { Show-Models; continue }
        if ($q -eq "help") { Show-Demo; continue }
        if ($q) { Send-Query $q }
    }
}

function Show-Demo {
    Write-Color "`n[Demo Queries]:" "Yellow"
    for ($i=0; $i -lt $script:DemoQueries.Count; $i++) {
        Write-Color "  $($i+1). $($script:DemoQueries[$i])" "White"
    }
}

function Run-Demo {
    Show-Demo
    Write-Color "  6. Run all  0. Cancel" "Yellow"
    $c = Read-Host "`nChoice (0-6)"
    if ($c -eq "6") {
        foreach ($q in $script:DemoQueries) { Send-Query $q }
    } elseif ($c -match "^[1-5]$") {
        Send-Query $script:DemoQueries[[int]$c - 1]
    }
}

# Main
$ok = Test-Connection
if (-not $ok) { exit 1 }

if ($Question) {
    Send-Query $Question
} else {
    Write-Color "`n[Menu]:" "Cyan"
    Write-Color "1. Interactive" "White"
    Write-Color "2. Demo queries" "White"
    Write-Color "3. Show models" "White"
    Write-Color "4. Exit" "White"
    $c = Read-Host "`nChoice (1-4)"
    switch ($c) {
        "1" { Start-Interactive }
        "2" { Run-Demo }
        "3" { Show-Models }
        "4" { Write-Color "Bye!" "Green" }
    }
}
Write-Color "`n[Done]" "Green"
