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
        
        try:
            response = requests.get(url, headers=headers, params=params)
            return response.json().get("items", [])
        except Exception as e:
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
        
        try:
            response = requests.get(url, params=params)
            return response.json()
        except Exception as e:
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
        
        try:
            response = requests.get(url, params=params)
            return response.json()
        except Exception as e:
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
