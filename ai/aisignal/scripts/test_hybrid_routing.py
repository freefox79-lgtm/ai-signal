import os
import sys
from dotenv import load_dotenv

# Path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load tiered env
load_dotenv(".env.local")

from data_router import router

def test_hybrid():
    print(f"📡 System Mode: {os.getenv('API_STATUS')}")
    print(f"🏠 Local DB: {os.getenv('DATABASE_URL')}")
    print(f"☁️ Cloud DB: {os.getenv('SUPABASE_DATABASE_URL')}")
    
    # 1. Test Local Routing (e.g., origin_tracking)
    route_raw = router.get_route("origin_tracking")
    print(f"\n🔍 Routing test for 'origin_tracking' (Macro): {route_raw}")
    
    # 2. Test Cloud Routing (active_realtime_trends)
    route_trend = router.get_route("active_realtime_trends")
    print(f"🔍 Routing test for 'active_realtime_trends' (Serving): {route_trend}")
    
    # 3. Connection Test
    try:
        conn = router.get_connection("active_realtime_trends")
        print("✅ SUCCESS: DataRouter connected to Supabase for trends!")
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM active_realtime_trends")
            print(f"📊 Trending Rows in Cloud: {cur.fetchone()[0]}")
        conn.close()
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    test_hybrid()

