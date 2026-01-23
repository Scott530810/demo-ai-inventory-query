# AGC AI 庫存查詢系統 - 架構文檔

## 系統概述

基於自然語言的資料庫查詢系統，使用者透過 Web UI 用中文提問，系統自動生成 SQL 並執行查詢。

### 技術棧

| 層級 | 技術 |
|------|------|
| 前端 | HTML/CSS/JavaScript (原生) |
| 後端 | FastAPI (Python 3.11) |
| LLM | Ollama (llama3:70b / qwen3 等) |
| 資料庫 | PostgreSQL 15 |
| 容器化 | Docker + Docker Compose |

---

## 系統架構

```
+------------------------------------------------------------------+
|                          Web Browser                             |
|  +------------------------------------------------------------+  |
|  |                    Web UI (index.html)                     |  |
|  +------------------------------------------------------------+  |
+-------------------------------+----------------------------------+
                                |
                                | HTTP (REST API)
                                v
+-------------------------------+----------------------------------+
|                        Docker Container                          |
|  +------------------------------------------------------------+  |
|  |               FastAPI Server (api_server.py)               |  |
|  |   /query, /health, /api/models, / (Web UI)                 |  |
|  +---------------+----------------------------+---------------+  |
|                  |                            |                  |
|    +-------------v-----------+    +-----------v-------------+    |
|    |      Query Engine       |    |     Ollama Client       |    |
|    |    (query_engine.py)    |    |   (ollama_client.py)    |    |
|    +-------------+-----------+    +-----------+-------------+    |
|                  |                            |                  |
|    +-------------v-----------+                |                  |
|    |    Database Client      |                |                  |
|    |      (database.py)      |                |                  |
|    +-------------+-----------+                |                  |
+------------------|----------------------------+------------------+
                   |                            |
      +------------v------------+    +----------v----------+
      |       PostgreSQL        |    |       Ollama        |
      |    (Docker Container)   |    |    (Host Machine)   |
      +-------------------------+    +---------------------+
```

**元件說明：**
- **Web UI**: 自然語言查詢輸入、模型切換、伺服器切換
- **FastAPI Server**: REST API 端點、靜態檔案服務
- **Query Engine**: SQL 生成、結果處理、回應生成
- **Ollama Client**: LLM API 調用、模型列表管理
- **Database Client**: PostgreSQL 連接、查詢執行

---

## 資料流

```
User Input --> POST /query --> Query Engine --> Ollama (SQL Gen)
                                    |
                                    v
                              SQL Validation
                                    |
                                    v
                              PostgreSQL Query
                                    |
                                    v
                              Ollama (Response Gen)
                                    |
                                    v
                              JSON Response --> Web UI
```

---

## 模組說明

### 核心模組 (`ambulance_inventory/`)

| 模組 | 功能 |
|------|------|
| `config.py` | 配置管理、提示詞定義、資料庫 Schema |
| `database.py` | PostgreSQL 連接與查詢執行 |
| `ollama_client.py` | Ollama API 封裝、模型管理 |
| `query_engine.py` | SQL 生成、結果處理、回應生成 |
| `utils/validators.py` | SQL 驗證、安全檢查 |
| `utils/logger.py` | 日誌系統 |

### API 服務 (`server/`)

| 檔案 | 功能 |
|------|------|
| `api_server.py` | FastAPI 應用、路由定義、CORS 設定 |
| `Dockerfile` | Docker 映像定義 |
| `docker-compose.yml` | 容器編排配置 |

### 前端 (`web/`)

| 檔案 | 功能 |
|------|------|
| `index.html` | 單頁應用、查詢介面、設定面板 |

---

## API 端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/` | GET | Web UI |
| `/health` | GET | 健康檢查（DB、Ollama 狀態） |
| `/query` | POST | 自然語言查詢 |
| `/tables` | GET | 資料表結構 |
| `/api/models` | GET | 可用模型列表 |
| `/api/models/select` | POST | 切換模型 |
| `/docs` | GET | Swagger API 文檔 |

---

## 部署架構

### 本地部署

```
Windows 11 / macOS / Linux
├── Docker Desktop
│   ├── ambulance-db (PostgreSQL)
│   └── ambulance-api (FastAPI)
└── Ollama (本機運行)
```

### 遠端部署 (SPARK)

```
SPARK Server (192.168.50.2)
├── Docker
│   ├── ambulance-db (PostgreSQL)
│   └── ambulance-api (FastAPI)
└── Ollama (本機運行)

Windows 11 Laptop
└── Web Browser → http://192.168.50.2:8000
```

---

## 安全考量

### 已實現
- SQL 驗證（只允許 SELECT）
- 危險操作檢測（DROP, DELETE, TRUNCATE）
- SQL 注入防護
- 非 root 用戶運行容器

### 建議加強
- HTTPS/SSL 加密
- API 金鑰認證
- IP 白名單
- 查詢頻率限制

---

## 效能參考

| 操作 | 預估時間 |
|------|----------|
| SQL 生成 (llama3:70b) | 3-8 秒 |
| 資料庫查詢 | < 1 秒 |
| 回應生成 | 3-8 秒 |
| 總計 | 7-17 秒 |

---

**版本**: 2.3.0 | **更新日期**: 2026-01-24
