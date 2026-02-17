import os
from urllib.parse import urlparse, parse_qs, urlunparse
from dotenv import load_dotenv

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
        if 'issues' in self.query:
            return ("AI 기본법, 규제 강화 vs 혁신 지원?", "정치")
        return (1, "Mock Data")

    def fetchall(self):
        if 'market_indices' in self.query:
            return [
                ("S&P 500", 5000.5, 1.2),
                ("NASDAQ", 16000.2, 0.8),
                ("KOSPI", 2600.8, -0.3),
                ("Bitcoin", 50000.5, 3.5)
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
        if 'agent_issue_votes' in self.query:
            if 'internal' in self.query:
                return [
                    ("Jwem", "PROS", 95, "시장 지표가 강력한 상방 신호를 보냅니다."),
                    ("Jfit", "PROS", 80, "커뮤니티 버즈가 긍정적으로 형성되고 있습니다.")
                ]
            if 'external' in self.query:
                return [
                    ("Moltbot", "CONS", 70, "보안 취약점 노출 가능성이 포착되었습니다."),
                    ("Open-Cro", "PROS", 88, "글로벌 거시 경제 흐름과 일치합니다.")
                ]
            return [
                ("Jwem", "PROS", 95, "시장 지표가 강력한 상방 신호를 보냅니다."),
                ("Jfit", "PROS", 80, "커뮤니티 버즈가 긍정적으로 형성되고 있습니다."),
                ("Moltbot", "CONS", 70, "보안 취약점 노출 가능성이 포착되었습니다."),
                ("Open-Cro", "PROS", 88, "글로벌 거시 경제 흐름과 일치합니다.")
            ]
        
        if 'external_agent_registry' in self.query:
            # id, agent_id, agent_name, developer, model_info, reputation_score
            return [
                (101, "molt-001", "Moltbot", "Molt Security", "Molt-LLM-v2", 0.98),
                (102, "cro-99", "Open-Cro", "Open Research", "Cro-AGI-Alpha", 0.95),
                (103, "sonic-x", "SonicAgent", "SpeedAI", "Sonic-7B", 0.82)
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
def get_db_connection(db_url=None, routing='default'):
    """
    중앙 집중식 DB 연결 유틸리티
    - routing: 'default' (기본/클라우드), 'local' (맥미니), 'cloud' (수파베이스 전용)
    """
    # Load environment variables
    if os.path.exists(".env.local"):
        load_dotenv(".env.local")
    else:
        load_dotenv()


    # Mock Mode Injection for Intelligence Layer Expansion
    if os.getenv("DB_MOCK_MODE") == "true":
        class MockCursor:
            def __init__(self, query=""):
                self.query = query or ""
                self.description = [("column",)]
            def execute(self, q, vars=None): # Added vars=None to match psycopg2 signature
                self.query = q
                return self
            def fetchall(self):
                q = self.query.lower()
                if "market_macro_correlations" in q:
                    return [("GS10", "AI 반도체", 0.8542, "국채 금리 하락 시점에 인공지능 하드웨어 섹터의 민감도가 상승합니다.")]
                if "local_district_intelligence" in q:
                    return [("강남역/신논현", 92, "SNS 언급량 폭증 중. F&B 테마와 연계된 팝업스토어 진입 적기.")]
                if "synthetic_briefings" in q:
                    return [("하이브리드 퀀텀 브리핑", "거시 지표의 안정세와 하위 문화권의 하이프가 결합되어 새로운 에너지 네트워크 테마를 형성하고 있습니다.", {"jwem": 0.95, "jfit": 0.88}, True)]
                if "market_indices" in q:
                    return [("KOSPI", 2650, 1.2), ("S&P 500", 5000, 0.5), ("BTC", 95000, 2.1), ("ETH", 2800, -0.4)]
                if "signals" in q:
                    return [("AI Agent DAO", "거버넌스 참여율 200% 증가", "Jfit"), ("L3 정기 점검", "네트워크 업그레이드 완료", "Jwem")]
                if 'count(*)' in q:
                    return [(42,)]
                if 'users' in q:
                    return [(100, "User", "user@example.com")]
                if 'issues' in q:
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
                if 'agent_issue_votes' in q:
                    if 'internal' in q:
                        return [
                            ("Jwem", "PROS", 95, "시장 지표가 강력한 상방 신호를 보냅니다."),
                            ("Jfit", "PROS", 80, "커뮤니티 버즈가 긍정적으로 형성되고 있습니다.")
                        ]
                    if 'external' in q:
                        return [
                            ("Moltbot", "CONS", 70, "보안 취약점 노출 가능성이 포착되었습니다."),
                            ("Open-Cro", "PROS", 88, "글로벌 거시 경제 흐름과 일치합니다.")
                        ]
                    return [
                        ("Jwem", "PROS", 95, "시장 지표가 강력한 상방 신호를 보냅니다."),
                        ("Jfit", "PROS", 80, "커뮤니티 버즈가 긍정적으로 형성되고 있습니다."),
                        ("Moltbot", "CONS", 70, "보안 취약점 노출 가능성이 포착되었습니다."),
                        ("Open-Cro", "PROS", 88, "글로벌 거시 경제 흐름과 일치합니다.")
                    ]
                
                if 'external_agent_registry' in q:
                    # id, agent_id, agent_name, developer, model_info, reputation_score
                    return [
                        (101, "molt-001", "Moltbot", "Molt Security", "Molt-LLM-v2", 0.98),
                        (102, "cro-99", "Open-Cro", "Open Research", "Cro-AGI-Alpha", 0.95),
                        (103, "sonic-x", "SonicAgent", "SpeedAI", "Sonic-7B", 0.82)
                    ]

                if 'origin_tracking' in q:
                    # id, source, target, type, confidence, timestamp, metadata
                    return [
                        (1, "Telegram_User_X", "X_Influencer_A", "leaked_to", 0.3, "2024-05-20T09:00:00", {"credibility": 20, "platform": "Telegram"}),
                        (2, "X_Influencer_A", "X_Community_B", "retweeted", 0.7, "2024-05-20T09:15:00", {"credibility": 60, "platform": "X"}),
                        (3, "X_Community_B", "Reddit_Thread_C", "discussed_on", 0.6, "2024-05-20T09:45:00", {"credibility": 50, "platform": "Reddit"}),
                        (4, "Reddit_Thread_C", "CryptoNews_Web", "cited_by", 0.8, "2024-05-20T10:30:00", {"credibility": 85, "platform": "Web News"}),
                        (5, "CryptoNews_Web", "Mainstream_Media_D", "reported_by", 0.95, "2024-05-20T12:00:00", {"credibility": 98, "platform": "Mainstream"})
                    ]
                return []
            def fetchone(self):
                q = self.query.lower()
                if 'issues' in q:
                    return ("AI 기본법, 규제 강화 vs 혁신 지원?", "정치")
                if 'count(*)' in q:
                    return (42,)
                if 'users' in q:
                    return (100, "User", "user@example.com")
                res = self.fetchall()
                return res[0] if res else None
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def close(self): pass # Added close method

        class MockConn:
            def cursor(self): return MockCursor()
            def commit(self): pass
            def close(self): pass
            def __enter__(self): return self # Added __enter__
            def __exit__(self, exc_type, exc_val, exc_tb): pass # Added __exit__
        return MockConn()
    else:
        # 환경 변수 로드 (moved here from original global scope)
        pass


        # 실제 DB 작업 시 드라이버 임포트
        try:
            import psycopg2
        except ImportError:
            print("❌ [DB_UTILS] psycopg2 not found.")
            raise

        # 하이브리드 라우팅 로직
        if db_url:
            target_url = db_url
        else:
            target_url = os.getenv("DATABASE_URL")

    if not target_url:
        raise ValueError(f"DATABASE_URL for routing '{routing}' is not set.")

    # Supabase (Cloud) 자동 감지 및 최적화
    is_supabase = 'supabase.com' in target_url or 'supabase.co' in target_url
    
    if is_supabase:
        # Pooler(6543) 또는 Direct(5432) 처리
        parsed = urlparse(target_url)
        query = parse_qs(parsed.query)
        if 'sslmode' not in query:
            query['sslmode'] = ['require']
        
        # User prefix for Pooler (postgres.project-ref)
        project_ref = os.getenv("SUPABASE_PROJECT_ID", "")
        if project_ref and parsed.username and project_ref not in parsed.username:
            new_netloc = f"{parsed.username}.{project_ref}:{parsed.password}@{parsed.hostname}:{parsed.port}"
            parsed = parsed._replace(netloc=new_netloc)
            
        new_query = "&".join([f"{k}={v[0]}" for k, v in query.items()])
        target_url = urlunparse(parsed._replace(query=new_query))

    try:
        # 연결 시도
        if is_supabase:
            return psycopg2.connect(target_url, sslmode='require')
        return psycopg2.connect(target_url)
    except Exception as e:
        print(f"[DB_UTILS] Connection Error ({routing}): {e}")
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
