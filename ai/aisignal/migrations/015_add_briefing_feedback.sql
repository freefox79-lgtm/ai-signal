-- ================================================
-- 💾 015_add_briefing_feedback.sql
-- Strategic Consensus Briefing & Feedback Loop
-- ================================================

-- 1. 브리핑 합의 결과 저장소
CREATE TABLE IF NOT EXISTS consensus_briefings (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    jwem_view TEXT, -- 쥄의 초기 의견
    jfit_view TEXT, -- 쥐핏의 초기 의견
    consensus_process TEXT, -- 합의 과정 기록
    source_data JSONB,
    model_used VARCHAR(50) DEFAULT 'gemma3:12b',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 사용자 피드백 저장소
CREATE TABLE IF NOT EXISTS briefing_feedback (
    id SERIAL PRIMARY KEY,
    briefing_id INTEGER REFERENCES consensus_briefings(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    is_reflected BOOLEAN DEFAULT FALSE, -- 다음 학습/브리핑에 반영 여부
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Supabase Live 데이터 미러링용 테이블 (이미 signals가 있으나 피드백 전용으로 확장 가능)
ALTER TABLE signals ADD COLUMN IF NOT EXISTS user_feedback_score FLOAT DEFAULT 0.0;
