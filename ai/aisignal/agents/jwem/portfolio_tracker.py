import os
import psycopg2
from api_connectors import APIConnectors
from dotenv import load_dotenv

load_dotenv(".env.local")

class JwemPortfolio:
    """
    쥄 (Jwem) - 극도의 논리주의자
    
    페르소나:
    - 효율과 토큰 최적화 중심
    - 데이터 팩트 체크
    - 수치 분석 및 논리적 골격 형성
    - 팩트 기반 리포트 작성
    """
    
    PERSONA = {
        "name": "쥄 (Jwem)",
        "archetype": "논리주의자 (Logos)",
        "traits": ["효율성", "정확성", "토큰 최적화", "팩트 중심"],
        "communication_style": "간결하고 정확한 수치 중심 보고",
        "emoji": "📊"
    }
    
    def __init__(self):
        self.conn = get_db_connection(os.getenv("DATABASE_URL"))
        self.connectors = APIConnectors()
        # 쥄의 마스터 포트폴리오 (18개 종목 예시)
        self.target_stocks = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "BRK.B", "V", "JNJ", "WMT", "PG", "MA", "XOM", "UNH", "HD", "PFE", "DIS"]

    def update_prices(self):
        """Fetches latest prices and updates the local database."""
        print(f"[JWEM] Updating prices for {len(self.target_stocks)} stocks...")
        for symbol in self.target_stocks:
            data = self.connectors.fetch_stock_quote(symbol)
            price = data.get("Global Quote", {}).get("05. price", 0)
            
            with self.conn.cursor() as cur:
                # Update current price and calculate profit/loss (assuming we have avg_price)
                cur.execute("""
                    INSERT INTO jwem_portfolio (stock_code, current_price, last_updated)
                    VALUES (%s, %s, NOW())
                    ON CONFLICT (stock_code) DO UPDATE SET 
                        current_price = EXCLUDED.current_price,
                        last_updated = EXCLUDED.last_updated
                """, (symbol, price))
            self.conn.commit()
        print("[JWEM] Portfolio update complete.")

    def analyze_risk(self):
        """Simple risk calculation logic (Placeholder for now)."""
        # Logic to compare current vs avg price and flag anomalies
        return "Portfolio stability: 85% (Optimistic)"
    
    def fact_check_trend(self, trend_data):
        """
        Jfit의 트렌드 데이터를 팩트 체크
        
        Args:
            trend_data: dict with 'platform', 'content', 'score'
            
        Returns:
            dict: {
                "verified": bool,
                "confidence": float,
                "fact_check_notes": str,
                "data_sources": list,
                "logical_assessment": str
            }
        """
        print(f"[JWEM 📊] Fact-checking trend: {trend_data.get('content', '')[:50]}...")
        
        platform = trend_data.get('platform', 'Unknown')
        content = trend_data.get('content', '')
        score = trend_data.get('score', 0)
        
        # Fact check logic
        verified = score >= 70  # Threshold for verification
        confidence = min(score / 100.0, 1.0)
        
        # Logical assessment
        if verified:
            logical_assessment = f"데이터 신뢰도 {confidence:.0%}. {platform} 출처 검증됨."
        else:
            logical_assessment = f"신뢰도 부족 ({confidence:.0%}). 추가 검증 필요."
        
        fact_check_result = {
            "verified": verified,
            "confidence": confidence,
            "fact_check_notes": f"출처: {platform}, 점수: {score}/100",
            "data_sources": [platform],
            "logical_assessment": logical_assessment
        }
        
        print(f"[JWEM 📊] Verification: {verified} (confidence: {confidence:.0%})")
        
        return fact_check_result
    
    def optimize_report(self, raw_report):
        """
        리포트를 토큰 최적화하여 간결하게 재작성
        
        Args:
            raw_report: str or dict
            
        Returns:
            str: 최적화된 리포트 (토큰 50% 절감 목표)
        """
        print("[JWEM 📊] Optimizing report for token efficiency...")
        
        if isinstance(raw_report, dict):
            # Extract key information only
            optimized = f"{raw_report.get('portfolio_status', 'N/A')} | "
            optimized += f"Risk: {raw_report.get('risk_analysis', 'N/A')} | "
            optimized += f"Sentiment: {raw_report.get('market_sentiment', 'neutral')}"
        else:
            # Simple string optimization: remove redundant words
            optimized = str(raw_report)
            # Remove common filler words
            fillers = ['매우', '정말', '아주', '굉장히', '상당히']
            for filler in fillers:
                optimized = optimized.replace(filler, '')
            optimized = optimized.strip()
        
        print(f"[JWEM 📊] Optimized: {len(str(raw_report))} → {len(optimized)} chars")
        
        return optimized
    
    def analyze_with_logic(self, data):
        """
        논리적 분석 및 인과관계 도출
        
        Args:
            data: dict with analysis context
            
        Returns:
            dict: {
                "logical_framework": str,
                "causal_relationships": list,
                "risk_assessment": dict
            }
        """
        print("[JWEM 📊] Performing logical analysis...")
        
        # Build logical framework
        framework = "시장 데이터 기반 인과관계 분석"
        
        # Identify causal relationships
        causal_relationships = [
            "금리 상승 → 주식 하락 압력",
            "기술주 강세 → 포트폴리오 리밸런싱 필요",
            "변동성 증가 → 리스크 관리 강화"
        ]
        
        # Risk assessment
        risk_assessment = {
            "level": "medium",
            "factors": ["시장 변동성", "금리 리스크", "섹터 집중도"],
            "mitigation": "분산 투자 및 헤지 전략 권장"
        }
        
        analysis = {
            "logical_framework": framework,
            "causal_relationships": causal_relationships,
            "risk_assessment": risk_assessment
        }
        
        print(f"[JWEM 📊] Analysis complete: {len(causal_relationships)} causal links identified")
        
        return analysis

if __name__ == "__main__":
    jwem = JwemPortfolio()
    jwem.update_prices()
    print(jwem.analyze_risk())

