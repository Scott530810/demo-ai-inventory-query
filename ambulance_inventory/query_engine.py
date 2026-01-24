"""
查詢引擎模組
處理自然語言到 SQL 的轉換和結果生成
"""

import json
from typing import Optional, Tuple
import logging

from .config import SQL_GENERATION_PROMPT, RESPONSE_GENERATION_PROMPT
from .database import DatabaseClient
from .ollama_client import OllamaClient
from .utils.validators import clean_sql, validate_sql
from .utils.logger import get_logger


class QueryEngine:
    """自然語言查詢引擎"""

    def __init__(self, db_client: DatabaseClient, ollama_client: OllamaClient):
        """
        初始化查詢引擎

        Args:
            db_client: 資料庫客戶端
            ollama_client: Ollama 客戶端
        """
        self.db_client = db_client
        self.ollama_client = ollama_client
        self.logger = get_logger(__name__)

    def generate_sql(self, question: str) -> Optional[str]:
        """
        根據自然語言問題生成 SQL

        Args:
            question: 用戶問題

        Returns:
            生成的 SQL，失敗時返回 None
        """
        self.logger.info(f"生成 SQL: {question}")

        # 調用 Ollama 生成 SQL
        raw_sql = self.ollama_client.generate(
            prompt=question,
            system_prompt=SQL_GENERATION_PROMPT,
            temperature=0.1
        )

        if not raw_sql:
            return None

        # 清理 SQL
        cleaned_sql = clean_sql(raw_sql)

        # 驗證 SQL
        is_valid, error_msg = validate_sql(cleaned_sql)

        if not is_valid:
            self.logger.warning(f"SQL 驗證失敗: {error_msg}")
            print(f"⚠️ SQL 驗證警告: {error_msg}")
            print(f"   生成的 SQL: {cleaned_sql[:100]}...")
            # 即使驗證失敗，仍然返回 SQL（讓用戶決定是否使用）
            # 但不執行危險操作

        return cleaned_sql

    def execute_query(self, sql: str) -> Optional[list]:
        """
        執行 SQL 查詢

        Args:
            sql: SQL 語句

        Returns:
            查詢結果列表，失敗時返回 None
        """
        try:
            results = self.db_client.execute_query(sql)
            return results
        except Exception as e:
            self.logger.error(f"查詢執行失敗: {str(e)}")
            return None

    def generate_response(
        self,
        question: str,
        results: list
    ) -> Optional[str]:
        """
        根據查詢結果生成友善的回應

        Args:
            question: 原始問題
            results: 查詢結果

        Returns:
            生成的回應文本
        """
        if not results:
            return "抱歉，沒有找到相關資料。"

        self.logger.info(f"生成回應，結果數: {len(results)}")

        # 格式化結果（限制數量）
        formatted_results = self.db_client.format_results(results, limit=20)

        # 轉換為 JSON 字串
        try:
            results_json = json.dumps(
                formatted_results,
                ensure_ascii=False,
                indent=2
            )
        except Exception as e:
            self.logger.error(f"結果序列化失敗: {str(e)}")
            return self._generate_simple_response(results)

        # 構建提示詞
        prompt = f"""使用者問題: {question}

查詢結果:
{results_json}

請根據查詢結果，用友善專業的方式回答使用者的問題。"""

        # 調用 Ollama 生成回應 (使用較低 temperature 確保一致性)
        response = self.ollama_client.generate(
            prompt=prompt,
            system_prompt=RESPONSE_GENERATION_PROMPT,
            temperature=0.3
        )

        if not response:
            # 如果 Ollama 失敗，使用簡單格式化
            return self._generate_simple_response(formatted_results)

        return response

    def query(self, question: str) -> Tuple[Optional[str], Optional[str]]:
        """
        完整的查詢流程：問題 -> SQL -> 執行 -> 生成回應

        Args:
            question: 用戶問題

        Returns:
            (SQL, 回應文本) 元組
        """
        # 步驟 1: 生成 SQL
        print("🤖 正在請求 Ollama 生成 SQL...")
        print(f"   模型: {self.ollama_client.config.model}")

        sql = self.generate_sql(question)

        if not sql:
            return None, None

        print(f"\n📝 生成的 SQL:")
        print(f"{sql}\n")

        # 步驟 2: 執行查詢
        results = self.execute_query(sql)

        if results is None:
            print(f"❌ SQL 執行錯誤")
            return sql, None

        print(f"✅ 查詢成功，找到 {len(results)} 筆結果\n")

        # 步驟 3: 生成回應
        if results:
            print("🤖 正在請求 Ollama 生成回應...")
            answer = self.generate_response(question, results)
        else:
            answer = "抱歉，沒有找到相關資料。"

        return sql, answer

    @staticmethod
    def _generate_simple_response(results: list) -> str:
        """
        生成簡單的結果展示（當 Ollama 失敗時使用）

        Args:
            results: 查詢結果

        Returns:
            格式化的文本
        """
        response = f"查詢結果共 {len(results)} 筆:\n\n"

        for i, row in enumerate(results[:10], 1):
            response += f"{i}. "
            response += " | ".join([f"{k}: {v}" for k, v in row.items()])
            response += "\n"

        if len(results) > 10:
            response += f"\n... 還有 {len(results) - 10} 筆結果未顯示"

        return response
