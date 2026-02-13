-- ================================================
-- 💾 init_db_v4.sql: AI Signal 통합 마스터 스키마
-- Project Code: Antigravity-Alpha-2026
-- ================================================

-- 1. 필수 익스텐션 활성화 (벡터 검색용)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. 유저 및 경제 시스템 (MOD-O 연동)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    points INTEGER DEFAULT 1000, -- 초기 가급 포인트 [cite: 2026-02-13]
    tier VARCHAR(20) DEFAULT 'BRONZE',
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 지능형 시그널 저장소 (MOD-T, MOD-W 연동)
CREATE TABLE IF NOT EXISTS signals (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(255) UNIQUE NOT NULL, -- 트렌드 키워드 [cite: 2026-02-13]
    category VARCHAR(50),
    insight TEXT, -- 통합 인사이트 [cite: 2026-02-14]
    agent VARCHAR(50), -- 담당 에이전트 [cite: 2026-02-14]
    synced BOOLEAN DEFAULT FALSE,
    logic_analysis TEXT, -- 쥄(Jwem)의 논리 분석 [cite: 2026-02-07]
    meme_content JSONB, -- 쥐핏(Jfit)의 밈과 커뮤니티 반응 [cite: 2026-02-07]
    sentiment_score INTEGER, -- 감성 지수 (%) [cite: 2026-02-13]
    embedding VECTOR(1536), -- GraphRAG용 벡터 데이터 [cite: 2026-02-13]
    metadata JSONB, -- 출처, 하이퍼링크 등 [cite: 2026-02-13]
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. 시그널 오라클 (예측 배팅 시스템 MOD-O)
CREATE TABLE IF NOT EXISTS oracle_bets (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    target_keyword VARCHAR(255) REFERENCES signals(keyword),
    bet_type VARCHAR(10) CHECK (bet_type IN ('UP', 'DOWN')),
    amount INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, WIN, LOSS
    settled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. MCP 서버 자동 관리 모듈 (MOD-M)
CREATE TABLE IF NOT EXISTS mcp_status (
    id SERIAL PRIMARY KEY,
    server_name VARCHAR(100) UNIQUE,
    status VARCHAR(20), -- RUNNING, DOWN
    last_health_check TIMESTAMPTZ,
    config_data JSONB -- mcp-config.json 연결 정보 [cite: 2026-02-13]
);

-- 6. 사장님 제어 및 윤리 로그 (Royal Control)
CREATE TABLE IF NOT EXISTS compliance_logs (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(50), -- Jwem or Jfit
    action_type TEXT,
    trace_id UUID, -- AgentOps 추적 ID [cite: 2026-02-13]
    safety_check BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS royal_signals (
    id SERIAL PRIMARY KEY,
    message TEXT NOT NULL, -- 골든 포스트잇 메시지 [cite: 2026-02-13]
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- [추가] Phase 4 수익화 대응 (Action Buttons)
CREATE TABLE IF NOT EXISTS action_buttons (
    id SERIAL PRIMARY KEY,
    target_keyword VARCHAR(255) REFERENCES signals(keyword),
    platform VARCHAR(50), -- coupang, naver, linkprice
    affiliate_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. 쥄(Jwem) 포트폴리오 스택 [cite: 2026-02-14]
CREATE TABLE IF NOT EXISTS jwem_portfolio (
    id BIGSERIAL PRIMARY KEY,
    stock_code TEXT UNIQUE NOT NULL,
    stock_name TEXT,
    account_type TEXT, -- 'general', 'isa', 'pension', 'irp'
    quantity INTEGER DEFAULT 0,
    avg_price DECIMAL DEFAULT 0,
    current_price DECIMAL DEFAULT 0,
    profit_loss DECIMAL DEFAULT 0,
    profit_rate DECIMAL DEFAULT 0,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);
