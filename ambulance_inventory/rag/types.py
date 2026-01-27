"""RAG data types."""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class RagChunk:
    source: str
    page: Optional[int]
    chunk_index: int
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[list] = None


@dataclass
class RagResult:
    id: int
    source: str
    page: Optional[int]
    chunk_index: int
    content: str
    metadata: Dict[str, Any]
    score: float
