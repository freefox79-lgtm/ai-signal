import os
import psycopg2
from data_router import router

def verify_tables():
    print("=== Database Table Verification (Hybrid Architecture) ===")
    
    # 1. Check Mac Mini (Local) Tables
    macmini_tables = ['raw_feeds', 'crawl_logs', 'signals', 'market_indices']
    print("\n[MAC MINI / LOCAL PG]")
    for table in macmini_tables:
        try:
            # We use a query that checks pg_catalog to see if table exists
            query = f"SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = '{table}');"
            result = router.execute_query(query, table_hint=table if table == 'raw_feeds' else 'macmini_default')
            exists = result[0][0] if result else False
            status = "✅ Created" if exists else "❌ NOT FOUND"
            print(f" - {table}: {status}")
        except Exception as e:
            print(f" - {table}: ❌ Error: {e}")

    # 2. Check Supabase (Cloud) Tables
    supabase_tables = ['signals', 'issues', 'market_indices', 'raw_feeds']
    print("\n[SUPABASE / CLOUD PG]")
    for table in supabase_tables:
        try:
            query = f"SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = '{table}');"
            # Force routing to Supabase
            result = router.execute_query(query, table_hint='signals') 
            exists = result[0][0] if result else False
            status = "✅ Created" if exists else "❌ NOT FOUND"
            print(f" - {table}: {status}")
        except Exception as e:
            print(f" - {table}: ❌ Error: {e}")

    print("\n=======================================================")

if __name__ == "__main__":
    verify_tables()
