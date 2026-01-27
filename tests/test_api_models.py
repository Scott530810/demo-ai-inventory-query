"""
Unit tests for API models
測試 API 請求和回應模型
"""

import pytest
import sys
from pathlib import Path
from typing import List, Optional, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pydantic import BaseModel, Field, field_validator, ValidationError


# 定義測試用的模型 (與 api_server.py 相同的結構)
# 這樣可以避免匯入 psycopg2 依賴

class QueryRequest(BaseModel):
    """查詢請求模型"""
    question: str = Field(..., min_length=1, description="使用者的問題")
    model: Optional[str] = Field(None, description="指定使用的模型")
    use_llm_answer: bool = Field(True, description="是否使用 LLM 生成回答")
    rag_mode: Optional[str] = Field("sql_only", description="RAG 模式")
    rag_top_k: Optional[int] = Field(None, description="RAG 取用片段數量")

    @field_validator('question')
    @classmethod
    def question_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('問題不能為空')
        return v.strip()


class QueryResponse(BaseModel):
    """查詢回應模型"""
    question: str
    sql: str
    answer: str
    answer_formatted: Optional[str] = None
    answer_html: Optional[str] = None
    results: Optional[List[Any]] = None
    result_count: Optional[int] = None
    rag_context: Optional[List[Any]] = None
    rag_mode: Optional[str] = None
    model_used: Optional[str] = Field(None, description="實際使用的模型名稱")
    use_llm_answer: Optional[bool] = Field(None, description="是否使用 LLM 生成回答（實際執行的模式）")
    success: bool
    error: Optional[str] = None


class ModelsResponse(BaseModel):
    """模型列表回應"""
    models: List[str]
    current: str


class ModelSelectRequest(BaseModel):
    """模型選擇請求"""
    model: str


class TestQueryRequest:
    """測試 QueryRequest 模型"""

    def test_valid_request(self):
        """測試有效的請求"""
        request = QueryRequest(question="列出所有庫存")
        assert request.question == "列出所有庫存"
        assert request.model is None
        assert request.use_llm_answer is True
        assert request.rag_mode == "sql_only"

    def test_request_with_model(self):
        """測試帶模型的請求"""
        request = QueryRequest(
            question="列出所有庫存",
            model="qwen3:8b",
            use_llm_answer=False,
            rag_mode="hybrid",
            rag_top_k=5
        )
        assert request.question == "列出所有庫存"
        assert request.model == "qwen3:8b"
        assert request.use_llm_answer is False
        assert request.rag_mode == "hybrid"
        assert request.rag_top_k == 5

    def test_empty_question(self):
        """測試空問題"""
        with pytest.raises(ValidationError):
            QueryRequest(question="")

    def test_whitespace_only_question(self):
        """測試只有空白的問題"""
        with pytest.raises(ValidationError):
            QueryRequest(question="   ")

    def test_default_use_llm_answer(self):
        """測試 use_llm_answer 預設值"""
        request = QueryRequest(question="test")
        assert request.use_llm_answer is True

    def test_question_trimmed(self):
        """測試問題會被去除前後空白"""
        request = QueryRequest(question="  查詢庫存  ")
        assert request.question == "查詢庫存"


class TestQueryResponse:
    """測試 QueryResponse 模型"""

    def test_success_response(self):
        """測試成功回應"""
        response = QueryResponse(
            question="列出所有庫存",
            sql="SELECT * FROM inventory",
            answer="找到 10 筆結果",
            answer_formatted="| id | name |",
            answer_html="<table></table>",
            results=[{"id": 1, "name": "AED"}],
            result_count=1,
            rag_context=[{"content": "spec"}],
            rag_mode="hybrid",
            model_used="qwen3:8b",
            use_llm_answer=True,
            success=True,
            error=None
        )
        assert response.success is True
        assert response.model_used == "qwen3:8b"
        assert response.use_llm_answer is True
        assert response.result_count == 1
        assert response.rag_mode == "hybrid"

    def test_error_response(self):
        """測試錯誤回應"""
        response = QueryResponse(
            question="test",
            sql="",
            answer="",
            success=False,
            error="Ollama not available"
        )
        assert response.success is False
        assert response.error == "Ollama not available"

    def test_fast_mode_response(self):
        """測試快速模式回應"""
        response = QueryResponse(
            question="test",
            sql="SELECT * FROM inventory",
            answer="",
            answer_formatted="| id | name |",
            result_count=5,
            model_used="qwen3:8b",
            use_llm_answer=False,
            success=True
        )
        assert response.use_llm_answer is False
        assert response.answer == ""
        assert response.answer_formatted is not None

    def test_model_used_field(self):
        """測試 model_used 欄位"""
        response = QueryResponse(
            question="test",
            sql="SELECT 1",
            answer="ok",
            model_used="llama3:70b",
            success=True
        )
        assert response.model_used == "llama3:70b"

    def test_use_llm_answer_field(self):
        """測試 use_llm_answer 欄位"""
        # LLM mode
        response_llm = QueryResponse(
            question="test",
            sql="SELECT 1",
            answer="ok",
            use_llm_answer=True,
            success=True
        )
        assert response_llm.use_llm_answer is True

        # Fast mode
        response_fast = QueryResponse(
            question="test",
            sql="SELECT 1",
            answer="",
            use_llm_answer=False,
            success=True
        )
        assert response_fast.use_llm_answer is False

    def test_optional_fields_default_none(self):
        """測試可選欄位預設為 None"""
        response = QueryResponse(
            question="test",
            sql="SELECT 1",
            answer="ok",
            success=True
        )
        assert response.answer_formatted is None
        assert response.answer_html is None
        assert response.results is None
        assert response.result_count is None
        assert response.rag_context is None
        assert response.rag_mode is None
        assert response.model_used is None
        assert response.use_llm_answer is None
        assert response.error is None


class TestModelsResponse:
    """測試 ModelsResponse 模型"""

    def test_models_response(self):
        """測試模型列表回應"""
        response = ModelsResponse(
            models=["qwen3:8b", "qwen3:70b", "llama3:8b"],
            current="qwen3:8b"
        )
        assert len(response.models) == 3
        assert response.current == "qwen3:8b"
        assert "qwen3:70b" in response.models

    def test_empty_models_list(self):
        """測試空模型列表"""
        response = ModelsResponse(
            models=[],
            current=""
        )
        assert len(response.models) == 0


class TestModelSelectRequest:
    """測試 ModelSelectRequest 模型"""

    def test_model_select_request(self):
        """測試模型選擇請求"""
        request = ModelSelectRequest(model="qwen3:70b")
        assert request.model == "qwen3:70b"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
