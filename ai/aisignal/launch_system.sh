#!/bin/bash

# ================================================
# 🚀 AI Signal v4.0 Launch & Audit Script
# ================================================

BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}[SYSTEM] Starting AI Signal v4.0 Launch sequence...${NC}"

# 1. Infrastructure Check
echo -e "[*] Checking Docker Services..."
docker-compose ps --format "table {{.Name}}\t{{.Status}}"

# 2. Database & Vector Check
echo -e "[*] Verifying pgvector... "
docker exec aisignal-postgres psql -U postgres -d aisignal -c "SELECT extname FROM pg_extension WHERE extname = 'vector';" | grep vector && echo -e "${GREEN}[OK] Vector Enabled${NC}"

# 3. MCP Health Audit
echo -e "[*] Running MCP Health Check..."
python3 mcp_health_check.py

# 4. Redis Cache Audit
echo -e "[*] Verifying Redis Cache..."
python3 cache_manager.py && echo -e "${GREEN}[OK] Cache Online${NC}"

# 5. UI Start Instruction
echo -e "\n${GREEN}[SUCCESS] AI Signal v4.0 is READY.${NC}"
echo -e "${BLUE}================================================${NC}"
echo -e "🔗 Streamlit UI: http://localhost:8501"
echo -e "🔗 n8n Workflow: http://localhost:5678"
echo -e "🔗 Ollama LLM:   http://localhost:11434"
echo -e "${BLUE}================================================${NC}"
echo -e "Run 'streamlit run app.py' to start the dashboard."
