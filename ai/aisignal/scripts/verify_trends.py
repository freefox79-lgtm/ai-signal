import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_utils import get_db_connection

def verify_trends():
    print("🔍 Verifying 'active_realtime_trends' table...")
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM active_realtime_trends")
            count = cur.fetchone()[0]
            print(f"📊 Total Rows: {count}")
            
            cur.execute("""
                SELECT rank, keyword, avg_score, status, source, updated_at 
                FROM active_realtime_trends 
                ORDER BY rank ASC
            """)
            rows = cur.fetchall()
            
            if rows:
                print(f"{'Rank':<5} | {'Keyword':<20} | {'Score':<6} | {'Status':<10} | {'Source':<10} | {'Updated At'}")
                print("-" * 80)
                for row in rows:
                    # rank, keyword, score, status, source, updated_at
                    print(f"{row[0]:<5} | {row[1]:<20} | {row[2]:<6} | {row[3]:<10} | {row[4]:<10} | {row[5]}")
            else:
                print("⚠️ No data found!")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verify_trends()
