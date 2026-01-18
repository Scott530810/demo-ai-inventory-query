# Windows 11 本地部署指南

使用 Ollama 在本地運行 AI 庫存查詢系統

## 系統需求

- **作業系統**: Windows 11
- **GPU**: NVIDIA RTX 系列 (建議 8GB+ VRAM)
- **軟體**: Docker Desktop, Ollama

## 快速開始 (5 分鐘)

### 步驟 1: 安裝 Ollama

1. 下載安裝: https://ollama.com/download
2. 下載模型:
```powershell
ollama pull llama3:70b
```

### 步驟 2: 設定 Ollama 允許外部訪問

```powershell
# PowerShell (管理員模式)
[Environment]::SetEnvironmentVariable("OLLAMA_HOST", "0.0.0.0", "User")
```

重啟 Ollama (系統托盤右鍵 → Quit → 重新開啟)

### 步驟 3: 啟動系統

```powershell
cd C:\path\to\demo-ai-inventory-query
.\run-ollama.ps1

# 選擇:
# 1 → 啟動系統
# 2 → 系統檢查
# 3 → 執行 Demo
# 4 → 互動模式
```

---

## Docker 使用方式

### 手動啟動

```bash
# 構建並啟動
docker compose -f docker-compose.ollama.yml up -d --build

# 進入互動模式
docker exec -it ambulance-query-ollama python run_refactored.py --interactive

# 執行 Demo
docker exec -it ambulance-query-ollama python run_refactored.py --demo

# 系統檢查
docker exec -it ambulance-query-ollama python run_refactored.py --check
```

### 容器管理

```bash
# 查看狀態
docker compose -f docker-compose.ollama.yml ps

# 查看日誌
docker compose -f docker-compose.ollama.yml logs -f query-app-ollama

# 停止服務
docker compose -f docker-compose.ollama.yml down

# 完全清理 (含資料)
docker compose -f docker-compose.ollama.yml down -v
```

---

## 配置說明

### 環境變數

在 `docker-compose.ollama.yml` 中設定:

| 變數 | 說明 | 預設值 |
|------|------|--------|
| `OLLAMA_HOST` | Ollama 服務位址 | `http://host.docker.internal:11434` |
| `OLLAMA_MODEL` | 使用的模型 | `llama3:70b` |
| `OLLAMA_TIMEOUT` | 請求超時秒數 | `120` |
| `DB_HOST` | 資料庫主機 | `postgres` |
| `DB_NAME` | 資料庫名稱 | `ambulance_inventory` |

### 更換模型

編輯 `docker-compose.ollama.yml`:

```yaml
environment:
  OLLAMA_MODEL: llama3:8b  # 更快但較不準確
```

或在互動模式中選擇「切換模型」。

---

## 使用範例

### 簡單查詢

```
💭 請輸入您的問題: 請問 AED 除顫器還有哪幾款有庫存？

🤖 AI 回應:
目前有庫存的 AED 除顫器共 4 款：
1. Philips HeartStart FRx - 庫存 15 台
2. Mindray BeneHeart D1 - 庫存 12 台
...
```

### 複雜查詢

```
💭 請輸入您的問題: 我需要配備一台新救護車，預算 15 萬，請推薦設備清單

🤖 AI 回應:
根據您 15 萬的預算，推薦以下配置：
1. AED 除顫器 - Mindray BeneHeart D1 (68,000 元)
2. 氧氣設備 - 攜帶式氧氣瓶 x3 (25,500 元)
...
總計: 143,500 元
```

---

## 效能參考

| GPU | 模型 | VRAM | SQL 生成 | 回應生成 |
|-----|------|------|----------|----------|
| RTX 4070 | llama3:8b | ~5GB | 2-4 秒 | 3-5 秒 |
| RTX 4070 | llama3:70b | ~40GB | 4-8 秒 | 5-10 秒 |
| RTX 5070 | llama3:70b | ~40GB | 3-6 秒 | 4-8 秒 |

---

## 故障排除

### 無法連接到 Ollama

```powershell
# 檢查 Ollama 是否運行
curl http://localhost:11434/api/tags

# 確認環境變數
echo $env:OLLAMA_HOST

# 重啟 Ollama
```

### 容器無法訪問 host.docker.internal

```powershell
# Docker Desktop 設定
# Settings → Resources → Network
# 確認 "Use the host network" 已啟用
```

### VRAM 不足

```powershell
# 使用更小的模型
ollama pull llama3:8b

# 修改 docker-compose.ollama.yml
# OLLAMA_MODEL: llama3:8b
```

### 資料庫連接失敗

```bash
# 檢查資料庫服務
docker compose -f docker-compose.ollama.yml ps postgres

# 檢查健康狀態
docker inspect ambulance-db-ollama | grep -A 10 Health
```

---

## 檔案結構

```
demo-ai-inventory-query/
├── docker-compose.ollama.yml    # Docker 配置
├── Dockerfile.ollama            # Docker 映像
├── run-ollama.ps1               # PowerShell 啟動腳本
├── run-ollama.sh                # Bash 啟動腳本 (WSL)
├── run_refactored.py            # Python 入口
└── ambulance_inventory/         # 核心模組
```

---

**版本**: 2.1.0
**更新日期**: 2026-01-18
