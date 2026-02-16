#!/usr/bin/env python3
"""
Manual Data Collector & Saver
Runs collection scripts and saves results directly to local PostgreSQL.
Useful for initial population or backup when n8n is down.
"""
import sys
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import Json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from agents.jwem.market_analyzer import JwemMarketAnalyzer
from agents.jfit.trend_hunter import JfitTrendHunter
from data_router import router

load_dotenv(".env.local")

from agents.persistence import save_market_data, save_trends

def main():
    print("🚀 Starting Manual Data Collection...")
    
    # 1. Market Data
    try:
        print("\n📊 Collecting Market Data...")
        jwem = JwemMarketAnalyzer()
        indices = jwem._analyze_major_indices()
        if indices:
            save_market_data(indices)
    except Exception as e:
        print(f"❌ Market collection failed: {e}")

    # 2. SNS Trends (Mock Only for Speed if no API key/Headless setup issue)
    # Stealth crawler might fail in docker if dependencies missing.
    try:
        print("\n📱 Collecting SNS Trends (Real Crawler)...")
        jfit = JfitTrendHunter()
        
        # Real Crawler Call (Dynamic Keywords)
        real_trends = jfit.hunt_trends("Auto_Manual_Run")
        
        if real_trends:
            save_trends(real_trends)
        else:
            print("⚠️ No trends found. Check network or stealth-crawler logs.")
        
    except Exception as e:
        print(f"❌ SNS collection failed: {e}")

    print("\n✨ Collection Complete!")

if __name__ == "__main__":
    main()
