import os
import sys
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db_utils import get_db_connection
from data_router import router
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
        다음 키워드들을 관련된 주제별로 그룹화하세요. 각 그룹을 대표하는 키워드는 반드시 구체적이고 트렌디한 **한국어** 키워드여야 합니다.
        
        CRITICAL INSTRUCTION: 
        - Representative Keyword MUST be in **Korean**.
        - It must be specific (e.g., "삼성전자" instead of "기술주").
        - Do not use generic categories like "암호화폐" or "음식". Use specific names like "비트코인" or "탕후루".
        
        Keywords: {", ".join(keywords)}
        
        Output Format (JSON):
        [
            {{"representative": "한국어핵심키워드", "members": ["kw1", "kw2"]}},
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

    def cross_verify_with_gemma(self, ranked_trends: List[Dict]) -> List[Dict]:
        """
        [Stage 2.7: Deep Reasoning & Governance]
        Uses Gemma 3 12B to cross-verify the analyst's findings and add 'Contrarian' or 'Deep Persona' insights.
        """
        if not ranked_trends:
            return []

        print(f"💎 [Gemma 3] Performing deep semantic reasoning on top {len(ranked_trends[:5])} trends...")
        
        context = "\n".join([f"- {i['keyword']} (Analytic Score: {i['final_score']})" for i in ranked_trends[:5]])
        
        prompt = f"""
        당신은 AI Signal 시스템의 '전략적 합의 엔진' Gemma 3입니다.
        분석 전문가가 도출한 상위 트렌드를 검토하고, 경제적 가치와 '사회문화적 영향력'사이의 균형 잡힌 통찰을 제시하십시오.
        
        트렌드 리스트:
        {context}
        
        작업:
        1. 각 트렌드가 대중의 라이프스타일이나 심리에 어떤 변화를 일으킬지 추론하십시오.
        2. 금융적 관점(쥄)과 트렌드 관점(쥐핏) 사이의 충돌을 해결하고 '전략적 합의(Strategic Consensus)'를 도출하십시오.
        3. 단순 수치 분석을 넘어선 '문화적 맥락'을 12B 모델의 깊이로 설명하십시오.
        
        출력 형식:
        한국어로 3-4문장의 강력한 리포트를 작성하십시오.
        """
        
        try:
            # We use the new MODEL_REASONING (Gemma 3)
            reasoning_report = self.ollama.generate(
                prompt=prompt,
                model=self.ollama.MODEL_REASONING,
                temperature=0.4,
                max_tokens=600,
                options={
                    "num_ctx": 8192,
                    "num_gpu": 99 # Maximize Mac Mini GPU power for 12B
                }
            )
            
            # Attach the deep reasoning to the top item or a global field
            if ranked_trends:
                ranked_trends[0]['gemma_deep_reasoning'] = reasoning_report
                
            return ranked_trends
        except Exception as e:
            print(f"⚠️ Gemma reasoning failed: {e}")
            return ranked_trends

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
        [SYSTEM: OUTPUT MUST BE IN KOREAN ONLY]
        당신은 데이터 분석 전문가입니다. 주어진 데이터를 바탕으로 '{keyword}'가 왜 현재 트렌딩인지 **반드시 한국어**로만 설명해 주세요.
        
        [Data Evidence]
        - Keyword: {keyword}
        - Related Keywords: {related_str}
        - {', '.join(evidence)}
        
        [Task]
        3줄의 객관적인 브리핑을 한국어로 작성하세요. 영어는 사용하지 마세요.
        1줄: {keyword}의 현재 지표를 해석 (바이럴, 급상승 등).
        2줄: 연관 키워드를 통한 트렌드 배경 추론.
        3줄: 트렌드의 지속성 및 향후 확산 가능성 결론.
        
        **주의: 분석 결과는 반드시 한국어(Korean)로만 출력하세요.**
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
        Saves the processed trends to 'active_realtime_trends' using the DataRouter.
        """
        # 1. Clear old active trends
        router.execute_query("DELETE FROM active_realtime_trends", table_hint='active_realtime_trends')
        
        import json
        # 2. Insert new ones
        for i, t in enumerate(trends[:10]): # Top 10
            router.execute_query("""
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
            ), table_hint='active_realtime_trends')
        
        print(f"✅ [TrendAnalyzer] Saved {min(len(trends), 10)} trends via DataRouter.")
