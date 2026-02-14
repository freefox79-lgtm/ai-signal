#!/usr/bin/env python3
"""
AI Signal System Health Check
전체 시스템 연동 상태 점검
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_postgresql():
    """PostgreSQL 연결 확인"""
    print("\n=== 1. PostgreSQL 연결 확인 ===")
    try:
        import psycopg2
        from dotenv import load_dotenv
        load_dotenv(".env.local")
        
        db_url = os.getenv("DATABASE_URL")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # 버전 확인
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        print(f"✅ PostgreSQL 연결 성공")
        print(f"   버전: {version.split(',')[0]}")
        
        # pgvector 확인
        cur.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'")
        result = cur.fetchone()
        if result:
            print(f"✅ pgvector 확장: {result[1]}")
        else:
            print("⚠️  pgvector 확장 없음")
        
        # 테이블 확인
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cur.fetchall()]
        print(f"✅ 테이블 수: {len(tables)}")
        print(f"   주요 테이블: {', '.join(tables[:5])}")
        
        # knowledge_graph 데이터 확인
        cur.execute("SELECT COUNT(*) FROM knowledge_graph")
        kg_count = cur.fetchone()[0]
        print(f"✅ Knowledge Graph 엔티티: {kg_count:,}개")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL 연결 실패: {e}")
        return False


def check_redis():
    """Redis 연결 확인"""
    print("\n=== 2. Redis 연결 확인 ===")
    try:
        import redis
        from dotenv import load_dotenv
        load_dotenv(".env.local")
        
        redis_pwd = os.getenv("REDIS_PASSWORD", "aisignal2026_secure")
        r = redis.Redis(
            host='localhost',
            port=6379,
            password=redis_pwd,
            decode_responses=True
        )
        
        # 연결 확인
        r.ping()
        print("✅ Redis 연결 성공")
        
        # 정보 확인
        info = r.info()
        print(f"   버전: {info['redis_version']}")
        print(f"   메모리 사용: {info['used_memory_human']}")
        print(f"   키 개수: {r.dbsize():,}")
        
        # 캐시 통계 확인
        cache_stats = r.hgetall("cache:stats")
        if cache_stats:
            print("✅ 캐시 통계:")
            for key, value in list(cache_stats.items())[:5]:
                print(f"   {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis 연결 실패: {e}")
        return False


def check_ollama():
    """Ollama 연결 확인"""
    print("\n=== 3. Ollama LLM 연결 확인 ===")
    try:
        from agents.llm.ollama_client import get_ollama_client
        
        ollama = get_ollama_client()
        
        # 사용 가능 여부
        if ollama.is_available():
            print("✅ Ollama 서비스 활성화")
        else:
            print("❌ Ollama 서비스 비활성화")
            return False
        
        # 모델 목록
        models = ollama.list_models()
        print(f"✅ 설치된 모델: {len(models)}개")
        for model in models:
            print(f"   - {model}")
        
        # 임베딩 테스트
        start = time.time()
        emb = ollama.embed("테스트")
        emb_time = time.time() - start
        print(f"✅ 임베딩 생성: {emb_time*1000:.2f}ms (dim={len(emb)})")
        
        # LLM 생성 테스트
        start = time.time()
        resp = ollama.generate("안녕하세요", temperature=0.2, max_tokens=50)
        gen_time = time.time() - start
        print(f"✅ LLM 생성: {gen_time*1000:.2f}ms")
        print(f"   응답: {resp[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Ollama 연결 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_graphrag():
    """GraphRAG 연결 확인"""
    print("\n=== 4. GraphRAG 시스템 확인 ===")
    try:
        from agents.graphrag.knowledge_graph import KnowledgeGraph
        
        kg = KnowledgeGraph()
        
        # 통계 확인
        stats = kg.get_graph_stats()
        print(f"✅ GraphRAG 초기화 성공")
        print(f"   노드: {stats['node_count']:,}개")
        print(f"   엣지: {stats['edge_count']:,}개")
        print(f"   타입: {stats['type_count']}개")
        
        # 검색 테스트
        if stats['node_count'] > 0:
            results = kg.find_related_entities("반도체", top_k=3, threshold=0.3)
            print(f"✅ 검색 테스트: {len(results)}개 결과")
            for r in results[:3]:
                print(f"   - {r['entity']} ({r['similarity']:.2%})")
        
        return True
        
    except Exception as e:
        print(f"❌ GraphRAG 연결 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_n8n():
    """n8n 연결 확인"""
    print("\n=== 5. n8n 워크플로우 확인 ===")
    try:
        import requests
        
        # n8n API 확인
        response = requests.get("http://localhost:5678/healthz", timeout=5)
        if response.status_code == 200:
            print("✅ n8n 서비스 활성화")
        else:
            print(f"⚠️  n8n 응답 코드: {response.status_code}")
        
        # Docker 컨테이너 확인
        import subprocess
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=n8n", "--format", "{{.Status}}"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            print(f"✅ n8n 컨테이너: {result.stdout.strip()}")
        
        return True
        
    except Exception as e:
        print(f"⚠️  n8n 확인 실패: {e}")
        return False


def check_streamlit():
    """Streamlit 앱 확인"""
    print("\n=== 6. Streamlit 앱 확인 ===")
    try:
        import requests
        
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✅ Streamlit 앱 실행 중")
            print(f"   URL: http://localhost:8501")
        else:
            print(f"⚠️  Streamlit 응답 코드: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Streamlit 확인 실패: {e}")
        return False


def check_cron_jobs():
    """Cron 작업 확인"""
    print("\n=== 7. Cron 작업 확인 ===")
    try:
        import subprocess
        
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            cron_lines = [line for line in result.stdout.split('\n') if line and not line.startswith('#')]
            print(f"✅ Cron 작업: {len(cron_lines)}개")
            for line in cron_lines:
                print(f"   {line}")
        else:
            print("⚠️  Cron 작업 없음")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Cron 확인 실패: {e}")
        return False


def main():
    print("=" * 60)
    print("AI SIGNAL SYSTEM HEALTH CHECK")
    print("=" * 60)
    
    results = {
        "PostgreSQL": check_postgresql(),
        "Redis": check_redis(),
        "Ollama": check_ollama(),
        "GraphRAG": check_graphrag(),
        "n8n": check_n8n(),
        "Streamlit": check_streamlit(),
        "Cron Jobs": check_cron_jobs()
    }
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for service, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {service}")
    
    print(f"\n총 {passed}/{total} 서비스 정상")
    
    if passed == total:
        print("\n🎉 모든 시스템 정상 작동!")
        print("✅ 배포 준비 완료")
        return 0
    else:
        print(f"\n⚠️  {total - passed}개 서비스 점검 필요")
        return 1


if __name__ == "__main__":
    sys.exit(main())
