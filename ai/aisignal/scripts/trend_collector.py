import os
import sys
import time
import requests
from datetime import datetime

# Force OLLAMA_BASE_URL to localhost for this script (running on host)
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"

# Path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_connectors import APIConnectors
from agents.trend.trend_algorithm import TrendAnalyzer
from db_utils import get_db_connection

def collect_and_analyze_trends():
    print(f"🚀 [TrendCollector] Starting cycle at {datetime.now()}")
    
    try:
        connectors = APIConnectors()
        analyzer = TrendAnalyzer()
        
        # 1. Fetch Candidate Keywords (Seed List)
        # In a real scenario, we'd crawl scraping sites or use a fixed "monitoring list".
        # For now, we mix some 'static' monitoring words with 'dynamic' ones from existing sources.
        
        # A. Get Monitoring Candidates from Google Trends or News
        seed_keywords = []
        
        # Fetch basic Google Trends/Naver News to get a "pool" of words
        print("   ... Sourcing seed keywords")
        g_trends = connectors.fetch_google_trends() # Existing regular fetch
        seed_keywords.extend(g_trends)
        
        # Fetch recent YouTube trending titles to extract Nouns using basic split
        # (In prod, use a proper morphological analyzer like Mecab or the Local LLM)
        yt_trends = connectors.fetch_youtube_trends()
        for item in yt_trends:
            # Naive keyword extraction: Take first 2 words of title
            words = item['title'].split()[:2]
            seed_keywords.append(" ".join(words))

        # Deduplicate
        unique_candidates = list(set(seed_keywords))[:20] # Limit to 20 for this prototype loop
        print(f"   ... Candidates: {unique_candidates}")

        # 2. Gather Signal Metrics (Naver Datalab & YouTube Live)
        naver_signals = []
        youtube_signals = []
        
        # Bulk fetch Datalab (5 at a time)
        # Naver Datalab limits: 5 keyword groups per call.
        # We will just do one batch of top 5 for demo efficiency.
        batch_keywords = unique_candidates[:5] 
        
        print(f"   ... Fetching Naver Datalab for: {batch_keywords}")
        datalab_data = connectors.fetch_naver_datalab_search(batch_keywords)
        
        # Process Datalab Response
        # Response structure: {'startDate': '...', 'endDate': '...', 'results': [{'title': 'kw', 'data': [{'period': '...', 'ratio': 100}]}]}
        if datalab_data and 'results' in datalab_data:
            for res in datalab_data['results']:
                keyword = res['title']
                data_points = res['data'] # List of {period, ratio}
                
                if not data_points:
                    continue
                    
                # Extract history for Z-Score
                # Datalab returns daily granularity usually.
                # If we want "real-time" we might rely on the 'ratio' of the LAST point vs Average
                # For this MVP, we treat the 'ratio' history as our time series
                ratios = [d['ratio'] for d in data_points]
                current_val = ratios[-1]
                history_vals = ratios[:-1] if len(ratios) > 1 else ratios
                
                z_score = analyzer.calculate_z_score(current_val, history_vals)
                
                if z_score > 1.5: # Lower threshold for "Candidate"
                    naver_signals.append({
                        'keyword': keyword,
                        'z_score': z_score,
                        'current_vol': current_val,
                        'source': 'Naver'
                    })

        # Fetch YouTube Live for the same batch
        print(f"   ... Checking YouTube Live Signals")
        for kw in batch_keywords:
            live_items = connectors.fetch_youtube_live(kw)
            if len(live_items) > 0:
                # Velocity proxy: Number of live streams + Viewers (if available)
                # We assign a simple velocity score based on count
                velocity = len(live_items) * 2.0 # Arbitrary weight
                youtube_signals.append({
                    'keyword': kw,
                    'velocity': velocity,
                    'source': 'YouTube'
                })
                
        # 3. Algorithm Core: Cross-Ref & Ranking
        print("   ... Running Trend Algorithm (Z-Score + CrossRef)")
        merged_trends = analyzer.cross_reference_signals(naver_signals, youtube_signals)
        
        # 4. Clustering (Local LLM)
        print("   ... Clustering with Local LLM")
        try:
            final_trends = analyzer.cluster_keywords(merged_trends)
        except Exception as e:
            print(f"⚠️ Clustering failed: {e}")
            final_trends = merged_trends

        # 5. Enrich with Reasons (LLM) - Optional final polish
        # (The system already has 'related_insight' from various steps, ensuring it exists)
        for t in final_trends:
            if 'reason' not in t:
                 t['reason'] = f"Z-Score {t.get('z_score', 0):.1f} / Source: {t.get('source')}"

        # 6. Save to DB
        print(f"   ... Saving {len(final_trends)} trends to DB")
        analyzer.save_trends_to_db(final_trends)
        
        print("✅ Collection Cycle Complete.")
        
    except Exception as e:
        print(f"❌ [TrendCollector] Cycle failed: {e}")

if __name__ == "__main__":
    # Continuous Loop Mode (Default 10 mins)
    INTERVAL_SECONDS = 600
    
    print(f"🕰️ Trend Collector Service Started (Interval: {INTERVAL_SECONDS}s)")
    print(f"📍 Ollama URL: {os.environ.get('OLLAMA_BASE_URL')}")
    
    while True:
        collect_and_analyze_trends()
        print(f"💤 Sleeping for {INTERVAL_SECONDS} seconds...")
        time.sleep(INTERVAL_SECONDS)
