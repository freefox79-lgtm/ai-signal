import sys
import os
import time

# Path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_utils import get_db_connection

def verify_signal_breakdown():
    print("Test: Verifying signal_breakdown in active_realtime_trends...")
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT keyword, avg_score, signal_breakdown 
                FROM active_realtime_trends 
                LIMIT 5
            """)
            rows = cur.fetchall()
            
            if not rows:
                print("❌ No data found in active_realtime_trends.")
                return

            print(f"✅ Found {len(rows)} rows.")
            for row in rows:
                kw, score, breakdown = row
                print(f"   Keyword: {kw} | Score: {score} | Breakdown: {breakdown}")
                if not breakdown or breakdown == {}:
                    print("   ⚠️ Breakdown is empty!")
                else:
                    print("   ✅ Breakdown data confirmed.")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_signal_breakdown()
