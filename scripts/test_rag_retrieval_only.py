#!/usr/bin/env python3
"""
RAG 檢索測試（不含 LLM 生成）
專注測試 RAG 檢索功能和評分機制
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ambulance_inventory.config import DatabaseConfig, OllamaConfig, RagConfig
from ambulance_inventory.database import DatabaseClient
from ambulance_inventory.ollama_client import OllamaClient
from ambulance_inventory.rag.retriever import RagRetriever
from ambulance_inventory.utils.logger import get_logger

logger = get_logger(__name__)

# 測試問題組
TEST_QUERIES = [
    {
        "category": "承重查詢 (Load Limit)",
        "boost": 2.0,
        "questions": [
            "請問24型擔架床的最大承重是多少kg？",
            "哪些擔架床可以承載超過300kg的重量？",
            "Model 25的Load Limit是多少？",
        ]
    },
    {
        "category": "規格查詢 (Specifications)",
        "boost": 1.5,
        "questions": [
            "請列出24型擔架床的規格，包含尺寸和重量",
            "Model 25展開時的長度和寬度是多少？",
            "Model 28HD的折收高度是多少？",
        ]
    },
    {
        "category": "型號查詢 (Model)",
        "boost": 1.6,
        "questions": [
            "請問Ferno有哪些型號的擔架床？",
            "Model 24和Model 25有什麼區別？",
            "椅式擔架床有哪些型號？",
        ]
    },
    {
        "category": "特色查詢 (Features)",
        "boost": 1.3,
        "questions": [
            "24型擔架床有哪些主要特色？",
            "擔架床的高度和角度可以調整嗎？",
            "擔架床使用什麼材質製造？",
        ]
    },
    {
        "category": "角度查詢 (Angle)",
        "boost": 1.4,
        "questions": [
            "24型擔架床的靠背角度可以調整嗎？有幾段？",
            "擔架床的高度可以做幾段調整？",
            "椅式擔架床的傾斜角度是多少？",
        ]
    },
]


def main():
    print("="*80)
    print("RAG 檢索測試（不含 LLM 生成）")
    print("="*80)

    # 初始化
    db_config = DatabaseConfig.from_env()
    ollama_config = OllamaConfig.from_env()
    rag_config = RagConfig.from_env()

    db_client = DatabaseClient(db_config)
    ollama_client = OllamaClient(ollama_config)
    retriever = RagRetriever(db_client, ollama_client, rag_config)

    # 檢查資料
    chunk_count = retriever.get_chunk_count()
    sources = retriever.get_sources()

    print(f"\nRAG 資料庫狀態:")
    print(f"  總片段數: {chunk_count}")
    print(f"  文件來源: {', '.join(sources)}")
    print(f"  混合檢索權重: BM25={rag_config.bm25_weight}, Vector={rag_config.vector_weight}")

    total_tests = 0
    successful_retrievals = 0
    total_score = 0.0

    for query_group in TEST_QUERIES:
        category = query_group["category"]
        boost = query_group["boost"]

        print(f"\n{'='*80}")
        print(f"{category} (預期加權: {boost}x)")
        print(f"{'='*80}")

        for question in query_group["questions"]:
            total_tests += 1
            print(f"\n問題: {question}")
            print("-" * 80)

            try:
                # 混合檢索
                results = retriever.retrieve(question, top_k=3, use_hybrid=True)

                if results:
                    successful_retrievals += 1
                    top_score = results[0].score
                    total_score += top_score

                    print(f"✅ 找到 {len(results)} 個相關片段 (最高分數: {top_score:.4f})")

                    for i, result in enumerate(results, 1):
                        print(f"\n  [{i}] 來源: {result.source}")
                        print(f"      片段索引: {result.chunk_index}")
                        print(f"      相關分數: {result.score:.4f}")

                        # 顯示內容片段
                        content_lines = result.content.strip().split('\n')
                        preview = '\n      '.join(content_lines[:5])
                        if len(content_lines) > 5:
                            preview += "\n      ..."

                        print(f"      內容預覽:\n      {preview}")
                else:
                    logger.warning(f"⚠️  未找到相關片段")

            except Exception as e:
                logger.error(f"❌ 檢索失敗: {e}")
                import traceback
                traceback.print_exc()

    # 統計結果
    print(f"\n{'='*80}")
    print(f"測試統計:")
    print(f"  總測試數: {total_tests}")
    print(f"  成功檢索: {successful_retrievals}")
    print(f"  成功率: {successful_retrievals/total_tests*100:.1f}%")
    if successful_retrievals > 0:
        print(f"  平均最高分數: {total_score/successful_retrievals:.4f}")
    print(f"{'='*80}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
