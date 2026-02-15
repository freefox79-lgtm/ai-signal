#!/usr/bin/env python3
"""
Supabase 데이터 동기화 스크립트
로컬 PostgreSQL → Supabase PostgreSQL 동기화
"""

import os
import psycopg2.extras
from dotenv import load_dotenv
import argparse
from datetime import datetime
import sys

# 중앙 집중식 DB 유틸리티 임포트
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_utils import get_db_connection

# 환경 변수 로드
load_dotenv('.env.local')

# 동기화 간격 설정 (분 단위)
SYNC_INTERVALS = {
    'signals': 15,  # 시그널 데이터 (15분)
    'data_sources': 60,  # 데이터 소스 (1시간)
}

class SupabaseSync:
    def __init__(self):
        # 로컬 DB 연결
        self.local_conn = get_db_connection(os.getenv('DATABASE_URL'))
        # Supabase DB 연결
        self.supabase_conn = get_db_connection(os.getenv('SUPABASE_DATABASE_URL'))
        
        print("✅ 데이터베이스 연결 성공\n")
    
    def sync_signals(self, minutes=15):
        """signals 테이블 동기화"""
        try:
            local_cur = self.local_conn.cursor()
            supabase_cur = self.supabase_conn.cursor()
            
            # 로컬 DB에서 최근 데이터 가져오기
            query = """
                SELECT id, keyword, category, logic_analysis, meme_content, 
                       sentiment_score, metadata, updated_at, insight, agent, synced
                FROM signals
                WHERE updated_at > NOW() - INTERVAL '%s minutes'
                ORDER BY updated_at DESC
            """
            local_cur.execute(query, (minutes,))
            rows = local_cur.fetchall()
            
            if not rows:
                print(f"  ℹ️  최근 {minutes}분 동안 새 시그널 없음")
                return 0
            
            # Supabase에 UPSERT
            upsert_query = """
                INSERT INTO signals 
                (id, keyword, category, logic_analysis, meme_content, 
                 sentiment_score, metadata, updated_at, insight, agent, synced)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (keyword) 
                DO UPDATE SET
                    category = EXCLUDED.category,
                    logic_analysis = EXCLUDED.logic_analysis,
                    meme_content = EXCLUDED.meme_content,
                    sentiment_score = EXCLUDED.sentiment_score,
                    metadata = EXCLUDED.metadata,
                    updated_at = EXCLUDED.updated_at,
                    insight = EXCLUDED.insight,
                    agent = EXCLUDED.agent,
                    synced = EXCLUDED.synced
            """
            
            for row in rows:
                supabase_cur.execute(upsert_query, row)
            
            self.supabase_conn.commit()
            print(f"  ✅ {len(rows)}개 시그널 동기화 완료")
            
            local_cur.close()
            supabase_cur.close()
            return len(rows)
            
        except Exception as e:
            print(f"  ❌ 시그널 동기화 실패: {e}")
            self.supabase_conn.rollback()
            return 0
    
    def sync_data_sources(self, minutes=60):
        """data_sources 테이블 동기화"""
        try:
            local_cur = self.local_conn.cursor()
            supabase_cur = self.supabase_conn.cursor()
            
            # 로컬 DB에서 최근 데이터 가져오기
            query = """
                SELECT id, source_name, source_type, category, description,
                       api_endpoint, api_key_env, rate_limit_per_minute,
                       target_url, requires_stealth, requires_login,
                       assigned_agent, service_contribution, is_active,
                       priority, created_at, updated_at
                FROM data_sources
                WHERE updated_at > NOW() - INTERVAL '%s minutes'
                ORDER BY updated_at DESC
            """
            local_cur.execute(query, (minutes,))
            rows = local_cur.fetchall()
            
            if not rows:
                print(f"  ℹ️  최근 {minutes}분 동안 새 데이터 소스 없음")
                return 0
            
            # Supabase에 UPSERT (간소화된 구조)
            upsert_query = """
                INSERT INTO data_sources 
                (source_type, source_name, url, raw_data, collected_at, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """
            
            for row in rows:
                # 로컬 구조를 Supabase 구조로 변환
                source_type = row[2]  # source_type
                source_name = row[1]  # source_name
                url = row[8] or row[5]  # target_url or api_endpoint
                raw_data = {
                    'category': row[3],
                    'description': row[4],
                    'api_endpoint': row[5],
                    'rate_limit': row[7],
                    'requires_stealth': row[9],
                    'requires_login': row[10],
                    'assigned_agent': row[11],
                    'priority': row[14]
                }
                collected_at = row[16]  # updated_at
                status = 'active' if row[13] else 'inactive'  # is_active
                
                supabase_cur.execute(upsert_query, (
                    source_type, source_name, url, 
                    psycopg2.extras.Json(raw_data), 
                    collected_at, status
                ))
            
            self.supabase_conn.commit()
            print(f"  ✅ {len(rows)}개 데이터 소스 동기화 완료")
            
            local_cur.close()
            supabase_cur.close()
            return len(rows)
            
        except Exception as e:
            print(f"  ❌ 데이터 소스 동기화 실패: {e}")
            self.supabase_conn.rollback()
            return 0
    
    def sync_all(self, mode='auto'):
        """전체 동기화"""
        total_synced = 0
        
        print(f"=== 데이터 동기화 시작 ({mode} mode) ===")
        print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        if mode in ['auto', 'signals', 'all']:
            print("[1] 시그널 동기화 (15분 간격)")
            minutes = 1440 if mode == 'all' else SYNC_INTERVALS['signals']
            total_synced += self.sync_signals(minutes)
            print()
        
        if mode in ['auto', 'data_sources', 'all']:
            print("[2] 데이터 소스 동기화 (1시간 간격)")
            minutes = 1440 if mode == 'all' else SYNC_INTERVALS['data_sources']
            total_synced += self.sync_data_sources(minutes)
            print()
        
        print(f"=== 동기화 완료: 총 {total_synced}개 레코드 ===\n")
        return total_synced
    
    def close(self):
        """연결 종료"""
        self.local_conn.close()
        self.supabase_conn.close()

def main():
    parser = argparse.ArgumentParser(description='Supabase 데이터 동기화')
    parser.add_argument('--mode', 
                       choices=['auto', 'signals', 'data_sources', 'all'],
                       default='auto',
                       help='동기화 모드 (auto: 자동 간격, all: 전체 데이터)')
    
    args = parser.parse_args()
    
    try:
        syncer = SupabaseSync()
        syncer.sync_all(mode=args.mode)
        syncer.close()
    except Exception as e:
        print(f"❌ 동기화 실패: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == '__main__':
    main()
