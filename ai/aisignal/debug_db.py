
import os
import json
import psycopg2
from dotenv import load_dotenv

def check_db():
    load_dotenv('.env.production')
    # Use the Supabase URL specifically
    db_url = os.getenv("SUPABASE_DATABASE_URL")
    if not db_url:
        print("SUPABASE_DATABASE_URL not found")
        return

    print(f"Connecting to: {db_url.split('@')[-1]}")
    try:
        conn = psycopg2.connect(db_url, sslmode='require')
        with conn.cursor() as cur:
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = cur.fetchall()
            print("Tables in public schema:")
            for t in tables:
                print(f"- {t[0]}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
