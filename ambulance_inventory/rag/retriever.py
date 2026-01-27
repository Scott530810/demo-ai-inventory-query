"""
RAG 檢索器模組
實現向量搜尋和 BM25 混合檢索
"""

import json
import requests
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import numpy as np

from ..config import RagConfig
from ..database import DatabaseClient
from ..ollama_client import OllamaClient
from ..utils.logger import get_logger


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
        """
        初始化 RAG 檢索器

        Args:
            db_client: 資料庫客戶端
            ollama_client: Ollama 客戶端
            config: RAG 配置
        """
        self.db_client = db_client
        self.ollama_client = ollama_client
        self.config = config
        self.logger = get_logger(__name__)

        # Ollama embedding API
        self.embed_url = f"{ollama_client.config.host}/api/embeddings"

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        使用 Ollama 生成文本嵌入向量

        Args:
            text: 輸入文本

        Returns:
            嵌入向量列表，失敗時返回 None
        """
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
            return result.get('embedding')
        except Exception as e:
            self.logger.error(f"生成嵌入向量失敗: {e}")
            return None

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None
    ) -> List[RetrievalResult]:
        """
        檢索相關文件片段

        Args:
            query: 查詢文本
            top_k: 返回的結果數量

        Returns:
            檢索結果列表
        """
        k = top_k or self.config.top_k

        # 生成查詢向量
        query_embedding = self.get_embedding(query)

        if query_embedding is None:
            self.logger.warning("無法生成查詢向量，回退到關鍵字搜尋")
            return self._keyword_search(query, k)

        # 向量搜尋
        return self._vector_search(query_embedding, k)

    def _vector_search(
        self,
        query_embedding: List[float],
        top_k: int
    ) -> List[RetrievalResult]:
        """
        向量相似度搜尋

        Args:
            query_embedding: 查詢向量
            top_k: 返回數量

        Returns:
            檢索結果列表
        """
        try:
            # 將向量轉為 PostgreSQL 格式
            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'

            sql = """
            SELECT
                source,
                page,
                chunk_index,
                content,
                metadata,
                1 - (embedding <=> %s::vector) AS score
            FROM document_chunks
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """

            results = self.db_client.execute_query(
                sql,
                (embedding_str, embedding_str, top_k)
            )

            return [
                RetrievalResult(
                    source=row['source'],
                    page=row['page'],
                    chunk_index=row['chunk_index'],
                    content=row['content'],
                    score=float(row['score']) if row['score'] else 0.0,
                    metadata=row['metadata'] if row['metadata'] else {}
                )
                for row in results
            ]

        except Exception as e:
            self.logger.error(f"向量搜尋失敗: {e}")
            return []

    def _keyword_search(
        self,
        query: str,
        top_k: int
    ) -> List[RetrievalResult]:
        """
        關鍵字搜尋（回退方案）

        Args:
            query: 查詢文本
            top_k: 返回數量

        Returns:
            檢索結果列表
        """
        try:
            # 使用 PostgreSQL 全文搜索
            sql = """
            SELECT
                source,
                page,
                chunk_index,
                content,
                metadata,
                ts_rank(to_tsvector('simple', content), plainto_tsquery('simple', %s)) AS score
            FROM document_chunks
            WHERE to_tsvector('simple', content) @@ plainto_tsquery('simple', %s)
            ORDER BY score DESC
            LIMIT %s
            """

            results = self.db_client.execute_query(sql, (query, query, top_k))

            return [
                RetrievalResult(
                    source=row['source'],
                    page=row['page'],
                    chunk_index=row['chunk_index'],
                    content=row['content'],
                    score=float(row['score']) if row['score'] else 0.0,
                    metadata=row['metadata'] if row['metadata'] else {}
                )
                for row in results
            ]

        except Exception as e:
            self.logger.error(f"關鍵字搜尋失敗: {e}")
            return []

    def get_chunk_count(self) -> int:
        """
        獲取已索引的文件片段數量

        Returns:
            片段數量
        """
        try:
            results = self.db_client.execute_query(
                "SELECT COUNT(*) as count FROM document_chunks"
            )
            return results[0]['count'] if results else 0
        except Exception as e:
            self.logger.error(f"獲取片段數量失敗: {e}")
            return 0

    def get_sources(self) -> List[str]:
        """
        獲取所有已索引的文件來源

        Returns:
            文件來源列表
        """
        try:
            results = self.db_client.execute_query(
                "SELECT DISTINCT source FROM document_chunks ORDER BY source"
            )
            return [row['source'] for row in results]
        except Exception as e:
            self.logger.error(f"獲取文件來源失敗: {e}")
            return []
