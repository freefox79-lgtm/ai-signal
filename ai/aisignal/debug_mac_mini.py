
import os
import sys
from api_connectors import APIConnectors
from dotenv import load_dotenv

# Load env
load_dotenv(".env.local")

def debug_mac_mini():
    print("🚀 Debugging '맥미니' Search Results...")
    connectors = APIConnectors(mode="REAL")
    
    query = "맥미니"
    
    # 1. Unified Search (Naver + YouTube)
    print(f"\n🔍 Fetching raw results for '{query}'...")
    results = connectors.unified_search(query)
    
    print(f"✅ Fetched {len(results)} raw results.")
    for i, r in enumerate(results[:5]):
        print(f"[{i+1}] Source: {r.get('source')}")
        print(f"    Title: {r.get('title')}")
        print(f"    Snippet: {r.get('snippet')}")
        print("-" * 40)

    # 2. Enrich with CURRENT prompt
    print("\n🦙 Enriching with CURRENT prompt...")
    enriched = connectors.enrich_search_results_with_ollama(results[:3])
    for item in enriched:
        print(f"    [Enriched Title] {item.get('title')}")
        print(f"    [Enriched Summary] {item.get('snippet')}")

if __name__ == "__main__":
    debug_mac_mini()
