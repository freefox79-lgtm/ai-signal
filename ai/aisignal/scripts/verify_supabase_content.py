import os
import sys
import psycopg2
from dotenv import load_dotenv

# Path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load tiered env
load_dotenv(".env.local")

db_url = os.getenv("SUPABASE_DATABASE_URL")

def verify():
    print(f"📡 Connecting to Supabase...")
    try:
        conn = psycopg2.connect(db_url)
        with conn.cursor() as cur:
            cur.execute("SELECT rank, keyword, avg_score, related_insight, status FROM active_realtime_trends ORDER BY rank LIMIT 5")
            rows = cur.fetchall()
            print("\n--- Live Supabase Trends ---")
            for row in rows:
                print(f"[{row[0]}] {row[1]} (Score: {row[2]})")
                print(f"    Status: {row[4]}")
                print(f"    Insight: {row[3][:100]}...")
                print("-" * 50)
        conn.close()
    except Exception as e:
        print(f"❌ Verification failed: {e}")

if __name__ == "__main__":
    verify()
