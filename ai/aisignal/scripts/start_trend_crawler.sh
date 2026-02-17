#!/bin/bash

# Move to project root
cd "$(dirname "$0")/.."

# Activate virtual environment
source venv/bin/activate

# Set environment variables just in case
export OLLAMA_BASE_URL="http://localhost:11434"
# DATABASE_URL is now managed dynamically by DataRouter via .env.local

# Run the collector in loop mode
echo "🚀 Starting Trend Collector Service (10 min interval)..."
echo "logs: tail -f trend_collector.log"

nohup python3 -u scripts/trend_collector.py > trend_collector.log 2>&1 &

echo "✅ Service started with PID $!"
