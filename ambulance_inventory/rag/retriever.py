"""Hybrid retriever using BM25 + vector search."""

from __future__ import annotations

import math
from typing import Dict, List, Optional

from ..config import RagConfig
from ..database import DatabaseClient
from ..ollama_client import OllamaClient
from ..utils.logger import get_logger
from .types import RagResult


class RagRetriever:
    def __init__(self, db_client: DatabaseClient, ollama_client: OllamaClient, rag_config: RagConfig):
        self.db_client = db_client
        self.ollama_client = ollama_client
        self.rag_config = rag_config
        self.logger = get_logger(__name__)

    def retrieve(self, question: str, top_k: Optional[int] = None) -> List[RagResult]:
        top_k = top_k or self.rag_config.top_k

        embedding = self.ollama_client.embed(question, model=self.rag_config.embedding_model)
        if embedding is None:
            self.logger.error("Embedding failed for query")
            return []
        embedding = self._resize_embedding(embedding)

        bm25_rows = self._bm25_search(question, self.rag_config.bm25_k)
        vector_rows = self._vector_search(embedding, self.rag_config.vector_k)

        merged = self._merge_results(bm25_rows, vector_rows)
        if not merged:
            return []

        merged = self._apply_query_bias(question, merged)
        rerank_k = self.rag_config.rerank_k
        merged = merged[:max(rerank_k, top_k)]

        if self.rag_config.rerank_model:
            merged = self._rerank(question, merged, self.rag_config.rerank_model)

        return merged[:top_k]

    def _bm25_search(self, question: str, limit: int) -> List[Dict]:
        sql = """
        SELECT id, source, page, chunk_index, content, metadata,
               ts_rank(tsv, q) AS score
        FROM rag_chunks, plainto_tsquery('simple', %s) q
        WHERE tsv @@ q
        ORDER BY score DESC
        LIMIT %s;
        """
        return self.db_client.execute_query(sql, (question, limit))

    def _vector_search(self, embedding: list, limit: int) -> List[Dict]:
        vector_str = "[" + ",".join(f"{v:.6f}" for v in embedding) + "]"
        sql = """
        SELECT id, source, page, chunk_index, content, metadata,
               (embedding <=> %s::vector) AS distance
        FROM rag_chunks
        WHERE embedding IS NOT NULL
        ORDER BY distance ASC
        LIMIT %s;
        """
        return self.db_client.execute_query(sql, (vector_str, limit))

    def _merge_results(self, bm25_rows: List[Dict], vector_rows: List[Dict]) -> List[RagResult]:
        scores: Dict[int, Dict[str, float]] = {}
        items: Dict[int, Dict] = {}

        max_bm25 = max((row.get("score", 0.0) for row in bm25_rows), default=0.0)

        for row in bm25_rows:
            doc_id = row["id"]
            items[doc_id] = row
            score = row.get("score", 0.0)
            scores.setdefault(doc_id, {})["bm25"] = score / max_bm25 if max_bm25 > 0 else 0.0

        for row in vector_rows:
            doc_id = row["id"]
            items[doc_id] = row
            distance = row.get("distance", 2.0)
            similarity = 1.0 - min(distance, 2.0) / 2.0
            scores.setdefault(doc_id, {})["vector"] = similarity

        results: List[RagResult] = []
        for doc_id, row in items.items():
            bm25 = scores.get(doc_id, {}).get("bm25", 0.0)
            vector = scores.get(doc_id, {}).get("vector", 0.0)
            score = 0.5 * bm25 + 0.5 * vector
            results.append(
                RagResult(
                    id=doc_id,
                    source=row.get("source"),
                    page=row.get("page"),
                    chunk_index=row.get("chunk_index"),
                    content=row.get("content"),
                    metadata=row.get("metadata") or {},
                    score=score
                )
            )

        results.sort(key=lambda r: r.score, reverse=True)
        return results

    def _apply_query_bias(self, question: str, results: List[RagResult]) -> List[RagResult]:
        if not results:
            return results

        q = question.lower()
        wants_specs = "規格" in q or "spec" in q or "specification" in q
        wants_load = any(term in q for term in ("承重", "載重", "負重", "load limit", "weight limit"))
        if wants_load:
            wants_specs = True
        wants_features = any(term in q for term in ("特色", "功能", "特點", "feature"))
        wants_angle = any(term in q for term in ("角度", "調整", "可調", "背靠", "angle", "degree", "°"))
        min_kg = self._extract_min_kg(q)

        model_number = None
        for token in q.replace("版", " ").split():
            if token.isdigit():
                model_number = token
                break
        brand_hint = "ferno" if "ferno" in q else None

        boosted: List[RagResult] = []
        for item in results:
            bonus = 0.0
            content_lower = (item.content or "").lower()

            if wants_specs:
                if "specifications" in content_lower:
                    bonus += 0.35
                if "imperial" in content_lower or "metric" in content_lower:
                    bonus += 0.2
                if any(unit in content_lower for unit in (" mm", " in", " kg", " lb")):
                    bonus += 0.15

            if wants_load and min_kg:
                max_kg = self._extract_max_kg(content_lower)
                if max_kg is not None:
                    if max_kg >= min_kg:
                        bonus += 0.45
                    else:
                        bonus -= 0.15
                if "load limit" in content_lower or "weight limit" in content_lower:
                    bonus += 0.2
                if "specifications" in content_lower:
                    bonus += 0.2
            elif wants_load:
                if "load limit" in content_lower or "weight limit" in content_lower:
                    bonus += 0.25
                if "最大載重" in content_lower or "max load" in content_lower:
                    bonus += 0.25
                if "kg" in content_lower or "lb" in content_lower:
                    bonus += 0.1

            if wants_features:
                if "Ì" in item.content or "•" in item.content:
                    bonus += 0.2
                if any(term in content_lower for term in ("features", "converts", "wheels", "sidearms")):
                    bonus += 0.2

            if wants_angle:
                if any(term in content_lower for term in ("angle", "°", "backrest")):
                    bonus += 0.3

            if model_number:
                if f"model {model_number}" in content_lower:
                    bonus += 0.25
                elif f"{model_number} 型" in item.content or f"{model_number}型" in item.content:
                    bonus += 0.2
                elif f" {model_number} " in f" {content_lower} ":
                    bonus += 0.1
                else:
                    bonus -= 0.05

            if brand_hint and brand_hint in content_lower:
                bonus += 0.1

            boosted.append(
                RagResult(
                    id=item.id,
                    source=item.source,
                    page=item.page,
                    chunk_index=item.chunk_index,
                    content=item.content,
                    metadata=item.metadata,
                    score=item.score + bonus
                )
            )

        boosted.sort(key=lambda r: r.score, reverse=True)
        return boosted

    @staticmethod
    def _extract_min_kg(question: str) -> Optional[float]:
        import re
        match = re.search(r"(\\d+(?:\\.\\d+)?)\\s*kg", question)
        if match:
            return float(match.group(1))
        match = re.search(r"(\\d+(?:\\.\\d+)?)\\s*公斤", question)
        if match:
            return float(match.group(1))
        return None

    @staticmethod
    def _extract_max_kg(text: str) -> Optional[float]:
        import re
        kg_values = [float(v) for v in re.findall(r"(\\d+(?:\\.\\d+)?)\\s*kg", text)]
        if kg_values:
            return max(kg_values)
        return None

    def _rerank(self, question: str, candidates: List[RagResult], model: str) -> List[RagResult]:
        reranked: List[RagResult] = []
        for cand in candidates:
            prompt = (
                "請為下面的段落與問題的相關性打分數，\n"
                "0 表示完全無關，5 表示非常相關。\n"
                "請只輸出數字。\n\n"
                f"問題: {question}\n"
                f"段落: {cand.content}"
            )
            response = self.ollama_client.generate(prompt=prompt, system_prompt="", temperature=0.0, model=model)
            score = self._parse_score(response)
            if score is None:
                score = cand.score
            reranked.append(
                RagResult(
                    id=cand.id,
                    source=cand.source,
                    page=cand.page,
                    chunk_index=cand.chunk_index,
                    content=cand.content,
                    metadata=cand.metadata,
                    score=score
                )
            )

        reranked.sort(key=lambda r: r.score, reverse=True)
        return reranked

    def _resize_embedding(self, embedding: list) -> list:
        target = self.rag_config.embedding_dim
        if len(embedding) < target:
            raise ValueError(f"Embedding dim {len(embedding)} < target {target}")
        if len(embedding) > target:
            return embedding[:target]
        return embedding

    @staticmethod
    def _parse_score(text: Optional[str]) -> Optional[float]:
        if not text:
            return None
        try:
            value = float(text.strip().split()[0])
            return max(0.0, min(5.0, value))
        except ValueError:
            return None
