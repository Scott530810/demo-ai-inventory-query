"""
系統檢查模組
檢查資料庫、Ollama 和系統狀態
"""

from ..database import DatabaseClient
from ..ollama_client import OllamaClient


def check_system(db_client: DatabaseClient, ollama_client: OllamaClient) -> bool:
    """
    檢查系統狀態

    Args:
        db_client: 資料庫客戶端
        ollama_client: Ollama 客戶端

    Returns:
        系統是否正常
    """
    print("\n" + "="*70)
    print("  🔍 系統狀態檢查")
    print("="*70 + "\n")

    all_ok = True

    # 1. 檢查資料庫
    print("1️⃣ 檢查資料庫連接...")
    try:
        if db_client.test_connection():
            count = db_client.get_inventory_count()
            print(f"   ✅ 資料庫連接成功！共 {count} 項商品\n")
        else:
            print("   ❌ 資料庫連接失敗\n")
            all_ok = False
    except Exception as e:
        print(f"   ❌ 資料庫連接失敗: {str(e)}\n")
        all_ok = False

    # 2. 檢查 Ollama
    print("2️⃣ 檢查 Ollama 連接...")
    print(f"   主機: {ollama_client.config.host}")
    print(f"   模型: {ollama_client.config.model}")

    try:
        if ollama_client.test_connection():
            models = ollama_client.get_available_models()
            print(f"   ✅ Ollama 連接成功！")
            print(f"   📦 已安裝的模型: {', '.join(models)}")

            if ollama_client.is_model_available():
                print(f"   ✅ 目標模型 {ollama_client.config.model} 已就緒\n")
            else:
                print(f"   ⚠️ 目標模型 {ollama_client.config.model} 未安裝")
                print(f"   請執行: ollama pull {ollama_client.config.model}\n")
                all_ok = False
        else:
            print("   ❌ Ollama 連接失敗")
            print("\n   請確認:")
            print("   • Ollama 正在運行")
            print("   • 允許外部訪問（OLLAMA_HOST=0.0.0.0）\n")
            all_ok = False

    except Exception as e:
        print(f"   ❌ Ollama 連接失敗: {str(e)}")
        print("\n   請確認:")
        print("   • Ollama 正在運行")
        print("   • 允許外部訪問（OLLAMA_HOST=0.0.0.0）\n")
        all_ok = False

    # 3. 測試推理
    print("3️⃣ 測試 Ollama 推理能力...")

    try:
        test_prompt = "請用一句話說明什麼是資料庫。"
        response = ollama_client.generate(test_prompt, "", 0.7)

        if response and len(response) > 10:
            print(f"   ✅ Ollama 推理測試成功")
            print(f"   回應: {response[:100]}...\n")
        else:
            print(f"   ❌ Ollama 推理測試失敗\n")
            all_ok = False

    except Exception as e:
        print(f"   ❌ Ollama 推理測試失敗: {str(e)}\n")
        all_ok = False

    # 總結
    print("="*70)
    if all_ok:
        print("  ✅ 系統檢查完成！一切正常")
    else:
        print("  ⚠️ 系統檢查發現問題，請查看上方錯誤訊息")
    print("="*70 + "\n")

    return all_ok
