-- ================================================
-- Migration: Add Data Source Management Tables
-- Created: 2026-02-14
-- Description: Adds comprehensive data source tracking and health monitoring
-- ================================================

BEGIN;

-- 1. Create data_sources table (Master Registry)
CREATE TABLE IF NOT EXISTS data_sources (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(100) UNIQUE NOT NULL,
    source_type VARCHAR(20) NOT NULL CHECK (source_type IN ('API', 'CRAWL')),
    category VARCHAR(50),
    description TEXT,
    
    -- API-specific fields
    api_endpoint TEXT,
    api_key_env VARCHAR(100),
    rate_limit_per_minute INTEGER,
    
    -- Crawling-specific fields
    target_url TEXT,
    requires_stealth BOOLEAN DEFAULT FALSE,
    requires_login BOOLEAN DEFAULT FALSE,
    
    -- Agent assignment
    assigned_agent VARCHAR(50),
    service_contribution TEXT,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Create source_health table (Health Monitoring)
CREATE TABLE IF NOT EXISTS source_health (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES data_sources(id) ON DELETE CASCADE,
    
    -- Health metrics
    status VARCHAR(20) DEFAULT 'HEALTHY' CHECK (status IN ('HEALTHY', 'DEGRADED', 'DOWN')),
    last_success_at TIMESTAMPTZ,
    last_failure_at TIMESTAMPTZ,
    consecutive_failures INTEGER DEFAULT 0,
    
    -- Performance metrics
    avg_response_time_ms INTEGER,
    success_rate_24h DECIMAL(5,2),
    total_requests_24h INTEGER DEFAULT 0,
    
    -- Rate limiting
    requests_this_minute INTEGER DEFAULT 0,
    rate_limit_hit_count INTEGER DEFAULT 0,
    
    -- Error tracking
    last_error_message TEXT,
    last_error_code VARCHAR(50),
    
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_source_health_source_id ON source_health(source_id);

-- 3. Create crawl_sessions table (Stealth Session Pool)
CREATE TABLE IF NOT EXISTS crawl_sessions (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES data_sources(id) ON DELETE CASCADE,
    
    -- Session identification
    session_token VARCHAR(255) UNIQUE NOT NULL,
    browser_fingerprint JSONB,
    
    -- Authentication
    is_authenticated BOOLEAN DEFAULT FALSE,
    login_cookies JSONB,
    auth_expires_at TIMESTAMPTZ,
    
    -- Session state
    status VARCHAR(20) DEFAULT 'IDLE' CHECK (status IN ('IDLE', 'ACTIVE', 'EXPIRED', 'BANNED')),
    last_used_at TIMESTAMPTZ,
    use_count INTEGER DEFAULT 0,
    max_uses INTEGER DEFAULT 100,
    
    -- Anti-detection
    user_agent TEXT,
    viewport_width INTEGER,
    viewport_height INTEGER,
    timezone VARCHAR(50),
    language VARCHAR(10),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '24 hours'
);

CREATE INDEX IF NOT EXISTS idx_crawl_sessions_source_status ON crawl_sessions(source_id, status);
CREATE INDEX IF NOT EXISTS idx_crawl_sessions_expires ON crawl_sessions(expires_at);

-- 4. Create data_cache_stats table (Cache Performance Tracking)
CREATE TABLE IF NOT EXISTS data_cache_stats (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES data_sources(id) ON DELETE CASCADE,
    
    -- Cache metrics
    cache_hits INTEGER DEFAULT 0,
    cache_misses INTEGER DEFAULT 0,
    cache_hit_rate DECIMAL(5,2),
    
    -- Cost savings
    api_calls_saved INTEGER DEFAULT 0,
    estimated_cost_saved DECIMAL(10,2),
    
    -- Time window
    stats_date DATE DEFAULT CURRENT_DATE,
    
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(source_id, stats_date)
);

CREATE INDEX IF NOT EXISTS idx_cache_stats_date ON data_cache_stats(stats_date DESC);

-- 5. Insert initial data sources (정형 데이터 - APIs)
INSERT INTO data_sources (source_name, source_type, category, description, api_endpoint, api_key_env, rate_limit_per_minute, assigned_agent, service_contribution, priority) VALUES
-- 금융/경제 APIs
('alpha_vantage', 'API', '금융/경제', '글로벌 주식, 외환(FX), 암호화폐 시세', 'https://www.alphavantage.co/query', 'ALPHA_VANTAGE_API_KEY', 5, 'Jwem', '자산 시장 변동성 및 트렌드 상관관계 분석', 1),
('coingecko', 'API', '금융/경제', '10,000개 이상의 코인 메타데이터 및 시황', 'https://api.coingecko.com/api/v3', NULL, 50, 'Jwem', '암호화폐 섹터의 펌핑 및 덤핑 시그널 포착', 2),
('fred', 'API', '금융/경제', '미국 연준 금리, GDP, 소비자 물가 지수', 'https://api.stlouisfed.org/fred', 'FRED_API_KEY', 120, 'Jwem', '거시 경제 흐름에 따른 투자 제언(MOD-C) 생성', 1),

-- 공공/국내 APIs
('data_go_kr', 'API', '공공/국내', '전국 상권 정보, 교통 통계, 미세먼지', 'https://www.data.go.kr', 'DATA_GO_KR_KEY', 100, 'Jfit', '국내 실생활 밀착형 트렌드 및 유동 인구 분석', 3),
('seoul_open_data', 'API', '공공/국내', '서울시 실시간 지하철/버스 혼잡도, 따릉이', 'https://data.seoul.go.kr', 'SEOUL_DATA_KEY', 100, 'Jfit', '서울 지역별 실시간 핫플레이스 예측', 3),
('kosis', 'API', '공공/국내', '인구 통계, 산업생산지수, 고용 지표', 'https://kosis.kr/openapi', 'KOSIS_KEY', 50, 'Jwem', '장기적인 사회 구조 변화 및 산업 트렌드 파악', 4),

-- 기술/소셜 APIs
('github', 'API', '기술/소셜', '오픈소스 Star 증가율, 신규 Repo 키워드', 'https://api.github.com', 'GITHUB_TOKEN', 60, 'Jfit', '최신 IT 기술 스택 및 개발자 트렌드 선점', 2),
('youtube_data', 'API', '기술/소셜', '키워드별 조회수, 좋아요, 채널 성장률', 'https://www.googleapis.com/youtube/v3', 'YOUTUBE_API_KEY', 100, 'Jfit', '영상 콘텐츠의 바이럴 지수 정량화 분석', 2),
('stack_exchange', 'API', '기술/소셜', '기술적 질문 빈도 및 태그 트렌드', 'https://api.stackexchange.com/2.3', NULL, 300, 'Jfit', '개발자들의 실시간 고민 및 신기술 수요 파악', 3),

-- 생활/문화 APIs
('openweathermap', 'API', '생활/문화', '전 세계 도시별 실시간 기상 및 예보', 'https://api.openweathermap.org/data/2.5', 'OPENWEATHER_KEY', 60, 'Jfit', '날씨 변동에 따른 소비 패턴(의류, 식품) 분석', 4),
('tmdb', 'API', '생활/문화', '최신 영화/TV 프로그램 평점 및 메타데이터', 'https://api.themoviedb.org/3', 'TMDB_KEY', 40, 'Jfit', '엔터테인먼트 시장의 흥행 트렌드 분석', 4),

-- 기존 Naver API
('naver_search', 'API', '뉴스/검색', '네이버 통합 검색 API', 'https://openapi.naver.com/v1/search', 'NAVER_CLIENT_ID', 100, 'Jfit', '실시간 뉴스 및 블로그 트렌드 파악', 2)
ON CONFLICT (source_name) DO NOTHING;

-- 6. Insert crawling sources (비정형 데이터)
INSERT INTO data_sources (source_name, source_type, category, description, target_url, requires_stealth, requires_login, assigned_agent, service_contribution, priority) VALUES
-- 커뮤니티
('dcinside', 'CRAWL', '커뮤니티', '갤러리별 실시간 개념글 및 신조어', 'https://www.dcinside.com', FALSE, FALSE, 'Jfit', '최신 밈 및 킹받는 유머 키워드 발굴', 1),
('fmkorea', 'CRAWL', '커뮤니티', '포텐 게시판 중심의 실시간 화제성 이슈', 'https://www.fmkorea.com', FALSE, FALSE, 'Jwem', '커뮤니티 여론의 논리적 흐름 및 찬반 분석', 2),
('ruliweb', 'CRAWL', '커뮤니티', '서브컬처, 게임, 특정 취미 분야 심층 여론', 'https://www.ruliweb.com', FALSE, FALSE, 'Jfit', '매니아층의 소비 트렌드 및 바이럴 요소 포착', 3),
('arcalive', 'CRAWL', '커뮤니티', '특정 주제별 채널 심층 분석', 'https://arca.live', FALSE, FALSE, 'Jfit', '니치 커뮤니티의 트렌드 선점', 3),

-- SNS/블로그
('naver_blog', 'CRAWL', 'SNS/블로그', '사용자 실사용 후기 및 감성적 리뷰 데이터', 'https://blog.naver.com', FALSE, FALSE, 'Jwem', '실제 제품/서비스의 만족도 및 문제점 도출', 2),
('youtube_comments', 'CRAWL', 'SNS/블로그', '영상 시청자들의 실시간 반응 및 감정 분석', 'https://www.youtube.com', FALSE, FALSE, 'Jfit', '대중의 감정적 동요 및 폭발적 반응 지점 파악', 2),
('news_comments', 'CRAWL', 'SNS/블로그', '정치, 사회 이슈에 대한 대중의 직접적인 비판', 'https://news.naver.com', FALSE, FALSE, 'Jwem', '사회적 합의점 및 여론의 양극화 지표 산출', 3),

-- 직장/전문
('blind', 'CRAWL', '직장/전문', '직장인들의 연봉, 이직, 기업 내부 분위기', 'https://www.teamblind.com', FALSE, TRUE, 'Jwem', '산업별 실질적인 고용 시장 트렌드 분석', 2),
('everytime', 'CRAWL', '직장/전문', '대학생들의 캠퍼스 문화 및 Z세대 관심사', 'https://everytime.kr', FALSE, TRUE, 'Jfit', '젊은 층의 새로운 라이프스타일 시그널 포착', 2),

-- SNS (Stealth Required)
('twitter', 'CRAWL', 'SNS', '실시간 트렌드 및 바이럴 이슈', 'https://twitter.com', TRUE, TRUE, 'Jfit', '매크로 이슈(트럼프 SNS), 챌린지 트렌드 포착', 1),
('instagram', 'CRAWL', 'SNS', '시각적 트렌드 및 인플루언서 동향', 'https://www.instagram.com', TRUE, TRUE, 'Jfit', '시각적 밈 및 패션 트렌드 선점', 1),
('tiktok', 'CRAWL', 'SNS', '숏폼 바이럴 콘텐츠 및 챌린지', 'https://www.tiktok.com', TRUE, TRUE, 'Jfit', 'Z세대 바이럴 트렌드 실시간 포착', 1)
ON CONFLICT (source_name) DO NOTHING;

-- 7. Initialize health records for all sources
INSERT INTO source_health (source_id, status)
SELECT id, 'HEALTHY' FROM data_sources
ON CONFLICT (source_id) DO NOTHING;

COMMIT;

-- Verification queries
SELECT 'Data Sources Created:' AS info, COUNT(*) AS count FROM data_sources;
SELECT 'Health Records Created:' AS info, COUNT(*) AS count FROM source_health;
SELECT 'Tables Created:' AS info, COUNT(*) AS count FROM information_schema.tables 
WHERE table_name IN ('data_sources', 'source_health', 'crawl_sessions', 'data_cache_stats');
