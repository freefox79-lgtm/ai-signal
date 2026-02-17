import os
import psycopg2
import sys

# Hardcoded for total isolation
DB_URL = "postgresql://postgres.dlyquzckbwpjbquruhml:Fosl08281!!@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"

def simple_test():
    print(f"🚀 Testing connection to Sydney: {DB_URL}")
    try:
        conn = psycopg2.connect(DB_URL, sslmode='require', connect_timeout=10)
        print("✅ SUCCESS: Connected to Supabase!")
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM active_realtime_trends")
            print(f"📊 Row count: {cur.fetchone()[0]}")
        conn.close()
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    simple_test()
