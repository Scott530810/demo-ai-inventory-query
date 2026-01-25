"""
Unit tests for QueryEngine
測試查詢引擎功能（使用 Mock）
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Check if psycopg2 is available
try:
    import psycopg2
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

# Conditionally import QueryEngine
if HAS_PSYCOPG2:
    from ambulance_inventory.query_engine import QueryEngine
    from ambulance_inventory.config import OllamaConfig


# Skip all tests in this module if psycopg2 is not available
pytestmark = pytest.mark.skipif(
    not HAS_PSYCOPG2,
    reason="psycopg2 not installed (required for QueryEngine import)"
)


class TestQueryEngineModelParameter:
    """測試 QueryEngine 的模型參數傳遞"""

    def setup_method(self):
        """設置測試環境"""
        # Create mock database client
        self.mock_db_client = Mock()
        self.mock_db_client.execute_query = Mock(return_value=[
            {"id": 1, "name": "AED", "stock_quantity": 10}
        ])
        self.mock_db_client.format_results = Mock(return_value=[
            {"id": 1, "name": "AED", "stock_quantity": 10}
        ])

        # Create mock ollama client
        self.mock_ollama_client = Mock()
        self.mock_ollama_client.config = Mock()
        self.mock_ollama_client.config.model = "default_model"

    def test_generate_sql_passes_model(self):
        """測試 generate_sql 傳遞模型參數"""
        self.mock_ollama_client.generate = Mock(return_value="SELECT * FROM inventory")

        engine = QueryEngine(self.mock_db_client, self.mock_ollama_client)
        engine.generate_sql("列出庫存", model="qwen3:8b")

        # Verify generate was called with the model parameter
        self.mock_ollama_client.generate.assert_called_once()
        call_kwargs = self.mock_ollama_client.generate.call_args[1]
        assert call_kwargs.get('model') == "qwen3:8b"

    def test_generate_sql_uses_default_model_when_none(self):
        """測試未指定模型時使用預設模型"""
        self.mock_ollama_client.generate = Mock(return_value="SELECT * FROM inventory")

        engine = QueryEngine(self.mock_db_client, self.mock_ollama_client)
        engine.generate_sql("列出庫存", model=None)

        # Verify generate was called with model=None (will use default)
        call_kwargs = self.mock_ollama_client.generate.call_args[1]
        assert call_kwargs.get('model') is None

    def test_generate_response_passes_model(self):
        """測試 generate_response 傳遞模型參數"""
        self.mock_ollama_client.generate = Mock(return_value="找到 1 筆結果")

        engine = QueryEngine(self.mock_db_client, self.mock_ollama_client)
        results = [{"id": 1, "name": "AED"}]
        engine.generate_response("列出庫存", results, model="qwen3:70b")

        call_kwargs = self.mock_ollama_client.generate.call_args[1]
        assert call_kwargs.get('model') == "qwen3:70b"

    def test_query_with_mode_passes_model(self):
        """測試 query_with_mode 傳遞模型參數"""
        self.mock_ollama_client.generate = Mock(
            side_effect=["SELECT * FROM inventory", "找到結果"]
        )

        engine = QueryEngine(self.mock_db_client, self.mock_ollama_client)
        sql, llm_answer, _, _, _, timing = engine.query_with_mode(
            "列出庫存",
            use_llm_answer=True,
            model="llama3:70b"
        )

        # Both calls should use the specified model
        calls = self.mock_ollama_client.generate.call_args_list
        assert len(calls) == 2
        assert calls[0][1].get('model') == "llama3:70b"
        assert calls[1][1].get('model') == "llama3:70b"

        # Verify timing dictionary is returned
        assert isinstance(timing, dict)
        assert 'sql_generation' in timing
        assert 'query_execution' in timing

    def test_query_with_mode_fast_mode(self):
        """測試快速模式不調用 LLM 生成回應"""
        self.mock_ollama_client.generate = Mock(return_value="SELECT * FROM inventory")

        engine = QueryEngine(self.mock_db_client, self.mock_ollama_client)
        sql, llm_answer, formatted, html, results, timing = engine.query_with_mode(
            "列出庫存",
            use_llm_answer=False,
            model="qwen3:8b"
        )

        # Only one call for SQL generation (no LLM response generation)
        assert self.mock_ollama_client.generate.call_count == 1
        assert llm_answer is None
        assert formatted is not None
        assert html is not None

        # Verify timing dictionary (no llm_response in fast mode)
        assert isinstance(timing, dict)
        assert 'sql_generation' in timing
        assert 'query_execution' in timing
        assert 'formatting' in timing
        assert 'llm_response' not in timing


class TestQueryEngineFormatting:
    """測試 QueryEngine 的格式化功能"""

    def test_format_results_programmatic(self):
        """測試程式化格式化結果"""
        results = [
            {"id": 1, "name": "AED", "stock": 10},
            {"id": 2, "name": "擔架", "stock": 5}
        ]

        formatted = QueryEngine.format_results_programmatic(results)

        assert "id" in formatted
        assert "name" in formatted
        assert "AED" in formatted
        assert "擔架" in formatted
        assert "共 2 筆結果" in formatted

    def test_format_results_programmatic_empty(self):
        """測試空結果的程式化格式化"""
        formatted = QueryEngine.format_results_programmatic([])
        assert "查無資料" in formatted

    def test_format_results_html_table(self):
        """測試 HTML 表格格式化"""
        results = [
            {"id": 1, "name": "AED", "stock": 10}
        ]

        html = QueryEngine.format_results_html_table(results)

        assert "<table" in html
        assert "<th>id</th>" in html
        assert "<th>name</th>" in html
        assert "<td>AED</td>" in html
        assert "共 1 筆結果" in html

    def test_format_results_html_table_empty(self):
        """測試空結果的 HTML 格式化"""
        html = QueryEngine.format_results_html_table([])
        assert "查無資料" in html

    def test_get_display_width_ascii(self):
        """測試 ASCII 字元寬度計算"""
        width = QueryEngine._get_display_width("hello")
        assert width == 5

    def test_get_display_width_chinese(self):
        """測試中文字元寬度計算"""
        width = QueryEngine._get_display_width("你好")
        assert width == 4  # 2 characters * 2 width each

    def test_get_display_width_mixed(self):
        """測試混合字元寬度計算"""
        width = QueryEngine._get_display_width("Hello世界")
        assert width == 5 + 4  # 5 ASCII + 2 Chinese chars * 2

    def test_pad_to_width(self):
        """測試填充到指定寬度"""
        padded = QueryEngine._pad_to_width("test", 10)
        assert len(padded) == 10
        assert padded == "test      "

    def test_pad_to_width_chinese(self):
        """測試中文填充"""
        padded = QueryEngine._pad_to_width("中文", 10)
        # "中文" takes 4 display width, so 6 spaces should be added
        assert QueryEngine._get_display_width(padded) == 10


class TestQueryEngineConcurrency:
    """測試 QueryEngine 並發安全性"""

    def test_model_parameter_isolation(self):
        """測試模型參數隔離（每次調用獨立）"""
        mock_db = Mock()
        mock_db.execute_query = Mock(return_value=[{"id": 1}])
        mock_db.format_results = Mock(return_value=[{"id": 1}])

        mock_ollama = Mock()
        mock_ollama.config = Mock()
        mock_ollama.config.model = "default"
        mock_ollama.generate = Mock(return_value="SELECT 1 FROM inventory")

        engine = QueryEngine(mock_db, mock_ollama)

        # Simulate concurrent requests with different models
        engine.generate_sql("query1", model="model_a")
        engine.generate_sql("query2", model="model_b")

        # Each call should use its own model
        calls = mock_ollama.generate.call_args_list
        assert calls[0][1]['model'] == "model_a"
        assert calls[1][1]['model'] == "model_b"

        # Default model should not be modified
        assert mock_ollama.config.model == "default"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
