# 更新日誌

## [2.4.0] - 2026-01-25

### 效能優化與使用體驗改進

---

### 新增功能

#### 查詢時間追蹤
- 顯示各階段耗時分解（SQL 生成、查詢執行、格式化、LLM 回答）
- Web UI 新增時間明細顯示區塊
- API 回應新增 `elapsed_time` 欄位，包含詳細時間資訊

#### 模型選擇器優化
- 僅顯示推薦模型（80b⭐最準確、30b⚡平衡、8b🚀極速）
- 模型標籤直觀顯示效能特性
- 過濾非推薦模型，減少使用者選擇困難

### 改進

#### 效能調整
- 預設模型改為 `qwen3-next:80b-a3b-instruct-q4_K_M`（載入後推理最快）
- Ollama 超時時間增至 180 秒（應對大模型載入）
- 建議設定 `OLLAMA_MAX_LOADED_MODELS=3` 保持多模型常駐

#### 單元測試
- 更新 `query_with_mode` 測試以支援新的時間回傳值
- 新增時間字典驗證測試

### Ollama 建議設定

```bash
# /etc/systemd/system/ollama.service.d/override.conf
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
Environment="OLLAMA_MAX_LOADED_MODELS=3"
Environment="OLLAMA_NUM_PARALLEL=4"
Environment="OLLAMA_KEEP_ALIVE=10m"
```

### 效能測試結果（模型已載入）

| 模型 | 推理時間 |
|------|---------|
| 80b  | ~3.6s   |
| 30b  | ~31s    |
| 8b   | ~21s    |

---

## [2.3.0] - 2026-01-24

### 重大更新：Web 版本整合

簡化專案架構，移除命令行介面，專注於 Web 版本

---

### 新增功能

#### Web UI 增強
- Web UI 模型切換功能（下拉選單）
- 伺服器快速切換按鈕（本地 / SPARK）
- 自訂伺服器位址設定

#### API 端點
- `/api/models` - 取得可用模型列表
- `/api/models/select` - 切換使用的模型

### 改進

#### 專案結構簡化
- 移除 `client/` 目錄（命令行客戶端）
- 移除 `ambulance_inventory/ui/` 目錄（Tkinter GUI）
- 移除 `ambulance_inventory/main.py`
- 移除舊的啟動腳本和測試檔案
- 統一使用 `docker-compose.yml` 和 `Dockerfile`

#### LLM 回應優化
- 修改提示詞，防止 LLM 添加「補充建議」等額外內容
- 回應更簡潔、專注於查詢結果

### 檔案變更

#### 重新命名
- `docker-compose.spark.yml` → `docker-compose.yml`
- `Dockerfile.spark` → `Dockerfile`

#### 刪除的檔案
- `client/` 目錄
- `ambulance_inventory/ui/` 目錄
- `ambulance_inventory/main.py`
- `run_refactored.py`
- `run-ollama.ps1`
- `test_llm_query_ollama.py`
- `docker-compose.ollama.yml`
- `Dockerfile.ollama`

---

## [2.2.0] - 2026-01-20

### 新增功能
- Web UI 模型選擇器
- 動態載入 Ollama 可用模型
- 模型切換 API

---

## [2.1.0] - 2026-01-17

### 新增功能

#### FastAPI 遠端服務器
- RESTful API 端點：`/query`, `/health`, `/tables`
- Swagger UI 文檔 (`/docs`)
- CORS 支援

#### Docker 部署
- PostgreSQL + API Server 容器化
- Docker Compose 配置

#### Windows 11 客戶端
- PowerShell 客戶端
- Python 客戶端
- SSH 隧道支援

---

## [2.0.0] - 2026-01-14

### 重大更新：代碼重構

將單一檔案重構為模組化架構

#### 模組化架構
- `ambulance_inventory` 套件
- 配置、資料庫、Ollama、查詢引擎模組分離
- 工具函數模組（logger, validators）

#### 安全性增強
- SQL 驗證器（只允許 SELECT）
- 危險操作檢測
- SQL 注入防護

#### Docker 支援
- Dockerfile
- docker-compose.yml
- .dockerignore

---

## 專案結構 (v2.3.0)

```
demo-ai-inventory-query/
├── ambulance_inventory/        # 核心模組
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── ollama_client.py
│   ├── query_engine.py
│   └── utils/
├── server/                     # API 服務
│   ├── api_server.py
│   ├── Dockerfile
│   └── docker-compose.yml
├── web/                        # Web 前端
│   └── index.html
├── ambulance_inventory_demo.sql
└── requirements.txt
```

---

**版本**: 2.4.0 | **作者**: Scott
