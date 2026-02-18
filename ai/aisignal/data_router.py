import os
import psycopg2
from urllib.parse import urlparse, parse_qs, urlunparse
from dotenv import load_dotenv

# Load environment variables (WITHOUT OVERRIDE to respect Docker/System env)
if os.path.exists(".env.local"):
    load_dotenv(".env.local", override=False)
else:
    load_dotenv(override=False)


class DataRouter:
    """
    Intelligent Data Router for AI Signal Hybrid Architecture.
    Routes queries between Supabase (Frontend/Light) and Mac Mini (Factory/Heavy).
    """
    
    # Routing Tables
    SUPABASE_TABLES = [
        'ai_signals', 'trending_top_20', 'system_status', 
        'daily_briefings', 'portfolio_summary', 'user_settings',
        'signals', 'issues', 'market_indices', 'active_realtime_trends',
        'raw_feeds' 
    ]
    
    MACMINI_TABLES = [
        'crawl_logs', 'social_media_posts',
        'graph_rag_nodes', 'vector_embeddings', 'market_analysis_details',
        'market_macro_correlations', 'origin_tracking', 'stealth_asymmetric_intel',
        'intel_persona_reports', 'intel_synthetic_spatial'
    ]

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_DATABASE_URL")
        self.macmini_url = os.getenv("DATABASE_URL")
        
        if not self.supabase_url:
            # Fallback if specific var missing - use Mac Mini URL but ensure it's not None
            self.supabase_url = self.macmini_url or "postgresql://postgres:postgres@localhost:5432/aisignal"
            
    def get_connection(self, table_name: str = None):
        """
        Returns a database connection based on the table name.
        """
        route = self.get_route(table_name)
        url = self.supabase_url if route == "SUPABASE" else self.macmini_url
        
        try:
            if url and ('supabase' in url or 'pooler' in url):
                return psycopg2.connect(url, sslmode='require')
            if url:
                return psycopg2.connect(url)
            raise ValueError(f"Database URL for {route} is None")

        except Exception as e:
            print(f"❌ [DataRouter] Connection Error ({route}): {e}")
            # Final fallback to Mac Mini if Supabase fails (or vice-versa)
            return psycopg2.connect(self.macmini_url)

    def get_route(self, table_name: str) -> str:
        """
        Decides the target destination based on table classification.
        """
        if not table_name:
            return "SUPABASE" # Default to light layer
            
        t = table_name.lower()
        if t in self.SUPABASE_TABLES:
            return "SUPABASE"
        if t in self.MACMINI_TABLES:
            return "MACMINI"
            
        # Default policy: If unknown, check if it's a 'log' or 'raw' table
        if 'raw' in t or 'log' in t or 'feed' in t or 'embed' in t:
            return "MACMINI"
            
        return "SUPABASE"

    def execute_query(self, query: str, params: tuple = None, table_hint: str = None):
        """
        Helper to execute query on the correct router.
        """
        conn = self.get_connection(table_hint)
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                if query.strip().lower().startswith("select"):
                    return cur.fetchall()
                conn.commit()
                return True
        finally:
            conn.close()

# Singleton instance
router = DataRouter()
