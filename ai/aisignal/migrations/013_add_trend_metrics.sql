-- 1. Historical Metrics for Z-Score Calculation (24h retention policy recommended)
CREATE TABLE IF NOT EXISTS trend_metrics_history (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(255) NOT NULL,
    source VARCHAR(50) NOT NULL, -- 'Naver', 'YouTube', 'Google'
    metric_type VARCHAR(50) NOT NULL, -- 'search_volume', 'view_count', 'posting_velocity'
    metric_value FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_trend_history_keyword_time ON trend_metrics_history(keyword, timestamp);

-- 2. Active Real-time Trends for UI Display (Replaces simple list)
CREATE TABLE IF NOT EXISTS active_realtime_trends (
    id SERIAL PRIMARY KEY,
    rank INT NOT NULL,
    keyword VARCHAR(255) NOT NULL UNIQUE,
    avg_score FLOAT NOT NULL, -- Combined Z-Score or weighted average
    related_insight TEXT, -- "Why is this trending?" (from LLM)
    status VARCHAR(20) DEFAULT 'NEW', -- 'NEW', 'RISING', 'PEAK', 'FADING'
    source VARCHAR(50) DEFAULT 'System',
    link TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_active_trends_rank ON active_realtime_trends(rank);

-- 3. Function to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_active_trends_modtime ON active_realtime_trends;

CREATE TRIGGER update_active_trends_modtime
    BEFORE UPDATE ON active_realtime_trends
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
