import psycopg2
import os
from dotenv import load_dotenv

def list_supabase_tables():
    print("Listing Supabase Tables...")
    load_dotenv(".env.production")
    url = os.getenv("SUPABASE_DATABASE_URL")
    
    try:
        conn = psycopg2.connect(url, sslmode='require')
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = cur.fetchall()
            print(f"✅ Found {len(tables)} tables in 'public' schema:")
            for t in tables:
                print(f"- {t[0]}")
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    list_supabase_tables()
