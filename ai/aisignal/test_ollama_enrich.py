
import os
import json
from api_connectors import APIConnectors

def test_enrichment():
    connector = APIConnectors(mode="LIVE") # Force LIVE to try connecting
    
    # Mock search results mimicking Naver output
    mock_results = [
        {
            "source": "Naver", 
            "title": "<b>비스포크 AI</b> 콤보, 출시 3일 만에 1000대 판매 돌파", 
            "link": "https://news.naver.com/main/read.nhn?mode=LSD&mid=sec&sid1=101&oid=001&aid=0014567890",
            "snippet": "삼성전자의 올인원 세탁건조기 '<b>비스포크 AI</b> 콤보'가 출시 사흘 만에 판매량 1000대를 넘어섰다."
        },
        {
            "source": "Naver",
            "title": "오픈AI, <b>Sora</b> 공개... 텍스트로 고화질 영상 생성",
            "link": "https://www.aitimes.com/news/articleView.html?idxno=157890",
            "snippet": "오픈AI가 텍스트를 입력하면 최대 1분 길이의 고화질 동영상을 만들어주는 생성형 AI 모델 '<b>소라(Sora)</b>'를 공개했다."
        }
    ]
    
    print("running enrichment...")
    enriched = connector.enrich_search_results_with_ollama(mock_results)
    
    print("\n--- Enriched Results ---")
    for item in enriched:
        print(f"Original Link Preserved: {item['link']}")
        print(f"New Title: {item['title']}")
        print(f"New Snippet: {item['snippet']}")
        print("-" * 30)
        
        # Verification
        if item['link'] == "":
            print("❌ Link Lost!")
        else:
            print("✅ Link OK")

if __name__ == "__main__":
    test_enrichment()
