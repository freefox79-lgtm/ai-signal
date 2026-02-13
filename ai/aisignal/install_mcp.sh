#!/bin/bash

# ================================================
# 🛠️ AI Signal MCP Auto-Installation Script v3.0
# Project Code: Antigravity-Alpha-2026
# ================================================

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}[MCP] Starting Full-Spectrum Installation for AI Signal...${NC}"

# 1. 환경 감지 및 필수 도구 확인
WORKDIR="$(pwd)/mcp_infrastructure"
mkdir -p "$WORKDIR"
cd "$WORKDIR" || exit

# 2. 서버별 맞춤형 설치 및 빌드
# [FILESYSTEM] - Reference
echo -e "${BLUE}[MCP] Setting up Filesystem Server...${NC}"
if [ ! -d "servers" ]; then
    git clone https://github.com/modelcontextprotocol/servers.git
fi
cd servers/src/filesystem && npm install && npm run build && cd ../../../

# [POSTGRES, PUPPETEER, GOOGLE-SEARCH] - Archived Reference
echo -e "${BLUE}[MCP] Setting up Archived Reference Servers...${NC}"
if [ ! -d "servers-archived" ]; then
    git clone https://github.com/modelcontextprotocol/servers-archived.git
fi

setup_archived() {
    local name=$1
    echo -e "[MCP] Building archived server: $name..."
    cd "servers-archived/src/$name" && npm install && npm run build && cd ../../../
}

setup_archived "postgres"
setup_archived "puppeteer"
setup_archived "google-search"

# [BRAVE SEARCH] - Official External
echo -e "${BLUE}[MCP] Setting up Brave Search Server...${NC}"
if [ ! -d "brave-search-mcp-server" ]; then
    git clone https://github.com/brave/brave-search-mcp-server.git
fi
cd brave-search-mcp-server && npm install && npm run build && cd ..

# 3. mcp-config.json 생성
echo -e "${BLUE}[MCP] Generating mcp-config.json...${NC}"

CONFIG_PATH="$(pwd)/../mcp-config.json"
ABS_PATH="$(pwd)"

cat <<EOF > "$CONFIG_PATH"
{
  "mcpServers": {
    "google-search": {
      "command": "node",
      "args": ["$ABS_PATH/servers-archived/src/google-search/dist/index.js"],
      "env": {
        "GOOGLE_API_KEY": "YOUR_API_KEY_HERE",
        "GOOGLE_CX": "YOUR_CX_HERE"
      }
    },
    "brave-search": {
      "command": "node",
      "args": ["$ABS_PATH/brave-search-mcp-server/dist/index.js"],
      "env": {
        "BRAVE_API_KEY": "YOUR_API_KEY_HERE"
      }
    },
    "puppeteer": {
      "command": "node",
      "args": ["$ABS_PATH/servers-archived/src/puppeteer/dist/index.js"]
    },
    "postgres": {
      "command": "node",
      "args": ["$ABS_PATH/servers-archived/src/postgres/dist/index.js"],
      "env": {
        "POSTGRES_URL": "postgresql://postgres:postgres@localhost:5432/postgres"
      }
    },
    "filesystem": {
      "command": "node",
      "args": ["$ABS_PATH/servers/src/filesystem/dist/index.js"],
      "env": {
        "ALLOWED_DIRECTORIES": ["/Users/freefox79gmail.com/개발프로젝트"]
      }
    }
  }
}
EOF

echo -e "${GREEN}[MCP] Full-Spectrum Installation Complete!${NC}"
echo -e "${GREEN}[MCP] Config generated at: $CONFIG_PATH${NC}"
