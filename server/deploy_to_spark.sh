#!/bin/bash
# Deploy to DGX SPARK Server
# 部署到 DGX SPARK 服務器

set -e

echo "🚀 Deploying Ambulance Inventory Query System to DGX SPARK..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/opt/ambulance-inventory"
SERVICE_NAME="ambulance-query-api"
SERVICE_USER="ambulance"
PYTHON_VERSION="3.11"

echo -e "${YELLOW}Step 1: Checking system requirements...${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 not found. Installing...${NC}"
    apt-get update
    apt-get install -y python3 python3-pip python3-venv
fi

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}PostgreSQL client not found. Installing...${NC}"
    apt-get install -y postgresql-client
fi

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}Ollama not found. Please install Ollama first:${NC}"
    echo "curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

echo -e "${GREEN}✅ System requirements check passed${NC}"

echo -e "${YELLOW}Step 2: Creating project directory...${NC}"

# Create project directory
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

echo -e "${GREEN}✅ Project directory created: $PROJECT_DIR${NC}"

echo -e "${YELLOW}Step 3: Setting up Python virtual environment...${NC}"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

echo -e "${GREEN}✅ Virtual environment created${NC}"

echo -e "${YELLOW}Step 4: Installing Python dependencies...${NC}"

# Install dependencies
pip install fastapi uvicorn[standard] pydantic psycopg2-binary requests python-dotenv

echo -e "${GREEN}✅ Dependencies installed${NC}"

echo -e "${YELLOW}Step 5: Creating service user...${NC}"

# Create service user if doesn't exist
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -s /bin/false $SERVICE_USER
    echo -e "${GREEN}✅ Service user created: $SERVICE_USER${NC}"
else
    echo -e "${YELLOW}Service user already exists: $SERVICE_USER${NC}"
fi

echo -e "${YELLOW}Step 6: Creating environment configuration...${NC}"

# Create .env file template
cat > $PROJECT_DIR/.env << EOF
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ambulance_db
DB_USER=postgres
DB_PASSWORD=your_password_here

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3:30b
OLLAMA_TIMEOUT=120

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
EOF

echo -e "${GREEN}✅ Environment template created: $PROJECT_DIR/.env${NC}"
echo -e "${YELLOW}⚠️  Please edit .env file with your actual configuration${NC}"

echo -e "${YELLOW}Step 7: Creating systemd service...${NC}"

# Create systemd service file
cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=Ambulance Inventory Query API Service
After=network.target postgresql.service

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$PROJECT_DIR/venv/bin/uvicorn server.api_server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ Systemd service created: ${SERVICE_NAME}.service${NC}"

echo -e "${YELLOW}Step 8: Configuring firewall...${NC}"

# Allow port 8000 through firewall (if ufw is installed)
if command -v ufw &> /dev/null; then
    ufw allow 8000/tcp
    echo -e "${GREEN}✅ Firewall configured (port 8000 opened)${NC}"
else
    echo -e "${YELLOW}UFW not installed, skipping firewall configuration${NC}"
fi

echo -e "${YELLOW}Step 9: Setting permissions...${NC}"

# Set ownership
chown -R $SERVICE_USER:$SERVICE_USER $PROJECT_DIR

echo -e "${GREEN}✅ Permissions set${NC}"

echo -e "${GREEN}🎉 Deployment completed!${NC}"
echo ""
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo "1. Copy your project files to: $PROJECT_DIR"
echo "2. Edit .env file: nano $PROJECT_DIR/.env"
echo "3. Ensure Ollama is running with qwen3:30b model:"
echo "   ollama pull qwen3:30b"
echo "   ollama serve"
echo "4. Start the service:"
echo "   systemctl daemon-reload"
echo "   systemctl enable ${SERVICE_NAME}"
echo "   systemctl start ${SERVICE_NAME}"
echo "5. Check service status:"
echo "   systemctl status ${SERVICE_NAME}"
echo "6. View logs:"
echo "   journalctl -u ${SERVICE_NAME} -f"
echo "7. Test API from remote Windows 11:"
echo "   http://SPARK_IP:8000/docs"
echo ""
echo -e "${YELLOW}🔐 Security Recommendations:${NC}"
echo "- Configure PostgreSQL authentication"
echo "- Set up SSL/TLS for API (use nginx as reverse proxy)"
echo "- Restrict API access by IP if possible"
echo "- Use strong database passwords"
echo "- Keep system and packages updated"
