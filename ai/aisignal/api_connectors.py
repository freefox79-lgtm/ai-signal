import os
import requests
import json
from dotenv import load_dotenv

load_dotenv(".env.local")

class APIConnectors:
    """
    Handles data retrieval from external APIs like Naver and Kakao.
    Supports both MOCK and REAL modes based on environment state.
    """
    
    def __init__(self):
        self.naver_id = os.getenv("NAVER_CLIENT_ID")
        self.naver_secret = os.getenv("NAVER_CLIENT_SECRET")
        self.mode = os.getenv("API_STATUS", "MOCK").upper()

    def fetch_naver_search(self, query):
        """Fetches Naver Search results."""
        if self.mode == "MOCK":
            return [
                {"source": "Naver", "title": f"MOCK: {query} 관련 최신 트렌드", "link": "https://search.naver.com"},
                {"source": "Naver", "title": f"MOCK: {query} 뉴스 분석", "link": "https://news.naver.com"}
            ]
            
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

    def fetch_kakao_trends(self, keyword):
        """Fetches Kakao Trend/Search data (Mocked skeleton)."""
        # Kakao typically requires specific OAuth flow, mock for now
        return [
            {"source": "Kakao", "content": f"MOCK: {keyword} 카카오톡 채널 반응 폭발적"},
            {"source": "Kakao", "content": f"MOCK: {keyword} 관련 선물하기 랭킹 급상승"}
        ]

if __name__ == "__main__":
    connectors = APIConnectors()
    print(f"[API] Running in {connectors.mode} mode.")
    results = connectors.fetch_naver_search("AI Signal")
    print(json.dumps(results, indent=2, ensure_ascii=False))
