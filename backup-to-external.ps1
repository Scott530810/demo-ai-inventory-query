# 自動備份腳本 - 備份到外接硬碟
# 使用方式: .\backup-to-external.ps1

param(
    [string]$BackupDrive = "E:",  # 修改為您的外接硬碟代號
    [string]$BackupFolder = "Backup\ambulance-inventory"
)

$SourcePath = $PSScriptRoot
$Timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$BackupPath = Join-Path $BackupDrive $BackupFolder
$BackupName = "backup_$Timestamp"
$FullBackupPath = Join-Path $BackupPath $BackupName

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  救護車庫存查詢系統 - 備份工具" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# 檢查外接硬碟是否存在
if (-not (Test-Path $BackupDrive)) {
    Write-Host "❌ 錯誤: 找不到外接硬碟 $BackupDrive" -ForegroundColor Red
    Write-Host "   請確認外接硬碟已連接，或修改腳本中的 BackupDrive 參數" -ForegroundColor Yellow
    exit 1
}

# 檢查 Git 狀態
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
Write-Host "📁 創建備份目錄..." -ForegroundColor Yellow
if (-not (Test-Path $BackupPath)) {
    New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null
}

# 執行備份
Write-Host "💾 開始備份..." -ForegroundColor Yellow
Write-Host "   來源: $SourcePath" -ForegroundColor Gray
Write-Host "   目標: $FullBackupPath" -ForegroundColor Gray

try {
    Copy-Item -Path $SourcePath -Destination $FullBackupPath -Recurse -Force
    Write-Host "✅ 備份成功！" -ForegroundColor Green
    Write-Host ""

    # 顯示備份資訊
    $backupSize = (Get-ChildItem $FullBackupPath -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "📊 備份資訊:" -ForegroundColor Cyan
    Write-Host "   備份位置: $FullBackupPath" -ForegroundColor Gray
    Write-Host "   備份大小: $([math]::Round($backupSize, 2)) MB" -ForegroundColor Gray
    Write-Host "   備份時間: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray

    # 清理舊備份（保留最近 5 個）
    Write-Host ""
    Write-Host "🗑️  清理舊備份..." -ForegroundColor Yellow
    $allBackups = Get-ChildItem $BackupPath | Sort-Object Name -Descending
    if ($allBackups.Count -gt 5) {
        $oldBackups = $allBackups | Select-Object -Skip 5
        foreach ($old in $oldBackups) {
            Write-Host "   刪除: $($old.Name)" -ForegroundColor Gray
            Remove-Item $old.FullName -Recurse -Force
        }
        Write-Host "✅ 已清理 $($oldBackups.Count) 個舊備份，保留最近 5 個" -ForegroundColor Green
    } else {
        Write-Host "   目前共有 $($allBackups.Count) 個備份" -ForegroundColor Gray
    }

    # 列出所有備份
    Write-Host ""
    Write-Host "📋 現有備份列表:" -ForegroundColor Cyan
    Get-ChildItem $BackupPath | Sort-Object Name -Descending | Select-Object -First 5 | ForEach-Object {
        $size = (Get-ChildItem $_.FullName -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
        Write-Host "   $($_.Name) - $([math]::Round($size, 2)) MB" -ForegroundColor Gray
    }

} catch {
    Write-Host "❌ 備份失敗: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  備份完成！" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
