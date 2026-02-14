-- Supabase 테이블 생성 스크립트
-- 로컬 PostgreSQL과 동일한 구조

-- ================================================
-- 1. signals 테이블
-- ================================================
CREATE TABLE IF NOT EXISTS signals (
    id SERIAL PRIMARY KEY,
    signal_type VARCHAR(50),
    source VARCHAR(100),
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_signals_created_at ON signals(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_signals_source ON signals(source);
CREATE INDEX IF NOT EXISTS idx_signals_type ON signals(signal_type);

-- ================================================
-- 2. data_sources 테이블
-- ================================================
CREATE TABLE IF NOT EXISTS data_sources (
    id SERIAL PRIMARY KEY,
    source_type VARCHAR(50),
    source_name VARCHAR(100),
    data JSONB,
    collected_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_data_sources_collected_at ON data_sources(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_data_sources_type ON data_sources(source_type);
CREATE INDEX IF NOT EXISTS idx_data_sources_name ON data_sources(source_name);

-- ================================================
-- 3. 기존 테이블 확인
-- ================================================
-- knowledge_graph, knowledge_relationships, jwem_portfolio는
-- 이미 생성되어 있어야 함

-- ================================================
-- 4. 데이터 정리 정책 (선택사항)
-- ================================================
-- 오래된 데이터 자동 삭제 (90일 이상)
-- 비용 절감 및 성능 최적화

-- signals 정리 함수
CREATE OR REPLACE FUNCTION cleanup_old_signals()
RETURNS void AS $$
BEGIN
    DELETE FROM signals
    WHERE created_at < NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;

-- data_sources 정리 함수
CREATE OR REPLACE FUNCTION cleanup_old_data_sources()
RETURNS void AS $$
BEGIN
    DELETE FROM data_sources
    WHERE collected_at < NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;

-- ================================================
-- 5. 통계 뷰 (선택사항)
-- ================================================
-- 데이터 현황 파악용

CREATE OR REPLACE VIEW data_sync_stats AS
SELECT 
    'signals' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN created_at > NOW() - INTERVAL '1 hour' THEN 1 END) as last_hour,
    COUNT(CASE WHEN created_at > NOW() - INTERVAL '24 hours' THEN 1 END) as last_24h,
    MAX(created_at) as latest_record
FROM signals
UNION ALL
SELECT 
    'data_sources' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN collected_at > NOW() - INTERVAL '1 hour' THEN 1 END) as last_hour,
    COUNT(CASE WHEN collected_at > NOW() - INTERVAL '24 hours' THEN 1 END) as last_24h,
    MAX(collected_at) as latest_record
FROM data_sources;

-- ================================================
-- 완료
-- ================================================
-- 테이블 생성 완료
-- 다음 단계: sync_to_supabase.py 실행
