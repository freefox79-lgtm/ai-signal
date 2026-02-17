import os
import sys
import time
import requests
from datetime import datetime

# Force OLLAMA_BASE_URL to localhost for this script (running on host)
# This is crucial because 'localhost' inside this script refers to the Mac Mini
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"

# Path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_connectors import APIConnectors
from agents.trend.trend_algorithm import TrendAnalyzer
from db_utils import get_db_connection
from telegram_notifier import TelegramNotifier

# Persistent alert cache for the current session
sent_alerts = set()

def collect_and_analyze_trends():
    global sent_alerts
    print(f"🚀 [TrendCollector] Starting cycle at {datetime.now()}")
    
    try:
        connectors = APIConnectors()
        analyzer = TrendAnalyzer()
        
        # Unified Candidate Storage: {keyword: {signals...}}
        # We use a dictionary to merge signals for the same keyword from different sources
        candidates = {}
        
        def update_candidate(keyword, source_type, metric_value, meta=None):
            kw = keyword.strip()
            # Basic normalization (remove special chars if needed)
            import re
            kw = re.sub(r'[^\w\s]', '', kw).strip()
            
            if not kw:
                return

            if kw not in candidates:
                candidates[kw] = {
                    'keyword': kw,
                    'sources': set(),
                    'z_score': 0, 
                    'velocity': 0,
                    'sns_volume': 0,
                    'community_activity': 0,
                    'finance_volatility': 0,
                    'related_insight': ''
                }
            
            candidates[kw]['sources'].add(source_type)
            
            # Map metrics to standard fields
            if source_type == 'search':
                candidates[kw]['z_score'] = max(candidates[kw]['z_score'], metric_value)
            elif source_type == 'video':
                candidates[kw]['velocity'] = max(candidates[kw]['velocity'], metric_value)
            elif source_type == 'sns':
                candidates[kw]['sns_volume'] = max(candidates[kw]['sns_volume'], metric_value)
            elif source_type == 'community':
                candidates[kw]['community_activity'] = max(candidates[kw]['community_activity'], metric_value)
            elif source_type == 'finance':
                candidates[kw]['finance_volatility'] = max(candidates[kw]['finance_volatility'], metric_value)
            
            if meta and 'insight' in meta and not candidates[kw]['related_insight']:
                candidates[kw]['related_insight'] = meta['insight']

        # 1. Fetch Finance Trends (Upbit)
        print("   ... Fetching Finance Trends")
        finance_items = connectors.fetch_finance_trends()
        for item in finance_items:
            update_candidate(item['keyword'], 'finance', item['finance_volatility'])

        # 2. Fetch Community Trends (Mock/Scrape)
        print("   ... Fetching Community Trends")
        comm_items = connectors.fetch_community_trends()
        for item in comm_items:
            update_candidate(item['keyword'], 'community', item['community_activity'])

        # 3. Fetch Search Trends (Google/Naver)
        print("   ... Fetching Search Trends")
        g_trends = connectors.fetch_google_trends()
        # For Google Trends (which are just strings), we assign a default "New" score
        for kw in g_trends:
            update_candidate(kw, 'search', 3.0) # Z-Score 3.0 equivalent

        # 4. Fetch YouTube Trends
        print("   ... Fetching YouTube Trends")
        yt_trends = connectors.fetch_youtube_trends()
        for item in yt_trends:
            # View count parsing needed in real app, here we assume it's high
            update_candidate(item['title'], 'video', 8.0) # velocity 8.0

        # 5. Enrich with Phase 14 Precision (Naver Slope & Density)
        print("   ... Enriching Top Candidates (Slope & Density)")
        # Filter top 10 potential candidates to save API quota
        top_candidates = sorted(candidates.values(), 
            key=lambda x: max(x['z_score'], x['velocity'], x['finance_volatility']), 
            reverse=True)[:10]
        
        keywords_to_enrich = [c['keyword'] for c in top_candidates]
        
        if keywords_to_enrich:
            # A. Datalab Slope
            try:
                datalab_results = connectors.fetch_naver_datalab_search(keywords_to_enrich)
                for kw, data_points in datalab_results.items():
                    if data_points:
                        # Extract ratios [10, 20, 50...]
                        series = [d['ratio'] for d in data_points]
                        slope = analyzer.calculate_slope(series)
                        print(f"      - {kw}: Slope {slope:.2f}")
                        if kw in candidates:
                            candidates[kw]['slope'] = slope
            except Exception as e:
                print(f"⚠️ Datalab Enrichment Failed: {e}")

            # B. Blog Density (Posting Rate)
            for kw in keywords_to_enrich:
                try:
                    count = connectors.fetch_naver_blog_count(kw)
                    print(f"      - {kw}: Density {count}")
                    if kw in candidates:
                        candidates[kw]['search_density'] = count
                except Exception as e:
                    print(f"⚠️ Blog Density Check Failed for {kw}: {e}")

        # Run Analysis
        print(f"   ... Analyzing {len(candidates)} unique candidates")
        candidate_list = list(candidates.values())
        
        # Calculate Weighted Scores
        ranked_trends = analyzer.cross_reference_signals(candidate_list)
        
        # Cluster
        print("   ... Clustering with Local LLM")
        try:
            final_trends = analyzer.cluster_keywords(ranked_trends)
        except Exception as e:
            print(f"⚠️ Clustering failed: {e}")
            final_trends = ranked_trends
            
        # Enrich with Reasons (Briefing)
        print("   ... Generating Briefings (Top 10)")
        for i, t in enumerate(final_trends):
            # Only process top 10 for performance
            if i < 10:
                if 'related_insight' not in t or not t.get('related_insight'):
                     briefing = analyzer.generate_trend_briefing(
                         t['keyword'], 
                         t.get('slope', 0), 
                         t.get('search_density', 0),
                         t.get('members', [])
                     )
                     t['related_insight'] = briefing
                     print(f"      [{i+1}] {t['keyword']} -> Briefing Generated")
            
        for t in final_trends:
            source_list = list(t.get('sources', []))
            
            # Format breakdown string for easy reading
            breakdown = t.get('signal_breakdown', {})
            breakdown_str = " | ".join([f"{k[:3].upper()}:{v}" for k,v in breakdown.items() if v > 0])
            
            if 'reason' not in t:
                if breakdown_str:
                    t['reason'] = f"Signals: {breakdown_str}"
                else:
                    t['reason'] = f"Sources: {', '.join(source_list)}"
            
            # Serialize sources for DB (VARCHAR compatible)
            if 'sources' in t and isinstance(t['sources'], set):
                t['source'] = ','.join(t['sources'])

        # Save
        print(f"   ... Saving {len(final_trends)} trends to DB")
        analyzer.save_trends_to_db(final_trends)
        
        # 6. Telegram Alerting (Phase 16)
        print("   ... Checking for high-intensity alerts (>85)")
        notifier = TelegramNotifier()
        for t in final_trends:
            score = t.get('avg_score', 0)
            keyword = t.get('keyword', '')
            if score > 85 and keyword not in sent_alerts:
                briefing = t.get('related_insight', '인계 분석 대기 중...')
                breakdown = t.get('signal_breakdown', {})
                success = notifier.send_trend_alert(keyword, score, breakdown, briefing)
                if success:
                    sent_alerts.add(keyword)
        
        print("✅ Collection Cycle Complete.")
        
    except Exception as e:
        print(f"❌ [TrendCollector] Cycle failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Continuous Loop Mode
    INTERVAL_SECONDS = 600
    
    print(f"🕰️ Trend Collector Service Started (Interval: {INTERVAL_SECONDS}s)")
    print(f"📍 Ollama URL: {os.environ.get('OLLAMA_BASE_URL')}")
    print(f"🗄️ Database URL: {os.environ.get('DATABASE_URL')}")
    
    while True:
        collect_and_analyze_trends()
        print(f"💤 Sleeping for {INTERVAL_SECONDS} seconds...")
        time.sleep(INTERVAL_SECONDS)
