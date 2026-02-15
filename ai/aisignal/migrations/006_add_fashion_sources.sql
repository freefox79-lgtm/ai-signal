-- ==========================================
-- 006_add_fashion_sources.sql
-- Add Fashion classification and specialized crawlers.
-- ==========================================

BEGIN;

INSERT INTO data_sources (source_name, source_type, category, description, target_url, requires_stealth, requires_login, assigned_agent, service_contribution, priority) VALUES
-- 패션/트렌드 (Fashion & Hype)
('hypebeast', 'CRAWL', '패션/트렌드', '글로벌 스트릿 패션, 스니커즈, 컬처 뉴스', 'https://hypebeast.com', FALSE, FALSE, 'Jfit', '글로벌 하이프 아이템 및 브랜드 협업 시그널 포착', 2),
('kream', 'CRAWL', '패션/트렌드', '한정판 거래 플랫폼 시세 및 실시간 거래 트렌드', 'https://kream.co.kr', TRUE, FALSE, 'Jwem', '리셀 시장 가격 변동성 및 자산 가치 분석', 1),
('29cm', 'CRAWL', '패션/트렌드', '라이프스타일 및 감성 브랜드 큐레이션 트렌드', 'https://www.29cm.co.kr', FALSE, FALSE, 'Jfit', 'MZ세대 취향 기반 브랜드 라이징 시그널 식별', 2)
ON CONFLICT (source_name) DO NOTHING;

-- Initialize health records
INSERT INTO source_health (source_id, status)
SELECT id, 'HEALTHY' FROM data_sources WHERE source_name IN ('hypebeast', 'kream', '29cm')
ON CONFLICT (source_id) DO NOTHING;

COMMIT;
