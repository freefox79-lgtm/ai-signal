-- ==========================================
-- 009_add_stealth_intelligence_layer.sql
-- Specialized storage for Stealth Agent's Asymmetric Intelligence.
-- ==========================================

BEGIN;

-- 1. Asymmetric Intelligence Reports (Stealth Agent's Core Output)
CREATE TABLE IF NOT EXISTS stealth_asymmetric_intel (
    id SERIAL PRIMARY KEY,
    intel_type VARCHAR(50) NOT NULL, -- LEAK, VULN, PRIVATE_BUZZ, ASYMMETRIC_MARKET, INSIDER_TIPS
    severity_level VARCHAR(20) DEFAULT 'MEDIUM', -- LOW, MEDIUM, HIGH, CRITICAL, ROYAL_ONLY
    title VARCHAR(255),
    content TEXT,
    source_origin VARCHAR(100), -- Dark Web, Private Forum, encrypted_sns
    evidence_metadata JSONB, -- screenshot_path, raw_hash, verification_link
    
    -- Verification status (usually reviewed by Jwem or Human)
    verification_status VARCHAR(20) DEFAULT 'UNVERIFIED', -- UNVERIFIED, CROSS_CHECKED, DISMISSED
    is_confidential BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ -- Intel often has a shelf-life
);

-- Indexes for rapid lookup of critical threats
CREATE INDEX IF NOT EXISTS idx_stealth_intel_type ON stealth_asymmetric_intel(intel_type);
CREATE INDEX IF NOT EXISTS idx_stealth_severity ON stealth_asymmetric_intel(severity_level);
CREATE INDEX IF NOT EXISTS idx_stealth_confidential ON stealth_asymmetric_intel(is_confidential);

-- 2. Link Stealth Intel to Global Signals for Cross-Agent Synthesis
ALTER TABLE signals ADD COLUMN IF NOT EXISTS stealth_intel_id INTEGER REFERENCES stealth_asymmetric_intel(id);

COMMIT;
