import json
import os
from datetime import datetime

class DataDensityCalculator:
    """
    Calculates the 'intelligence density' of data sources to optimize collection frequency.
    Factors: Update frequency, Keyword relevance, Hype score (JFIT), and Logical impact (JWEM).
    """
    
    def __init__(self, config_path="data_sources_config.json"):
        self.config_path = config_path
        self.sources = self._load_config()

    def _load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                return json.load(f)
        return {}

    def calculate_score(self, source_name, raw_data_count, unique_keywords_count, sentiment_vibrancy):
        """
        Calculates a density score between 0 and 100.
        """
        # weightage
        W_QUANTITY = 0.3
        W_QUALITY = 0.5
        W_VIBRANCY = 0.2
        
        quantity_score = min(raw_data_count / 100, 1.0) * 100
        quality_score = min(unique_keywords_count / 20, 1.0) * 100
        vibrancy_score = sentiment_vibrancy * 100 # 0.0 to 1.0
        
        final_score = (quantity_score * W_QUANTITY) + \
                      (quality_score * W_QUALITY) + \
                      (vibrancy_score * W_VIBRANCY)
        
        return round(final_score, 2)

    def suggest_interval(self, score):
        """
        Suggests sync interval in seconds based on density score.
        High score (High Density) -> Frequent sync (e.g., 5 mins)
        Low score (Low Density) -> Sparse sync (e.g., 6 hours)
        """
        if score > 80:
            return 300 # 5 mins
        elif score > 50:
            return 1800 # 30 mins
        elif score > 20:
            return 7200 # 2 hours
        else:
            return 21600 # 6 hours

if __name__ == "__main__":
    calc = DataDensityCalculator()
    # Test calculation
    test_score = calc.calculate_score("Naver_Finance", 150, 45, 0.8)
    print(f"[DENSITY] Test Source Score: {test_score}")
    print(f"[DENSITY] Suggested Interval: {calc.suggest_interval(test_score)}s")
