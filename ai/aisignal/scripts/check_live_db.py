import os
import sys
from dotenv import load_dotenv

# Path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load env
if os.path.exists(".env.local"):
    load_dotenv(".env.local")
else:
    load_dotenv()

from db_utils import get_db_connection

def check_db():
    db_url = os.getenv("DATABASE_URL")
    print(f"🚀 DB URL: {db_url}")
    try:
        conn = get_db_connection(db_url)
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM active_realtime_trends")
            count = cur.fetchone()[0]
            print(f"✅ Total trends: {count}")
            
            if count > 0:
                # Also check the latest update timestamp
                cur.execute("SELECT MAX(created_at) FROM active_realtime_trends")
                latest = cur.fetchone()[0]
                print(f"⏰ Latest update in DB: {latest}")

                cur.execute("SELECT rank, keyword, avg_score, created_at FROM active_realtime_trends ORDER BY rank LIMIT 10")
                rows = cur.fetchall()
                print("\n--- Current Trends ---")
                for row in rows:
                    print(f"[{row[0]}] {row[1]}: {row[2]} (Created: {row[3]})")
            else:
                print("⚠️ Table is empty!")
        conn.close()
    except Exception as e:
        print(f"❌ DB Check failed: {e}")

if __name__ == "__main__":
    check_db()
