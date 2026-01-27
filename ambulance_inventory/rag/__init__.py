"""
RAG (Retrieval Augmented Generation) 模組
提供文件檢索和向量搜尋功能
"""

from .retriever import RagRetriever, RetrievalResult
from .chunker import chunk_catalog_text, chunk_text
from .types import RagChunk

__all__ = ['RagRetriever', 'RetrievalResult', 'chunk_catalog_text', 'chunk_text', 'RagChunk']
