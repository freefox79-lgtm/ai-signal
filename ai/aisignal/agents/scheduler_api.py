from fastapi import FastAPI, HTTPException, Body
import sys
import os
import asyncio
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

# Import the collection logic
from agents.jwem.market_analyzer import JwemMarketAnalyzer
from db_utils import get_db_connection
from scripts.manual_collect_and_save import save_market_data, save_trends
from scripts.sync_to_supabase import SupabaseSync

app = FastAPI(title="AI Signal Scheduler API")

# Global System State
SYSTEM_STATUS = {
    "is_collecting": True
}

@app.get("/")
def health_check():
    return {
        "status": "ok", 
        "service": "scheduler-api",
        "system_status": SYSTEM_STATUS
    }

@app.post("/control/status")
async def set_status(active: bool = Body(..., embed=True)):
    """Enables or disables data collection"""
    SYSTEM_STATUS["is_collecting"] = active
    return {"status": "success", "is_collecting": SYSTEM_STATUS["is_collecting"]}

@app.post("/sync")
async def trigger_sync():
    """Triggers Immediate Supabase Sync"""
    if not SYSTEM_STATUS["is_collecting"]:
        return {"status": "skipped", "reason": "System is paused"}
        
    try:
        print("[API] Starting Supabase Sync...")
        syncer = SupabaseSync()
        count = syncer.sync_all(mode='all')
        syncer.close()
        return {
            "status": "success",
            "synced_records": count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/collect/market")
async def collect_market_data():
    """Triggers Jwem Market Analysis and saves to DB"""
    if not SYSTEM_STATUS["is_collecting"]:
        return {"status": "skipped", "reason": "System is paused"}

    try:
        print("[API] Starting Market Collection...")
        conn = get_db_connection()
        jwem = JwemMarketAnalyzer()
        indices = jwem._analyze_major_indices()
        
        saved_count = 0
        if indices:
            save_market_data(conn, indices)
            saved_count = len(indices)
            
        conn.close()
        return {
            "status": "success", 
            "data_type": "market_indices",
            "items_collected": saved_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/collect/trends")
async def collect_trends():
    """Triggers Trending Analysis (Mock/Live)"""
    if not SYSTEM_STATUS["is_collecting"]:
        return {"status": "skipped", "reason": "System is paused"}

    try:
        print("[API] Starting Trend Collection...")
        conn = get_db_connection()
        
        mock_trends = [
            {"platform": "X", "content": f"Trend check at {datetime.now().strftime('%H:%M')}: AI Adoption"},
            {"platform": "Instagram", "content": "#DailyAIUpdate"},
            {"platform": "Community", "content": "Development in progress"}
        ]
        save_trends(conn, mock_trends)
        
        conn.close()
        return {
            "status": "success",
            "data_type": "sns_trends",
            "items_collected": len(mock_trends),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
