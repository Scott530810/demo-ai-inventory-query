# Docker 使用指南 - 重構版本

## 🐳 Docker 配置已更新

Docker 配置已經更新以支援新的模組化代碼結構 (v2.0)。

---

## 📋 前置需求

### 1. Ollama 運行在主機上
```powershell
# 確認 Ollama 正在運行
curl http://localhost:11434/api/tags

# 確認模型已下載
ollama list
# 應該看到 qwen3:30b

# 如果沒有，下載模型
ollama pull qwen3:30b
```

### 2. Ollama 允許外部訪問
```powershell
# 設定環境變數（永久）
[Environment]::SetEnvironmentVariable("OLLAMA_HOST", "0.0.0.0", "User")

# 重啟 Ollama
```

### 3. Docker Desktop 運行
```powershell
docker info
```

---

## 🚀 快速開始

### 方法 1: 使用 PowerShell 腳本（推薦）

```powershell
# 使用現有的 run-ollama-fixed.ps1
.\run-ollama-fixed.ps1

# 選擇選項 1: 啟動系統
```

### 方法 2: 手動啟動

```bash
# 1. 構建並啟動容器
docker-compose -f docker-compose.ollama.yml up -d --build

# 2. 查看日誌
docker-compose -f docker-compose.ollama.yml logs -f query-app-ollama

# 3. 進入容器互動
docker exec -it ambulance-query-ollama python run_refactored.py --interactive
```

---

## 🎮 使用不同模式

### 互動模式（預設）
```bash
docker exec -it ambulance-query-ollama python run_refactored.py --interactive
```

### Demo 模式
```bash
docker exec -it ambulance-query-ollama python run_refactored.py --demo
```

### 系統檢查
```bash
docker exec -it ambulance-query-ollama python run_refactored.py --check
```

### 使用舊版本（向後兼容）
```bash
docker exec -it ambulance-query-ollama python test_llm_query_ollama.py --interactive
```

---

## ⚙️ 配置說明

### Dockerfile.ollama

```dockerfile
# 新版本會複製整個 ambulance_inventory 模組
COPY ambulance_inventory/ ./ambulance_inventory/
COPY run_refactored.py .

# 也保留舊版本以便向後兼容
COPY test_llm_query_ollama.py .

# 預設使用新版本
CMD ["python", "run_refactored.py", "--interactive"]
```

### docker-compose.ollama.yml

關鍵環境變數：
```yaml
environment:
  # 資料庫設定
  DB_HOST: postgres
  DB_PORT: 5432
  DB_NAME: ambulance_inventory
  DB_USER: postgres
  DB_PASSWORD: demo123

  # Ollama 設定
  OLLAMA_HOST: http://host.docker.internal:11434
  OLLAMA_MODEL: qwen3:30b
  OLLAMA_TIMEOUT: 120
```

---

## 🔧 自訂配置

### 更改啟動模式

編輯 [docker-compose.ollama.yml](docker-compose.ollama.yml)：

```yaml
# 互動模式（預設）
command: python run_refactored.py --interactive

# Demo 模式
command: python run_refactored.py --demo

# 系統檢查
command: python run_refactored.py --check

# 使用選單
command: python run_refactored.py
```

### 使用不同的 Ollama 模型

```yaml
environment:
  OLLAMA_MODEL: qwen3:14b  # 或其他模型
```

### 調整超時時間

```yaml
environment:
  OLLAMA_TIMEOUT: 180  # 增加到 3 分鐘
```

---

## 📊 容器管理

### 啟動服務
```bash
docker-compose -f docker-compose.ollama.yml up -d
```

### 查看運行狀態
```bash
docker-compose -f docker-compose.ollama.yml ps
```

### 查看日誌
```bash
# 所有服務
docker-compose -f docker-compose.ollama.yml logs -f

# 只看應用
docker-compose -f docker-compose.ollama.yml logs -f query-app-ollama

# 只看資料庫
docker-compose -f docker-compose.ollama.yml logs -f postgres
```

### 停止服務
```bash
docker-compose -f docker-compose.ollama.yml down
```

### 重建容器（代碼更新後）
```bash
docker-compose -f docker-compose.ollama.yml up -d --build
```

### 完全清理（包含資料）
```bash
docker-compose -f docker-compose.ollama.yml down -v
```

---

## 🔍 除錯技巧

