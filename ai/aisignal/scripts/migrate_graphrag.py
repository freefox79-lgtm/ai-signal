#!/usr/bin/env python3
"""
GraphRAG 마이그레이션 스크립트
knowledge_relationships 테이블 생성
"""

import os
import psycopg2
from dotenv import load_dotenv

# 중앙 집중식 DB 유틸리티 임포트
from db_utils import get_db_connection

load_dotenv(".env.local")

def run_migration():
    """GraphRAG 마이그레이션 실행"""
    
    db_url = os.getenv("DATABASE_URL")
    try:
        conn = get_db_connection(db_url)
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        return
    cur = conn.cursor()
    
    print("=== GraphRAG 마이그레이션 시작 ===\n")
    
    # 1. knowledge_relationships 테이블 생성
    print("1. knowledge_relationships 테이블 생성...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_relationships (
            id SERIAL PRIMARY KEY,
            source_entity TEXT NOT NULL,
            target_entity TEXT NOT NULL,
            relationship_type VARCHAR(100),
            confidence FLOAT DEFAULT 1.0,
            metadata JSONB,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(source_entity, target_entity, relationship_type)
        )
    """)
    print("✅ knowledge_relationships 테이블 생성 완료")
    
    # 2. 인덱스 생성
    print("\n2. 인덱스 생성...")
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_kr_source ON knowledge_relationships(source_entity)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_kr_target ON knowledge_relationships(target_entity)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_kr_type ON knowledge_relationships(relationship_type)
    """)
    print("✅ 인덱스 생성 완료")
    
    conn.commit()
    
    # 3. 확인
    print("\n3. 테이블 확인...")
    cur.execute("SELECT COUNT(*) FROM knowledge_graph")
    kg_count = cur.fetchone()[0]
    print(f"✅ knowledge_graph: {kg_count}개")
    
    cur.execute("SELECT COUNT(*) FROM knowledge_relationships")
    kr_count = cur.fetchone()[0]
    print(f"✅ knowledge_relationships: {kr_count}개")
    
    conn.close()
    
    print("\n=== 마이그레이션 완료 ===")

if __name__ == "__main__":
    run_migration()
