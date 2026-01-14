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
    print("  🚀 進入互動模式（本地 Ollama 版本）")
    print(f"  模型: {ollama_client.config.model}")
    print(f"  主機: {ollama_client.config.host}")
    print("  輸入 'exit' 或 'quit' 離開")
    print("="*70 + "\n")

    # 測試 Ollama 連接
    print("🔍 測試 Ollama 連接...")

    if not ollama_client.test_connection():
        print("❌ Ollama 連接失敗，請檢查設定\n")
        return

    print("✅ Ollama 連接成功！\n")

    # 主循環
    while True:
        try:
            question = input("\n💭 請輸入您的問題: ").strip()

            if not question:
                continue

            if question.lower() in ['exit', 'quit', '離開', '退出']:
                print("\n👋 再見！")
                break

            # 執行查詢
            _execute_query(query_engine, question)

        except KeyboardInterrupt:
            print("\n\n👋 再見！")
            break
        except Exception as e:
            print(f"\n❌ 發生錯誤: {str(e)}")


def _execute_query(query_engine: QueryEngine, question: str):
    """
    執行查詢並顯示結果

    Args:
        query_engine: 查詢引擎
        question: 用戶問題
    """
    print(f"\n{'='*70}")
    print(f"❓ 問題: {question}")
    print(f"🤖 使用模型: {query_engine.ollama_client.config.model}")
    print(f"{'='*70}\n")

    sql, answer = query_engine.query(question)

    if sql and answer:
        print(f"💬 AI 回應:")
        print(f"{answer}\n")
    elif sql and not answer:
        print("⚠️ SQL 生成成功但執行失敗\n")
    else:
        print("❌ 查詢失敗\n")
