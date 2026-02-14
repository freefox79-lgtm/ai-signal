-- Migration: Remove Personal Portfolio Tables
-- Created: 2026-02-14
-- Purpose: Remove personal portfolio tracking, align with AI Signal public service

-- Remove personal portfolio table
DROP TABLE IF EXISTS jwem_portfolio;

-- Optional: Add market analysis cache for performance
CREATE TABLE IF NOT EXISTS market_analysis_cache (
    id SERIAL PRIMARY KEY,
    analysis_type VARCHAR(50) NOT NULL,  -- 'indices', 'sectors', 'economic', 'risk'
    data JSONB NOT NULL,                 -- Analysis results
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    CONSTRAINT valid_analysis_type CHECK (analysis_type IN ('indices', 'sectors', 'economic', 'risk'))
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_market_analysis_type ON market_analysis_cache(analysis_type);
CREATE INDEX IF NOT EXISTS idx_market_analysis_expires ON market_analysis_cache(expires_at);

-- Comments
COMMENT ON TABLE market_analysis_cache IS 'Cache for market analysis results to reduce API calls';
COMMENT ON COLUMN market_analysis_cache.analysis_type IS 'Type of analysis: indices, sectors, economic, risk';
COMMENT ON COLUMN market_analysis_cache.data IS 'JSON data containing analysis results';
COMMENT ON COLUMN market_analysis_cache.expires_at IS 'Expiration timestamp for cache invalidation';
