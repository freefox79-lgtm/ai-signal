import os
from urllib.parse import urlparse, parse_qs, urlunparse

class MockCursor:
    """UI 개발을 위한 가짜 커서"""
    def __init__(self):
        self.description = [("column",)]
        self.rowcount = 1
        self.query = ""

    def execute(self, query, vars=None):
        self.query = query.lower()
        return None

    def fetchone(self):
        if 'count(*)' in self.query:
            return (42,)
        if 'users' in self.query:
            return (100, "User", "user@example.com")
        return (1, "Mock Data", "Insight")

    def fetchall(self):
        if 'jwem_portfolio' in self.query:
            return [
                ("AAPL", 230.5, 15.2),
                ("TSLA", 180.2, -5.4),
                ("NVDA", 125.8, 45.1),
                ("MSFT", 410.5, 8.2),
                ("GOOGL", 160.2, 12.4)
            ]
        if 'issues' in self.query:
             # id, category, title, pros_count, cons_count, agent_pros_count, agent_cons_count, is_closed
             return [
                 (1, "정치", "AI 기본법, 규제 강화 vs 혁신 지원?", 4520, 3120, 8000, 1500, False),
                 (2, "경제", "금투세 폐지 확정, 개인 투자자 영향은?", 6890, 1240, 9200, 800, False),
                 (3, "사회", "의대 증원 2천명, 의료 대란 해법인가?", 2340, 5670, 3100, 6900, False),
                 (4, "문화", "K-컨텐츠 예산 삭감 논란", 1200, 890, 1500, 500, True),
                 (5, "엔터", "버추얼 아이돌의 음악방송 출연 허용?", 3400, 2100, 4800, 1200, False),
                 (6, "경제", "비트코인 ETF, 제도권 안착 성공인가?", 5600, 4800, 7000, 3000, True),
                 (7, "사회", "저출산 대책, 현금 지원 실효성 논란", 1500, 6700, 2000, 8000, True)
             ]
        if 'signals' in self.query:
            # Home.py: keyword, insight, agent (3 columns)
            # Intelligence.py (Jfit): keyword, insight (2 columns)
            if 'keyword, insight, agent' in self.query:
                return [
                    ("엔비디아 H200 수요", "클라우드 제공업체들이 자본 지출을 늘리고 있습니다. 반도체 공급망 노드 과열 중.", "Jwem"),
                    ("ETF 유입 급증", "95k 달러 구간에서 기관 매수 벽이 감지되었습니다. 상방 변동성 확대를 예상합니다.", "Jwem"),
                    ("사이버-메타 패션", "가상 패션 플랫폼 거래량 300% 폭증! 새로운 온체인 트렌드 식별 완료.", "Jfit"),
                    ("양자 보안 레이어", "L2 네트워크의 양자 내성 업그레이드가 시작되었습니다. 보안 자산으로 매수세 유입.", "Jfit"),
                    ("에너지 그리드 최적화", "AI 연산용 송전망 효율화 시그널 포착. 바이오 에너지 섹터와 연동 시너지 발생.", "Jwem"),
                    ("스마트 팩토리 2.0", "제조업의 AI 도입 가속화. 로보틱스 및 자동화 관련주 주목.", "Jfit"),
                    ("DeFi 4.0 프로토콜", "기관 전용 유동성 풀 출시 임박. 관련 거버넌스 토큰 가격 변동성 확대.", "Stealth"),
                    ("우주 항공 물류", "민간 우주 발사 비용 절감에 따른 위성 인터넷 및 물류 네트워크 확장 기대.", "Jwem"),
                    ("블록체인 게이밍", "P2E 모델의 진화. AAA급 게임 출시로 인한 유저 유입 가속화.", "Jfit"),
                    ("인공지능 신약 개발", "단백질 구조 예측 AI 기술의 상용화 성공. 바이오테크 섹터 리레이팅 가능성.", "Stealth")
                ]
            else:
                return [
                    ("AI 칩셋", "차세대 H200 생산 가속화 중."),
                    ("메타버스", "가상 패션 플랫폼 거래량 폭증.")
                ]

        if 'origin_tracking' in self.query:
             # id, source, target, type, confidence, timestamp, metadata
             return [
                 (1, "Telegram_User_X", "X_Influencer_A", "leaked_to", 0.3, "2024-05-20T09:00:00", {"credibility": 20, "platform": "Telegram"}),
                 (2, "X_Influencer_A", "X_Community_B", "retweeted", 0.7, "2024-05-20T09:15:00", {"credibility": 60, "platform": "X"}),
                 (3, "X_Community_B", "Reddit_Thread_C", "discussed_on", 0.6, "2024-05-20T09:45:00", {"credibility": 50, "platform": "Reddit"}),
                 (4, "Reddit_Thread_C", "CryptoNews_Web", "cited_by", 0.8, "2024-05-20T10:30:00", {"credibility": 85, "platform": "Web News"}),
                 (5, "CryptoNews_Web", "Mainstream_Media_D", "reported_by", 0.95, "2024-05-20T12:00:00", {"credibility": 98, "platform": "Mainstream"})
             ]

        return []

    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): pass
    def close(self): pass

