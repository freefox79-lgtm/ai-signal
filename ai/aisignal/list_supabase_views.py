import psycopg2
import os
from dotenv import load_dotenv

def list_supabase_views():
    print("Listing Supabase Views...")
    load_dotenv(".env.production")
    url = os.getenv("SUPABASE_DATABASE_URL")
    
    try:
        conn = psycopg2.connect(url, sslmode='require')
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.views 
                WHERE table_schema = 'public'
            """)
            views = cur.fetchall()
            print(f"✅ Found {len(views)} views in 'public' schema:")
            for v in views:
                print(f"- {v[0]}")
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    list_supabase_views()
