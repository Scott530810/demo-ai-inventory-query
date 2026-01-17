# DGX SPARK 部署指南

從 Windows 11 筆電遠端連線到 DGX SPARK 服務器

## 📋 目錄

1. [系統架構](#系統架構)
2. [服務器端設置 (DGX SPARK)](#服務器端設置)
3. [客戶端設置 (Windows 11)](#客戶端設置)
4. [遠端連線方式](#遠端連線方式)
5. [使用方式](#使用方式)
6. [故障排除](#故障排除)

---

## 🏗️ 系統架構

```
┌─────────────────────────────────────────────────────────────┐
│                     Windows 11 筆電                         │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ PowerShell   │  │ Python Client│  │  SSH Tunnel  │     │
│  │   Client     │  │              │  │              │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                 │              │
│         └─────────────────┴─────────────────┘              │
│                           │                                │
│                           │ HTTP/SSH                       │
└───────────────────────────┼────────────────────────────────┘
                            │
                    Internet/LAN
                            │
┌───────────────────────────┼────────────────────────────────┐
│                           │                                │
│                  DGX SPARK 服務器                          │
│                           │                                │
│  ┌────────────────────────▼──────────────────────────┐    │
│  │          FastAPI Server (Port 8000)               │    │
│  │                                                    │    │
│  │  ┌─────────────┐    ┌──────────────┐             │    │
│  │  │ Query Engine│───▶│ Ollama Client│             │    │
│  │  │             │    │ (qwen3:30b)  │             │    │
│  │  └──────┬──────┘    └──────────────┘             │    │
│  │         │                                         │    │
│  │         ▼                                         │    │
│  │  ┌─────────────┐                                 │    │
│  │  │ DB Client   │                                 │    │
│  │  └──────┬──────┘                                 │    │
│  └─────────┼────────────────────────────────────────┘    │
│            │                                              │
│  ┌─────────▼─────────┐      ┌──────────────────┐        │
│  │  PostgreSQL DB    │      │  Ollama Service  │        │
│  │                   │      │  (qwen3:30b)     │        │
│  └───────────────────┘      └──────────────────┘        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 🖥️ 服務器端設置

### 步驟 1: 系統需求

**硬體需求:**
- CPU: 8 核心以上
- RAM: 32GB 以上
- GPU: NVIDIA GPU (建議 16GB+ VRAM for qwen3:30b)
- 儲存: 100GB+ 可用空間

**軟體需求:**
- Ubuntu 20.04 LTS 或更新版本
- Python 3.11+
- PostgreSQL 15+
- Ollama
- SSH Server

### 步驟 2: 安裝基礎環境

```bash
# 更新系統
sudo apt update && sudo apt upgrade -y

# 安裝 Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# 安裝 PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# 安裝 SSH Server (如果還沒有)
sudo apt install -y openssh-server
sudo systemctl enable ssh
sudo systemctl start ssh

# 安裝 Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 下載 qwen3:30b 模型
ollama pull qwen3:30b
```

### 步驟 3: 上傳專案文件到 SPARK

**方式 A: 使用 Git (推薦)**

```bash
# 在 SPARK 服務器上
cd /opt
sudo git clone https://github.com/Scott530810/demo-ai-inventory-query.git
cd demo-ai-inventory-query
```

**方式 B: 使用 SCP 從 Windows 11**

```powershell
# 在 Windows 11 上
scp -r "c:\Users\scott\Desktop\files (1)" scott@SPARK_IP:/opt/ambulance-inventory
```

**方式 C: 使用 WinSCP**

1. 下載安裝 WinSCP: https://winscp.net/
2. 連線到 SPARK 服務器
3. 上傳整個專案資料夾到 `/opt/ambulance-inventory`

### 步驟 4: 配置資料庫

```bash
# 切換到 postgres 用戶
sudo -u postgres psql

# 在 PostgreSQL 中執行
CREATE DATABASE ambulance_db;
CREATE USER ambulance WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE ambulance_db TO ambulance;

# 退出
\q

# 匯入資料
psql -U ambulance -d ambulance_db -f /opt/ambulance-inventory/ambulance_equipment.sql
```

### 步驟 5: 設置 Python 環境

```bash
cd /opt/ambulance-inventory

# 創建虛擬環境
python3.11 -m venv venv
source venv/bin/activate

# 安裝依賴
pip install --upgrade pip
pip install -r server/requirements.txt
```

### 步驟 6: 配置環境變數

```bash
# 創建 .env 文件
cat > .env << EOF
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ambulance_db
DB_USER=ambulance
DB_PASSWORD=your_secure_password

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3:30b
OLLAMA_TIMEOUT=120

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
EOF

# 設置權限
chmod 600 .env
```

### 步驟 7: 測試服務器

```bash
# 測試資料庫連接
python run_refactored.py --check

# 測試 API 服務器 (前台運行)
python -m uvicorn server.api_server:app --host 0.0.0.0 --port 8000

# 在另一個終端測試
curl http://localhost:8000/health
```

### 步驟 8: 部署為系統服務 (Production)

```bash
# 使用部署腳本
sudo chmod +x server/deploy_to_spark.sh
sudo ./server/deploy_to_spark.sh

# 或手動創建 systemd 服務
sudo nano /etc/systemd/system/ambulance-api.service
```

服務文件內容:

```ini
[Unit]
Description=Ambulance Inventory Query API
After=network.target postgresql.service

[Service]
Type=simple
User=ambulance
WorkingDirectory=/opt/ambulance-inventory
Environment="PATH=/opt/ambulance-inventory/venv/bin"
EnvironmentFile=/opt/ambulance-inventory/.env
ExecStart=/opt/ambulance-inventory/venv/bin/uvicorn server.api_server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

啟動服務:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ambulance-api
sudo systemctl start ambulance-api
sudo systemctl status ambulance-api

# 查看日誌
sudo journalctl -u ambulance-api -f
```

### 步驟 9: 配置防火牆

```bash
# 允許 SSH (port 22)
sudo ufw allow 22/tcp

# 允許 API (port 8000) - 選項 1: 對所有 IP 開放
sudo ufw allow 8000/tcp

# 選項 2: 只對特定 IP 開放 (更安全)
sudo ufw allow from YOUR_WINDOWS11_IP to any port 8000 proto tcp

# 啟用防火牆
sudo ufw enable
sudo ufw status
```

---

## 💻 客戶端設置 (Windows 11)

### 步驟 1: 安裝 Python (如果使用 Python 客戶端)

1. 下載 Python 3.11+: https://www.python.org/downloads/
2. 安裝時勾選 "Add Python to PATH"

### 步驟 2: 安裝 OpenSSH Client (用於 SSH 隧道)

```powershell
# 檢查是否已安裝
Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Client*'

# 如果沒有,安裝
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0

# 或通過 GUI:
# Settings > Apps > Optional Features > Add a feature > OpenSSH Client
```

### 步驟 3: 設置 SSH 金鑰認證 (可選但推薦)

```powershell
# 生成 SSH 金鑰
ssh-keygen -t ed25519 -C "scott@windows11"

# 複製公鑰到 SPARK 服務器
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh scott@SPARK_IP "cat >> ~/.ssh/authorized_keys"
```

### 步驟 4: 配置客戶端腳本

**編輯 PowerShell 客戶端:**

```powershell
# 編輯 connect_to_spark.ps1
notepad client\connect_to_spark.ps1

# 修改這一行:
$SparkIP = "SPARK_IP_HERE"  # 改為實際的 SPARK IP,例如 "192.168.1.100"
```

**編輯 Python 客戶端:**

```powershell
# 編輯 spark_client.py
notepad client\spark_client.py

# 修改這一行:
host: str = "SPARK_IP_HERE"  # 改為實際的 SPARK IP
```

**編輯 SSH 隧道腳本:**

```powershell
# 編輯 ssh_tunnel.ps1
notepad client\ssh_tunnel.ps1

# 修改:
$SparkIP = "SPARK_IP_HERE"  # 改為實際的 SPARK IP
$SparkUser = "your_username"  # 改為您的 SPARK 用戶名
```

---

## 🌐 遠端連線方式

### 方式 1: 直接 HTTP 連線 (適合內網)

**條件:**
- Windows 11 和 SPARK 在同一內網
- SPARK 防火牆允許 port 8000

**使用方式:**

```powershell
# PowerShell 客戶端
.\client\connect_to_spark.ps1 -SparkIP 192.168.1.100

# Python 客戶端
python client\spark_client.py --host 192.168.1.100 --interactive

# 瀏覽器
# 開啟 http://192.168.1.100:8000/docs
```

### 方式 2: SSH 隧道 (適合外網或更安全)

**條件:**
- 需要 SSH 訪問權限
- 更安全,所有流量加密

**建立隧道:**

```powershell
# 方式 A: 使用腳本
.\client\ssh_tunnel.ps1 -SparkIP 192.168.1.100 -SparkUser scott

# 方式 B: 手動建立
ssh -L 8000:localhost:8000 scott@192.168.1.100 -N
```

**使用隧道後:**

```powershell
# 然後使用 localhost 連接
.\client\connect_to_spark.ps1 -SparkIP localhost

# 或 Python
python client\spark_client.py --host localhost --interactive

# 或瀏覽器
# http://localhost:8000/docs
```

### 方式 3: VPN 連線 (企業環境)

如果有 VPN,先連接 VPN,然後使用方式 1。

---

## 🎮 使用方式

### PowerShell 客戶端

```powershell
# 互動模式
.\client\connect_to_spark.ps1 -SparkIP 192.168.1.100

# 單一查詢
.\client\connect_to_spark.ps1 -SparkIP 192.168.1.100 -Question "請問AED除顫器還有哪幾款有庫存？"
```

### Python 客戶端

```bash
# 互動模式
python client\spark_client.py --host 192.168.1.100 --interactive

# 單一查詢
python client\spark_client.py --host 192.168.1.100 --query "請問AED除顫器還有哪幾款有庫存？"

# 健康檢查
python client\spark_client.py --host 192.168.1.100 --health
```

### Web 介面

```
http://SPARK_IP:8000/docs
```

或通過 SSH 隧道:

```
http://localhost:8000/docs
```

### API 調用範例

**使用 PowerShell:**

```powershell
$body = @{
    question = "請問AED除顫器還有哪幾款有庫存？"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://192.168.1.100:8000/query" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

**使用 Python:**

```python
import requests

response = requests.post(
    "http://192.168.1.100:8000/query",
    json={"question": "請問AED除顫器還有哪幾款有庫存？"}
)

result = response.json()
print(result["answer"])
```

**使用 curl:**

```bash
curl -X POST "http://192.168.1.100:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "請問AED除顫器還有哪幾款有庫存？"}'
```

---

## 🔧 故障排除

### 問題 1: 無法連接到 SPARK 服務器

**檢查步驟:**

```powershell
# 1. 測試網路連通性
ping SPARK_IP

# 2. 測試 port 8000 是否開放
Test-NetConnection -ComputerName SPARK_IP -Port 8000

# 3. 測試 SSH (如果使用 SSH 隧道)
ssh scott@SPARK_IP "echo 'Connection OK'"
```

**可能原因:**
- SPARK 防火牆阻擋
- API 服務未啟動
- IP 地址錯誤

**解決方案:**

```bash
# 在 SPARK 上檢查服務
sudo systemctl status ambulance-api

# 檢查 API 是否監聽
sudo netstat -tulpn | grep 8000

# 檢查防火牆
sudo ufw status

# 測試本地 API
curl http://localhost:8000/health
```

### 問題 2: API 回應超時

**可能原因:**
- Ollama 模型未啟動
- 資料庫連接問題
- 查詢太複雜

**解決方案:**

```bash
# 檢查 Ollama
ollama list
ollama serve  # 如果沒有運行

# 檢查資料庫
psql -U ambulance -d ambulance_db -c "SELECT 1;"

# 查看 API 日誌
sudo journalctl -u ambulance-api -n 50
```

### 問題 3: SSH 隧道建立失敗

**可能原因:**
- SSH 服務未啟動
- 認證失敗
- Port 已被佔用

**解決方案:**

```bash
# 在 SPARK 上檢查 SSH
sudo systemctl status ssh

# 檢查 SSH 日誌
sudo tail -f /var/log/auth.log

# 在 Windows 11 上檢查 port 佔用
netstat -ano | findstr :8000

# 殺掉佔用 port 的程序
taskkill /PID <PID> /F
```

### 問題 4: 查詢失敗或結果錯誤

**檢查步驟:**

```bash
# 在 SPARK 上手動測試
source venv/bin/activate
python run_refactored.py --check
python run_refactored.py --demo
```

**查看詳細日誌:**

```bash
# API 日誌
sudo journalctl -u ambulance-api -f

# 或如果前台運行
python -m uvicorn server.api_server:app --host 0.0.0.0 --port 8000 --log-level debug
```

---

## 🔐 安全建議

### 1. 使用 HTTPS (生產環境必須)

```bash
# 安裝 nginx 作為反向代理
sudo apt install -y nginx certbot python3-certbot-nginx

# 配置 nginx
sudo nano /etc/nginx/sites-available/ambulance-api

# 配置內容:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# 啟用站點
sudo ln -s /etc/nginx/sites-available/ambulance-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 安裝 SSL 證書
sudo certbot --nginx -d your-domain.com
```

### 2. IP 白名單

```python
# 在 api_server.py 添加中間件
from fastapi import Request
from fastapi.responses import JSONResponse

ALLOWED_IPS = ["192.168.1.100", "YOUR_WINDOWS11_IP"]

@app.middleware("http")
async def ip_whitelist_middleware(request: Request, call_next):
    client_ip = request.client.host
    if client_ip not in ALLOWED_IPS:
        return JSONResponse(status_code=403, content={"detail": "Forbidden"})
    return await call_next(request)
```

### 3. API 金鑰認證

```python
# 添加 API 金鑰認證
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

API_KEY = "your-secret-api-key"
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# 在端點中使用
@app.post("/query", dependencies=[Security(verify_api_key)])
async def query(request: QueryRequest):
    ...
```

### 4. 限流 (Rate Limiting)

```bash
pip install slowapi

# 在 api_server.py 添加
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/query")
@limiter.limit("10/minute")
async def query(request: Request, query_request: QueryRequest):
    ...
```

---

## 📊 監控和維護

### 日誌查看

```bash
# 實時查看 API 日誌
sudo journalctl -u ambulance-api -f

# 查看最近 100 行
sudo journalctl -u ambulance-api -n 100

# 查看特定時間
sudo journalctl -u ambulance-api --since "2026-01-17 10:00"
```

### 性能監控

```bash
# CPU 和記憶體使用
htop

# 查看 API 進程
ps aux | grep uvicorn

# 網路連接
sudo netstat -tulpn | grep 8000
```

### 備份

```bash
# 備份資料庫
pg_dump -U ambulance ambulance_db > backup_$(date +%Y%m%d).sql

# 備份配置
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env server/

# 自動化備份 (crontab)
0 2 * * * /opt/ambulance-inventory/backup.sh
```

---

## 🎯 快速參考

### SPARK 服務器常用命令

```bash
# 啟動/停止/重啟 API 服務
sudo systemctl start ambulance-api
sudo systemctl stop ambulance-api
sudo systemctl restart ambulance-api
sudo systemctl status ambulance-api

# 查看日誌
sudo journalctl -u ambulance-api -f

# 手動運行 (測試)
cd /opt/ambulance-inventory
source venv/bin/activate
python -m uvicorn server.api_server:app --host 0.0.0.0 --port 8000
```

### Windows 11 常用命令

```powershell
# PowerShell 客戶端
.\client\connect_to_spark.ps1 -SparkIP 192.168.1.100

# Python 客戶端
python client\spark_client.py --host 192.168.1.100 --interactive

# SSH 隧道
.\client\ssh_tunnel.ps1 -SparkIP 192.168.1.100 -SparkUser scott

# 測試連接
Test-NetConnection -ComputerName 192.168.1.100 -Port 8000
```

---

## 📞 需要幫助?

1. 查看 API 文檔: `http://SPARK_IP:8000/docs`
2. 查看健康狀態: `http://SPARK_IP:8000/health`
3. 查看服務日誌: `sudo journalctl -u ambulance-api -f`
4. 測試系統: `python run_refactored.py --check`

---

**版本**: 2.1.0
**更新日期**: 2026-01-17
**模型**: qwen3:30b
**部署環境**: DGX SPARK Server + Windows 11 Client
