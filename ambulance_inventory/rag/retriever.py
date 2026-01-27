"""
RAG 檢索器（改良版）
支援混合檢索：BM25 + 向量搜索 + 查詢偏好加權
"""

import requests
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from ..config import RagConfig
from ..database import DatabaseClient
from ..ollama_client import OllamaClient
from ..utils.logger import get_logger


# 查詢偏好加權（針對特定關鍵字提升相關性）
QUERY_PREFERENCES = {
    "規格": {"boost": 1.5, "keywords": ["SPEC", "規格", "參數"]},
    "承重": {"boost": 2.0, "keywords": ["Load Limit", "承重", "載重", "重量限制"]},
    "特色": {"boost": 1.3, "keywords": ["特色", "特點", "功能", "Features"]},
    "角度": {"boost": 1.4, "keywords": ["角度", "傾斜", "Angle", "Tilt"]},
    "型號": {"boost": 1.6, "keywords": ["Model", "型號"]},
    "品牌": {"boost": 1.3, "keywords": ["Ferno", "ZOLL", "Philips", "品牌"]},
}


@dataclass
class RetrievalResult:
    """檢索結果"""
    source: str
    page: Optional[int]
    chunk_index: int
    content: str
    score: float
    metadata: Dict[str, Any]


class RagRetriever:
    """RAG 檢索器"""

    def __init__(
        self,
        db_client: DatabaseClient,
        ollama_client: OllamaClient,
        config: RagConfig
    ):
        self.db_client = db_client
        self.ollama_client = ollama_client
        self.config = config
        self.logger = get_logger(__name__)
        self.embed_url = f"{ollama_client.config.host}/api/embeddings"

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        use_hybrid: bool = True
    ) -> List[RetrievalResult]:
        """
        檢索相關文件片段

        Args:
            query: 查詢文字
            top_k: 返回片段數量
            use_hybrid: 是否使用混合檢索（BM25 + 向量）

        Returns:
            相關片段列表
        """
        k = top_k or self.config.top_k

        if use_hybrid:
            return self._hybrid_search(query, k)
        else:
            query_embedding = self.get_embedding(query)
            if query_embedding is None:
                return self._bm25_search(query, k)
            return self._vector_search(query_embedding, k)

    def _hybrid_search(self, query: str, top_k: int) -> List[RetrievalResult]:
        """混合檢索：BM25 + 向量 + 查詢偏好"""
        try:
            # 生成查詢向量
            embedding = self.get_embedding(query)
            if not embedding:
                self.logger.warning("Failed to generate embedding, falling back to BM25")
                return self._bm25_search(query, top_k)

            # 檢測查詢偏好
            boost_factor = self._calculate_boost_factor(query)

            # 混合檢索 SQL（BM25 + 向量相似度）
            sql = """
            WITH vector_scores AS (
                SELECT
                    id, source, page, chunk_index, content, metadata,
                    1 - (embedding <=> %s::vector) AS vec_score
                FROM rag_chunks
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            ),
            bm25_scores AS (
                SELECT
                    id, source, page, chunk_index, content, metadata,
                    ts_rank(tsv, plainto_tsquery('simple', %s)) AS bm25_score
                FROM rag_chunks
                WHERE tsv @@ plainto_tsquery('simple', %s)
                ORDER BY bm25_score DESC
                LIMIT %s
            ),
            combined AS (
                SELECT
                    COALESCE(v.id, b.id) AS id,
                    COALESCE(v.source, b.source) AS source,
                    COALESCE(v.page, b.page) AS page,
                    COALESCE(v.chunk_index, b.chunk_index) AS chunk_index,
                    COALESCE(v.content, b.content) AS content,
                    COALESCE(v.metadata, b.metadata) AS metadata,
                    (COALESCE(v.vec_score, 0) * %s + COALESCE(b.bm25_score, 0) * %s) * %s AS final_score
                FROM vector_scores v
                FULL OUTER JOIN bm25_scores b ON v.id = b.id
            )
            SELECT source, page, chunk_index, content, metadata, final_score
            FROM combined
            ORDER BY final_score DESC
            LIMIT %s;
            """

            # 執行查詢
            vector_str = "[" + ",".join(str(x) for x in embedding) + "]"
            params = (
                vector_str, vector_str, top_k * 2,  # 向量查詢
                query, query, top_k * 2,            # BM25 查詢
                self.config.vector_weight,
                self.config.bm25_weight,
                boost_factor,
                top_k
            )

            rows = self.db_client.execute_query(sql, params)

            return [
                RetrievalResult(
                    source=row[0],
                    page=row[1],
                    chunk_index=row[2],
                    content=row[3],
                    score=float(row[5]),
                    metadata=row[4] or {}
                )
                for row in rows
            ]

        except Exception as e:
            self.logger.error(f"Hybrid search failed: {e}")
            return self._bm25_search(query, top_k)

    def _vector_search(self, query_embedding: List[float], top_k: int) -> List[RetrievalResult]:
        """純向量搜索"""
        try:
            embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

            sql = """
            SELECT source, page, chunk_index, content, metadata,
                   1 - (embedding <=> %s::vector) AS score
            FROM rag_chunks
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
            """

            rows = self.db_client.execute_query(sql, (embedding_str, embedding_str, top_k))

            return [
                RetrievalResult(
                    source=row[0],
                    page=row[1],
                    chunk_index=row[2],
                    content=row[3],
                    score=float(row[5]),
                    metadata=row[4] or {}
                )
                for row in rows
            ]

        except Exception as e:
            self.logger.error(f"Vector search failed: {e}")
            return []

    def _bm25_search(self, query: str, top_k: int) -> List[RetrievalResult]:
        """純 BM25 搜索"""
        try:
            sql = """
            SELECT source, page, chunk_index, content, metadata,
                   ts_rank(tsv, plainto_tsquery('simple', %s)) AS score
            FROM rag_chunks
            WHERE tsv @@ plainto_tsquery('simple', %s)
            ORDER BY score DESC
            LIMIT %s;
            """

            rows = self.db_client.execute_query(sql, (query, query, top_k))

            return [
                RetrievalResult(
                    source=row[0],
                    page=row[1],
                    chunk_index=row[2],
                    content=row[3],
                    score=float(row[5]),
                    metadata=row[4] or {}
                )
                for row in rows
            ]

        except Exception as e:
            self.logger.error(f"BM25 search failed: {e}")
            return []

    def _calculate_boost_factor(self, query: str) -> float:
        """計算查詢偏好加權因子"""
        max_boost = 1.0
        for pref_name, pref_config in QUERY_PREFERENCES.items():
            keywords = pref_config["keywords"]
            if any(kw in query for kw in keywords):
                max_boost = max(max_boost, pref_config["boost"])
        return max_boost

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """生成文字嵌入向量"""
        try:
            response = requests.post(
                self.embed_url,
                json={
                    "model": self.config.embedding_model,
                    "prompt": text
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result.get("embedding")
        except Exception as e:
            self.logger.error(f"Failed to generate embedding: {e}")
            return None

    def get_chunk_count(self) -> int:
        """取得片段總數"""
        try:
            results = self.db_client.execute_query("SELECT COUNT(*) as count FROM rag_chunks")
            return results[0]['count'] if results else 0
        except Exception as e:
            self.logger.error(f"Failed to get chunk count: {e}")
            return 0

    def get_sources(self) -> List[str]:
        """取得所有來源文件"""
        try:
            results = self.db_client.execute_query("SELECT DISTINCT source FROM rag_chunks ORDER BY source")
            return [row['source'] for row in results]
        except Exception as e:
            self.logger.error(f"Failed to get sources: {e}")
            return []
