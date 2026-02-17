import os
import sys

# Add parent directory to path to import db_utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_utils import get_db_connection

def run_migration():
    print("🚀 Starting Migration: 013_add_trend_metrics.sql")
    
    # Load SQL file
    migration_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "migrations", "013_add_trend_metrics.sql")
    
    with open(migration_file, 'r') as f:
        sql = f.read()
        
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Split by statements if needed, or execute as one block
        cur.execute(sql)
        conn.commit()
        
        print("✅ Migration 013 executed successfully!")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
