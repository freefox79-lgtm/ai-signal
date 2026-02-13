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
    
    # 1. Collection
    raw_results = connectors.fetch_naver_search(query)
    # Mocking metadata for density calculation
    count = len(raw_results)
    unique_keywords = count * 2 # Mocked ratio
    vibrancy = 0.75 # Mocked sentiment
    
    # 2. Density Assessment
    score = calculator.calculate_score(f"Naver_{query}", count, unique_keywords, vibrancy)
    interval = calculator.suggest_interval(score)
    
    # 3. Output Synthesis
    discovery_report = {
        "query": query,
        "results_count": count,
        "density_score": score,
        "suggested_sync_interval": interval,
        "top_signals": raw_results[:3]
    }
    
    return discovery_report

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "AI Trend"
    report = run_discovery(target)
    print(json.dumps(report, indent=2, ensure_ascii=False))
