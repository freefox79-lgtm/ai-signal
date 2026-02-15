-- ==========================================
-- 007_add_finance_news_sources.sql
-- Add Yahoo Finance API and Naver Finance Crawling.
-- ==========================================

BEGIN;

INSERT INTO data_sources (source_name, source_type, category, description, target_url, api_endpoint, api_key_env, requires_stealth, requires_login, assigned_agent, service_contribution, priority) VALUES
-- 뉴스/금융 (Financial News)
('yahoo_finance', 'API', '뉴스/금융', '글로벌 실시간 금융 뉴스 및 시장 요약', NULL, 'https://query1.finance.yahoo.com/v8/finance/chart/', 'YAHOO_FINANCE_KEY', FALSE, FALSE, 'Jwem', '글로벌 경제 지표와 뉴스 센티먼트 결합 분석', 1),
('naver_finance', 'CRAWL', '뉴스/금융', '국내 증시 시황, 상장사 공시, 투자자 토론방', 'https://finance.naver.com', NULL, NULL, FALSE, FALSE, 'Jwem', '국내 투자자 여론 및 실시간 증시 변동성 연동', 1)
ON CONFLICT (source_name) DO NOTHING;

-- Initialize health records
INSERT INTO source_health (source_id, status)
SELECT id, 'HEALTHY' FROM data_sources WHERE source_name IN ('yahoo_finance', 'naver_finance')
ON CONFLICT (source_id) DO NOTHING;

COMMIT;
