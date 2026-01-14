"""
Demo 模式模組
執行預設的示範查詢
"""

import sys

from ..query_engine import QueryEngine
from ..ollama_client import OllamaClient
from ..config import DEMO_QUESTIONS


def demo_mode(query_engine: QueryEngine, ollama_client: OllamaClient):
    """
    執行 Demo 查詢

    Args:
        query_engine: 查詢引擎
        ollama_client: Ollama 客戶端
    """
    print("\n" + "="*70)
    print("  🎬 Demo 模式（本地 Ollama 版本）")
    print(f"  模型: {ollama_client.config.model}")
    print("="*70)

    # 測試 Ollama 連接
    print("\n🔍 測試 Ollama 連接...")

    if not ollama_client.test_connection():
        print("❌ Ollama 連接失敗")
        print("\n請確認:")
        print("  1. Ollama 正在運行")
        print(f"  2. 模型已下載: ollama pull {ollama_client.config.model}")
        return

    print("✅ Ollama 連接成功！\n")

    # 執行 Demo 查詢
    for i, question in enumerate(DEMO_QUESTIONS, 1):
        print(f"\n{'='*70}")
        print(f"Demo {i}/{len(DEMO_QUESTIONS)}")
        print(f"{'='*70}")

        # 檢查是否在互動式終端中
        if sys.stdin.isatty():
            input("按 Enter 繼續...")
        else:
            print("自動繼續...\n")

        # 執行查詢
        _execute_query(query_engine, question)

    print("\n" + "="*70)
    print("  ✅ Demo 完成！")
    print("="*70 + "\n")


def _execute_query(query_engine: QueryEngine, question: str):
    """
    執行單個查詢並顯示結果

    Args:
        query_engine: 查詢引擎
        question: 問題
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
