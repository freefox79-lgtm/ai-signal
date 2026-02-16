
import os
import json
import sys
from dotenv import load_dotenv

# Add parent directory to path to import api_connectors
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_connectors import APIConnectors

def test_unified_trends():
    print("🧪 Testing Unified Trend Engine...")
    
    # Initialize Connectors
    # You can change mode to "MOCK" or "REAL" (if env vars set)
    connectors = APIConnectors(mode="REAL") 
    
    print(f"📊 Mode: {connectors.mode}")
    
    try:
        # 1. Test Unified Aggregator
        print("\n[1] Fetching Unified Trends...")
        trends = connectors.fetch_unified_trends()
        
        print(f"\n✅ Fetched {len(trends)} items.")
        
        print("\n[Top 5 Trends]")
        for i, item in enumerate(trends[:5]):
            print(f"{i+1}. [{item['type']}] {item['keyword']} (Score: {item['avg_score']}) - {item['source']}")
            
        # 2. Verify Source Diversity
        sources = set(t['source'] for t in trends)
        print(f"\n[Source Diversity] Found: {sources}")
        
        # 3. Check for specific types
        has_shopping = any(t['type'] == 'SHOPPING' for t in trends)
        has_viral = any(t['type'] == 'VIRAL' for t in trends)
        
        if has_shopping: print("✅ Shopping trends included.")
        else: print("⚠️ No Shopping trends found.")
        
        if has_viral: print("✅ Viral trends included.")
        else: print("⚠️ No Viral trends found (maybe quota or cache empty).")

    except Exception as e:
        print(f"❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    load_dotenv()
    test_unified_trends()
