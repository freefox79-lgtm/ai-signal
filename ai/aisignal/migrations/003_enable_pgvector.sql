-- Migration 003: Enable pgvector and GraphRAG
-- Created: 2026-02-14
-- Purpose: Vector search and knowledge graph for GraphRAG

-- ========================================
-- pgvector Extension
-- ========================================
CREATE EXTENSION IF NOT EXISTS vector;

-- ========================================
-- Knowledge Graph Tables
-- ========================================

-- 엔티티 테이블
CREATE TABLE IF NOT EXISTS knowledge_graph (
    id SERIAL PRIMARY KEY,
    entity TEXT NOT NULL UNIQUE,
    entity_type VARCHAR(50),  -- 'person', 'company', 'technology', 'concept', etc.
    embedding vector(768),    -- nomic-embed-text: 768 dimensions
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 엔티티 관계 테이블
CREATE TABLE IF NOT EXISTS entity_relationships (
    id SERIAL PRIMARY KEY,
    source_entity_id INTEGER REFERENCES knowledge_graph(id) ON DELETE CASCADE,
    target_entity_id INTEGER REFERENCES knowledge_graph(id) ON DELETE CASCADE,
    relationship_type VARCHAR(100),  -- 'related_to', 'part_of', 'causes', etc.
    confidence FLOAT DEFAULT 1.0,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(source_entity_id, target_entity_id, relationship_type)
);

-- 임베딩 테이블 (일반 텍스트)
CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    content_type VARCHAR(50),  -- 'signal', 'trend', 'article', 'comment'
    embedding vector(768),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- Indexes for Performance
-- ========================================

-- HNSW 인덱스 (빠른 벡터 검색)
CREATE INDEX IF NOT EXISTS idx_kg_embedding_hnsw 
ON knowledge_graph USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_embeddings_hnsw 
ON embeddings USING hnsw (embedding vector_cosine_ops);

-- 일반 인덱스
CREATE INDEX IF NOT EXISTS idx_kg_entity_type ON knowledge_graph(entity_type);
CREATE INDEX IF NOT EXISTS idx_kg_created_at ON knowledge_graph(created_at);
CREATE INDEX IF NOT EXISTS idx_er_source ON entity_relationships(source_entity_id);
CREATE INDEX IF NOT EXISTS idx_er_target ON entity_relationships(target_entity_id);
CREATE INDEX IF NOT EXISTS idx_er_type ON entity_relationships(relationship_type);
CREATE INDEX IF NOT EXISTS idx_embeddings_type ON embeddings(content_type);

-- ========================================
-- Helper Functions
-- ========================================

-- 유사도 검색 함수
CREATE OR REPLACE FUNCTION search_similar_content(
    query_embedding vector(768),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id int,
    content text,
    content_type varchar,
    similarity float,
    metadata jsonb
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        embeddings.id,
        embeddings.content,
        embeddings.content_type,
        1 - (embeddings.embedding <=> query_embedding) as similarity,
        embeddings.metadata
    FROM embeddings
    WHERE 1 - (embeddings.embedding <=> query_embedding) > match_threshold
    ORDER BY embeddings.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- 엔티티 유사도 검색 함수
CREATE OR REPLACE FUNCTION search_similar_entities(
    query_embedding vector(768),
    entity_type_filter varchar DEFAULT NULL,
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id int,
    entity text,
    entity_type varchar,
    similarity float,
    metadata jsonb
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        kg.id,
        kg.entity,
        kg.entity_type,
        1 - (kg.embedding <=> query_embedding) as similarity,
        kg.metadata
    FROM knowledge_graph kg
    WHERE 
        (entity_type_filter IS NULL OR kg.entity_type = entity_type_filter)
        AND 1 - (kg.embedding <=> query_embedding) > match_threshold
    ORDER BY kg.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- 엔티티 관계 그래프 조회 (재귀)
CREATE OR REPLACE FUNCTION get_entity_graph(
    entity_name text,
    max_depth int DEFAULT 2
)
RETURNS TABLE (
    entity text,
    entity_type varchar,
    depth int,
    relationship_path text[]
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE entity_tree AS (
        -- 시작 엔티티
        SELECT 
            kg.entity,
            kg.entity_type,
            0 as depth,
            ARRAY[kg.entity] as relationship_path
        FROM knowledge_graph kg
        WHERE kg.entity = entity_name
        
        UNION ALL
        
        -- 관련 엔티티 (재귀)
        SELECT 
            kg.entity,
            kg.entity_type,
            et.depth + 1,
            et.relationship_path || kg.entity
        FROM knowledge_graph kg
        JOIN entity_relationships er ON (
            er.source_entity_id = (
                SELECT id FROM knowledge_graph WHERE entity = et.entity
            )
        )
        JOIN entity_tree et ON kg.id = er.target_entity_id
        WHERE et.depth < max_depth
          AND NOT kg.entity = ANY(et.relationship_path)  -- 순환 방지
    )
    SELECT DISTINCT * FROM entity_tree;
END;
$$;

-- ========================================
-- Triggers
-- ========================================

-- updated_at 자동 업데이트
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_kg_updated_at BEFORE UPDATE ON knowledge_graph
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- Comments
-- ========================================

COMMENT ON TABLE knowledge_graph IS 'GraphRAG 지식 그래프 엔티티';
COMMENT ON TABLE entity_relationships IS '엔티티 간 관계';
COMMENT ON TABLE embeddings IS '텍스트 임베딩 (벡터 검색용)';
COMMENT ON FUNCTION search_similar_content IS '유사 콘텐츠 검색 (pgvector)';
COMMENT ON FUNCTION search_similar_entities IS '유사 엔티티 검색 (pgvector)';
COMMENT ON FUNCTION get_entity_graph IS '엔티티 관계 그래프 조회 (재귀)';
