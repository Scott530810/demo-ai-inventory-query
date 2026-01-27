"""Ingest catalog files into RAG index."""

import argparse
from pathlib import Path

from ambulance_inventory.config import DatabaseConfig, OllamaConfig, RagConfig
from ambulance_inventory.database import DatabaseClient
from ambulance_inventory.ollama_client import OllamaClient
from ambulance_inventory.rag.ingest import RagIngestor


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest catalog files into RAG index")
    parser.add_argument("path", nargs="?", default="docs/catalogs", help="Catalog directory")
    args = parser.parse_args()

    base = Path(args.path)
    if not base.exists():
        raise SystemExit(f"Path not found: {base}")

    db_client = DatabaseClient(DatabaseConfig.from_env())
    ollama_client = OllamaClient(OllamaConfig.from_env())
    rag_config = RagConfig.from_env()

    ingestor = RagIngestor(db_client, ollama_client, rag_config)
    total = ingestor.ingest_dir(str(base))
    print(f"Ingested {total} chunks from {base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
