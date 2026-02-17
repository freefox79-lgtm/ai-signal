import os
import psycopg2

# Force Prod DB
DATABASE_URL = "postgresql://postgres.dlyquzckbwpjbquruhml:Fosl08281!!@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"

def run_migration():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Run 013 (Create Tables)
        print("▶️ Running 013_add_trend_metrics.sql...")
        with open('migrations/013_add_trend_metrics.sql', 'r') as f:
            cur.execute(f.read())
            
        # Run 014 (Add Column - might fail if already exists but 013 creates table so it should be fine or needed)
        # Actually 014 alters the table created in 013.
        print("▶️ Running 014_add_signal_breakdown.sql...")
        with open('migrations/014_add_signal_breakdown.sql', 'r') as f:
            cur.execute(f.read())
            
        conn.commit()
        print("✅ Full Migration Success!")
        
    except Exception as e:
        print(f"❌ Migration Failed: {e}")
        conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_migration()
