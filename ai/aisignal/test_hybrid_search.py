
import os
import sys
from api_connectors import APIConnectors
from dotenv import load_dotenv

# Load env
load_dotenv(".env.local")

def test_pipeline():
    print("🚀 Starting Hybrid Search Pipeline Test...")
    connectors = APIConnectors(mode="REAL")
    
    query = "AI Agent Trends"
    
    # 1. Unified Search (Naver + YouTube)
    print(f"\n🔍 1. Fetching results for '{query}'...")
    results = connectors.unified_search(query)
    
    print(f"✅ Fetched {len(results)} raw results.")
    has_naver = any(r['source'] == 'Naver' for r in results)
    has_youtube = any(r['source'] == 'YouTube' for r in results)
    
    print(f"   - Naver Present: {has_naver}")
    print(f"   - YouTube Present: {has_youtube}")
    
    if not results:
        print("❌ No results found. Check API Keys.")
        return

    # 2. Enriched Results (Llama)
    print("\n🦙 2. Enriching top 6 results with Local LLM...")
    enriched = connectors.enrich_search_results_with_ollama(results[:6])
    
    print(f"✅ Enriched {len(enriched)} results.")
    for i, item in enumerate(enriched):
        print(f"   [{i+1}] [{item['source']}] {item['title']} (Link: {item['link']})")
        print(f"       Summary: {item['snippet'][:50]}...")

    # 3. Gemini Analysis
    print("\n🧠 3. Generating Quantum Analysis with Gemini...")
    analysis = connectors.fetch_gemini_analysis(query, enriched)
    print(f"✅ Analysis Result:\n{analysis}")

if __name__ == "__main__":
    test_pipeline()
