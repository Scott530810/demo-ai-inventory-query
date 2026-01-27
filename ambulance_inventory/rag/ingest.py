"""RAG ingestion pipeline for catalog files."""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from pypdf import PdfReader

from ..config import RagConfig
from ..database import DatabaseClient
from ..ollama_client import OllamaClient
from ..utils.logger import get_logger
from .chunker import chunk_catalog_text
from .types import RagChunk


class RagIngestor:
    def __init__(self, db_client: DatabaseClient, ollama_client: OllamaClient, rag_config: RagConfig):
        self.db_client = db_client
        self.ollama_client = ollama_client
        self.rag_config = rag_config
        self.logger = get_logger(__name__)

    def ingest_dir(self, directory: str) -> int:
        base = Path(directory)
        if not base.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        files = [p for p in base.rglob("*") if p.suffix.lower() in {".pdf", ".doc"}]
        if not files:
            self.logger.warning("No catalog files found")
            return 0

        total = 0
        for path in files:
            total += self.ingest_file(path)
        return total

    def ingest_file(self, path: Path) -> int:
        if path.suffix.lower() == ".pdf":
            pages = self._extract_pdf_pages(path)
        elif path.suffix.lower() == ".doc":
            pages = self._extract_doc_pages(path)
        else:
            self.logger.warning(f"Unsupported file type: {path}")
            return 0

        if not pages:
            self.logger.warning(f"No text extracted from {path}")
            return 0

        chunks: List[RagChunk] = []
        for page_num, text in pages:
            for idx, chunk in enumerate(chunk_catalog_text(text, self.rag_config.chunk_size, self.rag_config.chunk_overlap)):
                metadata = {
                    "source": path.name,
                    "page": page_num,
                    "chunk_index": idx
                }
                chunks.append(
                    RagChunk(
                        source=path.name,
                        page=page_num,
                        chunk_index=idx,
                        content=chunk,
                        metadata=metadata
                    )
                )

        if not chunks:
            return 0

        self._embed_chunks(chunks)
        self.db_client.insert_rag_chunks(chunks)
        self.logger.info(f"Ingested {len(chunks)} chunks from {path.name}")
        return len(chunks)

    def _embed_chunks(self, chunks: List[RagChunk]) -> None:
        model = self.rag_config.embedding_model
        for chunk in chunks:
            embedding = self.ollama_client.embed(chunk.content, model=model)
            if embedding is None:
                raise RuntimeError("Embedding failed; check Ollama and embedding model")
            embedding = self._resize_embedding(embedding)
            chunk.embedding = embedding

    def _resize_embedding(self, embedding: list) -> list:
        target = self.rag_config.embedding_dim
        if len(embedding) < target:
            raise ValueError(f"Embedding dim {len(embedding)} < target {target}")
        if len(embedding) > target:
            return embedding[:target]
        return embedding

    def _extract_pdf_pages(self, path: Path) -> List[Tuple[int, str]]:
        pages: List[Tuple[int, str]] = []
        reader = PdfReader(str(path))
        for i, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            text = text.strip()
            if text:
                pages.append((i, text))
        return pages

    def _extract_doc_pages(self, path: Path) -> List[Tuple[int, str]]:
        text = self._extract_doc_text(path)
        if not text:
            return []
        return [(1, text)]

    def _extract_doc_text(self, path: Path) -> Optional[str]:
        try:
            result = subprocess.run(
                ["antiword", str(path)],
                check=False,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                self.logger.warning(f"antiword failed for {path.name}: {result.stderr.strip()}")
                return None
            return result.stdout.strip()
        except FileNotFoundError:
            self.logger.warning("antiword not found; skipping .doc files")
            return None
