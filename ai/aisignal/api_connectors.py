import os
import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# 중앙 집중식 DB 유틸리티 임포트
from db_utils import get_db_connection
from cache_manager import CacheManager

load_dotenv(".env.local")

cache = CacheManager()

class APIConnectors:
    """
    Handles data retrieval from external APIs like Naver, Kakao, Alpha Vantage, etc.
    Supports transparent Redis caching and basic rate limiting.
    """
    
    def __init__(self, mode: str = None):
        self.naver_id = os.getenv("NAVER_CLIENT_ID")
        self.naver_secret = os.getenv("NAVER_CLIENT_SECRET")
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.fred_key = os.getenv("FRED_API_KEY")
        self.youtube_key = os.getenv("YOUTUBE_API_KEY")
        self.public_data_key = os.getenv("DATA_GO_KR_KEY")
        self.mode = mode or os.getenv("API_STATUS", "MOCK").upper()
        self.last_call_time = 0.0
        self.min_interval = 1.0  # Default 1s between calls to avoid rate limits
        
        self.db_url = os.getenv("DATABASE_URL")
        
        # 중앙 집중식 DB 유틸리티 사용
        try:
            if self.db_url:
                self.conn = get_db_connection(self.db_url)
            else:
                self.conn = None
        except Exception as e:
            print(f"[APIConnectors] DB 연결 실패 (연결 없이 계속): {e}")
            self.conn = None

        # Load source registry from database
        self.source_registry = self._load_source_registry()
    
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
            # Use self.conn if available, otherwise try to connect
            if self.conn:
                conn = self.conn
            else:
                conn = get_db_connection(self.db_url)
            
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

    @cache.cached(source="FRED", expiry=86400)
    def fetch_fred_series(self, series_id):
        """
        Fetches macro economic data from FRED (Federal Reserve Economic Data).
        Common IDs: GS10 (10Y Bond), CPIAUCSL (CPI), GDP (GDP)
        """
        if self.mode == "MOCK":
            return {"observations": [{"date": "2026-02-15", "value": "4.25"}]}

        if not self.fred_key:
            print("⚠️ [FRED] API Key is missing. Check .env.local")
            return {}

        self._throttle()
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": series_id,
            "api_key": self.fred_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 5
        }

        start_time = time.time()
        try:
            response = requests.get(url, params=params)
            response_time_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                self._update_source_health("fred", True, response_time_ms)
                return response.json()
            else:
                self._update_source_health("fred", False, response_time_ms,
                                          f"HTTP {response.status_code}", str(response.status_code))
                return {}
        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            self._update_source_health("fred", False, response_time_ms, str(e), "EXCEPTION")
            print(f"[ERROR] FRED Fetch Failed: {e}")
            return {}

    @cache.cached(source="YouTube", expiry=43200)
    def fetch_youtube_trends(self, query: str):
        """
        Fetches trending videos and basic metrics from YouTube Data API.
        """
        if self.mode == "MOCK":
            return [{"title": f"MOCK: {query} 바이럴 영상", "view_count": "1.2M", "channel": "TrendTV"}]

        if not self.youtube_key:
            print("⚠️ [YouTube] API Key is missing. Check .env.local")
            return []

        self._throttle()
        search_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "order": "viewCount",
            "maxResults": 5,
            "key": self.youtube_key
        }

        start_time = time.time()
        try:
            response = requests.get(search_url, params=params)
            response_time_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                self._update_source_health("youtube_data", True, response_time_ms)
                items = response.json().get("items", [])
                results = []
                for item in items:
                    results.append({
                        "video_id": item["id"]["videoId"],
                        "title": item["snippet"]["title"],
                        "channel": item["snippet"]["channelTitle"],
                        "published_at": item["snippet"]["publishedAt"],
                        "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"]
                    })
                return results
            else:
                self._update_source_health("youtube_data", False, response_time_ms,
                                          f"HTTP {response.status_code}", str(response.status_code))
                return []
        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            self._update_source_health("youtube_data", False, response_time_ms, str(e), "EXCEPTION")
            print(f"[ERROR] YouTube Fetch Failed: {e}")
            return []

    @cache.cached(source="PublicData", expiry=3600)
    def fetch_public_data(self, endpoint_url: str, params: Dict[str, Any]):
        """
        Fetches data from Data.go.kr (Public Data Portal).
        """
        if self.mode == "MOCK":
            return {"status": "OK", "data": "MOCK: 전국 미세먼지 농도 '보통'"}

        if not self.public_data_key:
            print("⚠️ [PublicData] API Key (Service Key) is missing. Check .env.local")
            return {}

        self._throttle()
        
        # Data.go.kr Service Keys are notoriously sensitive to URL encoding.
        # Often, they are already encoded in the portal. Passing them to requests' params
        # can cause double-encoding, leading to 401 errors.
        import urllib.parse
        decoded_key = urllib.parse.unquote(self.public_data_key)
        
        # Construct URL with raw serviceKey to prevent requests from encoding it again
        if "?" in endpoint_url:
            full_url = f"{endpoint_url}&serviceKey={decoded_key}"
        else:
            full_url = f"{endpoint_url}?serviceKey={decoded_key}"
            
        # Add other params
        params["_type"] = "json"

        start_time = time.time()
        try:
            # We pass params for the rest, but serviceKey is already in the URL
            response = requests.get(full_url, params=params)
            response_time_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                self._update_source_health("data_go_kr", True, response_time_ms)
                return response.json()
            else:
                self._update_source_health("data_go_kr", False, response_time_ms,
                                          f"HTTP {response.status_code}", str(response.status_code))
                return {}
        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            self._update_source_health("data_go_kr", False, response_time_ms, str(e), "EXCEPTION")
            print(f"[ERROR] Public Data Fetch Failed: {e}")
            return {}

    def fetch_from_api(self, source_name: str, endpoint: str = None, params: Dict[str, Any] = None):
        """
        Generic method to fetch data from any supported API source.
        Dispatches to specific methods based on source_name.
        """
        if params is None:
            params = {}
            
        source_key = source_name.lower().replace(" ", "_")
        
        if source_key == "alpha_vantage":
            symbol = params.get("symbol")
            if not symbol:
                return {}
            return self.fetch_stock_quote(symbol)
            
        elif source_key == "fred":
            series_id = params.get("series_id")
            if not series_id:
                return {}
            return self.fetch_fred_series(series_id)
            
        elif source_key == "youtube":
            query = params.get("query", "trending")
            return self.fetch_youtube_trends(query)
            
        elif source_key == "naver_search":
            query = params.get("query", "news")
            return self.fetch_naver_search(query)
            
        elif source_key == "coingecko":
            ids = params.get("ids", "bitcoin")
            return self.fetch_crypto_prices(ids)
            
        else:
            print(f"[APIConnectors] Unknown source: {source_name}")
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
