# DGX SPARK 部署指南

從 Windows 11 筆電遠端連線到 DGX SPARK 服務器

## 系統架構

```
┌─────────────────────────────────────────────────────────────┐
│                     Windows 11 筆電                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ PowerShell   │  │ Python Client│  │  SSH Tunnel  │     │
│  │   Client     │  │              │  │              │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         └─────────────────┴─────────────────┘              │
│                           │ HTTP/SSH                       │
└───────────────────────────┼────────────────────────────────┘
                            │
┌───────────────────────────┼────────────────────────────────┐
│                  DGX SPARK 服務器                          │
│  ┌────────────────────────▼──────────────────────────┐    │
│  │          FastAPI Server (Port 8000)               │    │
│  │  ┌─────────────┐    ┌──────────────┐             │    │
│  │  │ Query Engine│───▶│ Ollama Client│             │    │
│  │  └──────┬──────┘    └──────────────┘             │    │
│  │         ▼                                         │    │
│  │  ┌─────────────┐                                 │    │
│  │  │  PostgreSQL │                                 │    │
│  └──┴─────────────┴─────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

---

## 快速開始 (5 分鐘)

### 在 SPARK 服務器上

```bash
# 1. 克隆專案
cd /opt
sudo git clone https://github.com/Scott530810/demo-ai-inventory-query.git
cd demo-ai-inventory-query

# 2. 確保 Ollama 運行並下載模型
ollama pull llama3:70b
ollama serve &

# 3. 使用 Docker 部署
cd server
docker compose -f docker-compose.spark.yml up -d

# 4. 檢查服務狀態
curl http://localhost:8000/health

# 5. 開放防火牆
sudo ufw allow 8000/tcp
```

### 在 Windows 11 筆電上

```powershell
# 1. 編輯客戶端腳本,設置 SPARK IP
notepad client\connect_to_spark.ps1
# 修改: $SparkIP = "192.168.1.100"

# 2. 連接使用
.\client\connect_to_spark.ps1
```

---

## 服務器端設置

### 系統需求

- **CPU**: 8 核心以上
- **RAM**: 32GB 以上
- **GPU**: NVIDIA GPU (建議 16GB+ VRAM)
- **軟體**: Ubuntu 20.04+, Python 3.11+, PostgreSQL 15+, Ollama

### 手動安裝 (不使用 Docker)

```bash
# 安裝基礎環境
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql postgresql-contrib

# 安裝 Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3:70b

# 配置資料庫
sudo -u postgres psql
CREATE DATABASE ambulance_db;
CREATE USER ambulance WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ambulance_db TO ambulance;
\q

# 匯入資料
psql -U ambulance -d ambulance_db -f ambulance_inventory_demo.sql

# 設置 Python 環境
cd /opt/demo-ai-inventory-query
python3.11 -m venv venv
source venv/bin/activate
pip install -r server/requirements.txt

# 創建環境變數
cat > .env << EOF
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ambulance_db
DB_USER=ambulance
DB_PASSWORD=your_password
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3:70b
API_HOST=0.0.0.0
API_PORT=8000
EOF

# 啟動服務
python -m uvicorn server.api_server:app --host 0.0.0.0 --port 8000
```

### 部署為系統服務

```bash
# 創建 systemd 服務
sudo nano /etc/systemd/system/ambulance-api.service
```

```ini
[Unit]
Description=Ambulance Inventory Query API
After=network.target postgresql.service

[Service]
Type=simple
User=ambulance
WorkingDirectory=/opt/demo-ai-inventory-query
Environment="PATH=/opt/demo-ai-inventory-query/venv/bin"
EnvironmentFile=/opt/demo-ai-inventory-query/.env
ExecStart=/opt/demo-ai-inventory-query/venv/bin/uvicorn server.api_server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 啟動服務
sudo systemctl daemon-reload
sudo systemctl enable ambulance-api
sudo systemctl start ambulance-api
```

---

## 客戶端連線方式

### 方式 1: PowerShell 客戶端 (推薦)

```powershell
# 互動模式
.\client\connect_to_spark.ps1 -SparkIP 192.168.1.100

# 單一查詢
.\client\connect_to_spark.ps1 -SparkIP 192.168.1.100 -Question "請問AED有庫存嗎？"
```

### 方式 2: Python 客戶端

```bash
python client\spark_client.py --host 192.168.1.100 --interactive
python client\spark_client.py --host 192.168.1.100 --query "請問AED有庫存嗎？"
```

### 方式 3: Web 瀏覽器

```
http://192.168.1.100:8000/docs
```

### 方式 4: SSH 隧道 (外網訪問)

```powershell
# 建立 SSH 隧道
ssh -L 8000:localhost:8000 scott@192.168.1.100 -N

# 然後使用 localhost
.\client\connect_to_spark.ps1 -SparkIP localhost
```

---

## API 端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/health` | GET | 健康檢查 |
| `/query` | POST | 執行自然語言查詢 |
| `/tables` | GET | 取得資料表結構 |
| `/demo-queries` | GET | 取得範例查詢 |
| `/api/models` | GET | 取得可用模型列表 |
| `/api/models/select` | POST | 切換使用的模型 |

### 查詢範例

```bash
curl -X POST "http://192.168.1.100:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "請問AED除顫器還有哪幾款有庫存？"}'
```

---

## 故障排除

### 無法連接到 SPARK 服務器

```powershell
# 測試網路
ping 192.168.1.100
Test-NetConnection -ComputerName 192.168.1.100 -Port 8000
```

```bash
# 在 SPARK 上檢查
sudo systemctl status ambulance-api
sudo netstat -tulpn | grep 8000
sudo ufw status
```

### API 回應超時

```bash
# 檢查 Ollama
ollama list
ollama serve

# 檢查資料庫
psql -U ambulance -d ambulance_db -c "SELECT 1;"

# 查看 API 日誌
sudo journalctl -u ambulance-api -n 50
```

### Docker 容器問題

```bash
# 檢查容器狀態
docker compose -f server/docker-compose.spark.yml ps

# 查看日誌
docker compose -f server/docker-compose.spark.yml logs -f

# 重啟服務
docker compose -f server/docker-compose.spark.yml restart
```

---

## 安全建議

### 1. 使用 HTTPS

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 2. IP 白名單

```bash
sudo ufw allow from YOUR_WINDOWS11_IP to any port 8000 proto tcp
```

### 3. API 金鑰認證

在 `api_server.py` 中添加認證中間件。

---

## 檔案結構

```
demo-ai-inventory-query/
├── server/
│   ├── api_server.py              # FastAPI 服務器
│   ├── docker-compose.spark.yml   # SPARK Docker 配置
│   ├── Dockerfile.spark           # SPARK Docker 映像
│   ├── deploy_to_spark.sh         # 部署腳本
│   └── requirements.txt           # Python 依賴
├── client/
│   ├── connect_to_spark.ps1       # PowerShell 客戶端
│   ├── spark_client.py            # Python 客戶端
│   └── ssh_tunnel.ps1             # SSH 隧道腳本
└── ambulance_inventory/           # 核心模組
```

---

**版本**: 2.1.0
**更新日期**: 2026-01-18
