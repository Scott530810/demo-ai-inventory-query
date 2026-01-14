# ============================================
# 救護車庫存查詢系統 - Ollama 本地端版本 (PowerShell)
# ============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  救護車庫存查詢系統 - Ollama 版本" -ForegroundColor Cyan
Write-Host "  使用本地 LLM (qwen2.5:32b)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 檢查 Docker 是否運行
Write-Host "檢查 Docker 狀態..." -ForegroundColor Yellow
$dockerRunning = docker info 2>$null
if (-not $dockerRunning) {
    Write-Host "❌ Docker 未運行，請先啟動 Docker Desktop" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker 正在運行" -ForegroundColor Green
Write-Host ""

# 檢查 Ollama 是否運行
Write-Host "檢查 Ollama 狀態..." -ForegroundColor Yellow
try {
    $ollamaTest = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Ollama 正在運行" -ForegroundColor Green
    
    # 檢查模型是否存在
    $models = ($ollamaTest.Content | ConvertFrom-Json).models
    $modelNames = $models | ForEach-Object { $_.name }
    
    if ($modelNames -contains "qwen2.5:32b") {
        Write-Host "✅ 模型 qwen2.5:32b 已就緒" -ForegroundColor Green
    } else {
        Write-Host "⚠️  模型 qwen2.5:32b 未找到" -ForegroundColor Yellow
        Write-Host "   可用模型: $($modelNames -join ', ')" -ForegroundColor Gray
        Write-Host ""
        Write-Host "是否要下載 qwen2.5:32b 模型？(y/n)" -ForegroundColor Yellow
        $download = Read-Host
        if ($download -eq 'y') {
            Write-Host "正在下載模型（約 19GB，需要一些時間）..." -ForegroundColor Yellow
            ollama pull qwen2.5:32b
        } else {
            Write-Host "請手動下載模型: ollama pull qwen2.5:32b" -ForegroundColor Yellow
            exit 1
        }
    }
} catch {
    Write-Host "❌ Ollama 未運行或無法連接" -ForegroundColor Red
    Write-Host ""
    Write-Host "請確認：" -ForegroundColor Yellow
    Write-Host "  1. Ollama 已安裝 (https://ollama.com/download)" -ForegroundColor White
    Write-Host "  2. Ollama 正在運行 (檢查系統托盤)" -ForegroundColor White
    Write-Host "  3. 允許外部訪問 (設定 OLLAMA_HOST=0.0.0.0)" -ForegroundColor White
    Write-Host ""
    Write-Host "設定方法 (PowerShell 管理員模式):" -ForegroundColor Yellow
    Write-Host '  [Environment]::SetEnvironmentVariable("OLLAMA_HOST", "0.0.0.0", "User")' -ForegroundColor Gray
    Write-Host "  然後重啟 Ollama" -ForegroundColor Gray
    exit 1
}
Write-Host ""

# 顯示功能選單
Write-Host "請選擇操作：" -ForegroundColor Yellow
Write-Host "  1. 啟動系統（包含資料庫、應用）" -ForegroundColor White
Write-Host "  2. 系統檢查（測試所有組件）" -ForegroundColor White
Write-Host "  3. 執行 Demo 查詢" -ForegroundColor White
Write-Host "  4. 進入互動模式" -ForegroundColor White
Write-Host "  5. 啟動 pgAdmin（資料庫管理界面）" -ForegroundColor White
Write-Host "  6. 查看日誌" -ForegroundColor White
Write-Host "  7. 停止系統" -ForegroundColor White
Write-Host "  8. 完全清除（包含資料）" -ForegroundColor White
Write-Host ""

$choice = Read-Host "請輸入選項 (1-8)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "正在啟動系統..." -ForegroundColor Yellow
        docker-compose -f docker-compose.ollama.yml up -d
        Write-Host ""
        Write-Host "✅ 系統啟動完成！" -ForegroundColor Green
        Write-Host ""
        Write-Host "系統資訊：" -ForegroundColor Cyan
        Write-Host "  📊 資料庫：localhost:5432" -ForegroundColor White
        Write-Host "  🤖 LLM：本地 Ollama (qwen2.5:32b)" -ForegroundColor White
        Write-Host "  💾 GPU：RTX 5070 (VRAM: 約 20GB+)" -ForegroundColor White
        Write-Host ""
        Write-Host "下一步：" -ForegroundColor Yellow
        Write-Host "  .\run-ollama.ps1  (選擇 2 進行系統檢查)" -ForegroundColor White
    }
    "2" {
        Write-Host ""
        Write-Host "執行系統檢查..." -ForegroundColor Yellow
        Write-Host ""
        docker-compose -f docker-compose.ollama.yml run --rm query-app-ollama python test_llm_query_ollama.py --check
    }
    "3" {
        Write-Host ""
        Write-Host "執行 Demo 查詢..." -ForegroundColor Yellow
        Write-Host "（使用本地 Ollama，完全免費！）" -ForegroundColor Green
        Write-Host ""
        docker-compose -f docker-compose.ollama.yml run --rm query-app-ollama python test_llm_query_ollama.py --demo
    }
    "4" {
        Write-Host ""
        Write-Host "進入互動模式..." -ForegroundColor Yellow
        Write-Host "（輸入 'exit' 或 'quit' 離開）" -ForegroundColor Gray
        Write-Host ""
        docker-compose -f docker-compose.ollama.yml run --rm query-app-ollama python test_llm_query_ollama.py --interactive
    }
    "5" {
        Write-Host ""
        Write-Host "啟動 pgAdmin..." -ForegroundColor Yellow
        docker-compose -f docker-compose.ollama.yml --profile tools up -d pgadmin
        Start-Sleep -Seconds 3
        Write-Host ""
        Write-Host "✅ pgAdmin 已啟動！" -ForegroundColor Green
        Write-Host ""
        Write-Host "請在瀏覽器開啟：http://localhost:5050" -ForegroundColor Cyan
        Write-Host "登入資訊：" -ForegroundColor Yellow
        Write-Host "  Email: admin@example.com" -ForegroundColor White
        Write-Host "  密碼: admin123" -ForegroundColor White
        
        Start-Process "http://localhost:5050"
    }
    "6" {
        Write-Host ""
        Write-Host "查看日誌（按 Ctrl+C 退出）：" -ForegroundColor Yellow
        Write-Host ""
        docker-compose -f docker-compose.ollama.yml logs -f
    }
    "7" {
        Write-Host ""
        Write-Host "停止系統..." -ForegroundColor Yellow
        docker-compose -f docker-compose.ollama.yml down
        Write-Host ""
        Write-Host "✅ 系統已停止" -ForegroundColor Green
        Write-Host "（資料已保留，Ollama 模型仍在）" -ForegroundColor Gray
    }
    "8" {
        Write-Host ""
        Write-Host "⚠️  警告：此操作將刪除所有資料！" -ForegroundColor Red
        Write-Host "（Ollama 模型不會被刪除）" -ForegroundColor Gray
        $confirm = Read-Host "確定要繼續嗎？(yes/no)"
        if ($confirm -eq "yes") {
            Write-Host ""
            Write-Host "正在清除系統和資料..." -ForegroundColor Yellow
            docker-compose -f docker-compose.ollama.yml down -v
            Write-Host ""
            Write-Host "✅ 系統已完全清除" -ForegroundColor Green
        } else {
            Write-Host "已取消操作" -ForegroundColor Yellow
        }
    }
    default {
        Write-Host ""
        Write-Host "❌ 無效選項" -ForegroundColor Red
    }
}

Write-Host ""
