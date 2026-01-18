# 更新日誌

## [2.1.0] - 2026-01-17

### 🌐 重大更新：遠端 API 部署

新增 DGX SPARK 服務器部署支援，可從 Windows 11 筆電遠端連線使用

---

## ✨ 新增功能

### FastAPI 遠端服務器
- ✅ 創建 FastAPI API 服務器 (`server/api_server.py`)
- ✅ RESTful API 端點：`/query`, `/health`, `/tables`
- ✅ Swagger UI 文檔 (`/docs`)
- ✅ CORS 支援，允許遠端連線
- ✅ 完整的錯誤處理和日誌記錄

### 服務器部署工具
- ✅ 部署腳本 (`server/deploy_to_spark.sh`)
- ✅ Systemd 服務配置
- ✅ Docker 配置 (`server/Dockerfile.spark`, `docker-compose.spark.yml`)
- ✅ 環境變數模板和配置指南

### Windows 11 客戶端
- ✅ PowerShell 客戶端 (`client/connect_to_spark.ps1`)
- ✅ Python 客戶端 (`client/spark_client.py`)
- ✅ SSH 隧道工具 (`client/ssh_tunnel.ps1`)
- ✅ 互動模式和單次查詢支援
- ✅ 連接測試和健康檢查

### 文檔
- ✅ [DGX_SPARK_DEPLOYMENT.md](DGX_SPARK_DEPLOYMENT.md) - 完整部署指南
- ✅ [SPARK_QUICK_START.md](SPARK_QUICK_START.md) - 5 分鐘快速設置
- ✅ 包含架構圖、安全建議、故障排除

### 部署方式
- ✅ 直接 HTTP 連線（內網）
- ✅ SSH 隧道（外網/加密）
- ✅ Docker 容器化部署

---

## 🔧 改進

### 安全性
- ✅ 防火牆配置指南
- ✅ IP 白名單支援
- ✅ API 金鑰認證建議
- ✅ 限流（Rate Limiting）建議
- ✅ HTTPS/SSL 配置指南

### 監控和維護
- ✅ 系統日誌管理
- ✅ 性能監控指南
- ✅ 自動化備份建議

---

## 📊 架構更新

新增遠端部署架構：

```
Windows 11 筆電 ←→ Internet/LAN ←→ DGX SPARK 服務器
    (Client)                         (FastAPI + DB + Ollama)
```

---

## [2.0.0] - 2026-01-14

### 🎉 重大更新：代碼重構

將單一檔案（454行）重構為模組化架構（11個模組，約1000行代碼）

---

## ✨ 新增功能

### 模組化架構
- ✅ 創建 `ambulance_inventory` 套件
- ✅ 分離配置、資料庫、Ollama、查詢引擎、UI 模組
- ✅ 獨立的工具函數模組（logger, validators）

### 類型系統
- ✅ 所有函數添加完整類型提示
- ✅ 使用 Dataclass 進行配置管理
- ✅ IDE 完整支援自動補全

### 安全性增強
- ✅ SQL 驗證器（只允許 SELECT）
- ✅ 危險操作檢測（DROP, DELETE, TRUNCATE 等）
- ✅ SQL 注入防護
- ✅ SQL 清理和格式化

### 日誌系統
- ✅ 統一的日誌管理
- ✅ 可配置的日誌級別
- ✅ 結構化日誌輸出

### Docker 支援
- ✅ 更新 Dockerfile.ollama
- ✅ 更新 docker-compose.ollama.yml
- ✅ 創建 .dockerignore
- ✅ 向後兼容舊版本

### 文檔
- ✅ ARCHITECTURE.md - 架構設計文檔
- ✅ REFACTOR_GUIDE.md - 重構完整指南
- ✅ DOCKER_GUIDE.md - Docker 使用指南
- ✅ QUICK_START.md - 快速入門
- ✅ CHANGELOG.md - 本文件

---

## 🔄 變更

### 模型更新
- ⚠️ 從 `qwen2.5:32b` 更新為 `qwen3:30b`
- 所有配置檔案已更新
- 環境變數默認值已更新

### 入口點
- 新增 `run_refactored.py` 作為主要入口
- 保留 `test_llm_query_ollama.py` 作為向後兼容

### 配置管理
- 使用 Dataclass 替代字典
- 支援環境變數配置
- 類型安全的配置讀取

---

## 📦 新增文件

### 核心模組
```
ambulance_inventory/
├── __init__.py              # 套件初始化
├── config.py                # 配置管理 (97 行)
├── database.py              # 資料庫操作 (125 行)
├── ollama_client.py         # Ollama API (157 行)
├── query_engine.py          # 查詢引擎 (175 行)
├── main.py                  # 主程式 (109 行)
├── ui/
│   ├── __init__.py
│   ├── checker.py          # 系統檢查 (103 行)
│   ├── demo.py            # Demo 模式 (76 行)
│   └── interactive.py     # 互動模式 (71 行)
└── utils/
    ├── __init__.py
    ├── logger.py           # 日誌工具 (60 行)
    └── validators.py       # SQL 驗證 (120 行)
```

