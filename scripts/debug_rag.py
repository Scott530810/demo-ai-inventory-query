#!/usr/bin/env python3
"""RAG Debug 腳本"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ambulance_inventory.config import DatabaseConfig, OllamaConfig, RagConfig
from ambulance_inventory.database import DatabaseClient
from ambulance_inventory.ollama_client import OllamaClient
from ambulance_inventory.rag.retriever import RagRetriever

# 初始化
db_config = DatabaseConfig.from_env()
ollama_config = OllamaConfig.from_env()
rag_config = RagConfig.from_env()

db_client = DatabaseClient(db_config)
ollama_client = OllamaClient(ollama_config)
retriever = RagRetriever(db_client, ollama_client, rag_config)

print("="*60)
print("RAG Debug 測試")
print("="*60)

# 測試 1: 生成查詢嵌入
print("\n[1] 測試生成查詢嵌入...")
query = "24型擔架床的最大承重"
embedding = retriever.get_embedding(query)
if embedding:
    print(f"✅ 成功生成嵌入向量，維度: {len(embedding)}")
else:
    print("❌ 生成嵌入失敗")
    sys.exit(1)

# 測試 2: BM25 搜索
print("\n[2] 測試 BM25 搜索...")
try:
    results = retriever._bm25_search(query, 3)
    print(f"✅ BM25 搜索成功，找到 {len(results)} 個結果")
    for i, r in enumerate(results, 1):
        print(f"  [{i}] {r.source}: {r.content[:80]}... (分數: {r.score:.4f})")
except Exception as e:
    print(f"❌ BM25 搜索失敗: {e}")
    import traceback
    traceback.print_exc()

# 測試 3: 向量搜索
print("\n[3] 測試向量搜索...")
try:
    results = retriever._vector_search(embedding, 3)
    print(f"✅ 向量搜索成功，找到 {len(results)} 個結果")
    for i, r in enumerate(results, 1):
        print(f"  [{i}] {r.source}: {r.content[:80]}... (分數: {r.score:.4f})")
except Exception as e:
    print(f"❌ 向量搜索失敗: {e}")
    import traceback
    traceback.print_exc()

# 測試 4: 混合搜索
print("\n[4] 測試混合搜索...")
try:
    results = retriever._hybrid_search(query, 3)
    print(f"✅ 混合搜索成功，找到 {len(results)} 個結果")
    for i, r in enumerate(results, 1):
        print(f"  [{i}] {r.source}: {r.content[:80]}... (分數: {r.score:.4f})")
except Exception as e:
    print(f"❌ 混合搜索失敗: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
