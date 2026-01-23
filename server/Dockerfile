# AGC AI 庫存查詢系統 - Dockerfile
# FastAPI + Ollama

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ambulance_inventory/ /app/ambulance_inventory/
COPY server/ /app/server/

# Create non-root user
RUN useradd -m -u 1000 ambulance && \
    chown -R ambulance:ambulance /app

USER ambulance

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run API server
CMD ["uvicorn", "server.api_server:app", "--host", "0.0.0.0", "--port", "8000"]
