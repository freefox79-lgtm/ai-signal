from data_router import router
import os

def test_supabase_sync():
    print("Testing Supabase Data Routing...")
    # This should go to Supabase based on the router config
    query = "SELECT rank, keyword FROM trending_top_20 ORDER BY rank LIMIT 5"
    try:
        results = router.execute_query(query, table_hint='trending_top_20')
        print(f"✅ Success! Found {len(results)} items from Supabase.")
        for r in results:
            print(f"- Rank {r[0]}: {r[1]}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_supabase_sync()
