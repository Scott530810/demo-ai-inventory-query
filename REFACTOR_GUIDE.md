# 重構完成指南

## 🎉 重構完成！

代碼已經從單一檔案（454行）重構為模組化架構，大幅提升了可維護性和可擴展性。

---

## 📁 新的專案結構

```
ambulance_inventory/
├── __init__.py              # 套件初始化
├── config.py                # 配置管理 (97 行)
├── database.py              # 資料庫操作 (125 行)
├── ollama_client.py         # Ollama API 封裝 (157 行)
├── query_engine.py          # 查詢引擎 (175 行)
├── main.py                  # 主程式入口 (109 行)
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

總代碼行數：約 1000 行（原來 454 行）
模組數：11 個檔案

---

## 🚀 如何使用新版本

### 方法 1: 使用快速啟動腳本（推薦）

```bash
# 直接運行
python run_refactored.py

# 或指定模式
python run_refactored.py --check        # 系統檢查
python run_refactored.py --demo         # Demo 模式
python run_refactored.py --interactive  # 互動模式
```

### 方法 2: 作為 Python 模組運行

```bash
python -m ambulance_inventory.main --check
python -m ambulance_inventory.main --demo
python -m ambulance_inventory.main --interactive
```

### 方法 3: 在 Python 代碼中使用

```python
from ambulance_inventory.config import DatabaseConfig, OllamaConfig
from ambulance_inventory.database import DatabaseClient
from ambulance_inventory.ollama_client import OllamaClient
from ambulance_inventory.query_engine import QueryEngine

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

---

## ✨ 重構改進一覽

### 1. **模組化設計**
| 功能 | 舊版 | 新版 |
|------|------|------|
| 配置管理 | 散落在程式中 | 集中在 [config.py](ambulance_inventory/config.py) |
| 資料庫操作 | 函數散落 | 封裝在 [DatabaseClient](ambulance_inventory/database.py) 類別 |
| Ollama API | 單一函數 | 完整的 [OllamaClient](ambulance_inventory/ollama_client.py) 類別 |
| 查詢邏輯 | 混雜在主程式 | 獨立的 [QueryEngine](ambulance_inventory/query_engine.py) |
| UI 介面 | 3個大函數 | 分離為 3 個模組 |

### 2. **類型提示**
```python
# 舊版：沒有類型提示
def query_with_ollama(question):
    ...

# 新版：完整類型提示
def query(self, question: str) -> Tuple[Optional[str], Optional[str]]:
    ...
```

### 3. **錯誤處理**
- ✅ 所有 API 調用都有異常處理
- ✅ 統一的錯誤訊息格式
- ✅ 日誌記錄系統

### 4. **安全性增強**
- ✅ SQL 驗證和清理 ([validators.py](ambulance_inventory/utils/validators.py))
- ✅ 危險操作檢測
- ✅ SQL 注入防護

### 5. **代碼質量**
- ✅ 每個模組職責單一
- ✅ 函數長度合理（大部分 < 50 行）
- ✅ 清晰的文檔字串
- ✅ 可測試性高

---

## 📊 對比表

| 項目 | 舊版 (test_llm_query_ollama.py) | 新版 (ambulance_inventory/) |
|------|----------------------------------|------------------------------|
| **檔案數** | 1 個 | 11 個 |
| **總行數** | 454 行 | ~1000 行 |
| **模組化** | ❌ | ✅ |
| **類型提示** | ❌ | ✅ |
| **日誌系統** | ❌ | ✅ |
| **SQL 驗證** | ❌ | ✅ |
| **錯誤處理** | ⚠️ 部分 | ✅ 完整 |
| **可測試性** | ❌ 低 | ✅ 高 |
| **可維護性** | ⚠️ 中 | ✅ 高 |
| **可擴展性** | ⚠️ 低 | ✅ 高 |
| **IDE 支援** | ⚠️ 基本 | ✅ 完整自動補全 |

---

## 🎯 重要更新

### 1. 模型更新為 qwen3:30b
所有配置已更新為使用 **qwen3:30b** 模型（不再是 qwen2.5:32b）

