import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from agents.jwem.market_analyzer import JwemMarketAnalyzer
import asyncio

def populate_indices():
    print("🚀 Populating Market Indices...")
    jwem = JwemMarketAnalyzer()
    # This will fetch from APIs (AlphaVantage, etc.) and return dict
    # We need to save it to DB. Jwem's method returns dict but doesn't explicitly save to DB 
    # unless Orchestrator handles it.
    # Let's check Jwem code. _analyze_major_indices returns dict but also caches in Redis.
    # It seems Orchestrator or SyncWorker saves it.
    # I'll manually insert into DB for now to ensure data is there.
    
    indices = jwem._analyze_major_indices()
    print(f"Indices fetched: {indices}")
    
    # Save to SQLite/Postgres via DataRouter or direct
    try:
        from data_router import router
        
        for name, data in indices.items():
            # Clean value strings if needed
            val_str = str(data.get('value', 0)).replace(',', '')
            change_str = str(data.get('change', 0)).replace('%', '').replace('+', '')
            
            try:
                val = float(val_str)
            except:
                val = 0.0
                
            try:
                change = float(change_str)
            except:
                change = 0.0
            
            # Upsert
            router.execute_query(
                "INSERT INTO market_indices (name, value, change, updated_at) VALUES (%s, %s, %s, NOW()) "
                "ON CONFLICT (name) DO UPDATE SET value = EXCLUDED.value, change = EXCLUDED.change, updated_at = NOW()",
                (name, val, change),
                table_hint='market_indices'
            )
        print("✅ Market Indices Populated.")
    except Exception as e:
        print(f"❌ DB Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    populate_indices()
