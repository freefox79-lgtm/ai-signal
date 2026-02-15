-- ==========================================
-- 005_add_raw_feeds_table.sql
-- Store raw, unprocessed SNS data for traceability and future re-analysis.
-- ==========================================

CREATE TABLE IF NOT EXISTS raw_feeds (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,    -- 'x', 'instagram', 'community', etc.
    query VARCHAR(255),               -- Search query used
    raw_content JSONB NOT NULL,       -- Original JSON from crawler
    captured_at TIMESTAMP DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,  -- Whether it has been parsed into signals
    metadata JSONB                    -- Additional context (crawler version, speed, etc.)
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_raw_feeds_platform ON raw_feeds(platform);
CREATE INDEX IF NOT EXISTS idx_raw_feeds_captured ON raw_feeds(captured_at);

-- Add comment
COMMENT ON TABLE raw_feeds IS '로컬 맥미니에서 수집된 가공되지 않은 SNS 원본 데이터 저장용 테이블';
