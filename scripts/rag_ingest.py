#!/usr/bin/env python3
"""
RAG 文件匯入腳本
將 PDF/DOC 文件切割並存入向量資料庫

使用方式:
    python scripts/rag_ingest.py docs/catalogs
    python scripts/rag_ingest.py docs/catalogs/specific_file.pdf
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from typing import List, Optional, Generator

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ambulance_inventory.config import DatabaseConfig, OllamaConfig, RagConfig
from ambulance_inventory.database import DatabaseClient
from ambulance_inventory.utils.logger import get_logger

logger = get_logger(__name__)


def extract_text_from_pdf(file_path: Path) -> Generator[tuple, None, None]:
    """
    從 PDF 提取文字

    Args:
        file_path: PDF 檔案路徑

    Yields:
        (page_number, text) 元組
    """
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                yield i + 1, text.strip()
    except Exception as e:
        logger.error(f"PDF 解析失敗 {file_path}: {e}")


def extract_text_from_doc(file_path: Path) -> Generator[tuple, None, None]:
    """
    從 DOC/DOCX 提取文字

    Args:
        file_path: DOC 檔案路徑

    Yields:
        (page_number, text) 元組
    """
    suffix = file_path.suffix.lower()

    if suffix == '.docx':
        try:
            from docx import Document
            doc = Document(file_path)
            full_text = '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
            if full_text:
                yield None, full_text
        except Exception as e:
            logger.error(f"DOCX 解析失敗 {file_path}: {e}")

    elif suffix == '.doc':
        # 使用 antiword 處理舊版 .doc
        try:
            import subprocess
            result = subprocess.run(
                ['antiword', str(file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                yield None, result.stdout.strip()
            else:
                logger.error(f"antiword 處理失敗 {file_path}: {result.stderr}")
        except FileNotFoundError:
            logger.error("antiword 未安裝，無法處理 .doc 檔案")
        except Exception as e:
            logger.error(f"DOC 解析失敗 {file_path}: {e}")


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[str]:
    """
    將文字切割成片段

    Args:
        text: 原始文字
        chunk_size: 片段大小（字元數）
        chunk_overlap: 重疊大小

    Returns:
        片段列表
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # 嘗試在句號或換行處斷開
        if end < len(text):
            # 找最近的斷點
            for sep in ['\n\n', '\n', '。', '.', '，', ',', ' ']:
                pos = text.rfind(sep, start + chunk_size // 2, end + 50)
                if pos > start:
                    end = pos + len(sep)
                    break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - chunk_overlap

    return chunks


def get_embedding(
    text: str,
    ollama_host: str,
    model: str
) -> Optional[List[float]]:
    """
    使用 Ollama 生成嵌入向量

    Args:
        text: 輸入文字
        ollama_host: Ollama 主機
        model: 嵌入模型

    Returns:
        嵌入向量
    """
    try:
        response = requests.post(
            f"{ollama_host}/api/embeddings",
            json={"model": model, "prompt": text},
            timeout=30
        )
        response.raise_for_status()
        return response.json().get('embedding')
    except Exception as e:
        logger.error(f"生成嵌入失敗: {e}")
        return None


def ingest_file(
    file_path: Path,
    db_client: DatabaseClient,
    ollama_host: str,
    rag_config: RagConfig
) -> int:
    """
    匯入單一檔案

    Args:
        file_path: 檔案路徑
        db_client: 資料庫客戶端
        ollama_host: Ollama 主機
        rag_config: RAG 配置

    Returns:
        匯入的片段數量
    """
    suffix = file_path.suffix.lower()
    source = file_path.name

    logger.info(f"處理檔案: {source}")

    # 先清除該檔案的舊資料
    try:
        db_client.execute_query(
            "DELETE FROM document_chunks WHERE source = %s",
            (source,)
        )
    except Exception as e:
        logger.warning(f"清除舊資料失敗（可能是首次匯入）: {e}")

    # 提取文字
    if suffix == '.pdf':
        text_generator = extract_text_from_pdf(file_path)
    elif suffix in ('.doc', '.docx'):
        text_generator = extract_text_from_doc(file_path)
    else:
        logger.warning(f"不支援的檔案類型: {suffix}")
        return 0

    chunk_count = 0
    chunk_index = 0

    for page, text in text_generator:
        # 切割文字
        chunks = chunk_text(
            text,
            rag_config.chunk_size,
            rag_config.chunk_overlap
        )

        for chunk in chunks:
            # 生成嵌入向量
            embedding = get_embedding(
                chunk,
                ollama_host,
                rag_config.embedding_model
            )

            if embedding is None:
                logger.warning(f"跳過片段 {chunk_index}（無法生成嵌入）")
                chunk_index += 1
                continue

            # 儲存到資料庫
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'

            try:
                import psycopg2
                conn = psycopg2.connect(**db_client.config.to_dict())
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO document_chunks
                    (source, page, chunk_index, content, embedding, metadata)
                    VALUES (%s, %s, %s, %s, %s::vector, %s)
                    """,
                    (
                        source,
                        page,
                        chunk_index,
                        chunk,
                        embedding_str,
                        json.dumps({"file_path": str(file_path)})
                    )
                )
                conn.commit()
                cursor.close()
                conn.close()

                chunk_count += 1
                chunk_index += 1

                if chunk_count % 10 == 0:
                    print(f"  已處理 {chunk_count} 個片段...")

            except Exception as e:
                logger.error(f"儲存片段失敗: {e}")

    return chunk_count


def main():
    parser = argparse.ArgumentParser(
        description='RAG 文件匯入工具'
    )
    parser.add_argument(
        'path',
        type=str,
        help='檔案或目錄路徑'
    )
    parser.add_argument(
        '--ollama-host',
        type=str,
        default=os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
        help='Ollama 主機地址'
    )

    args = parser.parse_args()
    path = Path(args.path)

    if not path.exists():
        print(f"錯誤: 路徑不存在: {path}")
        sys.exit(1)

    # 載入配置
    db_config = DatabaseConfig.from_env()
    rag_config = RagConfig.from_env()

    # 建立資料庫連線
    db_client = DatabaseClient(db_config)

    if not db_client.test_connection():
        print("錯誤: 無法連線到資料庫")
        sys.exit(1)

    print(f"RAG 文件匯入工具")
    print(f"================")
    print(f"嵌入模型: {rag_config.embedding_model}")
    print(f"片段大小: {rag_config.chunk_size}")
    print(f"重疊大小: {rag_config.chunk_overlap}")
    print()

    # 收集要處理的檔案
    files: List[Path] = []

    if path.is_file():
        files.append(path)
    elif path.is_dir():
        for ext in ['*.pdf', '*.doc', '*.docx']:
            files.extend(path.glob(ext))

    if not files:
        print(f"警告: 沒有找到可處理的檔案")
        sys.exit(0)

    print(f"找到 {len(files)} 個檔案:")
    for f in files:
        print(f"  - {f.name}")
    print()

    # 處理每個檔案
    total_chunks = 0
    for file_path in files:
        count = ingest_file(
            file_path,
            db_client,
            args.ollama_host,
            rag_config
        )
        total_chunks += count
        print(f"✅ {file_path.name}: {count} 個片段")

    print()
    print(f"================")
    print(f"匯入完成！總共 {total_chunks} 個片段")


if __name__ == '__main__':
    main()
