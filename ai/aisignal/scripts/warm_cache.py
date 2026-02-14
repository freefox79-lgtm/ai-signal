#!/usr/bin/env python3
"""
Cache Warming Script
자주 사용되는 쿼리로 캐시 예열
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.graphrag.knowledge_graph import KnowledgeGraph
from agents.llm.ollama_client import get_ollama_client
from agents.cache.cache_monitor import get_cache_monitor


def warm_cache():
    """캐시 예열"""
    
    print("=== Cache Warming Started ===\n")
    
    # Ollama 클라이언트
    ollama = get_ollama_client()
    
    # 자주 사용되는 검색어
    common_queries = [
        "반도체",
        "AI",
        "전기차",
        "배터리",
        "로봇",
        "SK 하이닉스",
        "삼성전자",
        "엔비디아",
        "테슬라",
        "HBM3e"
    ]
    
    print("1. Warming entity embeddings...")
    try:
        kg = KnowledgeGraph()
        
        for query in common_queries:
            # 임베딩 생성 (캐시됨)
            results = kg.find_related_entities(query, top_k=5)
            print(f"  ✅ {query}: {len(results)} entities")
    
    except Exception as e:
        print(f"  ⚠️  Entity warming failed: {e}")
    
    print("\n2. Warming LLM responses...")
    
    # 자주 사용되는 프롬프트 (temperature=0.2로 캐싱 가능)
    common_prompts = [
        "다음 키워드의 주요 특징을 3줄로 요약하세요: 반도체",
        "다음 키워드의 주요 특징을 3줄로 요약하세요: AI",
        "다음 키워드의 주요 특징을 3줄로 요약하세요: 전기차"
    ]
    
    for prompt in common_prompts:
        try:
            response = ollama.generate(prompt, temperature=0.2)
            print(f"  ✅ Cached: {prompt[:30]}...")
        except Exception as e:
            print(f"  ⚠️  LLM warming failed: {e}")
    
    print("\n=== Cache Warming Complete ===\n")
    
    # 캐시 통계 출력
    try:
        monitor = get_cache_monitor()
        monitor.print_stats()
    except Exception as e:
        print(f"⚠️  Cache stats unavailable: {e}")


if __name__ == "__main__":
    warm_cache()
