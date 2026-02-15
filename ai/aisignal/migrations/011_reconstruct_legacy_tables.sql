-- 🏛️ Reconstruction of Legacy Tables (v011)
-- These tables are used by oracle.py and wiki.py but were missing from unified migrations.

BEGIN;

-- 1. Issues Table (Target for Oracle Voting)
CREATE TABLE IF NOT EXISTS issues (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    pros_count INTEGER DEFAULT 0,
    cons_count INTEGER DEFAULT 0,
    agent_pros_count INTEGER DEFAULT 0,
    agent_cons_count INTEGER DEFAULT 0,
    external_agent_pros_count INTEGER DEFAULT 0,
    external_agent_cons_count INTEGER DEFAULT 0,
    is_closed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Origin Tracking Table (Target for GraphRAG Trace)
CREATE TABLE IF NOT EXISTS origin_tracking (
    id SERIAL PRIMARY KEY,
    source VARCHAR(255) NOT NULL,
    target VARCHAR(255) NOT NULL,
    type VARCHAR(100),
    confidence INTEGER DEFAULT 50,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed some mock data for verification if empty
INSERT INTO issues (category, title, pros_count, cons_count, agent_pros_count, agent_cons_count)
SELECT '금융/경제', '삼전 4만전자 진입설: 저점인가? 추가 하락인가?', 120, 85, 10, 5
WHERE NOT EXISTS (SELECT 1 FROM issues LIMIT 1);

INSERT INTO origin_tracking (source, target, type, timestamp, metadata)
SELECT 'X_User_A', 'Influencer_B', 'retweet', NOW(), '{"credibility": 30}'
WHERE NOT EXISTS (SELECT 1 FROM origin_tracking LIMIT 1);

COMMIT;
