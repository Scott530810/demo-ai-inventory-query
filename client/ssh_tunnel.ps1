# SSH Tunnel Setup for Windows 11
# 從 Windows 11 建立 SSH 隧道到 SPARK 服務器

param(
    [string]$SparkIP = "SPARK_IP_HERE",
    [string]$SparkUser = "your_username",
    [int]$LocalPort = 8000,
    [int]$RemotePort = 8000,
    [switch]$Background
)

$ErrorActionPreference = "Stop"

Write-Host "🔐 SSH Tunnel Setup - Windows 11 to SPARK" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

# Check configuration
if ($SparkIP -eq "SPARK_IP_HERE") {
    Write-Host "❌ Error: Please configure SPARK_IP!" -ForegroundColor Red
    Write-Host "Usage: .\ssh_tunnel.ps1 -SparkIP 192.168.1.100 -SparkUser scott" -ForegroundColor Yellow
    exit 1
}

if ($SparkUser -eq "your_username") {
    Write-Host "❌ Error: Please configure SparkUser!" -ForegroundColor Red
    Write-Host "Usage: .\ssh_tunnel.ps1 -SparkIP 192.168.1.100 -SparkUser scott" -ForegroundColor Yellow
    exit 1
}

# Check if ssh is available
if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
    Write-Host "❌ SSH not found!" -ForegroundColor Red
    Write-Host "Please install OpenSSH Client:" -ForegroundColor Yellow
    Write-Host "   Settings > Apps > Optional Features > Add a feature > OpenSSH Client" -ForegroundColor White
    exit 1
}

Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "   SPARK IP: $SparkIP" -ForegroundColor White
Write-Host "   SPARK User: $SparkUser" -ForegroundColor White
Write-Host "   Local Port: $LocalPort" -ForegroundColor White
Write-Host "   Remote Port: $RemotePort" -ForegroundColor White
Write-Host "   Tunnel: localhost:$LocalPort -> ${SparkIP}:$RemotePort" -ForegroundColor White

Write-Host "`n🔍 Testing SSH connection..." -ForegroundColor Yellow

# Test SSH connection
try {
    $testResult = ssh -o ConnectTimeout=5 -o BatchMode=yes "${SparkUser}@${SparkIP}" "echo 'Connection successful'" 2>&1

    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  SSH connection test failed" -ForegroundColor Yellow
        Write-Host "This might be normal if you haven't set up SSH keys yet" -ForegroundColor White
    } else {
        Write-Host "✅ SSH connection successful!" -ForegroundColor Green
    }
}
catch {
    Write-Host "⚠️  Could not test SSH connection" -ForegroundColor Yellow
}

Write-Host "`n🚇 Creating SSH tunnel..." -ForegroundColor Yellow

# Build SSH command
$sshCommand = "ssh -L ${LocalPort}:localhost:${RemotePort} ${SparkUser}@${SparkIP}"

if ($Background) {
    $sshCommand += " -N -f"
    Write-Host "Running in background mode..." -ForegroundColor White
} else {
    $sshCommand += " -N"
    Write-Host "Running in foreground mode (press Ctrl+C to stop)..." -ForegroundColor White
}

Write-Host "`nExecuting: $sshCommand" -ForegroundColor Gray
Write-Host "=" * 60 -ForegroundColor Gray

Write-Host "`n💡 After tunnel is established:" -ForegroundColor Yellow
Write-Host "   1. Open browser: http://localhost:$LocalPort/docs" -ForegroundColor White
Write-Host "   2. Or run: .\connect_to_spark.ps1 -SparkIP localhost" -ForegroundColor White
Write-Host "   3. Or use Python client: python spark_client.py --host localhost --interactive" -ForegroundColor White
Write-Host ""

# Execute SSH tunnel
try {
    Invoke-Expression $sshCommand
}
catch {
    Write-Host "`n❌ SSH tunnel failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`n💡 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "   1. Ensure SSH server is running on SPARK" -ForegroundColor White
    Write-Host "   2. Check firewall allows SSH (port 22)" -ForegroundColor White
    Write-Host "   3. Verify username and IP are correct" -ForegroundColor White
    Write-Host "   4. Set up SSH key authentication:" -ForegroundColor White
    Write-Host "      ssh-keygen -t ed25519" -ForegroundColor Gray
    Write-Host "      ssh-copy-id ${SparkUser}@${SparkIP}" -ForegroundColor Gray
    exit 1
}

Write-Host "`n✨ SSH tunnel closed" -ForegroundColor Green