class MockConnection:
    """UI 개발을 위한 가짜 연결"""
    def cursor(self): return MockCursor()
    def commit(self): pass
    def close(self): pass
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): pass

def get_db_connection(db_url=None):
    """
    고도화된 데이터베이스 연결 유틸리티
    - DB_MOCK_MODE=true 일 경우 가짜 데이터 반환 (UI 개발용)
    - Supabase URL 자동 감지 및 SSL 설정
    - 포트 6543(Pooler) 사용 시 사용자명 접두사 자동 처리
    """
    # 0. Mock Mode 체크 (UI 개발용)
    if os.getenv("DB_MOCK_MODE", "").lower() == "true":
        print("⚠️ [DB_UTILS] Running in MOCK MODE (Returning fake data)")
        return MockConnection()

    # 환경 변수 로드 (실제 작업 시에만)
    try:
        from dotenv import load_dotenv
        load_dotenv(".env.local")
    except ImportError:
        print("ℹ️ [DB_UTILS] python-dotenv not found. Continuing with current environment.")

    # 실제 DB 작업 시에만 드라이버 임포트
    try:
        import psycopg2
    except ImportError:
        print("❌ [DB_UTILS] psycopg2 not found. Please install it or set DB_MOCK_MODE=true.")
        raise

    url = db_url or os.getenv("DATABASE_URL")
    if not url:
        # DB_MOCK_MODE가 아니고 DATABASE_URL도 없으면 에러지만, 
        # UI 개발을 위해 Mock 모드를 추천하는 메시지 출력
        print("⚠️ [DB_UTILS] DATABASE_URL is missing. Please set DB_MOCK_MODE=true for UI testing.")
        raise ValueError("DATABASE_URL environment variable is not set.")

    # Supabase 포트 6543(Pooler) 환경 체크
    if 'supabase.com:6543' in url or 'supabase.co:6543' in url:
        parsed = urlparse(url)
        
        # 1. SSL 설정 강제 (Pooler 필수)
        query = parse_qs(parsed.query)
        if 'sslmode' not in query:
            query['sslmode'] = ['require']
            
        # 2. 사용자명 접두사 확인 (postgres.project-ref)
        supabase_url = os.getenv("SUPABASE_URL", "")
        project_ref = ""
        if supabase_url:
            project_ref = urlparse(supabase_url).netloc.split('.')[0]
            
        username = parsed.username
        if project_ref and username and project_ref not in username:
            new_netloc = f"{username}.{project_ref}:{parsed.password}@{parsed.hostname}:{parsed.port}"
            parsed = parsed._replace(netloc=new_netloc)
            
        new_query = "&".join([f"{k}={v[0]}" for k, v in query.items()])
        parsed = parsed._replace(query=new_query)
        url = urlunparse(parsed)

    try:
        # 연결 시도
        if 'supabase' in url and 'sslmode=require' not in url:
            conn = psycopg2.connect(url, sslmode='require')
        else:
            conn = psycopg2.connect(url)
        return conn
    except Exception as e:
        print(f"[DB_UTILS] Connection Error: {e}")
        print("💡 TIP: Set DB_MOCK_MODE=true in .env to develop UI without a database.")
        raise

if __name__ == "__main__":
    # 테스트 코드
    os.environ["DB_MOCK_MODE"] = "true"
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM signals")
            print(f"✅ Mock connectivity test: {cur.fetchall()[0]}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
