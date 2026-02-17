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

    def cross_reference_signals(self, naver_candidates: List[Dict], youtube_candidates: List[Dict]) -> List[Dict]:
        """
        Boosts scores if a keyword appears in both Naver (Interest Start) and YouTube (Viral Spread).
        """
        refined_list = []
        
        # Simple exact match or partial match map
        # In production, vector similarity would be better, but we start with string matching
        yt_map = {item['keyword']: item for item in youtube_candidates}
        
        for n_item in naver_candidates:
            keyword = n_item['keyword']
            base_score = n_item['z_score']
            
            # Cross-ref check
            if keyword in yt_map:
                # Boost!
                yt_velocity = yt_map[keyword].get('velocity', 0)
                boost_factor = 1.0 + (min(yt_velocity, 10.0) * 0.1) # Max 2x burst
                final_score = base_score * 1.5 * boost_factor
                
                n_item['cross_ref_source'] = 'YouTube'
                n_item['status'] = 'VIRAL'
            else:
                final_score = base_score
                n_item['status'] = 'RISING'
                
            n_item['final_score'] = round(final_score, 2)
            refined_list.append(n_item)
            
        # Add YouTube-only items if they are super hot (Velocity > Threshold)
        for y_item in youtube_candidates:
            if y_item['keyword'] not in [r['keyword'] for r in refined_list]:
                if y_item.get('velocity', 0) > 5.0: # High velocity threshold
                    y_item['final_score'] = y_item.get('velocity', 0) * 10 
                    y_item['status'] = 'BREAKING'
                    refined_list.append(y_item)
                    
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

    def save_trends_to_db(self, trends: List[Dict]):
        """
        Saves the processed trends to 'active_realtime_trends'
        """
        conn = get_db_connection(self.db_url)
        try:
            with conn.cursor() as cur:
                # 1. Clear old active trends (or archive them if we had a history table)
                cur.execute("DELETE FROM active_realtime_trends")
                
                # 2. Insert new ones
                for i, t in enumerate(trends[:10]): # Top 10
                    cur.execute("""
                        INSERT INTO active_realtime_trends 
                        (rank, keyword, avg_score, related_insight, status, source, link)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        i+1, 
                        t['keyword'], 
                        t['final_score'], 
                        t.get('reason', 'AI Detection'), 
                        t.get('status', 'NEW'),
                        t.get('source', 'System'),
                        t.get('link', '#')
                    ))
            conn.commit()
        except Exception as e:
            print(f"❌ DB Save failed: {e}")
        finally:
            conn.close()
