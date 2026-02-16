import os
import psycopg2
from data_router import router

def check_data_counts():
    print("=== Data Destination Verification ===")
    
    # 1. Check 'signals' (Should be in Supabase)
    try:
        results = router.execute_query("SELECT COUNT(*) FROM signals", table_hint="signals")
        count = results[0][0] if results else 0
        print(f"📍 Table: signals | Destination: SUPABASE | Record Count: {count}")
    except Exception as e:
        print(f"❌ Error checking signals: {e}")

    # 2. Check 'raw_feeds' (Should be in Local PG)
    try:
        results = router.execute_query("SELECT COUNT(*) FROM raw_feeds", table_hint="raw_feeds")
        count = results[0][0] if results else 0
        print(f"📍 Table: raw_feeds | Destination: MACMINI | Record Count: {count}")
    except Exception as e:
        print(f"❌ Error checking raw_feeds: {e}")

    print("======================================")

if __name__ == "__main__":
    check_data_counts()
