import os
import sys
from psycopg2.extras import Json
from data_router import router

def save_market_data(indices):
    """
    Saves market indices as signals. 
    Routed to SUPABASE (Flash/Refined).
    """
    for key, data in indices.items():
        # Standardized signal format
        insight = f"Value: {data.get('value')}, Change: {data.get('change')}, Trend: {data.get('trend')}"
        
        # signals table is routed to Supabase by DataRouter
        router.execute_query("""
            INSERT INTO signals (category, keyword, insight, agent, updated_at, synced)
            VALUES (%s, %s, %s, %s, NOW(), TRUE)
            ON CONFLICT (keyword) DO UPDATE 
            SET insight = EXCLUDED.insight, updated_at = NOW(), synced = TRUE
        """, ('Market', key, insight, 'Jwem'), table_hint='signals')
    print(f"✅ [PERSISTENCE] Saved {len(indices)} market indices to Supabase.")

def save_trends(trends):
    """
    Saves raw SNS trends.
    Routed to MACMINI (Raw).
    """
    for trend in trends:
        # raw_feeds table is routed to Mac Mini by DataRouter
        router.execute_query("""
            INSERT INTO raw_feeds (platform, raw_content, captured_at, processed)
            VALUES (%s, %s, NOW(), FALSE)
        """, (trend.get('platform', 'Unknown'), Json(trend)), table_hint='raw_feeds')
    print(f"✅ [PERSISTENCE] Saved {len(trends)} SNS trends to Mac Mini.")
