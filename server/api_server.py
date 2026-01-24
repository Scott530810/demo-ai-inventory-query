"""
FastAPI Server for Remote Ambulance Inventory Queries
可從遠端 Windows 11 筆電連線查詢的 API 服務器

運行方式:
    uvicorn server.api_server:app --host 0.0.0.0 --port 8000

遠端訪問:
    http://SPARK_IP:8000/docs
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ambulance_inventory.config import DatabaseConfig, OllamaConfig
from ambulance_inventory.database import DatabaseClient
from ambulance_inventory.ollama_client import OllamaClient
from ambulance_inventory.query_engine import QueryEngine
from ambulance_inventory.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Ambulance Inventory Query API",
    description="自然語言查詢救護車設備庫存系統 - 遠端 API 版本",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for remote access from Windows 11
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Windows 11 IP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for web UI
web_dir = Path(__file__).parent.parent / "web"
if web_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")

# Global clients (initialized on startup)
db_client: Optional[DatabaseClient] = None
ollama_client: Optional[OllamaClient] = None
query_engine: Optional[QueryEngine] = None


# Pydantic models
class QueryRequest(BaseModel):
    """查詢請求"""
    question: str = Field(..., description="自然語言問題", min_length=1)
    model: Optional[str] = Field(None, description="使用的模型（可選，不指定則使用當前模型）")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "請列出所有有庫存的AED除顫器，包含品牌、型號和庫存數量",
                "model": "llama3:70b"
            }
        }


class ModelsResponse(BaseModel):
    """模型列表回應"""
    models: List[str] = Field(..., description="可用模型列表")
    current: str = Field(..., description="當前使用的模型")


class ModelSelectRequest(BaseModel):
    """模型選擇請求"""
    model: str = Field(..., description="要使用的模型名稱")


class QueryResponse(BaseModel):
    """查詢回應"""
    question: str = Field(..., description="原始問題")
    sql: str = Field(..., description="生成的 SQL 查詢")
    answer: str = Field(..., description="AI 回答")
    success: bool = Field(..., description="查詢是否成功")
    error: Optional[str] = Field(None, description="錯誤訊息（如果有）")


class HealthResponse(BaseModel):
    """健康檢查回應"""
    status: str
    database: bool
    ollama: bool
    model: str
    version: str


class TableInfo(BaseModel):
    """資料表資訊"""
    table_name: str
    columns: List[Dict[str, str]]


@app.on_event("startup")
async def startup_event():
    """服務器啟動時初始化"""
    global db_client, ollama_client, query_engine

    try:
        logger.info("🚀 Initializing API server...")

        # Initialize database client
        db_config = DatabaseConfig.from_env()
        db_client = DatabaseClient(db_config)
        logger.info("✅ Database client initialized")

        # Initialize Ollama client
        ollama_config = OllamaConfig.from_env()
        ollama_client = OllamaClient(ollama_config)
        logger.info(f"✅ Ollama client initialized (model: {ollama_config.model})")

        # Initialize query engine
        query_engine = QueryEngine(db_client, ollama_client)
        logger.info("✅ Query engine initialized")

        logger.info("🎉 API server ready for remote connections!")

    except Exception as e:
        logger.error(f"❌ Failed to initialize server: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """服務器關閉時清理"""
    global db_client

    if db_client:
        db_client.close()
        logger.info("Database connection closed")


@app.get("/", tags=["General"])
async def root():
    """根端點 - 重定向到 Web UI"""
    return RedirectResponse(url="/web")


@app.get("/web", tags=["General"])
async def web_ui():
    """Web UI 介面"""
    web_file = Path(__file__).parent.parent / "web" / "index.html"
    if web_file.exists():
        return FileResponse(str(web_file), media_type="text/html")
    return {"error": "Web UI not found", "path": str(web_file)}


@app.get("/api", tags=["General"])
async def api_info():
    """API 資訊"""
    model_name = ollama_client.config.model if ollama_client else "unknown"
    return {
        "message": "Ambulance Inventory Query API",
        "version": "2.1.0",
        "model": model_name,
        "docs": "/docs",
        "health": "/health",
        "web_ui": "/web"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """
    健康檢查端點

    檢查資料庫和 Ollama 連接狀態
    """
    try:
        # Check database
        db_ok = db_client.test_connection() if db_client else False

        # Check Ollama
        ollama_ok = ollama_client.test_connection() if ollama_client else False

        model_name = ollama_client.config.model if ollama_client else "unknown"

        status = "healthy" if (db_ok and ollama_ok) else "unhealthy"

        return HealthResponse(
            status=status,
            database=db_ok,
            ollama=ollama_ok,
            model=model_name,
            version="2.1.0"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


@app.post("/query", response_model=QueryResponse, tags=["Query"])
async def query(request: QueryRequest):
    """
    執行自然語言查詢

    接收自然語言問題，生成 SQL，執行查詢，返回回答

    Args:
        request: 包含問題的查詢請求，可選指定模型

    Returns:
        QueryResponse: 包含 SQL、答案等資訊
    """
    if not query_engine:
        raise HTTPException(status_code=503, detail="Query engine not initialized")

    # Check Ollama connection first
    if ollama_client and not ollama_client.test_connection():
        return QueryResponse(
            question=request.question,
            sql="",
            answer="",
            success=False,
            error="Ollama service is not available. Please ensure Ollama is running on the server."
        )

    try:
        # Temporarily switch model if specified
        original_model = None
        if request.model and ollama_client:
            available_models = ollama_client.get_available_models()
            if request.model in available_models:
                original_model = ollama_client.config.model
                ollama_client.config.model = request.model
                logger.info(f"📝 Using model: {request.model}")

        logger.info(f"📝 Received query: {request.question}")

        # Execute query
        sql, answer = query_engine.query(request.question)

        # Restore original model if it was changed
        if original_model:
            ollama_client.config.model = original_model

        # Handle None values (Ollama might have failed silently)
        if sql is None or answer is None:
            return QueryResponse(
                question=request.question,
                sql=sql or "",
                answer=answer or "",
                success=False,
                error="Query failed - Ollama may not be responding. Check if Ollama service is running."
            )

        logger.info(f"✅ Query successful")

        return QueryResponse(
            question=request.question,
            sql=sql,
            answer=answer,
            success=True,
            error=None
        )

    except Exception as e:
        # Restore original model on error
        if original_model and ollama_client:
            ollama_client.config.model = original_model
        logger.error(f"❌ Query failed: {e}")
        return QueryResponse(
            question=request.question,
            sql="",
            answer="",
            success=False,
            error=str(e)
        )


@app.get("/tables", response_model=List[TableInfo], tags=["Database"])
async def get_tables():
    """
    取得資料表結構資訊

    Returns:
        List[TableInfo]: 所有資料表及其欄位資訊
    """
    if not db_client:
        raise HTTPException(status_code=503, detail="Database client not initialized")

    try:
        tables_info = []

        # Get table schema
        schema_query = """
        SELECT
            table_name,
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
        """

        rows = db_client.execute_query(schema_query)

        # Group by table
        from collections import defaultdict
        tables_dict = defaultdict(list)

        for row in rows:
            tables_dict[row[0]].append({
                "column_name": row[1],
                "data_type": row[2],
                "nullable": row[3]
            })

        # Convert to TableInfo list
        for table_name, columns in tables_dict.items():
            tables_info.append(TableInfo(
                table_name=table_name,
                columns=columns
            ))

        return tables_info

    except Exception as e:
        logger.error(f"Failed to get tables: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tables: {str(e)}")


@app.get("/demo-queries", tags=["Query"])
async def get_demo_queries():
    """
    取得 Demo 查詢範例

    Returns:
        List[str]: Demo 查詢列表
    """
    demo_queries = [
        "請列出所有有庫存的AED除顫器，包含品牌、型號和庫存數量",
        "請列出所有擔架設備的品牌、型號和庫存數量",
        "請列出單價低於50000元的監視器，包含品牌、型號和價格",
        "請列出庫存數量低於10件的商品，包含產品名稱、分類和庫存數量",
        "請列出所有Philips品牌的產品，包含名稱、型號和單價",
    ]

    return {
        "demo_queries": demo_queries,
        "usage": "使用 POST /query 端點執行這些查詢"
    }


@app.get("/api/models", response_model=ModelsResponse, tags=["Models"])
async def get_available_models():
    """
    取得可用的 Ollama 模型列表

    Returns:
        ModelsResponse: 可用模型列表和當前使用的模型
    """
    if not ollama_client:
        raise HTTPException(status_code=503, detail="Ollama client not initialized")

    try:
        models = ollama_client.get_available_models()
        current = ollama_client.config.model

        return ModelsResponse(
            models=models,
            current=current
        )
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")


@app.post("/api/models/select", tags=["Models"])
async def select_model(request: ModelSelectRequest):
    """
    切換使用的 Ollama 模型

    Args:
        request: 包含模型名稱的請求

    Returns:
        切換結果
    """
    global ollama_client, query_engine

    if not ollama_client:
        raise HTTPException(status_code=503, detail="Ollama client not initialized")

    try:
        # Check if model is available
        available_models = ollama_client.get_available_models()

        if request.model not in available_models:
            raise HTTPException(
                status_code=400,
                detail=f"Model '{request.model}' not found. Available: {available_models}"
            )

        # Update model in config
        old_model = ollama_client.config.model
        ollama_client.config.model = request.model

        # Recreate query engine with new model
        query_engine = QueryEngine(db_client, ollama_client)

        logger.info(f"🔄 Model switched from {old_model} to {request.model}")

        return {
            "success": True,
            "message": f"Model switched to {request.model}",
            "previous": old_model,
            "current": request.model
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to switch model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to switch model: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting API Server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")

    uvicorn.run(
        app,
        host="0.0.0.0",  # Listen on all interfaces for remote access
        port=8000,
        log_level="info"
    )
