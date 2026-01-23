# AGC AI 庫存查詢系統

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.3.0-brightgreen)](CHANGELOG.md)

基於自然語言的救護車設備庫存查詢系統，使用本地 Ollama 模型實現 SQL 生成和智能回答。

## 特色功能

- **自然語言查詢** - 使用中文提問，自動生成 SQL
- **Web UI** - 現代化網頁介面，支援模型與伺服器快速切換
- **動態模型選擇** - 支援切換任意 Ollama 模型
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
- 請問 AED 除顫器還有哪幾款有庫存？
- 預算 5 萬以內有什麼監視器可以買？
- 哪些商品庫存不足 10 件？

---

## 部署方式

### 本地部署 (Windows 11)

```powershell
# 1. 確保 Ollama 運行並下載模型
ollama pull llama3:70b

# 2. 啟動 Docker 服務
cd server
docker compose up -d

# 3. 開啟瀏覽器
start http://localhost:8000
```

### 遠端部署 (SPARK 伺服器)

```bash
# 在 SPARK 伺服器上
cd /opt
git clone https://github.com/Scott530810/demo-ai-inventory-query.git
cd demo-ai-inventory-query/server
docker compose up -d
```

在 Windows 筆電上：
1. 開啟瀏覽器 http://192.168.50.2:8000
2. 或使用 Web UI 的快速切換按鈕

---

## 模型切換

Web UI 支援動態切換 Ollama 模型：

1. 點擊狀態列的「切換」按鈕
2. 從下拉選單選擇模型
3. 系統會自動切換並同步顯示

**API 端點:**
```bash
# 取得可用模型
curl http://localhost:8000/api/models

# 切換模型
curl -X POST http://localhost:8000/api/models/select \
     -H "Content-Type: application/json" \
     -d '{"model": "llama3:8b"}'
```

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
- RAM: 16GB 以上
- GPU: NVIDIA GPU (建議 8GB+ VRAM，用於運行 Ollama)

**軟體:**
- Docker Desktop
- Ollama (需在主機上運行)

---

## 授權

MIT License

---

**版本**: 2.3.0 | **作者**: Scott
