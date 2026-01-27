#!/usr/bin/env python3
"""
RAG 查詢測試腳本
根據型錄內容設計測試問題，評估 RAG 系統效果
"""

import sys
import os
from pathlib import Path

# 添加專案路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from ambulance_inventory.config import DatabaseConfig, OllamaConfig, RagConfig
from ambulance_inventory.database import DatabaseClient
from ambulance_inventory.ollama_client import OllamaClient
from ambulance_inventory.rag.retriever import RagRetriever
from ambulance_inventory.utils.logger import get_logger

logger = get_logger(__name__)


# 測試問題組（針對型錄內容設計）
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


def test_rag_retrieval(retriever: RagRetriever):
    """測試 RAG 檢索功能"""
    logger.info("\n" + "="*60)
    logger.info("RAG 檢索功能測試")
    logger.info("="*60)

    total_tests = 0
    successful_retrievals = 0

    for query_group in TEST_QUERIES:
        category = query_group["category"]
        boost = query_group["boost"]

        logger.info(f"\n### {category} (預期加權: {boost}x) ###\n")

        for question in query_group["questions"]:
            total_tests += 1
            logger.info(f"問題: {question}")

            try:
                # 執行檢索
                results = retriever.retrieve(question, top_k=3, use_hybrid=True)

                if results:
                    successful_retrievals += 1
                    logger.info(f"✅ 找到 {len(results)} 個相關片段")

                    for i, result in enumerate(results[:2], 1):
                        logger.info(f"  [{i}] 來源: {result.source}")
                        logger.info(f"      分數: {result.score:.4f}")
                        logger.info(f"      內容: {result.content[:150]}...")
                else:
                    logger.warning(f"⚠️  未找到相關片段")

            except Exception as e:
                logger.error(f"❌ 檢索失敗: {e}")

            logger.info("")

    # 統計結果
    logger.info("\n" + "="*60)
    logger.info(f"測試統計:")
    logger.info(f"  總測試數: {total_tests}")
    logger.info(f"  成功檢索: {successful_retrievals}")
    logger.info(f"  成功率: {successful_retrievals/total_tests*100:.1f}%")
    logger.info("="*60)


def test_rag_with_llm(db_client: DatabaseClient, ollama_client: OllamaClient, retriever: RagRetriever):
    """測試 RAG + LLM 完整流程"""
    logger.info("\n" + "="*60)
    logger.info("RAG + LLM 完整流程測試")
    logger.info("="*60)

    # 選擇幾個代表性問題測試
    sample_questions = [
        "請問24型擔架床的最大承重是多少kg？",
        "請列出24型擔架床的規格，包含尺寸和重量",
        "24型擔架床的靠背角度可以調整嗎？有幾段？",
    ]

    for question in sample_questions:
        logger.info(f"\n問題: {question}")
        logger.info("-" * 60)

        try:
            # 1. RAG 檢索
            results = retriever.retrieve(question, top_k=3, use_hybrid=True)

            if not results:
                logger.warning("⚠️  未找到相關型錄資料")
                continue

            # 2. 組合 context
            context = "\n\n---\n\n".join([
                f"[來源: {r.source}]\n{r.content}"
                for r in results
            ])

            # 3. 生成回答
            prompt = f"""根據以下型錄資料回答問題。請只根據提供的資料回答，不可編造。

型錄資料:
{context}

問題: {question}

請用繁體中文簡潔回答，並註明資料來源。"""

            logger.info("\n📄 檢索到的型錄片段:")
            for i, r in enumerate(results, 1):
                logger.info(f"  [{i}] {r.source} (分數: {r.score:.4f})")

            logger.info("\n🤖 AI 回答:")
            response = ollama_client.generate(prompt)
            if response:
                logger.info(response)
            else:
                logger.warning("⚠️  AI 生成失敗")

        except Exception as e:
            logger.error(f"❌ 測試失敗: {e}")

        logger.info("")


def main():
    """主程式"""
    logger.info("RAG 查詢測試開始")
    logger.info("="*60)

    # 初始化配置
    db_config = DatabaseConfig.from_env()
    ollama_config = OllamaConfig.from_env()
    rag_config = RagConfig.from_env()

    logger.info(f"資料庫: {db_config.host}:{db_config.port}/{db_config.database}")
    logger.info(f"Ollama: {ollama_config.host}")
    logger.info(f"嵌入模型: {rag_config.embedding_model}")
    logger.info(f"混合檢索權重: BM25={rag_config.bm25_weight}, Vector={rag_config.vector_weight}")

    # 初始化客戶端
    db_client = DatabaseClient(db_config)
    ollama_client = OllamaClient(ollama_config)
    retriever = RagRetriever(db_client, ollama_client, rag_config)

    # 檢查 RAG 資料
    chunk_count = retriever.get_chunk_count()
    sources = retriever.get_sources()

    logger.info(f"\nRAG 資料庫狀態:")
    logger.info(f"  總片段數: {chunk_count}")
    logger.info(f"  文件來源: {len(sources)} 個")
    for source in sources:
        logger.info(f"    - {source}")

    if chunk_count == 0:
        logger.error("❌ RAG 資料庫為空，請先執行 rag_ingest.py")
        return 1

    # 執行測試
    test_rag_retrieval(retriever)
    test_rag_with_llm(db_client, ollama_client, retriever)

    logger.info("\n✅ 測試完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
