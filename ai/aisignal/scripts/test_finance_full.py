import os
import sys
from dotenv import load_dotenv

# Path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load env
if os.path.exists(".env.local"):
    load_dotenv(".env.local")
else:
    load_dotenv()

from api_connectors import APIConnectors

def test_full_finance():
    print("🚀 [Diagnostic] Testing Full Finance Signals (Upbit + Naver)")
    connectors = APIConnectors()
    
    # Force LIVE mode for testing if needed, or stick to .env
    print(f"Mode: {connectors.mode}")
    
    print("\n1. Fetching Finance Trends (Combined)...")
    results = connectors.fetch_finance_trends()
    
    if not results:
        print("❌ No results found. Check network or selectors.")
        return

    print(f"✅ Found {len(results)} financial signals.")
    
    # Group by source
    by_source = {}
    for r in results:
        src = r.get('source', 'Unknown')
        if src not in by_source:
            by_source[src] = []
        by_source[src].append(r)
        
    for src, items in by_source.items():
        print(f"\n--- Source: {src} ({len(items)} items) ---")
        for i, item in enumerate(items[:5]): # Top 5 per source
            print(f"[{i+1}] {item['keyword']}: Vol {item.get('finance_volatility')} | Info: {item.get('related_insight', 'N/A')}")

if __name__ == "__main__":
    test_full_finance()
