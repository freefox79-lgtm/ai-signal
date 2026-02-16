import os
import requests
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# 중앙 집중식 DB 유틸리티 임포트
from db_utils import get_db_connection
from cache_manager import CacheManager
from agents.llm.ollama_client import get_ollama_client
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Load local env only for development fallback
if os.path.exists(".env.local"):
    load_dotenv(".env.local", override=False)

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
        self.public_data_key = os.getenv("DATA_GO_KR_KEY")
        self.brave_key = os.getenv("BRAVE_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.mode = mode or os.getenv("API_STATUS", "MOCK").upper()
        self.last_call_time = 0.0
        self.min_interval = 1.0  # Default 1s between calls to avoid rate limits
        
        self.db_url = os.getenv("DATABASE_URL")
        
        # 로션 LLM 클라이언트 (Ollama)
        self.ollama = get_ollama_client()
        
        # 중앙 집중식 DB 유틸리티 사용 - Connection is managed per request now
        self.conn = None # Deprecated: Do not use self.conn directly

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
                conn = psycopg2.connect(db_url, sslmode='require', connect_timeout=3)
            else:
                conn = psycopg2.connect(db_url, connect_timeout=3)
            
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
            # Always get a fresh connection for health updates to avoid reusing closed connections
            with get_db_connection(self.db_url) as conn:
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

    @cache.cached(source="YouTube", expiry=21600)  # 6 Hours Cache for Quota Protection
    def fetch_youtube_trends(self, query: str = "trending"):
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

    @cache.cached(source="PublicData", expiry=86400) # 24h as these update monthly/daily
    def fetch_apt_transactions(self, lawd_cd: str = "11110", deal_ymd: str = "202602"):
        """
        Fetches APT transaction data (아파트 매매 실거래가).
        Default: Jongno-gu, Feb 2026.
        """
        endpoint = "http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTrade"
        params = {
            "LAWD_CD": lawd_cd,
            "DEAL_YMD": deal_ymd
        }
        # Data.go.kr XML responses need careful parsing or forcing json if supported
        return self.fetch_public_data(endpoint, params)

    @cache.cached(source="PublicData", expiry=86400)
    def fetch_shopping_district(self, div_id: str = "11110"):
        """
        Fetches Commercial District Info (소상공인시장진흥공단_상권정보).
        """
        endpoint = "http://apis.data.go.kr/B553077/api/open/sdsc2/baroApi"
        params = {
            "resType": "json",
            "catId": "dong",
            "divId": div_id
        }
        return self.fetch_public_data(endpoint, params)
        
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
            
        elif source_key == "search":
            query = params.get("query")
            if not query:
                return []
            return self.unified_search(query)
            
        else:
            print(f"[APIConnectors] Unknown source: {source_name}")
            return {}

    @cache.cached(source="GoogleTrends", expiry=3600)
    def fetch_google_trends(self, geo="KR"):
        """
        Fetches daily trending searches from Google Trends RSS.
        """
        if self.mode == "MOCK":
            return ["알트코인", "AI 에이전트", "삼성전자", "테슬라", "비트코인"]

        url = "https://trends.google.co.kr/trends/trendingsearches/daily/rss"
        params = {"geo": geo}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=5)
            if response.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                trends = []
                # RSS namespace usually requires handling, but simple find might work or iterate
                # Structure: channel -> item -> title
                for item in root.findall(".//item"):
                    title = item.find("title")
                    if title is not None:
                        trends.append(title.text)
                return trends[:10]  # Return top 10
            else:
                print(f"[API] Google Trends error: {response.status_code}")
                return []
        except Exception as e:
            print(f"[API] Google Trends exception: {e}")
            return []

    def fetch_kakao_trends(self, keyword):
        """Fetches Kakao Trend/Search data (Mocked skeleton)."""
        return [
            {"source": "Kakao", "content": f"MOCK: {keyword} 카카오톡 채널 반응 폭발적"},
            {"source": "Kakao", "content": f"MOCK: {keyword} 관련 선물하기 랭킹 급상승"}
        ]

    @cache.cached(source="Brave", expiry=3600)
    def fetch_brave_search(self, query: str):
        """Fetches search results from Brave Search API."""
        if self.mode == "MOCK":
            return [{"source": "Brave", "title": f"MOCK: {query} Brave 분석", "link": "https://brave.com"}]

        if not self.brave_key:
            print("⚠️ [Brave] API Key is missing.")
            return []

        self._throttle()
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {"X-Subscription-Token": self.brave_key, "Accept": "application/json"}
        params = {"q": query, "count": 10}
        
        start_time = time.time()
        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            response_time_ms = int((time.time() - start_time) * 1000)
            if response.status_code == 200:
                self._update_source_health("brave_search", True, response_time_ms)
                results = response.json().get("web", {}).get("results", [])
                return [{"source": "Brave", "title": r.get("title"), "link": r.get("url"), "snippet": r.get("description")} for r in results]
            else:
                self._update_source_health("brave_search", False, response_time_ms, f"HTTP {response.status_code}")
                return []
        except Exception as e:
            print(f"[Brave] Exception: {e}")
            return []

    @cache.cached(source="Gemini", expiry=3600)
    def fetch_gemini_analysis(self, query: str, search_results: List[Dict]):
        """
        Uses Google Gemini to generate a 'Quantum Analysis' based on search context.
        """
        if self.mode == "MOCK":
            return f"MOCK ANALYSIS: {query}에 대한 퀀텀 분석 결과 (Mock Mode)..."

        if not self.gemini_key or not genai:
            return "⚠️ Gemini API Key가 설정되지 않았거나 라이브러리가 설치되지 않았습니다."

        # RATE LIMITING (Free Tier Safety: 15 RPM)
        current_time = time.time()
        # Initialize token bucket if not exists
        if not hasattr(self, '_gemini_last_call'):
            self._gemini_last_call = 0
        
        # Enforce 4 seconds between calls (conservative 15 RPM = 60s/15 = 4s)
        time_since_last = current_time - self._gemini_last_call
        if time_since_last < 4.0:
            return f"⏳ 퀀텀 분석 쿨다운 중... ({int(4.0 - time_since_last)}초 대기)"
            
        self._gemini_last_call = current_time

        try:
            # 1. Local Expert Deep Analysis (Hierarchical Stage 2)
            expert_report = self._analyze_search_momentum(query, search_results)

            genai.configure(api_key=self.gemini_key)
            model = genai.GenerativeModel('gemini-flash-latest')
            
            # Context Construction
            context_text = "\n".join([f"- Title: {r.get('title', '')}\n  Summary: {r.get('snippet', '')}" for r in search_results])
            
            prompt = f"""
            You are a 'Global Strategy AI' in the AI Signal system.
            Review the following 'Local Expert Momentum Report' and search context for '{query}'.
            
            [LOCAL EXPERT REPORT]
            {expert_report}
            
            [DETAILED SEARCH SIGNALS]
            {context_text}
            
            TASK:
            Synthesize the Expert Report and raw signals into a high-level strategic insight. 
            Connect the local analysis with global trends.
            
            OUTPUT GUIDELINES:
            - **Tone**: Professional Intelligence Officer.
            - **Language**: Korean.
            - **Format**: 2-3 powerful, synthesis-heavy sentences.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"[Gemini] Error: {e}")
            return f"❌ 분석 생성 실패: {str(e)}"

    def unified_search(self, query: str):
        """
        Unified search dispatcher with fallback strategy.
        1. Try Brave Search (Premium results)
        2. Fallback to Naver (Local/News)
        """
        print(f"🔍 [Unified Search] Query: {query}")
        
        # 1. Default to Naver Search (Local/News) - User requested priority
        print("🔍 [Unified Search] Using Naver Search (Primary)...")
        naver_results = self.fetch_naver_search(query)
        
        # 2. YouTube Search - User requested refinement
        print("🔍 [Unified Search] Using YouTube Trends (Primary)...")
        youtube_results = self.fetch_youtube_trends(query)
        
        naver_processed = []
        youtube_processed = []
        
        # Process Naver Results
        if naver_results:
            print(f"✅ [Unified Search] {len(naver_results)} results fetched from Naver.")
            for r in naver_results:
                raw_title = r.get("title", "")
                raw_desc = r.get("description", "")
                
                clean_title = re.sub(r'<[^>]+>', '', raw_title).replace("&quot;", '"').replace("&amp;", "&")
                clean_snippet = re.sub(r'<[^>]+>', '', raw_desc).replace("&quot;", '"').replace("&amp;", "&")
                
                naver_processed.append({
                    "source": "Naver",
                    "title": clean_title,
                    "link": r.get("link"),
                    "snippet": clean_snippet
                })

        # Process YouTube Results
        if youtube_results:
            print(f"✅ [Unified Search] {len(youtube_results)} results fetched from YouTube.")
            for r in youtube_results:
                youtube_processed.append({
                    "source": "YouTube",
                    "title": r.get("title"),
                    "link": f"https://www.youtube.com/watch?v={r.get('video_id')}",
                    "snippet": f"[Video] {r.get('title')} by {r.get('channel')}" 
                })
        
        # Interleave Results (Naver, YouTube, Naver, YouTube...)
        combined_results = []
        max_len = max(len(naver_processed), len(youtube_processed))
        
        for i in range(max_len):
            if i < len(naver_processed):
                combined_results.append(naver_processed[i])
            if i < len(youtube_processed):
                combined_results.append(youtube_processed[i])
        
        if combined_results:
            return combined_results
            
        return []

    def fetch_live_signals_from_db(self, limit=5):
        """
        [Tier 1: High-Frequency]
        Fetches 'Breaking' signals (X, Finance) from internal DB.
        These are populated by the Stealth Crawler.
        """
        if self.mode == "MOCK":
            return [
                {"keyword": "비트코인 급락", "insight": "5분 전 바이낸스 대량 매도 포착 (크롤링)", "source": "Stealth"},
                {"keyword": "코스피 서킷브레이커", "insight": "장지수 급락 발동 (금융 속보)", "source": "Stealth"}
            ]

        try:
            with get_db_connection(self.db_url) as conn:
                with conn.cursor() as cur:
                    # Assuming 'signals' table has 'keyword', 'insight', 'agent' columns
                    # We prioritize 'Stealth' agent or specific sources if available
                    cur.execute("""
                        SELECT keyword, insight, agent, updated_at
                        FROM signals
                        WHERE agent IN ('Stealth', 'Jwem') 
                        ORDER BY updated_at DESC
                        LIMIT %s
                    """, (limit,))
                    
                    rows = cur.fetchall()
                    results = []
                    for r in rows:
                        results.append({
                            "keyword": r[0],
                            "avg_score": 99, # Breaking news is always hot
                            "score_trend": "up",
                            "related_insight": r[1] if r[1] else self._generate_persona_comment("BREAKING", r[0], "Stealth"),
                            "source": "Stealth" if r[2] == 'Stealth' else "Crawling",
                            "type": "BREAKING"
                        })
                    return results
        except Exception as e:
            print(f"[DB] Fetch Signals Error: {e}")
            return []

    @cache.cached(source="NaverShopping", expiry=3600)
    def fetch_naver_shopping(self, query: str = "인기상품"):
        """
        [Tier 2: Medium-Frequency]
        Fetches trending products from Naver Shopping.
        """
        if self.mode == "MOCK":
            return [
                {"title": "MOCK: 손흥민 축구화", "link": "#", "lprice": "150000"},
                {"title": "MOCK: 아이폰 16 케이스", "link": "#", "lprice": "25000"}
            ]
            
        self._throttle()
        url = "https://openapi.naver.com/v1/search/shop.json"
        headers = {
            "X-Naver-Client-Id": self.naver_id,
            "X-Naver-Client-Secret": self.naver_secret
        }
        # sim = similarity, date = date. 'sim' is better for 'trending' context usually 
        # but for specific query 'popular', date might be irrelevant.
        # We'll use a generic query or the passed query.
        params = {"query": query, "display": 5, "start": 1, "sort": "sim"}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                items = response.json().get("items", [])
                results = []
                for item in items:
                    title = re.sub(r'<[^>]+>', '', item['title'])
                    results.append({
                        "keyword": title,
                        "avg_score": 85,
                        "score_trend": "stable",
                        "related_insight": f"최저가 {int(item['lprice']):,}원 | 쇼핑 트렌드",
                        "source": "Naver Shopping",
                        "type": "SHOPPING",
                        "link": item['link']
                    })
                return results
            return []
        except Exception as e:
            print(f"[Shopping] Error: {e}")
            return []

    def _refine_with_local_llm(self, raw_items: List[Dict]) -> List[Dict]:
        """
        [Stage 2: Refinement]
        Uses Local LLM (llama3.2:3b) to deduplicate and clean raw trend data.
        """
        if self.mode == "MOCK":
            return raw_items[:10]

        # Optimize: Batch processing
        candidates_text = "\n".join([f"- {item['keyword']} ({item['source']})" for item in raw_items])
        
        prompt = f"""
        You are a Data Cleaner.
        Below is a list of raw trend keywords from various sources.
        
        TASKS:
        1. Remove duplicates (e.g., "Bitcoin" and "BTC" -> keep "Bitcoin").
        2. Remove generic/meaningless keywords (e.g., "Today", "News").
        3. Standardize formatting.
        4. Select the top 15 most distinct and interesting topics.
        
        RAW LIST:
        {candidates_text}
        
        OUTPUT FORMAT:
        Return ONLY a JSON array of strings. Example: ["Keyword1", "Keyword2", ...]
        """
        
        try:
            print(f"🧹 [Local AI] Refining {len(raw_items)} signals using {self.ollama.MODEL_FAST}...")
            output = self.ollama.generate(
                prompt=prompt,
                model=self.ollama.MODEL_FAST,
                temperature=0.1,
                max_tokens=200
            )
            
            if output:
                
                try:
                    start = output.find('[')
                    end = output.rfind(']') + 1
                    if start != -1 and end != -1:
                        refined_keywords = json.loads(output[start:end])
                        refined_items = []
                        for kw in refined_keywords:
                            original = next((i for i in raw_items if kw in i['keyword'] or i['keyword'] in kw), None)
                            if original:
                                new_item = original.copy()
                                new_item['keyword'] = kw
                                refined_items.append(new_item)
                        
                        if refined_items:
                            print(f"✅ [Local AI] Refined to {len(refined_items)} unique trends.")
                            return refined_items
                except Exception as parse_e:
                    print(f"⚠️ [Local AI] JSON Parse Failed: {parse_e}")
        except Exception as e:
            print(f"⚠️ [Local AI] Refinement Failed: {e}")
            
        # Fallback deduplication if LLM fails or parsing fails
        seen = set()
        fallback_list = []
        for item in raw_items:
            k = item['keyword'][:10].lower()
            if k not in seen:
                seen.add(k)
                fallback_list.append(item)
        return fallback_list[:15]

    def _analyze_with_local_expert(self, refined_items: List[Dict]) -> str:
        """
        [Stage 2.5: Deep Analysis]
        Uses qwen2.5-coder:7b to find correlations and momentum.
        """
        if self.mode == "MOCK":
            return "Mock Expert Report: Trends are showing high volatility in IT sector."

        print(f"🧠 [Local Expert] Analyzing momentum with {self.ollama.MODEL_ANALYTIC}...")
        
        context = "\n".join([f"- {i['keyword']} (Source: {i['source']}, Category: {i['type']})" for i in refined_items])
        
        prompt = f"""
        You are a Senior Market Intelligence Analyst.
        Analyze the following trend keywords and provide a deep " MOMENTUM REPORT".
        
        TRENDS:
        {context}
        
        TASKS:
        1. Group keywords into 2-3 logical clusters.
        2. Identify 'Cross-Impact' (e.g., How does Trend A affect Trend B?).
        3. Determine the 'Market Sentiment' (Bullish, Bearish, Neutral).
        
        OUTPUT FORMAT:
        Provide a concise 3-4 sentence report in KOREAN. 
        Focus on value-added insights, not just listing.
        """
        
        try:
            report = self.ollama.generate(
                prompt=prompt,
                model=self.ollama.MODEL_ANALYTIC,
                temperature=0.3,
                max_tokens=400
            )
            return report or "No deep analysis available."
        except Exception as e:
            print(f"⚠️ [Local Expert] Analysis Failed: {e}")
            return "Local expert report generation failed."

    def _analyze_search_momentum(self, query: str, results: List[Dict]) -> str:
        """
        [Stage 2: Expert Search Analysis]
        Uses Qwen 2.5 7B to find deeper meaning in search results.
        """
        if self.mode == "MOCK":
            return f"Expert Focus: Potential growth in '{query}' sector."

        print(f"🧠 [Local Expert] Analyzing search momentum for '{query}'...")
        
        context = "\n".join([f"- {r.get('title')} ({r.get('snippet')})" for r in results[:5]])
        
        prompt = f"""
        Analyze these search results for the keyword '{query}'. 
        Identify the 'Hidden Momentum'—what is the real story behind these updates?
        Answer in 2-3 short sentences in KOREAN.
        
        RESULTS:
        {context}
        """
        
        try:
            return self.ollama.generate(
                prompt=prompt,
                model=self.ollama.MODEL_ANALYTIC,
                temperature=0.3,
                max_tokens=300
            )
        except:
            return "Local expert analysis unavailable."

    def _rank_with_gemini(self, candidates: List[Dict], expert_report: str = "") -> List[Dict]:
        """
        [Stage 3: Ranking & Synthesis]
        Uses Gemini to finalize ranking based on Expert Report.
        """
        if not candidates:
            return []
            
        if self.mode == "MOCK":
            # Give mock scores
            for i, item in enumerate(candidates[:10]):
                item['avg_score'] = 90 - (i * 5)
                item['related_insight'] = "MOCK: Gemini synthesis complete."
            return candidates[:10]

        print("✨ [Cloud AI] Synthesizing final rankings with Gemini...")
        
        # Simplified context for Gemini
        candidates_json = json.dumps([
            {"id": i, "keyword": c['keyword'], "source": c['source']} 
            for i, c in enumerate(candidates)
        ], ensure_ascii=False)
        
        prompt = f"""
        You are a Global Strategy AI. 
        Review the following 'Local Expert Report' and trend candidates.
        
        [LOCAL EXPERT REPORT]
        {expert_report}
        
        [CANDIDATES]
        {candidates_json}
        
        TASKS:
        1. Select the Top 10 trends that have the highest global impact.
        2. Assign a Trend Score (0-100.0).
        3. Write a single-sentence "Global Insight" in KOREAN that synthesizes the local expert's analysis with global context.
        
        OUTPUT FORMAT (JSON ARRAY ONLY):
        [
          {{"original_id": 0, "score": 98.5, "insight": "글로벌 시장의..."}},
          ...
        ]
        """
        
        try:
             genai.configure(api_key=self.gemini_key)
             model = genai.GenerativeModel('gemini-flash-latest')
             response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
             
             
             ranked_data = json.loads(response.text)
             
             final_list = []
             for rank, r_item in enumerate(ranked_data):
                 orig_id = r_item.get('original_id')
                 if orig_id is not None and 0 <= orig_id < len(candidates):
                     original = candidates[orig_id]
                     original['avg_score'] = r_item.get('score', 80)
                     original['related_insight'] = r_item.get('insight', original.get('related_insight'))
                     original['keyword'] = r_item.get('keyword', original['keyword'])
                     final_list.append(original)
             
             print(f"✅ [Cloud AI] Successfully ranked {len(final_list)} items.")
             return final_list
             
        except Exception as e:
            print(f"⚠️ [Cloud AI] Ranking Failed: {e}")
            # High-quality Local Fallback using Qwen2.5-Coder
            return self._rank_with_local_expert(candidates)

    def _rank_with_local_expert(self, candidates: List[Dict]) -> List[Dict]:
        """
        [Stage 3 Fallback: Local Analytic Ranking]
        Uses Qwen2.5-Coder:7b (Expert model) if Gemini is offline.
        """
        print(f"🛡️ [Local Expert] Ranking with {self.ollama.MODEL_ANALYTIC}...")
        
        context = "\n".join([f"ID {i}: {item['keyword']} (Source: {item['source']})" for i, item in enumerate(candidates)])
        
        prompt = f"""
        Analyze these trend candidates as a Senior Data Analyst.
        1. Select the Top 10 most impactful trends.
        2. Assign a 'Trend Score' (0-100%).
        3. Write a 'Signal Insight' (1 short sentence, Korean).
        
        CANDIDATES:
        {context}
        
        OUTPUT FORMAT (JSON ONLY):
        [
          {{"keyword": "...", "score": 95, "insight": "...", "original_id": 0}},
          ...
        ]
        """
        
        try:
            output = self.ollama.generate(
                prompt=prompt,
                model=self.ollama.MODEL_ANALYTIC,
                temperature=0.1,
                max_tokens=800
            )
            
            
            start = output.find('[')
            end = output.rfind(']') + 1
            ranked_data = json.loads(output[start:end])
            
            final_list = []
            for r_item in ranked_data:
                orig_id = r_item.get('original_id')
                if orig_id is not None and 0 <= orig_id < len(candidates):
                    original = candidates[orig_id]
                    original['avg_score'] = r_item.get('score', 80)
                    original['related_insight'] = r_item.get('insight', original.get('related_insight'))
                    original['keyword'] = r_item.get('keyword', original['keyword'])
                    final_list.append(original)
            return final_list
        except Exception as e:
            print(f"⚠️ [Local Expert] Failed: {e}")
            return self._fallback_scoring(candidates)

    def _fallback_scoring(self, items):
        """Simple deterministic scoring for fallback."""
        for i, item in enumerate(items):
            # Deterministic pseudo-random score based on keyword length + source
            base = 70
            if item['type'] == 'BREAKING': base += 20
            elif item['type'] == 'VIRAL': base += 15
            elif item['type'] == 'MACRO': base += 10
            
            item['avg_score'] = min(99, base - (i * 2)) # Decay by rank
        return items

    def fetch_unified_trends(self):
        """
        [Hierarchical AI Pipeline]
        Collect -> Refine (Local Fast) -> Analyze (Local Expert) -> Synthesis (Cloud)
        """
        print("🔍 [Unified] Aggregating signals from all sources...")
        
        raw_list = []
        
        # 1. Collect Data
        # ... (same collection logic) ...
        db_signals = self.fetch_live_signals_from_db(limit=5)
        for item in db_signals:
            if 'source' not in item: item['source'] = 'Database'
            raw_list.append(item)
        
        shop_trends = self.fetch_naver_shopping("트렌드")
        for item in shop_trends[:5]:
             item['type'] = 'SHOPPING'
             item['source'] = 'Naver Shopping'
             raw_list.append(item)
             
        yt_trends = self.fetch_youtube_trends("trending")
        if yt_trends:
            for item in yt_trends[:5]:
                item['type'] = 'VIRAL'
                item['source'] = 'YouTube'
                item['keyword'] = item.get('keyword', item.get('title', 'YouTube Video')[:20])
                item['link'] = f"https://www.youtube.com/watch?v={item['video_id']}"
                raw_list.append(item)
        
        g_trends = self.fetch_google_trends()
        if g_trends:
            for keyword in g_trends[:5]:
                raw_list.append({
                    "keyword": keyword,
                    "source": "Google Trends",
                    "type": "MACRO",
                    "link": f"https://trends.google.com/trends/explore?q={keyword}",
                    "related_insight": "Google 검색량 급증"
                })
                
        # 2. Refine (Local LLM - Llama 3.2 3B)
        refined_list = self._refine_with_local_llm(raw_list)
        
        # 2.5 Expert Analysis (Local LLM - Qwen 2.5 7B)
        expert_report = self._analyze_with_local_expert(refined_list)
        
        # 3. Synthesis & Ranking (Cloud AI - Gemini)
        ranked_list = self._rank_with_gemini(refined_list, expert_report)
        
        if not ranked_list:
             return self._fallback_scoring(refined_list or raw_list)[:10]
             
        return ranked_list[:10]

    def _generate_persona_comment(self, type, keyword, source):
        """
        Generates a short, persona-based comment for a trend.
        Jwem (Analytical): For Macro, Finance, Tech.
        Jfit (Emotional): For Viral, Shopping, Entertainment.
        """
        import random
        
        # Jwem (Analytical) Comments
        jwem_comments = [
            f"데이터 패턴 분석 결과, {keyword} 관련 지표가 상승세입니다.",
            "거시 경제 흐름과 연동된 중요한 신호로 포착되었습니다.",
            f"시장 변동성을 주도할 가능성이 높은 키워드입니다.",
            "검색량 추이가 임계치를 돌파했습니다. 주시가 필요합니다.",
            f"{keyword}에 대한 기술적 분석 시그널이 발생했습니다."
        ]
        
        # Jfit (Emotional) Comments
        jfit_comments = [
            f"지금 진짜 핫해요! {keyword} 모르면 대화가 안 된다고요~ 🔥",
            "SNS에서 난리 났어요! 반응 속도가 엄청납니다!",
            f"이거 봤어요? {keyword} 진짜 대박인 것 같아요! 🤩",
            "트렌드세터라면 절대 놓치면 안 되는 소식입니다!",
            f"{keyword}! 지금 커뮤니티가 들썩이고 있어요!"
        ]
        
        # Jwem (Urgent/Warning)
        jwem_urgent = [
            f"🚨 긴급: {keyword} 관련 리스크 요인이 감지되었습니다.",
            "즉각적인 시장 대응이 필요한 변동성 구간입니다.",
            "비정상적인 데이터 스파이크가 발생했습니다. 주의하세요."
        ]

        if type in ['maco', 'MACRO', 'NEWS', 'BREAKING']:
            if type == 'BREAKING':
                return random.choice(jwem_urgent)
            return random.choice(jwem_comments)
        else:
            # VIRAL, SHOPPING, etc.
            return random.choice(jfit_comments)


    def enrich_search_results_with_ollama(self, results: List[Dict]):
        """
        Uses Local LLM (llama3.2:3b) to rewrite titles and summarize snippets.
        """
        if self.mode == "MOCK":
            return results

        print(f"🦙 [Local LLM] Enriching {len(results)} results using {self.ollama.MODEL_FAST}...")
        
        enriched_results = []
        
        for item in results:
            try:
                prompt = f"""
                Rewrite the following search result into a catchy title and a 1-sentence summary in KOREAN.
                Even if the input is English, valid output must be in KOREAN.
                
                Original Title: {item.get('title')}
                Original Snippet: {item.get('snippet')}
                
                Format:
                TITLE: [New Title in Korean]
                SUMMARY: [New Summary in Korean]
                """
                
                output = self.ollama.generate(
                    prompt=prompt,
                    model=self.ollama.MODEL_FAST,
                    temperature=0.3,
                    max_tokens=100
                )
                
                if output:
                    new_title = ""
                    new_summary = ""
                    for line in output.split('\n'):
                        if "TITLE:" in line: new_title = line.replace("TITLE:", "").strip()
                        if "SUMMARY:" in line: new_summary = line.replace("SUMMARY:", "").strip()
                    
                    if new_title:
                        enriched_results.append({
                            "title": new_title,
                            "snippet": new_summary or item.get('snippet'),
                            "source": item.get('source'),
                            "link": item.get('link'),
                            "enriched_by_ollama": True
                        })
                        continue
            except Exception as e:
                print(f"⚠️ Enrichment skipped for one item: {e}")
            
            enriched_results.append(item)
            
        return enriched_results

if __name__ == "__main__":
    connectors = APIConnectors()
    print(f"[API] Running in {connectors.mode} mode.")
    # Search Test
    print("\nUnified Search Test (AI Agents):")
    search_results = connectors.unified_search("AI Agents")
    print(json.dumps(search_results[:2], indent=2, ensure_ascii=False))
