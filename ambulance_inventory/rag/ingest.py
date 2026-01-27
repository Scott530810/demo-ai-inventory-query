"""
RAG 文件匯入模組
支援 PDF/DOC 文件的切分與向量化
"""

import subprocess
from pathlib import Path
from typing import List, Optional
import pypdf
import docx

from ..config import RagConfig
from ..database import DatabaseClient
from ..ollama_client import OllamaClient
from .chunker import chunk_catalog_text, chunk_text
from ..utils.logger import get_logger


logger = get_logger(__name__)


class RagIngestor:
    """RAG 文件匯入器"""

    def __init__(
        self,
        db_client: DatabaseClient,
        ollama_client: OllamaClient,
        config: RagConfig
    ):
        self.db_client = db_client
        self.ollama_client = ollama_client
        self.config = config

    def ingest_dir(self, directory: str) -> int:
        """
        匯入目錄中的所有文件

        Args:
            directory: 目錄路徑

        Returns:
            成功匯入的片段數
        """
        total_chunks = 0
        dir_path = Path(directory)

        # 支援的文件類型
        supported_exts = {'.pdf', '.doc', '.docx'}
        files = [f for f in dir_path.glob('*') if f.suffix.lower() in supported_exts]

        logger.info(f"找到 {len(files)} 個檔案:")
        for f in files:
            logger.info(f"  - {f.name}")

        for file_path in files:
            try:
                count = self.ingest_file(file_path)
                total_chunks += count
                logger.info(f"✅ {file_path.name}: {count} 個片段")
            except Exception as e:
                logger.error(f"❌ {file_path.name}: {e}")

        return total_chunks

    def ingest_file(self, file_path: Path) -> int:
        """
        匯入單個文件

        Args:
            file_path: 文件路徑

        Returns:
            成功匯入的片段數
        """
        file_path = Path(file_path)
        source_name = file_path.name
        suffix = file_path.suffix.lower()

        # 清除舊資料
        self._clear_source(source_name)

        # 提取文字
        if suffix == '.pdf':
            text = self._extract_pdf(file_path)
        elif suffix in ['.doc', '.docx']:
            text = self._extract_doc(file_path)
        else:
            logger.warning(f"不支援的文件類型: {suffix}")
            return 0

        if not text:
            logger.warning(f"無法提取文字: {file_path}")
            return 0

        # 切分文字
        chunks = chunk_catalog_text(
            text,
            max_chars=self.config.chunk_size,
            overlap=self.config.chunk_overlap
        )

        if not chunks:
            logger.warning(f"切分後無片段: {file_path}")
            return 0

        # 生成嵌入並儲存
        saved_count = 0
        for i, chunk_text in enumerate(chunks):
            try:
                # 生成嵌入向量
                embedding = self._get_embedding(chunk_text)
                if not embedding:
                    logger.warning(f"無法生成嵌入向量: chunk {i}")
                    continue

                # 儲存到資料庫
                self._save_chunk(
                    source=source_name,
                    page=None,  # PDF page extraction not implemented
                    chunk_index=i,
                    content=chunk_text,
                    embedding=embedding,
                    metadata={}
                )
                saved_count += 1

            except Exception as e:
                logger.error(f"儲存片段失敗 (chunk {i}): {e}")

        return saved_count

    def _extract_pdf(self, file_path: Path) -> str:
        """提取 PDF 文字"""
        try:
            with open(file_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                text_parts = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"PDF 提取失敗: {e}")
            return ""

    def _extract_doc(self, file_path: Path) -> str:
        """提取 DOC/DOCX 文字"""
        suffix = file_path.suffix.lower()

        # DOCX
        if suffix == '.docx':
            try:
                doc = docx.Document(file_path)
                return "\n\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            except Exception as e:
                logger.error(f"DOCX 提取失敗: {e}")
                return ""

        # DOC (需要 antiword)
        elif suffix == '.doc':
            try:
                result = subprocess.run(
                    ['antiword', str(file_path)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    return result.stdout
                else:
                    logger.warning(f"antiword 失敗: {result.stderr}")
                    return ""
            except FileNotFoundError:
                logger.warning("antiword 未安裝，無法處理 .doc 檔案")
                return ""
            except Exception as e:
                logger.error(f"DOC 提取失敗: {e}")
                return ""

        return ""

    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """生成嵌入向量"""
        try:
            import requests
            embed_url = f"{self.ollama_client.config.host}/api/embeddings"
            response = requests.post(
                embed_url,
                json={
                    "model": self.config.embedding_model,
                    "prompt": text
                },
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result.get("embedding")
        except Exception as e:
            logger.error(f"生成嵌入向量失敗: {e}")
            return None

    def _clear_source(self, source: str):
        """清除指定來源的舊資料"""
        try:
            sql = "DELETE FROM rag_chunks WHERE source = %s"
            self.db_client.execute_command(sql, (source,))
            logger.info(f"已清除舊資料: {source}")
        except Exception as e:
            logger.warning(f"清除舊資料失敗（可能是首次匯入）: {e}")

    def _save_chunk(
        self,
        source: str,
        page: Optional[int],
        chunk_index: int,
        content: str,
        embedding: List[float],
        metadata: dict
    ):
        """儲存文件片段"""
        try:
            # 將向量轉為 PostgreSQL 格式
            embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"

            sql = """
            INSERT INTO rag_chunks (source, page, chunk_index, content, metadata, embedding)
            VALUES (%s, %s, %s, %s, %s, %s::vector)
            """

            import json
            self.db_client.execute_command(
                sql,
                (source, page, chunk_index, content, json.dumps(metadata), embedding_str)
            )

        except Exception as e:
            logger.error(f"儲存片段失敗: {e}")
            raise
