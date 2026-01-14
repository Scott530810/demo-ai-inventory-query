# 🚑 Ambulance Inventory Query System

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-brightgreen)](CHANGELOG.md)

一個基於自然語言的救護車設備庫存查詢系統，使用本地 Ollama (qwen3:30b) 模型實現 SQL 生成和智能回答。

## ✨ 特色功能

- 🤖 **自然語言查詢** - 使用中文提問，自動生成 SQL
- 🔒 **安全驗證** - SQL 注入防護和危險操作檢測
- 📦 **模組化架構** - 11 個獨立模組，易於維護和擴展
- 🐳 **Docker 支援** - 一鍵部署，包含完整環境
- 📝 **完整類型提示** - IDE 自動補全支援
- 📊 **日誌系統** - 結構化日誌記錄
- 🔄 **向後兼容** - 保留舊版本代碼

## 🎬 快速演示

```bash
# 互動模式
python run_refactored.py --interactive

# 提問範例
💭 請問AED除顫器還有哪幾款有庫存？

# AI 會自動：
# 1. 生成 SQL 查詢
# 2. 執行查詢
# 3. 用友善的方式回答
```

## 🚀 快速開始

### 前置需求

- Python 3.11+
- PostgreSQL 15+
- Ollama (運行中)
- qwen3:30b 模型

### 安裝步驟

```bash
# 1. 克隆專案
git clone https://github.com/Scott530810/ambulance-inventory.git
cd ambulance-inventory

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 下載 Ollama 模型（如果還沒有）
ollama pull qwen3:30b

# 4. 設定 Ollama 允許外部訪問
# Windows PowerShell (管理員)
[Environment]::SetEnvironmentVariable("OLLAMA_HOST", "0.0.0.0", "User")
# 重啟 Ollama

# 5. 運行系統檢查
python run_refactored.py --check

# 6. 開始使用！
python run_refactored.py --interactive
```

### Docker 快速啟動

```bash
# 1. 確保 Ollama 在主機上運行
ollama list  # 確認 qwen3:30b 已安裝

# 2. 啟動所有服務
docker-compose -f docker-compose.ollama.yml up -d

# 3. 進入互動模式
docker exec -it ambulance-query-ollama python run_refactored.py --interactive
```

## 📚 文檔

- [📖 QUICK_START.md](QUICK_START.md) - 快速入門指南
- [🏗️ ARCHITECTURE.md](ARCHITECTURE.md) - 系統架構設計
- [🔄 REFACTOR_GUIDE.md](REFACTOR_GUIDE.md) - 重構完整說明
- [🐳 DOCKER_GUIDE.md](DOCKER_GUIDE.md) - Docker 使用指南
- [📝 CHANGELOG.md](CHANGELOG.md) - 版本更新記錄

## 🏗️ 架構概覽

```
ambulance_inventory/
├── config.py           # 配置管理 (Dataclass)
├── database.py         # PostgreSQL 資料庫操作
├── ollama_client.py    # Ollama API 客戶端
├── query_engine.py     # 查詢引擎 (NL → SQL → Response)
├── main.py             # 主程式入口
├── ui/                 # 使用者介面
│   ├── checker.py     # 系統檢查
│   ├── demo.py        # Demo 模式
│   └── interactive.py # 互動模式
└── utils/              # 工具函數
    ├── logger.py      # 日誌系統
    └── validators.py  # SQL 驗證和安全檢查
```

## 🎯 使用模式

### 系統檢查

```bash
python run_refactored.py --check
```

檢查資料庫連接、Ollama 連接、模型可用性和推理能力。

### Demo 模式

```bash
python run_refactored.py --demo
```

執行 5 個預設查詢範例，展示系統功能。

### 互動模式

```bash
python run_refactored.py --interactive
```

自由提問，即時回答。

### Python API

```python
from ambulance_inventory.query_engine import QueryEngine
from ambulance_inventory.config import DatabaseConfig, OllamaConfig
from ambulance_inventory.database import DatabaseClient
from ambulance_inventory.ollama_client import OllamaClient

# 初始化
db_config = DatabaseConfig.from_env()
ollama_config = OllamaConfig.from_env()
db_client = DatabaseClient(db_config)
ollama_client = OllamaClient(ollama_config)
query_engine = QueryEngine(db_client, ollama_client)

# 執行查詢
sql, answer = query_engine.query("請問AED除顫器還有哪幾款有庫存？")
print(answer)
```

## 🔒 安全特性

- ✅ **SQL 驗證** - 只允許 SELECT 查詢
- ✅ **危險操作檢測** - 阻止 DROP、DELETE、TRUNCATE 等
- ✅ **SQL 注入防護** - 自動檢測和清理
- ✅ **輸入驗證** - 完整的參數驗證

## 🛠️ 技術棧

- **語言**: Python 3.11+
- **資料庫**: PostgreSQL 15+
- **LLM**: Ollama (qwen3:30b)
- **容器化**: Docker + Docker Compose
- **依賴管理**: pip

## 📊 系統需求

### 硬體

- **CPU**: 建議 4 核心以上
- **RAM**: 16GB 以上
- **GPU**: NVIDIA GPU (8GB+ VRAM) 用於 Ollama
- **儲存**: 30GB+ 可用空間

### 軟體

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (選用)
- Ollama
- Windows 10/11 或 Linux

## 🤝 貢獻

歡迎提交 Pull Requests 或開 Issues！

### 開發指南

```bash
# 1. Fork 專案
# 2. 創建功能分支
git checkout -b feature/amazing-feature

# 3. 提交更改
git commit -m "Add amazing feature"

# 4. 推送到分支
git push origin feature/amazing-feature

# 5. 開啟 Pull Request
```

## 📝 授權

本專案採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 文件

## 👨‍💻 作者

- **Scott** - [Scott530810](https://github.com/Scott530810)

## 🙏 致謝

- [Ollama](https://ollama.ai/) - 本地 LLM 運行環境
- [Qwen](https://github.com/QwenLM/Qwen) - 強大的中文語言模型
- [PostgreSQL](https://www.postgresql.org/) - 可靠的資料庫系統

## 📞 支援

如有問題或建議，請：

1. 查看 [文檔](QUICK_START.md)
2. 開啟 [Issue](https://github.com/Scott530810/ambulance-inventory/issues)
3. 聯繫作者

## 🔮 未來計劃

- [ ] 添加單元測試（pytest）
- [ ] Web API (FastAPI)
- [ ] 前端介面 (React/Vue)
- [ ] 查詢快取 (Redis)
- [ ] 非同步支援 (asyncio)
- [ ] 數據視覺化
- [ ] 多語言支援

## 📈 版本歷史

查看 [CHANGELOG.md](CHANGELOG.md) 了解詳細的版本更新記錄。

---

**⭐ 如果這個專案對您有幫助，請給個 Star！**

**版本**: 2.0.0 | **日期**: 2026-01-14 | **模型**: qwen3:30b
