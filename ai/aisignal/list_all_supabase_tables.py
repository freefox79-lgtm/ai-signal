import psycopg2
import os
from dotenv import load_dotenv

def list_all_supabase_tables():
    print("Listing All Supabase Tables...")
    load_dotenv(".env.production")
    url = os.getenv("SUPABASE_DATABASE_URL")
    
    try:
        conn = psycopg2.connect(url, sslmode='require')
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
                ORDER BY table_schema, table_name
            """)
            tables = cur.fetchall()
            print(f"✅ Found {len(tables)} tables across all schemas:")
            for s, t in tables:
                print(f"- {s}.{t}")
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    list_all_supabase_tables()
