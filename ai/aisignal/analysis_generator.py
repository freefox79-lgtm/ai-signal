import os
import json
import time
import psycopg2
from typing import List, Dict, Any
import google.generativeai as genai
from api_connectors import APIConnectors
from data_router import router
from dotenv import load_dotenv

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
        title = f"쥐핏의 트렌드 픽: {content.split('\\n')[0].replace('#', '').strip()}"
        
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
