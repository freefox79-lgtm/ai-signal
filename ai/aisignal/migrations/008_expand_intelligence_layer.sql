-- 🧠 AI Signal Intelligence Layer Expansion (v008)
-- Targets: Local DB (Mac Mini) for heavy analysis & Cloud DB (Supabase) for shared results

-- 1. Macro-Micro Correlation Table (Local Repository)
CREATE TABLE IF NOT EXISTS market_macro_correlations (
    id SERIAL PRIMARY KEY,
    fred_series_id VARCHAR(50), -- GS10, CPIAUCSL
    signal_keyword VARCHAR(100),
    correlation_coefficient DECIMAL(5,4), -- AI calculated
    causality_score DECIMAL(5,4),
    insight_text TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Local District & SNS Hype Integration (Local Storage)
CREATE TABLE IF NOT EXISTS local_district_intelligence (
    id SERIAL PRIMARY KEY,
    district_code VARCHAR(50), -- from sdsc2
    district_name VARCHAR(100),
    jfit_hype_score INTEGER, -- 1-100 based on SNS growth
    active_trends TEXT[], -- matching keyword tags
    retail_density_level VARCHAR(20), -- from public data
    ai_recommendation TEXT,
    last_scan_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Synthetic Multi-Source Briefings (Cloud/Default for sharing)
CREATE TABLE IF NOT EXISTS synthetic_briefings (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200),
    summary TEXT,
    data_sources JSONB, -- {fred: true, youtube: true, public: true, graphrag: true}
    agent_consensus JSONB, -- {jwem: 0.8, jfit: 0.9}
    is_hot BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Knowledge Graph Context Links (Local)
CREATE TABLE IF NOT EXISTS knowledge_context_links (
    id SERIAL PRIMARY KEY,
    graph_node_id INTEGER,
    external_signal_id INTEGER, -- links to signals table in cloud
    link_strength DECIMAL(3,2),
    context_note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
