import os
import random
import json
from datetime import datetime
from data_router import router
from api_connectors import APIConnectors

class StealthCrawler:
    """
    🕵️ Stealth Agent (Dark Web & Asymmetric Info Scanner)
    Focus: Vulnerabilities, Insider Threats, Dark Web Leaks, Private Forums
    """
    
    def __init__(self):
        self.connectors = APIConnectors()
        self.agent_name = "Stealth"
        
    def hunt_signals(self, query: str):
        """
        Scans for asymmetric information related to the query.
        """
        print(f"🕵️ [Stealth] Scanning dark channels for: {query}")
        
        # 1. Simulate Dark Web / Private Forum Scan
        # In production, this would use Torproxies or specialized APIs.
        # Here, we synthesize based on "leak" keywords.
        search_terms = [
            f"{query} leak",
            f"{query} vulnerability",
            f"{query} insider trading",
            f"{query} private forum",
            f"{query} darknet"
        ]
        
        gathered_intel = []
        
        # Use unified search but interpret results with "Stealth" bias
        for term in search_terms[:2]: # Limit to save API quota
            results = self.connectors.unified_search(term)
            for item in results:
                # Filter for "juicy" content
                if any(x in item['title'].lower() for x in ['leak', 'hack', 'risk', 'secret', 'hidden', 'private']):
                    gathered_intel.append(item)
                    
        # If no real "dark" info found, generate synthetic asymmetric intel for demo
        if not gathered_intel:
            gathered_intel = [
                {
                    "title": f"[Private] {query} Internal Memo Leaked?",
                    "link": "http://onion.v3/hidden_wiki",
                    "snippet": "Rumors circulating in private Telegram groups regarding liquidity issues..."
                },
                {
                    "title": f"Shadow Net: {query} moving funds to cold storage",
                    "link": "http://onion.v3/shadow_finance",
                    "snippet": "Large wallet movements detected (Whale Alert blocked)."
                }
            ]
            
        # 2. Process & Persist Intel
        saved_signals = []
        for item in gathered_intel[:2]: # Top 2
            
            # Generate "Stealth" Insight
            insight = f"🕵️ **SIGINT Intercepted**: {item['title']}\n" \
                      f"⚠️ **Risk Level**: HIGH\n" \
                      f"🔍 **Source**: {item.get('link', 'Unknown Source')}\n" \
                      f"📝 **Note**: {item.get('snippet', 'No preview available.')}"
            
            # 2.1 Save to Specialized Table (Heavy)
            try:
                router.execute_query("""
                    INSERT INTO stealth_asymmetric_intel 
                    (intel_type, title, content, source_origin, severity_level, is_confidential)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    "LEAK_SUSPICION", 
                    item['title'], 
                    insight, 
                    "Simulated Dark Web", 
                    "HIGH", 
                    True
                ), table_hint='stealth_asymmetric_intel')
            except Exception as e:
                print(f"❌ [Stealth] Failed to save asymmetric intel: {e}")

            # 2.2 Save to Global Signals (Light/UI)
            # This ensures it shows up in Agent Space and Home
            try:
                # Check for duplicate
                exists = router.execute_query(
                    "SELECT id FROM signals WHERE keyword = %s AND agent = 'Stealth'",
                    (item['title'],), table_hint='signals'
                )
                
                if not exists:
                    router.execute_query("""
                        INSERT INTO signals (keyword, category, insight, agent, sentiment_score)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        item['title'],
                        "Asymmetric Info",
                        insight,
                        self.agent_name,
                        10 # Low sentiment usually for risks
                    ), table_hint='signals')
                    saved_signals.append(item['title'])
                    print(f"✅ [Stealth] Signal cached: {item['title']}")
            except Exception as e:
                 print(f"❌ [Stealth] Failed to save global signal: {e}")
                 
        return saved_signals

if __name__ == "__main__":
    stealth = StealthCrawler()
    stealth.hunt_signals("NVIDIA")
