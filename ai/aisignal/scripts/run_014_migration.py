import os
import psycopg2
from urllib.parse import urlparse

# Force Prod DB
DATABASE_URL = "postgresql://postgres.dlyquzckbwpjbquruhml:Fosl08281!!@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"

def run_migration():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        with open('migrations/014_add_signal_breakdown.sql', 'r') as f:
            sql = f.read()
            cur.execute(sql)
            
        conn.commit()
        print("✅ Migration 014 Success: Added signal_breakdown column")
        
    except Exception as e:
        print(f"❌ Migration Failed: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_migration()
