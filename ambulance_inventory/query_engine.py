"""
查詢引擎模組
處理自然語言到 SQL 的轉換和結果生成
"""

import json
import time
from typing import Optional, Tuple, Dict
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

    def generate_sql(self, question: str, model: Optional[str] = None) -> Optional[str]:
        """
        根據自然語言問題生成 SQL

        Args:
            question: 用戶問題
            model: 使用的模型（可選）

        Returns:
            生成的 SQL，失敗時返回 None
        """
        self.logger.info(f"生成 SQL: {question} (model: {model or self.ollama_client.config.model})")

        # 調用 Ollama 生成 SQL
        raw_sql = self.ollama_client.generate(
            prompt=question,
            system_prompt=SQL_GENERATION_PROMPT,
            temperature=0.1,
            model=model
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
            # 仍回傳 SQL 供使用者檢視，但後續查詢會拒絕執行

        return cleaned_sql

    def execute_query(self, sql: str) -> Optional[list]:
        """
        執行 SQL 查詢

        Args:
            sql: SQL 語句

        Returns:
            查詢結果列表，失敗時返回 None
        """
        is_valid, error_msg = validate_sql(sql)
        if not is_valid:
            self.logger.error(f"拒絕執行無效 SQL: {error_msg}")
            return None

        try:
            results = self.db_client.execute_query(sql)
            return results
        except Exception as e:
            self.logger.error(f"查詢執行失敗: {str(e)}")
            return None

    def generate_response(
        self,
        question: str,
        results: list,
        model: Optional[str] = None
    ) -> Optional[str]:
        """
        根據查詢結果生成友善的回應

        Args:
            question: 原始問題
            results: 查詢結果
            model: 使用的模型（可選）

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
            temperature=0.1,
            model=model
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

    @staticmethod
    def _get_display_width(text: str) -> int:
        """
        計算字串的顯示寬度（考慮中文字佔 2 個字元寬度）

        Args:
            text: 要計算的字串

        Returns:
            顯示寬度
        """
        import unicodedata
        width = 0
        for char in text:
            # East Asian Width: F(Fullwidth), W(Wide) 佔 2 個字元
            # A(Ambiguous) 在等寬字體中通常也佔 2 個字元
            ea_width = unicodedata.east_asian_width(char)
            if ea_width in ('F', 'W', 'A'):
                width += 2
            else:
                width += 1
        return width

    @staticmethod
    def _pad_to_width(text: str, target_width: int) -> str:
        """
        將字串填充到指定的顯示寬度

        Args:
            text: 原始字串
            target_width: 目標寬度

        Returns:
            填充後的字串
        """
        current_width = QueryEngine._get_display_width(text)
        if current_width >= target_width:
            # 需要截斷
            result = ""
            width = 0
            for char in text:
                import unicodedata
                ea_width = unicodedata.east_asian_width(char)
                char_width = 2 if ea_width in ('F', 'W', 'A') else 1
                if width + char_width > target_width:
                    break
                result += char
                width += char_width
            # 補齊剩餘空格
            result += " " * (target_width - width)
            return result
        else:
            # 需要填充空格
            return text + " " * (target_width - current_width)

    @staticmethod
    def format_results_programmatic(results: list, max_rows: int = 50) -> str:
        """
        程式化格式化查詢結果（不使用 LLM，快速且一致）
        返回純文字表格格式

        Args:
            results: 查詢結果
            max_rows: 最大顯示行數

        Returns:
            格式化的表格文本
        """
        if not results:
            return "查無資料"

        total = len(results)
        display_results = results[:max_rows]

        # 取得欄位名稱
        if isinstance(display_results[0], dict):
            columns = list(display_results[0].keys())
        else:
            columns = [f"欄位{i+1}" for i in range(len(display_results[0]))]

        # 計算每欄寬度（使用顯示寬度）
        col_widths = []
        for col in columns:
            max_width = QueryEngine._get_display_width(str(col))
            for row in display_results:
                if isinstance(row, dict):
                    val = str(row.get(col, ""))
                else:
                    val = str(row[columns.index(col)])
                max_width = max(max_width, QueryEngine._get_display_width(val))
            col_widths.append(min(max_width, 30))  # 限制最大寬度

        # 建立表格
        lines = []

        # 標題行
        header_parts = []
        for i, col in enumerate(columns):
            header_parts.append(QueryEngine._pad_to_width(str(col), col_widths[i]))
        header = " | ".join(header_parts)
        lines.append(header)

        # 分隔線（計算實際顯示寬度）
        separator_width = sum(col_widths) + (len(columns) - 1) * 3  # " | " 佔 3 字元
        lines.append("-" * separator_width)

        # 資料行
        for row in display_results:
            if isinstance(row, dict):
                values = [str(row.get(col, "")) for col in columns]
            else:
                values = [str(v) for v in row]

            row_parts = []
            for i, val in enumerate(values):
                row_parts.append(QueryEngine._pad_to_width(val, col_widths[i]))
            lines.append(" | ".join(row_parts))

        # 統計資訊
        lines.append("-" * separator_width)
        lines.append(f"共 {total} 筆結果")
        if total > max_rows:
            lines.append(f"(僅顯示前 {max_rows} 筆)")

        return "\n".join(lines)

    @staticmethod
    def format_results_html_table(results: list, max_rows: int = 50) -> str:
        """
        程式化格式化查詢結果為 HTML 表格（字體無關，完美對齊）

        Args:
            results: 查詢結果
            max_rows: 最大顯示行數

        Returns:
            HTML 表格字串
        """
        if not results:
            return "<p>查無資料</p>"

        total = len(results)
        display_results = results[:max_rows]

        # 取得欄位名稱
        if isinstance(display_results[0], dict):
            columns = list(display_results[0].keys())
        else:
            columns = [f"欄位{i+1}" for i in range(len(display_results[0]))]

        # 建立 HTML 表格
        html = ['<table class="result-table">']

        # 標題行
        html.append('<thead><tr>')
        for col in columns:
            html.append(f'<th>{col}</th>')
        html.append('</tr></thead>')

        # 資料行
        html.append('<tbody>')
        for row in display_results:
            html.append('<tr>')
            if isinstance(row, dict):
                for col in columns:
                    val = str(row.get(col, ""))
                    html.append(f'<td>{val}</td>')
            else:
                for val in row:
                    html.append(f'<td>{val}</td>')
            html.append('</tr>')
        html.append('</tbody>')

        html.append('</table>')

        # 統計資訊
        html.append(f'<p class="table-info">共 {total} 筆結果')
        if total > max_rows:
            html.append(f' (僅顯示前 {max_rows} 筆)')
        html.append('</p>')

        return '\n'.join(html)

    def query_with_mode(
        self,
        question: str,
        use_llm_answer: bool = True,
        model: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[list], Dict[str, float]]:
        """
        支援雙模式的查詢流程

        Args:
            question: 用戶問題
            use_llm_answer: 是否使用 LLM 生成回答
            model: 使用的模型（可選，不指定則使用預設模型）

        Returns:
            (SQL, LLM回答, 程式化回答, HTML表格, 原始結果, 計時資訊) 元組
        """
        # 計時資訊
        timing: Dict[str, float] = {}

        # 使用傳入的模型，若無則使用預設模型
        use_model = model if model else self.ollama_client.config.model

        # 步驟 1: 生成 SQL
        print("🤖 正在請求 Ollama 生成 SQL...")
        print(f"   模型: {use_model}")

        t0 = time.time()
        sql = self.generate_sql(question, model=use_model)
        timing['sql_generation'] = round(time.time() - t0, 2)

        if not sql:
            return None, None, None, None, None, timing

        print(f"\n📝 生成的 SQL:")
        print(f"{sql}\n")

        # 步驟 2: 執行查詢
        t0 = time.time()
        results = self.execute_query(sql)
        timing['query_execution'] = round(time.time() - t0, 2)

        if results is None:
            print(f"❌ SQL 執行錯誤")
            return sql, None, None, None, None, timing

        print(f"✅ 查詢成功，找到 {len(results)} 筆結果\n")

        # 步驟 3: 格式化結果
        t0 = time.time()
        formatted_results = self.db_client.format_results(results, limit=50)

        # 程式化格式（總是生成，快速）
        programmatic_answer = self.format_results_programmatic(formatted_results)

        # HTML 表格格式（總是生成，完美對齊）
        html_table = self.format_results_html_table(formatted_results)
        timing['formatting'] = round(time.time() - t0, 2)

        # LLM 回答（可選）
        llm_answer = None
        if use_llm_answer and results:
            print("🤖 正在請求 Ollama 生成回應...")
            t0 = time.time()
            llm_answer = self.generate_response(question, results, model=use_model)
            timing['llm_response'] = round(time.time() - t0, 2)
        elif not results:
            llm_answer = "抱歉，沒有找到相關資料。"

        return sql, llm_answer, programmatic_answer, html_table, formatted_results, timing
