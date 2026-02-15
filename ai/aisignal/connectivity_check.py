import os
import requests
import psycopg2
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(".env.local")

def check_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or "your_supabase" in url:
        return "❌ Supabase URL not set"
    try:
        supabase: Client = create_client(url, key)
        # Try to fetch from a generic table or just check connectivity
        supabase.table("signals").select("id").limit(1).execute()
        return "✅ Supabase Connected"
    except Exception as e:
        return f"❌ Supabase Error: {e}"

def check_postgres():
    db_url = os.getenv("DATABASE_URL")
    try:
        conn = get_db_connection(db_url)
        conn.close()
        return "✅ Local PostgreSQL Connected"
    except Exception as e:
        return f"❌ Local DB Error: {e}"

def check_tunnel():
    token = os.getenv("CLOUDFLARE_TUNNEL_TOKEN")
    if not token or "your_cloudflare" in token:
        return "⚠️ Cloudflare Token not set (Tunnel will not start)"
    return "✅ Cloudflare Token detected"

if __name__ == "__main__":
    print("=== AI SIGNAL Inc. Connectivity Check ===")
    print(check_local_db())
    print(check_supabase())
    print(check_tunnel())
    print("=========================================")
