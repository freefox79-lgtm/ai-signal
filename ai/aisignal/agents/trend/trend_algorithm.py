import os
import sys
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db_utils import get_db_connection
from agents.llm.ollama_client import get_ollama_client

class TrendAnalyzer:
    """
    Implements the core algorithmic logic for identifying real-time search trends.
    """
    
    def __init__(self):
        self.ollama = get_ollama_client()
        self.db_url = os.getenv("DATABASE_URL")
        
    def calculate_z_score(self, current_value: float, history: List[float]) -> float:
        """
        Calculates the Z-Score of the current value against the history.
        Z = (X - μ) / σ
        """
        if not history or len(history) < 3:
            return 0.0 # Not enough data
            
        mean = np.mean(history)
        std_dev = np.std(history)
        
        if std_dev == 0:
            return 0.0
            
        return (current_value - mean) / std_dev
        
    def get_velocity(self, current_value: float, previous_value: float, time_delta_minutes: int) -> float:
        """
        Calculates the rate of change per minute.
        """
        if time_delta_minutes == 0:
            return 0.0
        return (current_value - previous_value) / time_delta_minutes

    # Phase 13: Weighted Scoring Configuration
    WEIGHTS = {
        'search': 0.3,    # Naver/Google
        'sns': 0.25,      # Twitter/Insta
        'community': 0.2, # DC/FMKorea
        'video': 0.15,    # YouTube
        'finance': 0.15   # Stock/Crypto/Market
    }

    def calculate_weighted_score(self, signals: Dict[str, float]) -> float:
        """
        Calculates the Total Signal Score based on the 5-source weighted formula.
        Signals should be normalized to 0-100 range before calling.
        """
        total_score = 0.0
        details = {}
        
        for source, weight in self.WEIGHTS.items():
            raw_score = signals.get(source, 0.0)
            # Cap raw score at 100 for safety, though normalization should handle it
            normalized = min(max(raw_score, 0.0), 100.0)
            
            weighted_val = normalized * weight
            total_score += weighted_val
            details[source] = weighted_val
            
        return round(total_score, 2)

    def calculate_slope(self, series: List[float]) -> float:
        """
        Calculates the Rate of Change (Slope).
        Formula: (Current - Avg_History) / Avg_History
        """
        if not series or len(series) < 2:
            return 0.0
            
        current = series[-1]
        history = series[:-1]
        avg_hist = np.mean(history)
        
        if avg_hist == 0:
            return 0.0 if current == 0 else 1.0 # Jump from 0 is infinite, cap at 1.0 (100%)
            
        return (current - avg_hist) / avg_hist

    def cross_reference_signals(self, candidates: List[Dict]) -> List[Dict]:
        """
        Processes a list of candidates that already have raw signal data attached.
        Calculates the final weighted score for each.
        """
        refined_list = []
        
        for item in candidates:
            # 1. Normalize Signals (Enhanced with Phase 14 Precision)
            
            # Search Score: Composition of Z-Score, Slope, and Density
            z_score = item.get('z_score', 0)
            slope = item.get('slope', 0) # e.g. 0.5 = 50% increase
            density = item.get('search_density', 0) # e.g. 50 posts/3h
            
            # Heuristic: 
            # Z=3 -> 60pts
            # Slope=1.0 -> 50pts
            # Density=100 -> 50pts
            search_raw = (z_score * 20) + (slope * 50) + (density * 0.5)
            
            signals = {
                'search': min(search_raw, 100),
                'video': min(item.get('velocity', 0) * 10, 100),       # Vel=10 -> 100
                'sns': item.get('sns_volume', 0),                      # Direct (Mock)
                'community': item.get('community_activity', 0),        # Direct (Mock)
                'finance': min(item.get('finance_volatility', 0), 100) # Stock/Crypto Volatility
            }
            
            # 2. Calculate Weighted Score
            final_score = self.calculate_weighted_score(signals)
            item['final_score'] = final_score
            item['signal_breakdown'] = signals
            
            # 3. Determine Status
            if final_score > 80:
                item['status'] = 'BREAKING'
            elif final_score > 50:
                item['status'] = 'VIRAL'
            else:
                item['status'] = 'RISING'
                
            refined_list.append(item)
            
        return sorted(refined_list, key=lambda x: x['final_score'], reverse=True)

    def cluster_keywords(self, candidates: List[Dict]) -> List[Dict]:
        """
        Uses Local LLM to group similar keywords.
        Ex: "Son Heung-min goal", "Sonny highlight" -> "Son Heung-min"
        """
        if not candidates:
            return []
            
        # Prepare list for LLM
        keywords = [c['keyword'] for c in candidates[:20]] # Limit to top 20 for speed
        if not keywords:
            return candidates
            
        prompt = f"""
        Group the following keywords into distinct topics. Determine a single representative keyword for each group.
        
        Keywords: {", ".join(keywords)}
        
        Output Format (JSON):
        [
            {{"representative": "Topic A", "members": ["kw1", "kw2"]}},
            ...
        ]
        """
        
        try:
            response = self.ollama.generate(
                prompt=prompt,
                model=self.ollama.MODEL_FAST,
                temperature=0.1,
                max_tokens=500,
                options={
                    "num_ctx": 4096,   # Larger context for list processing
                    "num_gpu": 99      # Force full GPU offload (Mac Mini optimization)
                }
            )
            
            # Parse Mock-ish logic for now if LLM fails or simple rule-based fallback
            # Real implementation needs robust JSON parsing from LLM output
            # For this iteration, we trust the LLM or fallback to identity
            
            # Validating JSON
            import json
            import re
            
            # Extract JSON block if needed
            match = re.search(r'\[.*\]', response, re.DOTALL)
            if match:
                clusters = json.loads(match.group(0))
                
                clustered_results = []
                processed_keywords = set()
                
                for cluster in clusters:
                    rep = cluster['representative']
                    members = cluster['members']
                    
                    # Find the highest scoring member to inherit score
                    best_score = 0
                    best_item = None
                    
                    for m in members:
                        # Find original item
                        orig = next((x for x in candidates if x['keyword'] == m), None)
                        if orig:
                            processed_keywords.add(m)
                            if orig['final_score'] > best_score:
                                best_score = orig['final_score']
                                best_item = orig
                    
                    if best_item:
                        # Create fused item
                        fused = best_item.copy()
                        fused['keyword'] = rep
                        fused['members'] = members
                        clustered_results.append(fused)
                
                # Add leftovers
                for item in candidates:
                    if item['keyword'] not in processed_keywords:
                        clustered_results.append(item)
                        
                return sorted(clustered_results, key=lambda x: x['final_score'], reverse=True)
                
        except Exception as e:
            print(f"⚠️ Clustering failed: {e}")
            return candidates # Fallback to original list

        return candidates

    def generate_trend_briefing(self, keyword: str, slope: float, density: int, related_keywords: List[str] = None) -> str:
        """
        Uses Local LLM (Persona: Data Analysis Expert) to explain WHY this is trending.
        Input: Numerical evidence (Slope, Density).
        Output: 3-line briefing.
        """
        # Construct Numerical Evidence string
        evidence = []
        if slope > 0:
            evidence.append(f"Trend Slope: +{slope*100:.0f}% (Rapidly Rising)")
        elif slope < 0:
            evidence.append(f"Trend Slope: {slope*100:.0f}% (Cooling Down)")
        else:
            evidence.append("Trend Slope: Flat")
            
        evidence.append(f"Posting Density: {density} posts/3h")
        
        if density >= 50:
             evidence.append("(High Urgency/Viral)")
        elif density < 10:
             evidence.append("(Low Volume/Organic)")
             
        related_str = ", ".join(related_keywords) if related_keywords else "None"
             
        prompt = f"""
        You are a Data Analysis Expert. Your job is to explain why '{keyword}' is trending based on the provided data.
        
        [Data Evidence]
        - Keyword: {keyword}
        - Related Keywords: {related_str}
        - {', '.join(evidence)}
        
        [Task]
        Provide a 3-line objective briefing.
        Line 1: Interpret the metrics (Is it viral? Is it breaking news?).
        Line 2: Hypothesize the context based on related keywords.
        Line 3: Conclusion on the trend's momentum.
        
        Output only the 3 lines. Do not use markdown headers.
        """
        
        try:
            response = self.ollama.generate(
                prompt=prompt,
                model=self.ollama.MODEL_FAST, # Use faster model for 10x calls
                temperature=0.3,
                max_tokens=150,
                options={
                    "num_ctx": 2048,
                    "num_gpu": 99
                }
            )
            return response.strip()
        except Exception as e:
            print(f"⚠️ Briefing gen failed for {keyword}: {e}")
            # Structural Fallback
            desc = "상승 추세가 관측됩니다." if slope > 0 else "데이터 변동이 감지되었습니다."
            urgency = " (급상승 중)" if density > 30 else ""
            return f"{keyword}에 대한 {desc}{urgency} 분석 데이터 축적 중입니다."

    def save_trends_to_db(self, trends: List[Dict]):
        """
        Saves the processed trends to 'active_realtime_trends'
        """
        conn = get_db_connection(self.db_url)
        try:
            with conn.cursor() as cur:
                # 1. Clear old active trends (or archive them if we had a history table)
                cur.execute("DELETE FROM active_realtime_trends")
                
                import json
                # 2. Insert new ones
                for i, t in enumerate(trends[:10]): # Top 10
                    cur.execute("""
                        INSERT INTO active_realtime_trends 
                        (rank, keyword, avg_score, related_insight, status, source, link, signal_breakdown)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        i+1, 
                        t['keyword'], 
                        t['final_score'], 
                        t.get('related_insight') or t.get('reason') or 'AI Detection', 
                        t.get('status', 'NEW'),
                        t.get('source', 'System'),
                        t.get('link', '#'),
                        json.dumps(t.get('signal_breakdown', {}))
                    ))
            conn.commit()
        except Exception as e:
            print(f"❌ DB Save failed: {e}")
        finally:
            conn.close()
