-- ==========================================
-- 012_add_origin_tracking.sql
-- Missing table for Wiki GraphRAG Origin Tracking
-- ==========================================

BEGIN;

CREATE TABLE IF NOT EXISTS origin_tracking (
    id SERIAL PRIMARY KEY,
    source VARCHAR(255) NOT NULL,
    target VARCHAR(255) NOT NULL,
    relation_type VARCHAR(50), -- 'MENTIONED', 'SHARED', 'ATTACKED'
    confidence DECIMAL(3,2) DEFAULT 0.5,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB, -- { "platform": "Twitter", "url": "..." }
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for searching fast
CREATE INDEX IF NOT EXISTS idx_origin_source ON origin_tracking(source);
CREATE INDEX IF NOT EXISTS idx_origin_target ON origin_tracking(target);

COMMIT;
