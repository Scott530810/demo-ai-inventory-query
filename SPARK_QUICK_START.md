# SPARK 快速開始指南

從 Windows 11 筆電快速連線到 DGX SPARK 服務器

## 🚀 5 分鐘快速設置

### 在 SPARK 服務器上

```bash
# 1. 克隆專案
cd /opt
sudo git clone https://github.com/Scott530810/demo-ai-inventory-query.git
cd demo-ai-inventory-query

# 2. 確保 Ollama 運行並下載模型
ollama pull qwen3:30b
ollama serve &

# 3. 使用 Docker 部署 (最簡單)
cd server
docker-compose -f docker-compose.spark.yml up -d

# 4. 檢查服務狀態
docker-compose -f docker-compose.spark.yml ps
curl http://localhost:8000/health

# 5. 開放防火牆
sudo ufw allow 8000/tcp
```

### 在 Windows 11 筆電上

```powershell
# 1. 編輯客戶端腳本,設置 SPARK IP
notepad client\connect_to_spark.ps1
# 修改: $SparkIP = "192.168.1.100"  # 改為實際 IP

# 2. 測試連接
.\client\connect_to_spark.ps1

# 3. 開始使用!
```

## 📋 三種連線方式

### 方式 1: PowerShell 客戶端 ⭐ 推薦

```powershell
.\client\connect_to_spark.ps1 -SparkIP 192.168.1.100
```

### 方式 2: Python 客戶端

```bash
python client\spark_client.py --host 192.168.1.100 --interactive
```

### 方式 3: Web 瀏覽器

```
http://192.168.1.100:8000/docs
```

## 🔐 如果需要 SSH 隧道 (外網訪問)

```powershell
# 建立 SSH 隧道
.\client\ssh_tunnel.ps1 -SparkIP 192.168.1.100 -SparkUser scott

# 然後使用 localhost
.\client\connect_to_spark.ps1 -SparkIP localhost
```

## 🎮 使用範例

```
💭 Your question: 請問AED除顫器還有哪幾款有庫存？

✅ Query Successful!
============================================================

📊 SQL Query:
SELECT product_name, brand, stock_quantity
FROM ambulance_equipment
WHERE category = 'AED除顫器' AND stock_quantity > 0;

💡 Answer:
目前有庫存的AED除顫器有以下幾款：
1. Philips HeartStart HS1 - 庫存15台
2. ZOLL AED Plus - 庫存8台
3. Cardiac Science Powerheart G5 - 庫存12台
============================================================
```

## 🔧 故障排除

### 連不上服務器?

```powershell
# 測試網路
ping 192.168.1.100

# 測試 port
Test-NetConnection -ComputerName 192.168.1.100 -Port 8000
```

### 服務器上檢查

```bash
# 檢查 Docker 容器
docker-compose -f server/docker-compose.spark.yml ps

# 查看日誌
docker-compose -f server/docker-compose.spark.yml logs -f

# 重啟服務
docker-compose -f server/docker-compose.spark.yml restart
```

## 📚 完整文檔

詳細部署和配置請參考:
- [DGX_SPARK_DEPLOYMENT.md](DGX_SPARK_DEPLOYMENT.md) - 完整部署指南
- [README.md](README.md) - 專案概覽

---

**就這麼簡單! 🎉**

從 Windows 11 遠端使用 SPARK 服務器上的 AI 查詢系統
