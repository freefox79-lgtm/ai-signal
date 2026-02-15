import os
import json
from api_connectors import APIConnectors
from dotenv import load_dotenv

load_dotenv(".env.local")

def test_youtube_integration():
    print("🚀 YouTube Data API Verification Start")
    
    # 1. Initialize connector (FORCE REAL mode for test)
    connectors = APIConnectors(mode="REAL")
    
    # 2. Test query
    query = "AI Signal"
    print(f"\n📡 Searching YouTube for: '{query}'...")
    
    try:
        results = connectors.fetch_youtube_trends(query)
        if results:
            print(f"✅ Success! Found {len(results)} videos.")
            for i, video in enumerate(results):
                print(f"  {i+1}. [{video['channel']}] {video['title']} (ID: {video['video_id']})")
        else:
            print("❌ No results found or API error.")
    except Exception as e:
        print(f"💥 Exception during fetch: {e}")

if __name__ == "__main__":
    test_youtube_integration()
