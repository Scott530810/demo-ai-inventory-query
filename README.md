# Ambulance Inventory Query System

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.1.0-brightgreen)](docs/CHANGELOG.md)

基於自然語言的救護車設備庫存查詢系統，使用本地 Ollama 模型實現 SQL 生成和智能回答。

## 特色功能

- **自然語言查詢** - 使用中文提問，自動生成 SQL
- **動態模型選擇** - 支援切換任意 Ollama 模型
- **模組化架構** - 11 個獨立模組，易於維護
- **Docker 支援** - 一鍵部署
- **遠端 API** - FastAPI 服務器，支援遠端連線
- **安全驗證** - SQL 注入防護和危險操作檢測

## 快速演示

```bash
python run_refactored.py --interactive

# 提問範例
請輸入您的問題: 請問AED除顫器還有哪幾款有庫存？

# AI 會自動生成 SQL、執行查詢、返回結果
```

---

## 兩種部署方式

### 方式 1: Windows 11 本地部署

適用於在本地 Windows 11 電腦上運行 Ollama。

```powershell
# 1. 確保 Ollama 運行並下載模型
ollama pull llama3:70b

# 2. 設定 Ollama 允許外部訪問
[Environment]::SetEnvironmentVariable("OLLAMA_HOST", "0.0.0.0", "User")
# 重啟 Ollama

# 3. 啟動系統
.\run-ollama.ps1
```

**詳見:** [docs/WIN11_LOCAL.md](docs/WIN11_LOCAL.md)

### 方式 2: DGX SPARK 遠端部署

適用於從 Windows 11 筆電連線到遠端 SPARK 服務器。

```bash
# 在 SPARK 服務器上
cd /opt
git clone https://github.com/Scott530810/demo-ai-inventory-query.git
cd demo-ai-inventory-query
docker compose -f server/docker-compose.spark.yml up -d
```

```powershell
# 在 Windows 11 筆電上
.\client\connect_to_spark.ps1 -SparkIP YOUR_SPARK_IP
```

**詳見:** [docs/SPARK_DEPLOYMENT.md](docs/SPARK_DEPLOYMENT.md)

---

## 模型選擇

系統支援動態切換 Ollama 上任何可用的模型：

**互動模式:**
```
請輸入您的問題: models
當前模型: llama3:70b
可用模型:
  1. llama3:70b <-- 當前
  2. llama3:8b
  3. qwen2.5:32b
請選擇模型編號: 2
已切換模型: llama3:70b -> llama3:8b
```

**API 端點:**
```bash
# 取得可用模型
curl http://localhost:8000/api/models

# 切換模型
curl -X POST http://localhost:8000/api/models/select \
     -H "Content-Type: application/json" \
     -d '{"model": "llama3:8b"}'

# 單次查詢使用指定模型
curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"question": "AED有庫存嗎?", "model": "llama3:8b"}'
```

---

## 文檔

| 文檔 | 說明 |
|------|------|
| [docs/WIN11_LOCAL.md](docs/WIN11_LOCAL.md) | Windows 11 本地部署指南 |
| [docs/SPARK_DEPLOYMENT.md](docs/SPARK_DEPLOYMENT.md) | DGX SPARK 遠端部署指南 |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 系統架構設計 |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | 版本更新記錄 |

---

## 專案結構

```
demo-ai-inventory-query/
├── ambulance_inventory/        # 核心模組
│   ├── config.py              # 配置管理
│   ├── database.py            # PostgreSQL 操作
│   ├── ollama_client.py       # Ollama API
│   ├── query_engine.py        # 查詢引擎
│   └── ui/                    # 使用者介面
├── server/                     # SPARK 部署
│   ├── api_server.py          # FastAPI 服務器
│   └── docker-compose.spark.yml
├── client/                     # Windows 11 客戶端
│   ├── connect_to_spark.ps1
│   └── spark_client.py
├── docs/                       # 文檔
├── docker-compose.ollama.yml   # 本地 Docker 配置
├── run-ollama.ps1              # PowerShell 啟動腳本
└── run_refactored.py           # Python 入口
```

---

## 系統需求

**硬體:**
- CPU: 4 核心以上
- RAM: 16GB 以上
- GPU: NVIDIA GPU (建議 8GB+ VRAM)

**軟體:**
- Python 3.11+
- PostgreSQL 15+
- Ollama
- Docker (選用)

---

## 授權

MIT License - 詳見 [LICENSE](LICENSE)

---

**版本**: 2.1.0 | **日期**: 2026-01-18 | **模型**: llama3:70b (可切換)
