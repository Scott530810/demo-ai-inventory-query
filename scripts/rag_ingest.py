#!/usr/bin/env python3
"""
RAG 文件匯入腳本（使用 rag_chunks）

使用方式:
    python scripts/rag_ingest.py docs/catalogs
    python scripts/rag_ingest.py docs/catalogs/specific_file.pdf
"""

import argparse
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ambulance_inventory.config import DatabaseConfig, OllamaConfig, RagConfig
from ambulance_inventory.database import DatabaseClient
from ambulance_inventory.ollama_client import OllamaClient
from ambulance_inventory.rag.ingest import RagIngestor


def main() -> int:
    parser = argparse.ArgumentParser(description="RAG 文件匯入工具")
    parser.add_argument("path", nargs="?", default="docs/catalogs", help="檔案或資料夾路徑")
    args = parser.parse_args()

    base = Path(args.path)
    if not base.exists():
        raise SystemExit(f"找不到路徑: {base}")

    rag_config = RagConfig.from_env()

    print("RAG 文件匯入工具")
    print("================")
    print(f"嵌入模型: {rag_config.embedding_model}")
    print(f"片段大小: {rag_config.chunk_size}")
    print(f"重疊大小: {rag_config.chunk_overlap}")

    db_client = DatabaseClient(DatabaseConfig.from_env())
    ollama_client = OllamaClient(OllamaConfig.from_env())
    ingestor = RagIngestor(db_client, ollama_client, rag_config)

    if base.is_file():
        total = ingestor.ingest_file(base)
    else:
        total = ingestor.ingest_dir(str(base))

    print("\n================")
    print(f"匯入完成！總共 {total} 個片段")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
