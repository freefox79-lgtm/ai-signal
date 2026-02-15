import os
import psycopg2
from agents.jwem.portfolio_tracker import JwemPortfolio
from agents.jfit.trend_hunter import JfitTrendHunter
from api_connectors import APIConnectors
from cache_manager import CacheManager
from agents.sync_worker import SyncWorker

class Orchestrator:
    """
    Main coordinator for AI Signal agents.
    Manages data flow between crawlers, analyzers, and the hybrid DB sync.
    """
    def __init__(self):
        self.connectors = APIConnectors()
        self.cache = CacheManager()
        self.jwem = JwemPortfolio()
        self.jfit = JfitTrendHunter()
        self.sync_worker = SyncWorker()

    def process_signal_request(self, query):
        """
        Full Data Pipeline:
        1. Fetch real-time trends via Jfit
        2. Sync Portfolio health via Jwem
        3. Persist insights locally
        4. Trigger Cloud Sync
        """
        print(f"[ORCHESTRATOR] Starting Hybrid Pipeline for: {query}")
        
        # 1. Jfit: Trends
        trends = self.jfit.hunt_trends(query)
        
        # 2. Jwem: Portfolio Update
        self.jwem.update_prices()
        
        # 3. Persist Trends locally for Syncing
        conn = get_db_connection(os.getenv("DATABASE_URL"))
        with conn.cursor() as cur:
            for trend in trends:
                cur.execute("""
                    INSERT INTO signals (keyword, category, insight, agent, synced)
                    VALUES (%s, %s, %s, %s, FALSE)
                    ON CONFLICT (keyword) DO UPDATE SET
                        insight = EXCLUDED.insight,
                        synced = FALSE,
                        updated_at = NOW()
                """, (trend['content'], "TREND", trend['content'], "Jfit"))
        conn.commit()
        conn.close()
        
        # 4. Sync: Push to Cloud
        self.sync_worker.sync_to_supabase()
        
        return trends

if __name__ == "__main__":
    orch = Orchestrator()
    orch.process_signal_request("AI Signal Inc.")

