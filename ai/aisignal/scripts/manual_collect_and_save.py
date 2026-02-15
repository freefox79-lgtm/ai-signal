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
from db_utils import get_db_connection

load_dotenv(".env.local")

def save_market_data(conn, indices):
    """Save market indices to signals table (or specialized table)"""
    with conn.cursor() as cur:
        for key, data in indices.items():
            # For simplicity, saving as signal for now. 
            # Ideally should be in market_indices table if created.
            insight = f"Value: {data.get('value')}, Change: {data.get('change')}, Trend: {data.get('trend')}"
            cur.execute("""
                INSERT INTO signals (category, keyword, insight, agent, updated_at, synced)
                VALUES (%s, %s, %s, %s, NOW(), FALSE)
                ON CONFLICT (keyword) DO UPDATE 
                SET insight = EXCLUDED.insight, updated_at = NOW(), synced = FALSE
            """, ('Market', key, insight, 'Jwem'))
    conn.commit()
    print(f"✅ Saved {len(indices)} market indices to DB")

def save_trends(conn, trends):
    """Save SNS trends to raw_feeds table"""
    with conn.cursor() as cur:
        for trend in trends:
            cur.execute("""
                INSERT INTO raw_feeds (platform, raw_content, captured_at, processed)
                VALUES (%s, %s, NOW(), FALSE)
            """, (trend.get('platform', 'Unknown'), Json(trend)))
    conn.commit()
    print(f"✅ Saved {len(trends)} SNS trends to DB")

def main():
    print("🚀 Starting Manual Data Collection...")
    conn = get_db_connection()
    
    # 1. Market Data
    try:
        print("\n📊 Collecting Market Data...")
        jwem = JwemMarketAnalyzer()
        indices = jwem._analyze_major_indices()
        if indices:
            save_market_data(conn, indices)
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
            save_trends(conn, real_trends)
        else:
            print("⚠️ No trends found. Check network or stealth-crawler logs.")
        
    except Exception as e:
        print(f"❌ SNS collection failed: {e}")

    conn.close()
    print("\n✨ Collection Complete!")

if __name__ == "__main__":
    main()
