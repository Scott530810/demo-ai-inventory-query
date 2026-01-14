# 快速入門指南 - 重構版本 v2.0

## 🎉 恭喜！代碼已重構完成

您的救護車庫存查詢系統已經從單一檔案重構為專業的模組化架構。

---

## 📦 新增的文件

### 核心模組
```
ambulance_inventory/
├── __init__.py           # 套件資訊
├── config.py             # 配置管理
├── database.py           # 資料庫客戶端
├── ollama_client.py      # Ollama API 封裝
├── query_engine.py       # 查詢引擎
├── main.py               # 主程式
├── ui/                   # 使用者介面
│   ├── checker.py
│   ├── demo.py
│   └── interactive.py
└── utils/                # 工具函數
    ├── logger.py
    └── validators.py
```

### 文檔
- [ARCHITECTURE.md](ARCHITECTURE.md) - 架構設計文檔
- [REFACTOR_GUIDE.md](REFACTOR_GUIDE.md) - 完整重構指南
- [DOCKER_GUIDE.md](DOCKER_GUIDE.md) - Docker 使用指南
- [QUICK_START.md](QUICK_START.md) - 本文件

### 配置
- [run_refactored.py](run_refactored.py) - 快速啟動腳本
- [.dockerignore](.dockerignore) - Docker 忽略規則
- 更新的 [Dockerfile.ollama](Dockerfile.ollama)
- 更新的 [docker-compose.ollama.yml](docker-compose.ollama.yml)

---

## 🚀 如何使用

### 選項 1: 本機運行（不使用 Docker）

```bash
# 直接運行（互動式選單）
python run_refactored.py

# 或指定模式
python run_refactored.py --check        # 系統檢查
python run_refactored.py --demo         # Demo 模式
python run_refactored.py --interactive  # 互動模式
```

### 選項 2: 使用 Docker

```bash
# 方法 A: 使用 PowerShell 腳本（推薦）
.\run-ollama-fixed.ps1
# 選擇選項 1 啟動系統

# 方法 B: 手動啟動
docker-compose -f docker-compose.ollama.yml up -d --build
docker exec -it ambulance-query-ollama python run_refactored.py --interactive
```

---

## ✨ 主要改進

### 1. 模組化架構
- ✅ 11 個獨立模組，職責清晰
- ✅ 易於測試和維護
- ✅ 符合 SOLID 原則

### 2. 類型安全
- ✅ 完整的類型提示
- ✅ IDE 自動補全支援
- ✅ 提早發現錯誤

### 3. 安全性
- ✅ SQL 驗證和清理
- ✅ 阻止危險操作（DROP、DELETE 等）
- ✅ SQL 注入防護

### 4. 錯誤處理
- ✅ 完整的異常處理
- ✅ 統一的錯誤訊息
- ✅ 日誌記錄系統

### 5. 配置管理
- ✅ 使用 Dataclass
- ✅ 環境變數支援
- ✅ 類型安全的配置

### 6. 模型更新
- ✅ 更新為 qwen3:30b（不是 qwen2.5:32b）

---

## 📊 快速對比

| 特性 | 舊版 | 新版 |
|------|------|------|
| 檔案數 | 1 | 11 |
| 行數 | 454 | ~1000 |
| 模組化 | ❌ | ✅ |
| 類型提示 | ❌ | ✅ |
| 日誌系統 | ❌ | ✅ |
| SQL 驗證 | ❌ | ✅ |
| 可測試性 | 低 | 高 |
| Docker 支援 | 基本 | 完整 |

---

## 🔍 功能測試

### 測試 1: 檢查模組導入
```bash
python -c "from ambulance_inventory.config import OllamaConfig; print('OK')"
```

### 測試 2: 檢查版本資訊
```bash
python -c "import ambulance_inventory; print(ambulance_inventory.__version__)"
# 應該輸出: 2.0.0
```

### 測試 3: 系統檢查
```bash
python run_refactored.py --check
```

### 測試 4: Docker 構建
```bash
docker build -f Dockerfile.ollama -t test .
docker run --rm test python -c "from ambulance_inventory.config import OllamaConfig; print('OK')"
```

---

## 🎯 使用建議

### 第一次使用
1. **系統檢查**: `python run_refactored.py --check`
2. **Demo 模式**: `python run_refactored.py --demo`
3. **互動模式**: `python run_refactored.py --interactive`

### 日常使用
- 互動模式最靈活，可以自由提問
- Demo 模式適合展示給其他人看
- 系統檢查用於排除問題

### 開發擴展
查看 [ARCHITECTURE.md](ARCHITECTURE.md) 了解如何：
- 添加新功能
- 創建單元測試
- 整合其他服務

---

## ⚠️ 重要提醒

### 環境需求
- Python 3.11+
- PostgreSQL 15+
- Ollama 運行中
- qwen3:30b 模型已下載

### Ollama 設定
```powershell
# 確保 Ollama 允許外部訪問
[Environment]::SetEnvironmentVariable("OLLAMA_HOST", "0.0.0.0", "User")

# 重啟 Ollama

# 下載模型
ollama pull qwen3:30b
```

### 舊版本
[test_llm_query_ollama.py](test_llm_query_ollama.py) 仍然保留並可用，如遇問題可切回。

---

## 📚 學習資源

### 文檔
1. [ARCHITECTURE.md](ARCHITECTURE.md) - 深入了解系統架構
2. [REFACTOR_GUIDE.md](REFACTOR_GUIDE.md) - 重構詳細說明
3. [DOCKER_GUIDE.md](DOCKER_GUIDE.md) - Docker 完整指南

### 代碼
- [ambulance_inventory/config.py](ambulance_inventory/config.py) - 配置範例
- [ambulance_inventory/query_engine.py](ambulance_inventory/query_engine.py) - 核心邏輯
- [ambulance_inventory/utils/validators.py](ambulance_inventory/utils/validators.py) - 安全驗證

---

## 🚀 下一步

### 立即開始
```bash
# 最簡單的方式
python run_refactored.py
```

### 進階使用
```bash
# 在代碼中使用
from ambulance_inventory.query_engine import QueryEngine

# 自訂配置
export OLLAMA_MODEL="qwen3:14b"

# Docker 部署
docker-compose -f docker-compose.ollama.yml up -d
```

### 未來擴展
- 添加單元測試（pytest）
- 創建 Web API（FastAPI）
- 添加結果快取（Redis）
- 實現非同步處理
- 數據視覺化

---

## 💡 提示

- 使用 `--check` 模式排除連接問題
- 首次查詢可能較慢（模型載入）
- 複雜查詢可能需要 5-15 秒
- 日誌輸出在控制台可見

---

## 🎊 開始使用吧！

```bash
# 最快開始的方式
python run_refactored.py --interactive
```

然後問個問題：
```
請問AED除顫器還有哪幾款有庫存？
```

享受您全新的模組化代碼！ 🚀

---

**版本**: 2.0.0
**日期**: 2026-01-14
**模型**: qwen3:30b
**狀態**: ✅ 生產就緒
