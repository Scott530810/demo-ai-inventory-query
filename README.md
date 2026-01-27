# AGC AI 庫存查詢系統

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.4.0-brightgreen)](CHANGELOG.md)

基於自然語言的救護車設備庫存查詢系統，使用本地 Ollama 模型實現 SQL 生成和智能回答。

## 特色功能

- **自然語言查詢** - 使用中文提問，自動生成 SQL
- **Web UI** - 現代化網頁介面，支援模型與伺服器快速切換
- **查詢時間追蹤** - 顯示各階段耗時（SQL 生成、查詢、格式化、LLM 回答）
- **智慧模型選擇** - 推薦模型標籤（⭐最準確 / ⚡平衡 / 🚀極速）
- **Docker 部署** - 一鍵啟動 PostgreSQL + API Server
- **跨伺服器支援** - 可切換本地或遠端 SPARK 伺服器

## 快速開始

### 1. 啟動 Docker 服務

```powershell
cd server
docker compose up -d
```

### 2. 開啟 Web UI

瀏覽器開啟: http://localhost:8000

### 3. 開始查詢

在 Web 介面輸入問題，例如：
- 請列出所有有庫存的 AED 除顫器，包含品牌、型號和庫存數量
- 請列出單價低於 50000 元的監視器，包含品牌、型號和價格
- 請列出庫存數量低於 10 件的商品，包含產品名稱和分類

---

## 部署方式

### 本地部署 (Windows 11)

適用硬體：RTX 5070 8GB+ VRAM / RYZEN AI 7+ / 32GB+ RAM

```powershell
# 1. 確保 Ollama 運行並下載模型
ollama pull qwen3:30b
ollama pull qwen3:8b
ollama pull qwen3:4b

# 2. 啟動 Docker 服務
cd server
docker compose up -d

# 3. 開啟瀏覽器
start http://localhost:8000
```

### SPARK 伺服器部署 (128GB 統一記憶體)

適用於大記憶體伺服器，可運行 80b 模型

```bash
# 1. 設定 Ollama（參考系統需求章節的 Ollama 建議設定）
sudo systemctl edit ollama

# 2. 下載推薦模型
ollama pull qwen3-next:80b-a3b-instruct-q4_K_M
ollama pull qwen3:30b
ollama pull qwen3:8b

# 3. 部署應用
cd ~/demo-ai-inventory-query/server
docker compose up -d
```

### 從 Windows 連接 SPARK 伺服器

1. 開啟瀏覽器 http://192.168.50.2:8000
2. 或使用 Web UI 的伺服器切換按鈕

---

## 模型選擇

Web UI 顯示推薦模型，並標註效能特性：

| 模型 | 標籤 | 推理時間* | 說明 |
|------|------|----------|------|
| qwen3-next:80b | ⭐ 最準確 | ~3.6s | 預設模型，準確度最高 |
| qwen3:30b | ⚡ 平衡 | ~31s | 中等速度與準確度 |
| qwen3:8b | 🚀 極速 | ~21s | 快速回應，適合簡單查詢 |

*模型已載入記憶體時的推理時間

**切換方式:**
1. 點擊狀態列的「切換」按鈕
2. 從下拉選單選擇模型
3. 系統會自動切換

**API 端點:**
```bash
# 取得可用模型
curl http://localhost:8000/api/models

# 查詢（指定模型）
curl http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"question": "列出所有品牌", "model": "qwen3:8b"}'
```

---

## RAG 型錄查詢（混合檢索）

可將型錄資料寫入 RAG 索引，支援「SQL 庫存 + 型錄內容」混合回答。

### 1) 放置型錄
將 PDF/DOC 放入 `docs/catalogs/`。

### 2) 建立索引
```bash
python scripts/rag_ingest.py docs/catalogs
```

### 3) 查詢時啟用 RAG
```bash
curl http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"question": "Ferno 24-7 規格與庫存", "rag_mode": "hybrid", "rag_top_k": 8}'
```

### RAG 相關環境變數
- `RAG_EMBEDDING_MODEL`（預設：qwen3-embedding:8b）
- `RAG_RERANK_MODEL`（預設空字串，不啟用 rerank）
- `RAG_EMBEDDING_DIM`（預設：1536，需與資料表一致）
- `RAG_CHUNK_SIZE` / `RAG_CHUNK_OVERLAP`
- `RAG_BM25_K` / `RAG_VECTOR_K` / `RAG_RERANK_K` / `RAG_TOP_K`

---

## 專案結構

```
demo-ai-inventory-query/
├── ambulance_inventory/        # 核心模組
│   ├── __init__.py            # 版本資訊
│   ├── config.py              # 配置與提示詞
│   ├── database.py            # PostgreSQL 操作
│   ├── ollama_client.py       # Ollama API 客戶端
│   ├── query_engine.py        # 查詢引擎
│   └── utils/                 # 工具函數
├── server/                     # API 服務
│   ├── api_server.py          # FastAPI 服務器
│   ├── Dockerfile             # Docker 映像
│   └── docker-compose.yml     # Docker Compose
├── web/                        # Web 前端
│   └── index.html             # Web UI
├── ambulance_inventory_demo.sql # 資料庫初始化
└── requirements.txt           # Python 依賴
```

---

## 系統需求

**硬體:**
- CPU: 4 核心以上
- RAM: 64GB 以上（同時載入多模型需 128GB）
- GPU: NVIDIA GPU 或 Apple Silicon（建議 48GB+ 統一記憶體）

**軟體:**
- Docker Desktop
- Ollama (需在主機上運行)

**Ollama 建議設定:**
```bash
# 編輯 systemd 設定
sudo systemctl edit ollama

# 加入以下內容
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
Environment="OLLAMA_MAX_LOADED_MODELS=3"
Environment="OLLAMA_NUM_PARALLEL=4"
Environment="OLLAMA_KEEP_ALIVE=10m"
```

---

## 授權

MIT License

---

**版本**: 2.4.0 | **作者**: Scott