### 文檔
- ARCHITECTURE.md (5.8 KB)
- REFACTOR_GUIDE.md (7.7 KB)
- DOCKER_GUIDE.md (7.3 KB)
- QUICK_START.md (5.8 KB)
- CHANGELOG.md (本文件)

### 配置
- run_refactored.py
- .dockerignore

---

## 🔧 改進

### 代碼質量
- ✅ 每個模組職責單一
- ✅ 函數長度合理（< 50 行）
- ✅ 清晰的文檔字串
- ✅ 減少代碼重複

### 錯誤處理
- ✅ 所有 API 調用都有異常處理
- ✅ 統一的錯誤訊息格式
- ✅ 更好的錯誤追蹤

### 可維護性
- ✅ 易於測試（高內聚低耦合）
- ✅ 易於擴展（模組化設計）
- ✅ 易於理解（清晰的結構）

### 性能
- ✅ 更好的資源管理
- ✅ 連接正確關閉
- ✅ 記憶體使用優化

---

## 🐛 修復

### 安全問題
- ✅ 修復潛在的 SQL 注入風險
- ✅ 添加危險操作檢測
- ✅ 改進輸入驗證

### 功能問題
- ✅ 改進 SQL 清理邏輯
- ✅ 更好的 Decimal 類型處理
- ✅ 改進錯誤訊息

---

## 📊 對比分析

### 代碼指標

| 指標 | 舊版 | 新版 | 變化 |
|------|------|------|------|
| 檔案數 | 1 | 11 | +1000% |
| 總行數 | 454 | ~1000 | +120% |
| 模組化 | 無 | 完整 | ✅ |
| 類型提示 | 0% | 100% | ✅ |
| 測試覆蓋率 | 0% | 0% | - |
| 文檔完整度 | 低 | 高 | ✅ |

### 功能對比

| 功能 | 舊版 | 新版 |
|------|------|------|
| 基本查詢 | ✅ | ✅ |
| Demo 模式 | ✅ | ✅ |
| 互動模式 | ✅ | ✅ |
| 系統檢查 | ✅ | ✅ |
| SQL 驗證 | ❌ | ✅ |
| 日誌系統 | ❌ | ✅ |
| 類型提示 | ❌ | ✅ |
| 模組化 | ❌ | ✅ |
| 單元測試 | ❌ | ⏳ 準備中 |

---

## 🎯 向後兼容性

### 保留的功能
- ✅ 所有原有功能完整保留
- ✅ 相同的用戶介面
- ✅ 相同的環境變數
- ✅ 相同的 Docker 命令

### 舊版本支援
- ✅ `test_llm_query_ollama.py` 仍然可用
- ✅ Docker 容器包含兩個版本
- ✅ 可隨時切換回舊版本

---

## ⚠️ 破壞性變更

### 模型名稱
- ⚠️ 默認模型從 `qwen2.5:32b` 改為 `qwen3:30b`
- 可通過環境變數 `OLLAMA_MODEL` 覆蓋

### 導入路徑
```python
# 舊版（不再推薦）
python test_llm_query_ollama.py --interactive

# 新版（推薦）
python run_refactored.py --interactive

# 或作為模組
from ambulance_inventory.query_engine import QueryEngine
```

---

## 🚀 升級指南

### 本機使用
```bash
# 無需特別操作，直接使用新版本
python run_refactored.py --interactive
```

### Docker 使用
```bash
# 重新構建容器
docker-compose -f docker-compose.ollama.yml up -d --build
```

### 自訂代碼
如果您有自訂代碼使用舊版本，需要更新導入路徑：

```python
# 舊版
from test_llm_query_ollama import query_with_ollama

# 新版
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

# 使用
sql, answer = query_engine.query("你的問題")
```

---

## 🔮 未來計劃

### v2.1.0（計劃中）
- [ ] 添加單元測試（pytest）
- [ ] 集成測試
- [ ] 測試覆蓋率報告

### v2.2.0（計劃中）
- [ ] Web API（FastAPI）
- [ ] RESTful 接口
- [ ] Swagger 文檔

### v3.0.0（考慮中）
- [ ] 非同步支援（asyncio）
- [ ] 查詢快取（Redis）
- [ ] 結果匯出（CSV/Excel）
- [ ] 數據視覺化
- [ ] 前端介面

---

## 👥 貢獻者

- Scott - 初始版本和重構

---

## 📝 注意事項

### 系統需求
- Python 3.11+
- PostgreSQL 15+
- Ollama (運行中)
- qwen3:30b 模型

### 已知問題
- 暫無單元測試
- 文檔中的 Markdown 連結可能在某些編輯器中無法正確渲染

### 回報問題
如發現任何問題，請檢查：
1. [ARCHITECTURE.md](ARCHITECTURE.md) - 架構說明
2. [DOCKER_GUIDE.md](DOCKER_GUIDE.md) - Docker 問題
3. [QUICK_START.md](QUICK_START.md) - 快速開始

---

## 📜 授權

與原始版本相同

---

**發布日期**: 2026-01-14
**版本**: 2.0.0
**代號**: Modular Refactor
**狀態**: ✅ 穩定
