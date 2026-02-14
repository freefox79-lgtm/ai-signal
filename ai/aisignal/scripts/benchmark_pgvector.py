#!/usr/bin/env python3
"""
pgvector Performance Benchmark
HNSW 인덱스 및 배치 삽입 성능 테스트
"""

import time
import sys
import os
from typing import List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.graphrag.knowledge_graph import KnowledgeGraph


def benchmark_search(kg: KnowledgeGraph, queries: List[str], top_k: int = 10):
    """검색 성능 벤치마크"""
    
    print(f"\n=== Search Benchmark (top_k={top_k}) ===")
    
    times = []
    for query in queries:
        start = time.time()
        results = kg.find_related_entities(query, top_k=top_k, threshold=0.3)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  {query}: {elapsed*1000:.2f}ms ({len(results)} results)")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"\n평균: {avg_time*1000:.2f}ms")
        print(f"총합: {sum(times)*1000:.2f}ms")
        return avg_time
    return 0


def benchmark_insert(kg: KnowledgeGraph, count: int = 100):
    """삽입 성능 벤치마크"""
    
    print(f"\n=== Insert Benchmark ({count} entities) ===")
    
    # Generate test entities
    entities = [
        {
            'entity': f"benchmark_test_{i}",
            'entity_type': 'benchmark',
            'metadata': {'test': True, 'index': i}
        }
        for i in range(count)
    ]
    
    # Test 1: Single insert (only 10 for comparison)
    print("\n1. Single Insert (10 entities):")
    single_entities = entities[:10]
    start = time.time()
    for entity in single_entities:
        kg.add_entity(entity['entity'], entity['entity_type'], entity['metadata'])
    single_time = time.time() - start
    print(f"  시간: {single_time*1000:.2f}ms")
    print(f"  엔티티당: {single_time/10*1000:.2f}ms")
    
    # Test 2: Batch insert
    print(f"\n2. Batch Insert ({count} entities):")
    start = time.time()
    kg.add_entities_batch(entities)
    batch_time = time.time() - start
    print(f"  시간: {batch_time*1000:.2f}ms")
    print(f"  엔티티당: {batch_time/count*1000:.2f}ms")
    
    # Speedup calculation
    if batch_time > 0:
        speedup = (single_time / 10) / (batch_time / count)
        print(f"\n배치 속도 향상: {speedup:.2f}x")
        return speedup
    return 0


def benchmark_hnsw_params(kg: KnowledgeGraph):
    """HNSW 파라미터 확인"""
    
    print("\n=== HNSW Index Parameters ===")
    
    try:
        with kg.conn.cursor() as cur:
            # Check index configuration
            cur.execute("""
                SELECT 
                    indexname,
                    indexdef
                FROM pg_indexes
                WHERE tablename = 'knowledge_graph'
                AND indexname LIKE '%hnsw%'
            """)
            
            for row in cur.fetchall():
                print(f"\n인덱스: {row[0]}")
                print(f"정의: {row[1]}")
            
            # Check table stats
            cur.execute("""
                SELECT 
                    COUNT(*) as total_entities,
                    COUNT(DISTINCT entity_type) as entity_types
                FROM knowledge_graph
            """)
            
            stats = cur.fetchone()
            print(f"\n통계:")
            print(f"  총 엔티티: {stats[0]:,}")
            print(f"  엔티티 타입: {stats[1]}")
    
    except Exception as e:
        print(f"⚠️  파라미터 확인 실패: {e}")


def main():
    print("=== pgvector Performance Benchmark ===\n")
    
    try:
        kg = KnowledgeGraph()
        
        # Check HNSW parameters
        benchmark_hnsw_params(kg)
        
        # Search benchmark
        queries = ["반도체", "AI", "전기차", "배터리", "로봇"]
        search_time = benchmark_search(kg, queries)
        
        # Insert benchmark
        speedup = benchmark_insert(kg, count=50)
        
        print("\n=== Summary ===")
        if search_time > 0:
            print(f"평균 검색 시간: {search_time*1000:.2f}ms")
        if speedup > 0:
            print(f"배치 삽입 속도 향상: {speedup:.2f}x")
        
        print("\n✅ 벤치마크 완료")
    
    except Exception as e:
        print(f"\n❌ 벤치마크 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
