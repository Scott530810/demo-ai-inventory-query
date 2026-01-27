"""RAG 相關類型定義"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class RagChunk:
    """RAG 文件片段"""
    id: int
    source: str
    page: Optional[int]
    chunk_index: int
    content: str
    score: float
    metadata: Dict[str, Any]

    @classmethod
    def from_db_row(cls, row: tuple, score: float = 0.0) -> 'RagChunk':
        """從資料庫行創建"""
        return cls(
            id=row[0],
            source=row[1],
            page=row[2],
            chunk_index=row[3],
            content=row[4],
            score=score,
            metadata=row[5] if len(row) > 5 else {}
        )
