#!/usr/bin/env python3
"""
RAG 系統問題分析與測試
測試不同 top_k 值和查詢方式的影響
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ambulance_inventory.config import DatabaseConfig, OllamaConfig, RagConfig
from ambulance_inventory.database import DatabaseClient
from ambulance_inventory.ollama_client import OllamaClient
from ambulance_inventory.rag.retriever import RagRetriever

db_config = DatabaseConfig.from_env()
ollama_config = OllamaConfig.from_env()
rag_config = RagConfig.from_env()

db_client = DatabaseClient(db_config)
ollama_client = OllamaClient(ollama_config)
retriever = RagRetriever(db_client, ollama_client, rag_config)

# 測試問題組
TEST_CASES = [
    {
        "query": "載重250kg以上的擔架床有哪些選擇",
        "expected_models": ["Model 28 (295kg)"],
        "should_mention_24_25": "應該說明 Model 24 (180kg) 和 Model 25 (181kg) 不符合"
    },
    {
        "query": "Model 25 Cot的載重限制是多少",
        "expected_info": "181 kg 或 400 lb",
        "should_find_chunk": 0
    },
    {
        "query": "24型擔架床的最大承重",
        "expected_info": "180 KG",
        "should_find_chunk": 8
    },
    {
        "query": "所有擔架床的承重規格比較",
        "expected_models": ["Model 24: 180kg", "Model 25: 181kg", "Model 28: 295kg"]
    }
]

def analyze_retrieval(query: str, results: list, top_k: int):
    """分析檢索結果"""
    spec_chunks = []
    name_only_chunks = []
    other_chunks = []

    for i, r in enumerate(results[:top_k], 1):
        has_spec_keywords = any(kw in r.content for kw in [
            'SPECIFICATIONS', 'Load Limit', 'Weight Limit', '載重', '承重',
            '180', '181', '295', '400', '650'
        ])

        is_name_only = any(pattern in r.content for pattern in [
            'Model 25 Cot Only',
            'Model 25, Restraints',
            'Mattress',
            '#00'
        ]) and not has_spec_keywords

        if has_spec_keywords:
            spec_chunks.append((i, r))
        elif is_name_only:
            name_only_chunks.append((i, r))
        else:
            other_chunks.append((i, r))

    return spec_chunks, name_only_chunks, other_chunks


print("="*80)
print("RAG 系統問題分析與測試")
print("="*80)

for test_case in TEST_CASES:
    query = test_case["query"]
    print(f"\n{'='*80}")
    print(f"測試查詢: {query}")
    print(f"{'='*80}\n")

    # 測試不同 top_k 值
    for top_k in [5, 10, 15]:
        print(f"\n--- top_k={top_k} ---")
        results = retriever.retrieve(query, top_k=top_k, use_hybrid=True)

        spec_chunks, name_only, other = analyze_retrieval(query, results, top_k)

        print(f"規格片段: {len(spec_chunks)} 個")
        for rank, r in spec_chunks:
            print(f"  [{rank}] {r.source[:35]:35s} chunk={r.chunk_index:2d} score={r.score:.4f}")

        print(f"\n僅型號片段: {len(name_only)} 個")
        for rank, r in name_only[:3]:
            print(f"  [{rank}] {r.source[:35]:35s} chunk={r.chunk_index:2d} score={r.score:.4f}")

        print(f"\n其他片段: {len(other)} 個")

        # 檢查是否包含關鍵資訊
        all_content = " ".join([r.content for r in results[:top_k]])

        has_model_24_weight = "180" in all_content
        has_model_25_weight = "181" in all_content or "400 lb" in all_content
        has_model_28_weight = "295" in all_content or "650 lb" in all_content

        print(f"\n包含承重資訊:")
        print(f"  Model 24 (180kg): {'✅' if has_model_24_weight else '❌'}")
        print(f"  Model 25 (181kg): {'✅' if has_model_25_weight else '❌'}")
        print(f"  Model 28 (295kg): {'✅' if has_model_28_weight else '❌'}")

        # 建議
        if len(spec_chunks) == 0:
            print(f"\n⚠️  警告: 前 {top_k} 個片段中沒有規格資訊！")
        elif spec_chunks[0][0] > 5:
            print(f"\n⚠️  警告: 第一個規格片段排名第 {spec_chunks[0][0]}，可能被忽略！")

print(f"\n{'='*80}")
print("結論與建議")
print("="*80)
print("""
1. **增加 top_k**: 從 5 提高到 10-15，確保規格表被包含
2. **改進 Chunking**: 確保規格表作為完整單元，不要切分
3. **提升規格片段權重**: 對包含 SPECIFICATIONS 的片段額外加權
4. **改進 RESPONSE_GENERATION_PROMPT**: 明確要求在規格表中查找承重資訊
5. **考慮混合模式**: 承重範圍過濾用 SQL，詳細資訊用 RAG
""")
