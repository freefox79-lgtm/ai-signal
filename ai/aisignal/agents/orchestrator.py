import os
import psycopg2
from agents.jwem.market_analyzer import JwemMarketAnalyzer
from agents.jfit.trend_hunter import JfitTrendHunter
from agents.stealth_crawler import StealthCrawler
from api_connectors import APIConnectors
from cache_manager import CacheManager
from agents.sync_worker import SyncWorker
from agents.persistence import save_trends
from data_router import router

class Orchestrator:
    """
    Main coordinator for AI Signal agents.
    Manages data flow between crawlers, analyzers, and the hybrid DB sync.
    """
    def __init__(self):
        self.connectors = APIConnectors()
        self.cache = CacheManager()
        self.jwem = JwemMarketAnalyzer()
        self.jwem = JwemMarketAnalyzer()
        self.jfit = JfitTrendHunter()
        self.stealth = StealthCrawler()
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
        
        # 0. Stealth: Dark Web Scan (Asymmetric Intel)
        print(f"[ORCHESTRATOR] 🕵️ Starting Stealth Scan...")
        self.stealth.hunt_signals(query)

        # 1. Jfit: Trends
        trends = self.jfit.hunt_trends(query)
        
        # 2. Jwem: Portfolio Update
        self.jwem.update_prices()
        
        # 3. Persist Trends via Persistence Layer (Smart Routing)
        save_trends(trends)
        
        # 4. Sync: Push to Cloud (Backup sync)
        self.sync_worker.sync_to_supabase()
        
        return trends

if __name__ == "__main__":
    orch = Orchestrator()
    orch.process_signal_request("AI Signal Inc.")

