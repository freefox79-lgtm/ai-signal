import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api_connectors import APIConnectors

def test_ranking_pipeline():
    conn = APIConnectors()
    print("🚀 Starting AI Trend Ranking Pipeline Test...")
    
    # Check Ollama and Gemini access (if possible)
    print(f"Mode: {conn.mode}")
    
    try:
        trends = conn.fetch_unified_trends()
        print(f"\n✅ Pipeline completed! Found {len(trends)} ranked items.")
        
        for i, item in enumerate(trends):
            print(f"Rank {i+1}: {item['keyword']} | Score: {item.get('avg_score')}% | Source: {item['source']}")
            print(f"   Insight: {item.get('related_insight')}")
            print("-" * 50)
            
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ranking_pipeline()
