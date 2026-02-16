from fastapi import FastAPI, HTTPException, Body
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

# Import the collection logic
from agents.jwem.market_analyzer import JwemMarketAnalyzer
from agents.jfit.trend_hunter import JfitTrendHunter
from agents.persistence import save_market_data, save_trends
from data_router import router

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
        "system_status": SYSTEM_STATUS,
        "database_info": {
            "routes": {
                "signals": router.get_route("signals"),
                "raw_feeds": router.get_route("raw_feeds")
            }
        }
    }

@app.post("/control/status")
async def set_status(active: bool = Body(..., embed=True)):
    """Enables or disables data collection"""
    SYSTEM_STATUS["is_collecting"] = active
    return {"status": "success", "is_collecting": SYSTEM_STATUS["is_collecting"]}

@app.post("/collect/market")
async def collect_market_data():
    """Triggers Jwem Market Analysis and saves to DB"""
    if not SYSTEM_STATUS["is_collecting"]:
        return {"status": "skipped", "reason": "System is paused"}

    try:
        print("[API] Starting Market Collection...")
        jwem = JwemMarketAnalyzer()
        indices = jwem._analyze_major_indices()
        
        saved_count = 0
        if indices:
            save_market_data(indices)
            saved_count = len(indices)
            
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
    """Triggers Trending Analysis (Real Crawler)"""
    if not SYSTEM_STATUS["is_collecting"]:
        return {"status": "skipped", "reason": "System is paused"}

    try:
        print("[API] Starting Trend Collection...")
        jfit = JfitTrendHunter()
        # Query is now dynamic inside hunt_trends (via Google Trends)
        real_trends = jfit.hunt_trends("Auto_Daily_Trend") 
        
        if real_trends:
            save_trends(real_trends)
            count = len(real_trends)
            print(f"[API] Saved {count} real trends via DataRouter.")
        else:
            print("[API] No trends collected.")
            count = 0
        
        return {
            "status": "success",
            "data_type": "sns_trends",
            "items_collected": count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
