import os
import requests
import json
import time
from dotenv import load_dotenv
from cache_manager import CacheManager

load_dotenv(".env.local")

cache = CacheManager()

class APIConnectors:
    """
    Handles data retrieval from external APIs like Naver, Kakao, Alpha Vantage, etc.
    Supports transparent Redis caching and basic rate limiting.
    """
    
    def __init__(self):
        self.naver_id = os.getenv("NAVER_CLIENT_ID")
        self.naver_secret = os.getenv("NAVER_CLIENT_SECRET")
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.fred_key = os.getenv("FRED_API_KEY")
        self.mode = os.getenv("API_STATUS", "MOCK").upper()
        self.last_call_time = 0.0
        self.min_interval = 1.0  # Default 1s between calls to avoid rate limits
        
        # Load source registry from database
        self.source_registry = self._load_source_registry()
        self.db_url = os.getenv("DATABASE_URL")
    
    def _load_source_registry(self):
        """Load active API sources from database"""
        try:
            import psycopg2
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                print("[APIConnectors] DATABASE_URL not set, using hardcoded sources")
                return {}
            
            # Smart SSL detection
            if 'supabase' in db_url:
                conn = psycopg2.connect(db_url, sslmode='require')
            else:
                conn = psycopg2.connect(db_url)
            
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        source_name, 
                        api_endpoint, 
                        rate_limit_per_minute,
                        api_key_env,
                        id
                    FROM data_sources
                    WHERE source_type = 'API' AND is_active = TRUE
                """)
                registry = {}
                for row in cur.fetchall():
                    name, endpoint, rate_limit, key_env, source_id = row
                    registry[name] = {
                        "endpoint": endpoint,
                        "rate_limit": rate_limit or 60,
                        "api_key_env": key_env,
                        "source_id": source_id
                    }
            
            conn.close()
            print(f"[APIConnectors] Loaded {len(registry)} API sources from database")
            return registry
            
        except Exception as e:
            print(f"[APIConnectors] Error loading source registry: {e}")
            return {}
    
    def _update_source_health(self, source_name, success, response_time_ms=None, error_msg=None, error_code=None):
        """Update source health metrics after each API call"""
        if not self.db_url or source_name not in self.source_registry:
            return
        
        try:
            import psycopg2
            from datetime import datetime
            
            # Smart SSL detection
            if 'supabase' in self.db_url:
                conn = psycopg2.connect(self.db_url, sslmode='require')
            else:
                conn = psycopg2.connect(self.db_url)
            
            source_id = self.source_registry[source_name]['source_id']
            
            with conn.cursor() as cur:
                if success:
                    cur.execute("""
                        UPDATE source_health
                        SET last_success_at = NOW(),
                            consecutive_failures = 0,
                            avg_response_time_ms = COALESCE(
                                (avg_response_time_ms * 0.9 + %s * 0.1)::INTEGER, 
                                %s
                            ),
                            total_requests_24h = total_requests_24h + 1,
                            status = 'HEALTHY',
                            updated_at = NOW()
                        WHERE source_id = %s
                    """, (response_time_ms, response_time_ms, source_id))
                else:
                    cur.execute("""
                        UPDATE source_health
                        SET last_failure_at = NOW(),
                            consecutive_failures = consecutive_failures + 1,
                            last_error_message = %s,
                            last_error_code = %s,
                            total_requests_24h = total_requests_24h + 1,
                            status = CASE 
                                WHEN consecutive_failures + 1 >= 5 THEN 'DOWN'
                                WHEN consecutive_failures + 1 >= 2 THEN 'DEGRADED'
                                ELSE 'HEALTHY'
                            END,
                            updated_at = NOW()
                        WHERE source_id = %s
                    """, (error_msg, error_code, source_id))
                
                conn.commit()
            
            conn.close()
            
        except Exception as e:
            print(f"[APIConnectors] Error updating source health: {e}")

    def _throttle(self):
        """Simple throttling to respect rate limits."""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call_time = time.time()

    @cache.cached(source="Naver")
    def fetch_naver_search(self, query):
        """Fetches Naver Search results with transparent caching."""
        if self.mode == "MOCK":
            return [
                {"source": "Naver", "title": f"MOCK: {query} 관련 최신 트렌드", "link": "https://search.naver.com"},
                {"source": "Naver", "title": f"MOCK: {query} 뉴스 분석", "link": "https://news.naver.com"}
            ]
            
        self._throttle()
        url = "https://openapi.naver.com/v1/search/news.json"
        headers = {
            "X-Naver-Client-Id": self.naver_id,
            "X-Naver-Client-Secret": self.naver_secret
        }
        params = {"query": query, "display": 10, "start": 1, "sort": "sim"}
        
        start_time = time.time()
        try:
            response = requests.get(url, headers=headers, params=params)
            response_time_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                self._update_source_health("naver_search", True, response_time_ms)
                return response.json().get("items", [])
            else:
                self._update_source_health("naver_search", False, response_time_ms, 
                                          f"HTTP {response.status_code}", str(response.status_code))
                return []
        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            self._update_source_health("naver_search", False, response_time_ms, str(e), "EXCEPTION")
            print(f"[ERROR] Naver Fetch Failed: {e}")
            return []

    @cache.cached(source="CoinGecko", expiry=300)
    def fetch_crypto_prices(self, ids="bitcoin,ethereum,solana"):
        """Fetches real-time crypto prices from CoinGecko."""
        if self.mode == "MOCK":
            return {"bitcoin": {"usd": 50000}, "ethereum": {"usd": 2800}, "solana": {"usd": 105}}

        self._throttle()
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": ids, "vs_currencies": "usd", "include_24hr_change": "true"}
        
        start_time = time.time()
        try:
            response = requests.get(url, params=params)
            response_time_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                self._update_source_health("coingecko", True, response_time_ms)
                return response.json()
            else:
                self._update_source_health("coingecko", False, response_time_ms,
                                          f"HTTP {response.status_code}", str(response.status_code))
                return {}
        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            self._update_source_health("coingecko", False, response_time_ms, str(e), "EXCEPTION")
            print(f"[ERROR] CoinGecko Fetch Failed: {e}")
            return {}

    @cache.cached(source="AlphaVantage", expiry=3600)
    def fetch_stock_quote(self, symbol):
        """Fetches stock quotes from Alpha Vantage."""
        if self.mode == "MOCK":
            return {"Global Quote": {"01. symbol": symbol, "05. price": "150.00"}}

        self._throttle()
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.alpha_vantage_key
        }
        
        start_time = time.time()
        try:
            response = requests.get(url, params=params)
            response_time_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                self._update_source_health("alpha_vantage", True, response_time_ms)
                return response.json()
            else:
                self._update_source_health("alpha_vantage", False, response_time_ms,
                                          f"HTTP {response.status_code}", str(response.status_code))
                return {}
        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            self._update_source_health("alpha_vantage", False, response_time_ms, str(e), "EXCEPTION")
            print(f"[ERROR] Alpha Vantage Fetch Failed: {e}")
            return {}

    def fetch_kakao_trends(self, keyword):
        """Fetches Kakao Trend/Search data (Mocked skeleton)."""
        return [
            {"source": "Kakao", "content": f"MOCK: {keyword} 카카오톡 채널 반응 폭발적"},
            {"source": "Kakao", "content": f"MOCK: {keyword} 관련 선물하기 랭킹 급상승"}
        ]

if __name__ == "__main__":
    connectors = APIConnectors()
    print(f"[API] Running in {connectors.mode} mode.")
    # Crypto Test
    print("Crypto Prices (CoinGecko):")
    print(json.dumps(connectors.fetch_crypto_prices(), indent=2))
    # Naver Test
    print("\nNaver Search (AI Signal):")
    print(json.dumps(connectors.fetch_naver_search("AI Signal"), indent=2, ensure_ascii=False))
