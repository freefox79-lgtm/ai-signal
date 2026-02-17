import os
import sys
from dotenv import load_dotenv

# Path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load tiered env
load_dotenv(".env.local")

from api_connectors import APIConnectors

def test_youtube():
    print(f"📡 YouTube Key: {os.getenv('YOUTUBE_API_KEY')}")
    connectors = APIConnectors()
    print("🚀 Fetching YouTube Trends...")
    results = connectors.fetch_youtube_trends()
    if results:
        print(f"✅ SUCCESS: Found {len(results)} videos!")
        for r in results[:3]:
            print(f" - {r['title']} ({r['channel']})")
    else:
        print("❌ FAILED: No results or key missing.")

if __name__ == "__main__":
    test_youtube()
