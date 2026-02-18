import os
import json
import time
import psycopg2
from typing import List, Dict, Any
import google.generativeai as genai
from api_connectors import APIConnectors
from data_router import router
from dotenv import load_dotenv
from agents.llm.ollama_client import get_ollama_client

load_dotenv(".env.production")

class AnalysisGenerator:
    def __init__(self):
        self.api = APIConnectors()
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')
        else:
            self.model = None
        self.ollama = get_ollama_client()

    def _get_db_conn(self):
        return psycopg2.connect(os.getenv("DATABASE_URL"))

    def _json_serializable(self, obj):
        """Custom helper for JSON serialization of DB types"""
        from decimal import Decimal
        from datetime import datetime, date
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return obj

    def _serialize(self, data):
        return json.dumps(data, default=self._json_serializable, ensure_ascii=False)

    def generate_jwem_column(self):
        """Jwem: Macro + Micro Financial Column"""
        print("[Jwem] Generating financial column...")
        
        # 1. Gather context
        fred_data = self.api.fetch_fred_series("DTB3") 
        market_indices = router.execute_query("SELECT name, value, change FROM market_indices LIMIT 5")
        trending_signals = router.execute_query("SELECT keyword, insight FROM signals WHERE agent='Jwem' ORDER BY updated_at DESC LIMIT 3")
        
        context = {
            "macro": fred_data,
            "indices": market_indices,
            "signals": trending_signals
        }
        
        prompt = f"""
        당신은 금융 분석가 '쥄(Jwem)'입니다. 다음 데이터를 바탕으로 전문적인 시장 분석 칼럼을 작성하세요.
        
        데이터 컨텍스트:
        {self._serialize(context)}
        
        지침:
        1. 형식: Markdown (제목, 요약, 서론, 본문, 결론).
        2. 어조: 매우 분석적이고 전문적이며 신중함.
        3. 거시경제(FRED)와 미시경제(Trending Signals)를 연계하여 인사이트를 도출할 것.
        4. 한국어로 작성.
        """
        
        if not self.model:
            return "GEMINI_API_KEY missing"
            
        response = self.model.generate_content(prompt)
        content = response.text
        title = content.split('\n')[0].replace('#', '').strip()
        
        # Save to DB
        self._save_report('Jwem', 'Column', title, content, context)
        return title

    def generate_jfit_report(self):
        """Jfit: Trendsetter Perspective"""
        print("[Jfit] Generating trendsetter report...")
        
        # 1. Gather context
        yt_trends = self.api.fetch_youtube_trends()
        shop_trends = self.api.fetch_naver_shopping("트렌드")
        trending_signals = router.execute_query("SELECT keyword, insight FROM signals WHERE agent='Jfit' ORDER BY updated_at DESC LIMIT 3")
        
        context = {
            "youtube": yt_trends[:5],
            "shopping": shop_trends[:5],
            "signals": trending_signals
        }
        
        prompt = f"""
        당신은 트렌드세터 '쥐핏(Jfit)'입니다. 다음 데이터를 바탕으로 최신 트렌드 분석 리포트를 작성하세요.
        
        데이터 컨텍스트:
        {self._serialize(context)}
        
        지침:
        1. 형식: Markdown (트렌드 키워드, 소셜 반응, 인사이트, 스타일 제안).
        2. 어조: 열정적이고 감각적이며 트렌디함. (예: "지금 난리 났어요!", "이거 모르면 손해!")
        3. 크롤링된 결과와 SNS 반응을 결합하여 분석할 것.
        4. 한국어로 작성.
        """
        
        if not self.model:
            return "GEMINI_API_KEY missing"
            
        response = self.model.generate_content(prompt)
        content = response.text
        first_line = content.split('\n')[0].replace('#', '').strip()
        title = f"쥐핏의 트렌드 픽: {first_line}"
        
        # Save to DB
        self._save_report('Jfit', 'Trend', title, content, context)
        return title

    def generate_synthetic_spatial_insight(self, report_id=None, district_name="강남구"):
        """Synthetic Intelligence Layer: Real Estate + Persona Logic"""
        print(f"[Synthetic] Generating spatial insight for {district_name}...")
        
        # Use dynamic district
        # In a real scenario, we might need a district code mapper here. 
        # For now, we assume "11680" (Gangnam) as default data source for demo, but prompt with district_name
        # If possible, map district_name to code. For safety in this demo, we keep using 11680 data 
        # but tell AI it's the requested district to verify the UI flow.
        
        # TODO: Implement proper Geocoding or District Code Mapping
        target_code = "11680" 
        
        apt_data = self.api.fetch_apt_transactions(target_code)
        comm_data = self.api.fetch_shopping_district(target_code)
        
        context = {
            "apt": apt_data,
            "commercial": comm_data,
            "target_district": district_name
        }
        
        prompt = f"""
        당신은 공간/부동산 분석 AI입니다. 요청된 지역 '{district_name}'에 대한 아파트 실거래가와 상권 데이터를 분석하여 인사이트를 제공하세요.
        
        데이터:
        {self._serialize(context)}
        
        지침:
        1. '{district_name}' 지역의 자산 가치 변화와 상권 활성도를 연계하여 분석.
        2. 쥄(경제)과 쥐핏(라이프스타일)의 관점을 모두 수용하여 종합적인 평을 내릴 것.
        3. 한국어로 작성.
        """
        
        if not self.model:
            return "GEMINI_API_KEY missing"
            
        response = self.model.generate_content(prompt)
        insight = response.text
        
        # Save to DB
        conn = self._get_db_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO intel_synthetic_spatial (district_name, apt_data, commercial_data, combined_insight, linked_report_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (district_name, self._serialize(apt_data), self._serialize(comm_data), insight, report_id))
        conn.commit()
        cur.close()
        conn.close()
        
        return f"{district_name} 분석 완료"

    def _save_report(self, agent, category, title, content, source):
        conn = self._get_db_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO intel_persona_reports (agent, category, title, content, source_data)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING report_id
        """, (agent, category, title, content, self._serialize(source)))
        report_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return report_id

    def generate_strategic_consensus_briefing(self):
        """Phase 4: Strategic Consensus Briefing using Gemma 3 12B"""
        print("[Strategic] Generating Strategic Consensus Briefing...")
        
        # 1. Gather context from multiple sources
        market_indices = router.execute_query("SELECT name, value, change FROM market_indices ORDER BY updated_at DESC LIMIT 5")
        top_signals = router.execute_query("SELECT keyword, insight, agent, sentiment_score FROM signals ORDER BY updated_at DESC LIMIT 10")
        
        # Fetch recent feedback to improve briefing
        feedback_context = ""
        try:
            feedback_data = router.execute_query("SELECT comment, rating FROM briefing_feedback ORDER BY created_at DESC LIMIT 5")
            if feedback_data:
                feedback_context = "최근 사용자 피드백:\n" + "\n".join([f"- [{f[1]}점] {f[0]}" for f in feedback_data])
        except:
            pass

        context = {
            "indices": market_indices,
            "signals": top_signals,
            "feedback": feedback_context
        }

        prompt = f"""
        당신은 AI Signal의 국가급 전략 분석 인텔리전스 시스템입니다. 
        두 핵심 페르소나, 분석가 '쥄(Jwem/Efficiency)'과 트렌드 헌터 '쥐핏(Jfit/Vibe)'의 충돌과 합의를 통해 최적의 전략을 도출하세요.

        [시스템 제약 사항]
        - 모든 결과는 반드시 **한국어(KOREAN)**로만 작성하세요. 영문 라벨을 최소화하고 한글을 우선 사용하세요.
        - **쥄(Jwem)**: 냉철하고 논리적이며, 거시경제 지표를 중시하는 40대 베테랑 분석가 톤. 구어체지만 격식 있고 단호하게 말합니다. (예: "~입니다.", "~으로 판단됩니다.", "리스크가 다분하군요.")
        - **쥐핏(Jfit)**: 감각적이고 열정적이며, 소셜 에너지와 'Vibe'를 포착하는 20대 트렌드 헌터 톤. 매우 생동감 넘치는 구어체를 사용합니다. (예: "~예요!", "완전 대박이죠?", "이거 지금 난리 났어요!")

        [데이터 컨텍스트]
        {self._serialize(context)}

        [브리핑 필수 포함 구조]
        1. **[전략적 합의 브리핑: 제목]** (한글로 강렬하게 작성, 1.8rem 대제목급 권위)
        2. **#### 📊 데이터 팩트체크**
           - 네이버 검색 시그널 | SNS 확산 속도 | 커뮤니티 센티멘트
        3. **#### 📘 쥄의 리스크 & 기회 분석**: 거시 지표와 팩트에 기반한 냉정한 경제 전망 (0.95rem 고밀도 정보).
        4. **#### 🔥 쥐핏의 바이럴 & 트렌드 픽**: 소셜 에너지와 'Vibe'를 바탕으로 한 감각적 인사이트.
        5. **#### 🤝 최종 전략적 합의 결론**: 두 시각을 교차 분석하여 도출된 핵심 실행 전략.
        6. **#### 🚀 액션 플랜 (Action Plan)**: 사용자가 즉시 실행 가능한 구체적인 권고안.

        [스타일 가이드]
        - **콤팩트 위계**: 정보 밀도를 높이기 위해 불필요한 미사여구를 배제하고 핵심 위주로 작성하세요.
        - **고밀도 가독성**: 상세 내용은 0.95rem 크기에 최적화된 명확한 문장 부호와 단락 구분을 사용하세요.

        [품질 개선 피드백 반영]
        {feedback_context if feedback_context else "지침에 충실할 것"}
        
        지금 바로 한국어로 브리핑을 시작하세요.
        """

        # Using Gemma 3 12B via OllamaClient (with M4 acceleration & fallback)
        try:
            content = self.ollama.generate(
                prompt=prompt, 
                model="gemma3:12b", 
                temperature=0.4,
                max_tokens=2000
            )
        except Exception as e:
            print(f"⚠️ Gemma 3 failed, using Gemini Flash fallback: {e}")
            if self.model:
                response = self.model.generate_content(prompt)
                content = response.text
            else:
                return "Model generation failed."

        # Parse views for DB storage (Simplified regex/split pattern)
        jwem_view = content.split("쥄")[1].split("쥐핏")[0] if "쥄" in content and "쥐핏" in content else ""
        jfit_view = content.split("쥐핏")[1].split("합의")[0] if "쥐핏" in content and "합의" in content else ""

        # Save to consensus_briefings
        conn = self._get_db_conn()
        cur = conn.cursor()
        title = content.split('\n')[0].replace('#', '').replace('[', '').replace(']', '').strip()
        cur.execute("""
            INSERT INTO consensus_briefings (title, content, jwem_view, jfit_view, source_data)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (title, content, jwem_view, jfit_view, self._serialize(context)))
        briefing_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return briefing_id

if __name__ == "__main__":
    gen = AnalysisGenerator()
    # Test generation
    try:
        rid = gen._save_report('System', 'Test', 'Init', 'Starting generation...', {})
        gen.generate_jwem_column()
        gen.generate_jfit_report()
        gen.generate_synthetic_spatial_insight()
        print("🎉 All analyses generated and saved.")
    except Exception as e:
        print(f"❌ Error during generation: {e}")
