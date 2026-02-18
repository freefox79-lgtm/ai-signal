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
        
    def calculate_z_score(self, current_value: float, history: List[float], window_size: int = 24) -> float:
        """
        Calculates a stable Z-Score using a moving average window.
        Z = (X - μ_window) / σ_window
        """
        if not history or len(history) < 3:
            return 0.0
            
        # Use only the last window_size samples for the 24h-like effect
        effective_history = history[-window_size:]
        
        mean = np.mean(effective_history)
        std_dev = np.std(effective_history)
        
        if std_dev < 0.01: # Stabilize against near-zero variance
            return 0.0
            
        z = (current_value - mean) / std_dev
        return round(float(z), 2)
        
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

    def calculate_weighted_score(self, signals: Dict[str, float], category: str = "TECH") -> float:
        """
        Calculates the Total Signal Score with category-specific attenuation (λ_cat).
        Category Coefficients:
        - FINANCE: 0.5 (Dampen high volatility)
        - TECH/CELEB: 1.0 (Standard)
        - LIFESTYLE/SHOPPING: 1.2 (Boost organic impact)
        """
        total_score = 0.0
        
        # λ_cat: Dynamic Attenuation Coefficient
        LAMBDA_CAT = {
            'FINANCE': 0.5,
            'TECH': 1.0,
            'CELEB': 1.0,
            'LIFESTYLE': 1.2,
            'SHOPPING': 1.2
        }
        lam = LAMBDA_CAT.get(category.upper(), 1.0)
        
        for source, weight in self.WEIGHTS.items():
            raw_score = signals.get(source, 0.0)
            normalized = min(max(raw_score, 0.0), 100.0)
            total_score += (normalized * weight)
            
        # Apply Category Attenuation
        final_score = total_score * lam
            
        return round(float(final_score), 2)

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

    def categorize_keyword(self, item: Dict) -> str:
        """
        Heuristic categorization of keywords.
        """
        keyword = item.get('keyword', '').upper()
        source = item.get('source', '').upper()
        
        # Priority 1: Market/Finance sources
        if any(x in source for x in ['CRYPTO', 'STOCK', 'FINANCE', 'MARKET', 'UPBIT', 'BINANCE']):
            return 'FINANCE'
            
        # Priority 2: Keyword matching
        finance_keywords = ['주가', '비트코인', '이더리움', '삼성전자', '금리', '환율']
        if any(x in keyword for x in finance_keywords):
            return 'FINANCE'
            
        lifestyle_keywords = ['여행', '음식', '맛집', '패션', '쇼핑', '할인', '탕후루']
        if any(x in keyword for x in lifestyle_keywords):
            return 'LIFESTYLE'
            
        celeb_keywords = ['컴백', '루머', '열애', '아이돌', '뉴진스', 'BTS']
        if any(x in keyword for x in celeb_keywords):
            return 'CELEB'
            
        return 'TECH' # Default

    def cross_reference_signals(self, candidates: List[Dict]) -> List[Dict]:
        """
        Processes a list of candidates, categorizes them, and calculates the final 
        balanced score using λ_cat.
        """
        refined_list = []
        
        for item in candidates:
            # 0. Categorization
            cat = self.categorize_keyword(item)
            item['category'] = cat
            
            # 1. Normalize Signals
            z_score = item.get('z_score', 0)
            slope = item.get('slope', 0)
            density = item.get('search_density', 0)
            
            search_raw = (z_score * 20) + (slope * 50) + (density * 0.5)
            
            signals = {
                'search': min(search_raw, 100),
                'video': min(item.get('velocity', 0) * 10, 100),
                'sns': item.get('sns_volume', 0),
                'community': item.get('community_activity', 0),
                'finance': min(item.get('finance_volatility', 0), 100)
            }
            
            # 2. Calculate Weighted Score (with λ_cat)
            final_score = self.calculate_weighted_score(signals, category=cat)
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

    def generate_trend_briefing(self, item: Dict) -> str:
        """
        [AI Signal: Strategic Analysis Briefing]
        Direct synthesis focusing on 'Why' it's trending (Search spikes, SNS momentum).
        """
        keyword = item.get('keyword', 'Unknown')
        category = item.get('category', 'TECH')
        score = item.get('final_score', 0)
        z_value = item.get('z_score', 0)
        source = item.get('source', 'System')
        
        prompt = f"""
        당신은 AI Signal 시스템의 분석 엔진 Gemma 3입니다. 
        데이터 시그널을 분석하여 이 트렌드가 '왜' 발생했는지 대중이 이해하기 쉽게 직관적인 브리핑을 작성하세요.
        
        [데이터 요약]
        - 키워드: {keyword} ({category})
        - 분석 지표: 검색량(Z-Score {z_value}), 사회적 화제성(Score {score})
        - 주요 신호: {source}
        
        [작업 가이드]
        1. "네이버 검색량이 전일 대비 급증", "SNS 및 커뮤니티 언급 횟수 대폭 증가", "주요 매체 보도" 등 구체적인 원인을 언급하세요.
        2. 페르소나(쥄/쥐핏) 언급 없이, 객관적이고 전문가적인 어조로 핵심만 전달하세요.
        3. 반드시 2~3문장의 짧고 강렬한 Markdown 텍스트로 한국어로만 출력하세요.
        
        [출력 양식 예시]
        ### [AI SIGNAL: 전략 분석]
        해당 키워드는 현재 네이버 검색량이 급격히 상승 중이며, 주요 커뮤니티와 SNS상에서 언급 횟수가 빠르게 증가하고 있습니다. 특히 관련 매체의 보도가 이어지며 사회적 화제성이 임계치를 돌파한 것으로 분석됩니다. 향후 48시간 동안 높은 모멘텀이 유지될 것으로 예측됩니다.
        """
        
        try:
            response = self.ollama.generate(
                prompt=prompt,
                model=self.ollama.MODEL_REASONING, # Using Gemma 3 12B
                temperature=0.3,
                max_tokens=400,
                options={
                    "num_ctx": 4096,
                    "num_gpu": 99 # Maximize M4 Metal
                }
            )
            report = response.strip()
            if not report.startswith("###"):
                report = f"### [AI SIGNAL: 전략 분석]\n{report}"
            return report
        except Exception as e:
            print(f"⚠️ Briefing gen failed for {keyword}: {e}")
            return f"### [AI SIGNAL: 전략 분석]\n\n해당 키워드의 네이버 검색량 및 SNS 화제성 지표가 임계치를 돌파하여 분석 중입니다."

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
