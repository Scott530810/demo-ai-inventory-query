"""
資料庫操作模組
處理 PostgreSQL 連接、查詢執行和結果格式化
"""

import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from typing import List, Dict, Any, Optional
from decimal import Decimal
import json
import logging

from .config import DatabaseConfig
from .utils.logger import get_logger
from .rag.types import RagChunk


class DatabaseClient:
    """PostgreSQL 資料庫客戶端"""

    def __init__(self, config: DatabaseConfig):
        """
        初始化資料庫客戶端

        Args:
            config: 資料庫配置
        """
        self.config = config
        self.logger = get_logger(__name__)

    def execute_query(
        self,
        sql: str,
        params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        執行 SQL 查詢

        Args:
            sql: SQL 查詢語句
            params: 查詢參數（可選）

        Returns:
            查詢結果列表

        Raises:
            psycopg2.Error: 資料庫錯誤
        """
        conn = None
        cursor = None

        try:
            # 建立連接
            conn = psycopg2.connect(**self.config.to_dict())
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # 執行查詢
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            # 獲取結果
            results = cursor.fetchall()

            self.logger.info(f"查詢成功，返回 {len(results)} 筆結果")

            return [dict(row) for row in results]

        except psycopg2.Error as e:
            self.logger.error(f"資料庫錯誤: {str(e)}")
            raise

        finally:
            # 清理資源
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def test_connection(self) -> bool:
        """
        測試資料庫連接

        Returns:
            連接是否成功
        """
        try:
            conn = psycopg2.connect(**self.config.to_dict())
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            cursor.close()
            conn.close()
            self.logger.info("資料庫連接測試成功")
            return True
        except Exception as e:
            self.logger.error(f"資料庫連接測試失敗: {str(e)}")
            return False

    def close(self) -> None:
        """
        清理資源（目前為無狀態連線，保留介面相容）
        """
        return None

    def insert_rag_chunks(self, chunks: List[RagChunk]) -> None:
        """
        批次寫入 RAG 文件片段
        """
        if not chunks:
            return

        self.delete_rag_chunks_by_source({chunk.source for chunk in chunks})

        sql = """
        INSERT INTO rag_chunks (source, page, chunk_index, content, metadata, embedding)
        VALUES %s
        """

        values = []
        for chunk in chunks:
            embedding = None
            if chunk.embedding is not None:
                embedding = "[" + ",".join(f"{v:.6f}" for v in chunk.embedding) + "]"
            values.append(
                (
                    chunk.source,
                    chunk.page,
                    chunk.chunk_index,
                    chunk.content,
                    json.dumps(chunk.metadata, ensure_ascii=False),
                    embedding
                )
            )

        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(**self.config.to_dict())
            cursor = conn.cursor()
            execute_values(cursor, sql, values)
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"寫入 RAG 片段失敗: {str(e)}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def delete_rag_chunks_by_source(self, sources: set[str]) -> None:
        if not sources:
            return

        sql = "DELETE FROM rag_chunks WHERE source = ANY(%s);"
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(**self.config.to_dict())
            cursor = conn.cursor()
            cursor.execute(sql, (list(sources),))
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"清除 RAG 片段失敗: {str(e)}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_inventory_count(self) -> int:
        """
        獲取庫存商品總數

        Returns:
            商品總數
        """
        try:
            results = self.execute_query("SELECT COUNT(*) as count FROM inventory;")
            return results[0]['count'] if results else 0
        except Exception as e:
            self.logger.error(f"獲取庫存總數失敗: {str(e)}")
            return 0

    @staticmethod
    def format_results(results: List[Dict[str, Any]], limit: int = 20) -> List[Dict[str, Any]]:
        """
        格式化查詢結果
        - 限制結果數量
        - 轉換 Decimal 類型為 float

        Args:
            results: 原始查詢結果
            limit: 最大返回數量

        Returns:
            格式化後的結果
        """
        limited_results = results[:limit] if len(results) > limit else results

        formatted = []
        for row in limited_results:
            formatted_row = {}
            for key, value in row.items():
                # 轉換 Decimal 為 float
                if isinstance(value, Decimal):
                    formatted_row[key] = float(value)
                else:
                    formatted_row[key] = value
            formatted.append(formatted_row)

        return formatted