### 2. 配置使用 Dataclass
```python
@dataclass
class OllamaConfig:
    host: str
    model: str  # 預設: qwen3:30b
    timeout: int = 120
```

### 3. SQL 安全驗證
新增的驗證器會檢查：
- 只允許 SELECT 查詢
- 阻止 DROP、DELETE、TRUNCATE 等危險操作
- 檢測 SQL 注入嘗試
- 驗證基本語法

### 4. 日誌系統
```python
from ambulance_inventory.utils.logger import setup_logger

logger = setup_logger('my_app', logging.INFO)
logger.info("這是日誌訊息")
```

---

## 🔧 環境變數

新版本支援完整的環境變數配置：

```bash
# Ollama 設定
export OLLAMA_HOST="http://host.docker.internal:11434"
export OLLAMA_MODEL="qwen3:30b"
export OLLAMA_TIMEOUT="120"

# 資料庫設定
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="ambulance_inventory"
export DB_USER="postgres"
export DB_PASSWORD="demo123"
```

---

## 🧪 測試建議

雖然目前還沒有單元測試，但新架構非常容易測試：

```python
# 測試資料庫連接
def test_database_connection():
    config = DatabaseConfig(
        host="localhost",
        database="test_db",
        user="test_user",
        password="test_pass",
        port=5432
    )
    client = DatabaseClient(config)
    assert client.test_connection() == True

# 測試 SQL 驗證
def test_sql_validation():
    from ambulance_inventory.utils.validators import validate_sql

    # 應該通過
    valid, msg = validate_sql("SELECT * FROM inventory;")
    assert valid == True

    # 應該被阻止
    valid, msg = validate_sql("DROP TABLE inventory;")
    assert valid == False
```

---

## 📚 延伸閱讀

- [ARCHITECTURE.md](ARCHITECTURE.md) - 完整的架構文檔
- [README_OLLAMA.md](README_OLLAMA.md) - Ollama 使用指南
- [ambulance_inventory/config.py](ambulance_inventory/config.py) - 配置說明

---

## 🎓 學習重點

這次重構展示了以下軟體工程最佳實踐：

1. **單一職責原則** - 每個類別/模組只做一件事
2. **依賴注入** - 通過參數傳遞依賴，不在內部創建
3. **類型安全** - 使用類型提示和 Dataclass
4. **錯誤處理** - 完整的異常處理和日誌
5. **關注點分離** - UI、業務邏輯、資料存取分離
6. **可測試性** - 易於 mock 和單元測試

---

## 🚀 下一步建議

1. **添加單元測試** - 使用 pytest
2. **創建 Web API** - 使用 FastAPI
3. **添加快取** - 使用 Redis 快取查詢結果
4. **實現非同步** - 使用 asyncio 提升性能
5. **添加監控** - 整合 Prometheus/Grafana

---

## ⚠️ 注意事項

### 舊版本仍然可用
原始的 [test_llm_query_ollama.py](test_llm_query_ollama.py) 檔案仍然存在且可用，
如果您遇到任何問題，可以隨時切回舊版本。

### Docker 配置 ✅ 已更新
Docker 配置已更新為使用新版模組化代碼！

**快速啟動**:
```bash
docker-compose -f docker-compose.ollama.yml up -d --build
docker exec -it ambulance-query-ollama python run_refactored.py --interactive
```

詳細說明請查看 [DOCKER_GUIDE.md](DOCKER_GUIDE.md)

**新版 Docker 特性**:
- ✅ 使用模組化代碼結構
- ✅ 支援 qwen3:30b 模型
- ✅ 向後兼容（保留舊版本）
- ✅ 可選擇不同運行模式（--demo, --check, --interactive）

---

## 📞 需要幫助？

如果有任何問題：
1. 查看 [ARCHITECTURE.md](ARCHITECTURE.md)
2. 查看模組內的文檔字串
3. 使用 `--check` 模式檢查系統狀態

---

**重構完成日期**: 2026-01-14
**版本**: v2.0.0
**模型**: qwen3:30b
