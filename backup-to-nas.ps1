# 自動備份腳本 - 備份到 NAS
# 使用方式: .\backup-to-nas.ps1

param(
    [string]$NasPath = "\\192.168.1.100\backup",  # 修改為您的 NAS 路徑
    [string]$BackupFolder = "ambulance-inventory"
)

$SourcePath = $PSScriptRoot
$Timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$BackupPath = Join-Path $NasPath $BackupFolder
$BackupName = "backup_$Timestamp"
$FullBackupPath = Join-Path $BackupPath $BackupName

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  救護車庫存查詢系統 - NAS 備份工具" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# 檢查 NAS 連接
Write-Host "🔍 檢查 NAS 連接..." -ForegroundColor Yellow
if (-not (Test-Path $NasPath)) {
    Write-Host "❌ 錯誤: 無法連接到 NAS $NasPath" -ForegroundColor Red
    Write-Host "   請確認:" -ForegroundColor Yellow
    Write-Host "   1. NAS 已開機" -ForegroundColor Yellow
    Write-Host "   2. 網路連接正常" -ForegroundColor Yellow
    Write-Host "   3. NAS 路徑正確" -ForegroundColor Yellow
    Write-Host "   4. 有權限訪問該路徑" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ NAS 連接正常" -ForegroundColor Green

# 檢查 Git 狀態
Write-Host ""
Write-Host "🔍 檢查 Git 狀態..." -ForegroundColor Yellow
$gitStatus = git status --short
if ($gitStatus) {
    Write-Host "⚠️  警告: 有未提交的變更" -ForegroundColor Yellow
    Write-Host $gitStatus
    Write-Host ""
    $continue = Read-Host "是否繼續備份？(Y/N)"
    if ($continue -ne "Y" -and $continue -ne "y") {
        Write-Host "❌ 備份已取消" -ForegroundColor Red
        exit 0
    }
}

# 創建備份目錄
Write-Host ""
Write-Host "📁 創建備份目錄..." -ForegroundColor Yellow
if (-not (Test-Path $BackupPath)) {
    New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null
}

# 執行備份
Write-Host "💾 開始備份到 NAS..." -ForegroundColor Yellow
Write-Host "   來源: $SourcePath" -ForegroundColor Gray
Write-Host "   目標: $FullBackupPath" -ForegroundColor Gray

try {
    # 使用 Robocopy 進行高效備份
    $robocopyArgs = @(
        $SourcePath,
        $FullBackupPath,
        "/MIR",          # 鏡像模式
        "/R:3",          # 重試 3 次
        "/W:5",          # 等待 5 秒重試
        "/MT:8",         # 多線程（8 線程）
        "/XD", ".git",   # 排除 .git（太大）
        "/XF", "*.tmp",  # 排除臨時文件
        "/NFL",          # 不列出文件
        "/NDL",          # 不列出目錄
        "/NP"            # 不顯示進度
    )

    $result = Start-Process -FilePath "robocopy" -ArgumentList $robocopyArgs -Wait -NoNewWindow -PassThru

    # Robocopy 返回碼 0-7 都是成功
    if ($result.ExitCode -le 7) {
        Write-Host "✅ 備份成功！" -ForegroundColor Green
    } else {
        throw "Robocopy 失敗，返回碼: $($result.ExitCode)"
    }

    # 顯示備份資訊
    Write-Host ""
    $backupSize = (Get-ChildItem $FullBackupPath -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "📊 備份資訊:" -ForegroundColor Cyan
    Write-Host "   備份位置: $FullBackupPath" -ForegroundColor Gray
    Write-Host "   備份大小: $([math]::Round($backupSize, 2)) MB" -ForegroundColor Gray
    Write-Host "   備份時間: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray

    # 清理舊備份（保留最近 10 個）
    Write-Host ""
    Write-Host "🗑️  清理舊備份..." -ForegroundColor Yellow
    $allBackups = Get-ChildItem $BackupPath | Sort-Object Name -Descending
    if ($allBackups.Count -gt 10) {
        $oldBackups = $allBackups | Select-Object -Skip 10
        foreach ($old in $oldBackups) {
            Write-Host "   刪除: $($old.Name)" -ForegroundColor Gray
            Remove-Item $old.FullName -Recurse -Force
        }
        Write-Host "✅ 已清理 $($oldBackups.Count) 個舊備份，保留最近 10 個" -ForegroundColor Green
    } else {
        Write-Host "   目前共有 $($allBackups.Count) 個備份" -ForegroundColor Gray
    }

    # 列出所有備份
    Write-Host ""
    Write-Host "📋 現有備份列表:" -ForegroundColor Cyan
    Get-ChildItem $BackupPath | Sort-Object Name -Descending | Select-Object -First 5 | ForEach-Object {
        Write-Host "   $($_.Name)" -ForegroundColor Gray
    }

} catch {
    Write-Host "❌ 備份失敗: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  備份完成！" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
