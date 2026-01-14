#!/bin/bash

# ============================================
# 救護車庫存查詢系統 - Ollama 本地端版本 (Bash)
# ============================================

echo "========================================"
echo "  救護車庫存查詢系統 - Ollama 版本"
echo "  使用本地 LLM (qwen2.5:32b)"
echo "========================================"
echo ""

# 檢查 Docker 是否運行
echo "檢查 Docker 狀態..."
if ! docker info &> /dev/null; then
    echo "❌ Docker 未運行"
    exit 1
fi
echo "✅ Docker 正在運行"
echo ""

# 檢查 Ollama 是否運行
echo "檢查 Ollama 狀態..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama 正在運行"
    
    # 檢查模型
    models=$(curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
    if echo "$models" | grep -q "qwen2.5:32b"; then
        echo "✅ 模型 qwen2.5:32b 已就緒"
    else
        echo "⚠️  模型 qwen2.5:32b 未找到"
        echo "   可用模型: $models"
        echo ""
        echo "是否要下載 qwen2.5:32b 模型？(y/n)"
        read -r download
        if [ "$download" == "y" ]; then
            echo "正在下載模型（約 19GB，需要一些時間）..."
            ollama pull qwen2.5:32b
        else
            echo "請手動下載模型: ollama pull qwen2.5:32b"
            exit 1
        fi
    fi
else
    echo "❌ Ollama 未運行或無法連接"
    echo ""
    echo "請確認："
    echo "  1. Ollama 已安裝"
    echo "  2. Ollama 正在運行"
    echo "  3. 允許外部訪問 (設定 OLLAMA_HOST=0.0.0.0)"
    exit 1
fi
echo ""

# 顯示功能選單
echo "請選擇操作："
echo "  1. 啟動系統（包含資料庫、應用）"
echo "  2. 系統檢查（測試所有組件）"
echo "  3. 執行 Demo 查詢"
echo "  4. 進入互動模式"
echo "  5. 啟動 pgAdmin（資料庫管理界面）"
echo "  6. 查看日誌"
echo "  7. 停止系統"
echo "  8. 完全清除（包含資料）"
echo "  9. 直接連接資料庫 (psql)"
echo ""

read -p "請輸入選項 (1-9): " choice

case $choice in
    1)
        echo ""
        echo "正在啟動系統..."
        docker-compose -f docker-compose.ollama.yml up -d
        echo ""
        echo "✅ 系統啟動完成！"
        echo ""
        echo "系統資訊："
        echo "  📊 資料庫：localhost:5432"
        echo "  🤖 LLM：本地 Ollama (qwen2.5:32b)"
        echo "  💾 GPU：RTX 5070"
        echo ""
        echo "下一步："
        echo "  ./run-ollama.sh  (選擇 2 進行系統檢查)"
        ;;
    2)
        echo ""
        echo "執行系統檢查..."
        echo ""
        docker-compose -f docker-compose.ollama.yml run --rm query-app-ollama python test_llm_query_ollama.py --check
        ;;
    3)
        echo ""
        echo "執行 Demo 查詢..."
        echo "（使用本地 Ollama，完全免費！）"
        echo ""
        docker-compose -f docker-compose.ollama.yml run --rm query-app-ollama python test_llm_query_ollama.py --demo
        ;;
    4)
        echo ""
        echo "進入互動模式..."
        echo "（輸入 'exit' 或 'quit' 離開）"
        echo ""
        docker-compose -f docker-compose.ollama.yml run --rm query-app-ollama python test_llm_query_ollama.py --interactive
        ;;
    5)
        echo ""
        echo "啟動 pgAdmin..."
        docker-compose -f docker-compose.ollama.yml --profile tools up -d pgadmin
        sleep 3
        echo ""
        echo "✅ pgAdmin 已啟動！"
        echo ""
        echo "請在瀏覽器開啟：http://localhost:5050"
        echo "登入資訊："
        echo "  Email: admin@example.com"
        echo "  密碼: admin123"
        ;;
    6)
        echo ""
        echo "查看日誌（按 Ctrl+C 退出）："
        echo ""
        docker-compose -f docker-compose.ollama.yml logs -f
        ;;
    7)
        echo ""
        echo "停止系統..."
        docker-compose -f docker-compose.ollama.yml down
        echo ""
        echo "✅ 系統已停止"
        echo "（資料已保留，Ollama 模型仍在）"
        ;;
    8)
        echo ""
        echo "⚠️  警告：此操作將刪除所有資料！"
        echo "（Ollama 模型不會被刪除）"
        read -p "確定要繼續嗎？(yes/no): " confirm
        if [ "$confirm" == "yes" ]; then
            echo ""
            echo "正在清除系統和資料..."
            docker-compose -f docker-compose.ollama.yml down -v
            echo ""
            echo "✅ 系統已完全清除"
        else
            echo "已取消操作"
        fi
        ;;
    9)
        echo ""
        echo "連接到資料庫..."
        echo "（輸入 \\q 離開）"
        echo ""
        docker exec -it ambulance-db-ollama psql -U postgres -d ambulance_inventory
        ;;
    *)
        echo ""
        echo "❌ 無效選項"
        ;;
esac

echo ""
