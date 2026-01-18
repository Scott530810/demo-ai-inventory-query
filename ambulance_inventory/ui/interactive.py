"""
互動模式模組
提供命令列互動式查詢介面
"""

from ..query_engine import QueryEngine
from ..ollama_client import OllamaClient


def interactive_mode(query_engine: QueryEngine, ollama_client: OllamaClient):
    """
    互動查詢模式

    Args:
        query_engine: 查詢引擎
        ollama_client: Ollama 客戶端
    """
    print("\n" + "="*70)
    print("  進入互動模式（本地 Ollama 版本）")
    print(f"  模型: {ollama_client.config.model}")
    print(f"  主機: {ollama_client.config.host}")
    print("  命令: 'models' 切換模型 | 'exit' 離開")
    print("="*70 + "\n")

    # 測試 Ollama 連接
    print("測試 Ollama 連接...")

    if not ollama_client.test_connection():
        print("Ollama 連接失敗，請檢查設定\n")
        return

    print("Ollama 連接成功！\n")

    # 主循環
    while True:
        try:
            question = input("\n請輸入您的問題: ").strip()

            if not question:
                continue

            if question.lower() in ['exit', 'quit', '離開', '退出']:
                print("\n再見！")
                break

            if question.lower() in ['models', '模型', 'model']:
                _switch_model(ollama_client)
                continue

            # 執行查詢
            _execute_query(query_engine, question)

        except KeyboardInterrupt:
            print("\n\n再見！")
            break
        except Exception as e:
            print(f"\n發生錯誤: {str(e)}")


def _switch_model(ollama_client: OllamaClient):
    """
    切換 Ollama 模型

    Args:
        ollama_client: Ollama 客戶端
    """
    print("\n" + "="*70)
    print("  切換模型")
    print("="*70)

    # 獲取可用模型
    models = ollama_client.get_available_models()

    if not models:
        print("無法獲取模型列表\n")
        return

    current_model = ollama_client.config.model
    print(f"\n當前模型: {current_model}")
    print("\n可用模型:")

    for i, model in enumerate(models, 1):
        marker = " <-- 當前" if model == current_model else ""
        print(f"  {i}. {model}{marker}")

    print(f"  0. 取消")

    try:
        choice = input("\n請選擇模型編號: ").strip()

        if choice == '0' or not choice:
            print("已取消\n")
            return

        index = int(choice) - 1
        if 0 <= index < len(models):
            new_model = models[index]
            old_model = ollama_client.config.model
            ollama_client.config.model = new_model
            print(f"\n已切換模型: {old_model} -> {new_model}\n")
        else:
            print("無效的選擇\n")

    except ValueError:
        print("請輸入有效的數字\n")


def _execute_query(query_engine: QueryEngine, question: str):
    """
    執行查詢並顯示結果

    Args:
        query_engine: 查詢引擎
        question: 用戶問題
    """
    print(f"\n{'='*70}")
    print(f"問題: {question}")
    print(f"使用模型: {query_engine.ollama_client.config.model}")
    print(f"{'='*70}\n")

    sql, answer = query_engine.query(question)

    if sql and answer:
        print(f"AI 回應:")
        print(f"{answer}\n")
    elif sql and not answer:
        print("SQL 生成成功但執行失敗\n")
    else:
        print("查詢失敗\n")