### 1. 進入容器檢查
```bash
docker exec -it ambulance-query-ollama bash

# 檢查文件是否存在
ls -la ambulance_inventory/

# 測試 Python 導入
python -c "from ambulance_inventory.config import OllamaConfig; print('OK')"

# 手動運行檢查
python run_refactored.py --check
```

### 2. 檢查網路連接
```bash
# 進入容器
docker exec -it ambulance-query-ollama bash

# 測試連接到主機的 Ollama
curl http://host.docker.internal:11434/api/tags

# 測試資料庫連接
psql -h postgres -U postgres -d ambulance_inventory -c "SELECT COUNT(*) FROM inventory;"
```

### 3. 查看容器日誌
```bash
# 實時查看
docker logs -f ambulance-query-ollama

# 查看最後 100 行
docker logs --tail 100 ambulance-query-ollama
```

### 4. 檢查環境變數
```bash
docker exec ambulance-query-ollama env | grep -E "(OLLAMA|DB_)"
```

---

## 🆚 新舊版本對比

| 功能 | 舊版 Docker | 新版 Docker |
|------|-------------|-------------|
| **入口點** | `test_llm_query_ollama.py` | `run_refactored.py` |
| **代碼結構** | 單一文件 | 模組化 |
| **向後兼容** | N/A | ✅ 保留舊版本 |
| **模型** | qwen2.5:32b | qwen3:30b |
| **類型提示** | ❌ | ✅ |
| **日誌系統** | ❌ | ✅ |
| **SQL 驗證** | ❌ | ✅ |

---

## 🎯 常見問題

### Q1: 為什麼容器啟動後立即退出？

**原因**: 可能是 command 設定問題

**解決**:
```yaml
# 確保 docker-compose.yml 有正確的 command
command: python run_refactored.py --interactive

# 或者使用 tail 保持運行
command: tail -f /dev/null
```

### Q2: 容器內無法連接到 Ollama

**檢查清單**:
1. Ollama 在主機上運行？
2. OLLAMA_HOST 設定為 0.0.0.0？
3. Windows 防火牆允許？
4. `host.docker.internal` 可解析？

**測試**:
```bash
docker exec ambulance-query-ollama curl http://host.docker.internal:11434/api/tags
```

### Q3: 模型載入很慢

**原因**: 首次載入模型需要時間

**解決**:
```bash
# 預先在主機載入模型
ollama run qwen3:30b
# 輸入 /bye 退出但保持模型在記憶體
```

### Q4: 資料庫連接失敗

**檢查**:
```bash
# 確認資料庫服務正常
docker-compose -f docker-compose.ollama.yml ps postgres

# 檢查健康狀態
docker inspect ambulance-db-ollama | grep -A 10 Health
```

---

## 📝 與 run-ollama-fixed.ps1 整合

新的 Docker 配置可以直接與現有的 PowerShell 腳本配合使用：

```powershell
.\run-ollama-fixed.ps1

# 選項 1: 啟動系統 → 使用新版 Docker 配置
# 選項 2: 系統檢查 → 自動進入容器執行檢查
# 選項 3: 執行 Demo → 自動使用新版本
# 選項 4: 互動模式 → 使用新版重構代碼
```

---

## 🚀 效能優化建議

### 1. 使用 Docker 層快取
```dockerfile
# 先複製 requirements.txt（變動較少）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再複製代碼（變動較多）
COPY ambulance_inventory/ ./ambulance_inventory/
```

### 2. 多階段構建（未來優化）
```dockerfile
# 可以創建更小的生產映像
FROM python:3.11-slim as builder
# ... 構建步驟

FROM python:3.11-slim
COPY --from=builder /app /app
```

### 3. 使用 .dockerignore
創建 `.dockerignore` 檔案：
```
__pycache__/
*.pyc
*.pyo
.git/
.vscode/
*.md
```

---

## 📚 延伸閱讀

- [REFACTOR_GUIDE.md](REFACTOR_GUIDE.md) - 重構完整指南
- [ARCHITECTURE.md](ARCHITECTURE.md) - 架構文檔
- [README_OLLAMA.md](README_OLLAMA.md) - Ollama 使用指南

---

**更新日期**: 2026-01-14
**版本**: v2.0.0
**Docker Compose**: docker-compose.ollama.yml
**Dockerfile**: Dockerfile.ollama
