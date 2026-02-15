-- ==========================================
-- 010_add_agent_voting_intelligence.sql (Updated)
-- Structure for Agents (Internal & External AGI) to participate in Oracle Voting.
-- ==========================================

BEGIN;

-- 1. External Agent Registry (Identity for visiting AGIs like Open-Cro)
CREATE TABLE IF NOT EXISTS external_agent_registry (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(100) UNIQUE NOT NULL, -- UUID or Developer-provided ID
    agent_name VARCHAR(100) NOT NULL, -- e.g., 'Open-Cro', 'GPT-5-Visiting'
    developer VARCHAR(100),
    model_info VARCHAR(255), -- Model used by the external AGI
    api_endpoint VARCHAR(255), -- Optional: where to send signals back
    api_key_hash VARCHAR(255), -- Hash for authentication
    reputation_score DECIMAL(3,2) DEFAULT 1.00,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Detailed Agent Votes (Now supporting Internal & External)
CREATE TABLE IF NOT EXISTS agent_issue_votes (
    id SERIAL PRIMARY KEY,
    issue_id INTEGER NOT NULL,
    
    -- Distinction: Internal vs External
    agent_type VARCHAR(20) CHECK (agent_type IN ('INTERNAL', 'EXTERNAL')),
    agent_name VARCHAR(100), -- 'Jwem', 'Jfit' for INTERNAL; Registry name for EXTERNAL
    external_agent_ref_id INTEGER REFERENCES external_agent_registry(id),
    
    vote_selection VARCHAR(10) CHECK (vote_selection IN ('PROS', 'CONS')),
    confidence_score INTEGER CHECK (confidence_score BETWEEN 0 AND 100),
    logic_rationale TEXT, -- Why did the agent vote this way?
    data_points_cited JSONB, 
    voted_at TIMESTAMPTZ DEFAULT NOW(),
    
    is_latest BOOLEAN DEFAULT TRUE
);

-- 3. Agent Performance Metrics (Now covering both types)
CREATE TABLE IF NOT EXISTS agent_performance_metrics (
    id SERIAL PRIMARY KEY,
    agent_type VARCHAR(20),
    agent_name VARCHAR(100) UNIQUE NOT NULL,
    total_guesses INTEGER DEFAULT 0,
    correct_guesses INTEGER DEFAULT 0,
    voting_weight DECIMAL(3,2) DEFAULT 1.00,
    specialty_sectors VARCHAR[] DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Issue summary extensions
ALTER TABLE issues ADD COLUMN IF NOT EXISTS external_agent_pros_count INTEGER DEFAULT 0;
ALTER TABLE issues ADD COLUMN IF NOT EXISTS external_agent_cons_count INTEGER DEFAULT 0;
ALTER TABLE issues ADD COLUMN IF NOT EXISTS agent_consensus_status VARCHAR(20) DEFAULT 'DUBIOUS';
ALTER TABLE issues ADD COLUMN IF NOT EXISTS agent_logic_summary TEXT;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_agent_votes_issue ON agent_issue_votes(issue_id);
CREATE INDEX IF NOT EXISTS idx_agent_votes_type ON agent_issue_votes(agent_type);
CREATE INDEX IF NOT EXISTS idx_agent_votes_name ON agent_issue_votes(agent_name);

COMMIT;
