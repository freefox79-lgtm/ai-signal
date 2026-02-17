import json
import sys
from api_connectors import APIConnectors
from data_density_calculator import DataDensityCalculator

def run_discovery(query):
    """
    Orchestrates the discovery process:
    1. Fetch raw data via connectors.
    2. Calculate intelligence density.
    3. Return structured results for n8n/DB.
    """
    connectors = APIConnectors()
    calculator = DataDensityCalculator()
    
    print(f"[*] Starting discovery for: {query}")
    
    # 3. Discovery Reasoning (Phase 20: Gemma 3 Integration)
    from agents.llm.ollama_client import get_ollama_client
    ollama = get_ollama_client()
    
    print(f"💎 [Gemma 3] Performing Discovery Reasoning for '{query}'...")
    reasoning_prompt = f"""
    당신은 AI Signal의 '자율 탐색 전문가' Gemma 3입니다.
    탐색된 키워드 '{query}'와 관련된 상위 신호들을 검토하고, 이 트렌드의 '정성적 가치'를 분석하세요.
    
    상위 신호:
    {json.dumps(raw_results[:3], ensure_ascii=False)}
    
    작업:
    1. 이 키워드가 단순 노이즈인지, 아니면 구조적 변화인지를 판별하십시오.
    2. 데이터 밀도 점수({score:.2f})가 시사하는 바를 해석하십시오.
    
    출력:
    한국어로 2문장의 핵심 탐색 보고서를 작성하십시오.
    """
    
    try:
        discovery_reasoning = ollama.generate(
            prompt=reasoning_prompt,
            model=ollama.MODEL_REASONING,
            temperature=0.3
        )
    except Exception as e:
        discovery_reasoning = "AI 추론 엔진 응답 대기 중..."

    # 4. Output Synthesis
    discovery_report = {
        "query": query,
        "results_count": count,
        "density_score": score,
        "suggested_sync_interval": interval,
        "discovery_reasoning": discovery_reasoning,
        "top_signals": raw_results[:3]
    }
    
    return discovery_report

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "AI Trend"
    report = run_discovery(target)
    print(json.dumps(report, indent=2, ensure_ascii=False))
