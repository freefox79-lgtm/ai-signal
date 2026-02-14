"""
GraphRAG 지식 그래프

맥미니 로컬 자원 활용:
- Ollama로 임베딩 생성 (로컬)
- PostgreSQL pgvector로 벡터 검색
- 나무위키식 하이퍼링크 생성
"""

import os
import psycopg2
from typing import List, Dict, Optional, Tuple
from agents.llm.ollama_client import get_ollama_client

class KnowledgeGraph:
    """지식 그래프 관리"""
    
    def __init__(self, db_url: str = None):
        self.db_url = db_url or os.getenv("DATABASE_URL")
        self.conn = psycopg2.connect(self.db_url)
        self.ollama = get_ollama_client()
    
    def add_entity(
        self, 
        entity: str, 
        entity_type: str = "concept",
        metadata: dict = None
    ) -> int:
        """엔티티 추가 (로컬 임베딩)"""
        
        # Ollama로 임베딩 생성 (로컬)
        embedding = self.ollama.embed(entity)
        
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO knowledge_graph (entity, entity_type, embedding, metadata)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (entity) DO UPDATE SET
                    entity_type = EXCLUDED.entity_type,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata,
                    updated_at = NOW()
                RETURNING id
            """, (entity, entity_type, embedding, metadata))
            
            entity_id = cur.fetchone()[0]
        
        self.conn.commit()
        print(f"[GraphRAG] 엔티티 추가: {entity} (ID: {entity_id})")
        return entity_id
    
    def add_entities_batch(
        self,
        entities: List[Dict],
        batch_size: int = 50
    ) -> List[int]:
        """배치 엔티티 추가 (성능 최적화)"""
        
        entity_ids = []
        total = len(entities)
        
        # Process in batches
        for i in range(0, total, batch_size):
            batch = entities[i:i + batch_size]
            
            # Generate embeddings for batch
            embeddings = []
            for entity_data in batch:
                emb = self.ollama.embed(entity_data['entity'])
                embeddings.append(emb)
            
            # Prepare values for batch insert
            values = []
            for j, entity_data in enumerate(batch):
                values.append((
                    entity_data['entity'],
                    entity_data.get('entity_type', 'concept'),
                    embeddings[j],
                    entity_data.get('metadata')
                ))
            
            # Batch insert
            with self.conn.cursor() as cur:
                # Use execute_values for better performance
                from psycopg2.extras import execute_values
                
                execute_values(
                    cur,
                    """
                    INSERT INTO knowledge_graph (entity, entity_type, embedding, metadata)
                    VALUES %s
                    ON CONFLICT (entity) DO UPDATE SET
                        entity_type = EXCLUDED.entity_type,
                        embedding = EXCLUDED.embedding,
                        metadata = EXCLUDED.metadata,
                        updated_at = NOW()
                    RETURNING id
                    """,
                    values
                )
                
                # Fetch returned IDs
                batch_ids = [row[0] for row in cur.fetchall()]
                entity_ids.extend(batch_ids)
            
            self.conn.commit()
            print(f"[GraphRAG] 배치 삽입: {len(batch)}/{total} 엔티티")
        
        print(f"[GraphRAG] 총 {total}개 엔티티 삽입 완료")
        return entity_ids
    
    def find_related_entities(
        self, 
        query: str, 
        entity_type: str = None,
        top_k: int = 5,
        threshold: float = 0.7
    ) -> List[Dict]:
        """유사 엔티티 검색 (pgvector)"""
        
        # 쿼리 임베딩 생성
        query_embedding = self.ollama.embed(query)
        
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM search_similar_entities(
                    %s::vector,
                    %s,
                    %s,
                    %s
                )
            """, (query_embedding, entity_type, threshold, top_k))
            
            results = []
            for row in cur.fetchall():
                results.append({
                    'id': row[0],
                    'entity': row[1],
                    'entity_type': row[2],
                    'similarity': float(row[3]),
                    'metadata': row[4]
                })
        
        return results
    
    def add_relationship(
        self,
        source_entity: str,
        target_entity: str,
        relationship_type: str,
        confidence: float = 1.0,
        metadata: dict = None
    ):
        """엔티티 관계 추가"""
        
        with self.conn.cursor() as cur:
            # 엔티티 ID 조회
            cur.execute("""
                SELECT id FROM knowledge_graph WHERE entity = %s
            """, (source_entity,))
            source_row = cur.fetchone()
            
            cur.execute("""
                SELECT id FROM knowledge_graph WHERE entity = %s
            """, (target_entity,))
            target_row = cur.fetchone()
            
            if not source_row or not target_row:
                print(f"[GraphRAG] 엔티티를 찾을 수 없음: {source_entity} or {target_entity}")
                return
            
            source_id = source_row[0]
            target_id = target_row[0]
            
            # 관계 추가
            cur.execute("""
                INSERT INTO entity_relationships 
                (source_entity_id, target_entity_id, relationship_type, confidence, metadata)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (source_entity_id, target_entity_id, relationship_type) 
                DO UPDATE SET
                    confidence = EXCLUDED.confidence,
                    metadata = EXCLUDED.metadata
            """, (source_id, target_id, relationship_type, confidence, metadata))
        
        self.conn.commit()
        print(f"[GraphRAG] 관계 추가: {source_entity} --[{relationship_type}]--> {target_entity}")
    
    def get_entity_graph(self, entity: str, max_depth: int = 2) -> Dict:
        """엔티티 관계 그래프 조회"""
        
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM get_entity_graph(%s, %s)
            """, (entity, max_depth))
            
            nodes = []
            for row in cur.fetchall():
                nodes.append({
                    'entity': row[0],
                    'entity_type': row[1],
                    'depth': row[2],
                    'path': row[3]
                })
            
            # 관계 조회
            if nodes:
                entity_list = tuple([n['entity'] for n in nodes])
                cur.execute("""
                    SELECT 
                        kg1.entity as source,
                        kg2.entity as target,
                        er.relationship_type,
                        er.confidence
                    FROM entity_relationships er
                    JOIN knowledge_graph kg1 ON er.source_entity_id = kg1.id
                    JOIN knowledge_graph kg2 ON er.target_entity_id = kg2.id
                    WHERE kg1.entity = ANY(%s)
                """, (list(entity_list),))
                
                edges = []
                for row in cur.fetchall():
                    edges.append({
                        'source': row[0],
                        'target': row[1],
                        'type': row[2],
                        'confidence': float(row[3])
                    })
            else:
                edges = []
        
        return {
            'nodes': nodes,
            'edges': edges
        }
    
    def search_content(
        self,
        query: str,
        content_type: str = None,
        top_k: int = 5,
        threshold: float = 0.7
    ) -> List[Dict]:
        """콘텐츠 벡터 검색"""
        
        query_embedding = self.ollama.embed(query)
        
        with self.conn.cursor() as cur:
            if content_type:
                cur.execute("""
                    SELECT * FROM search_similar_content(
                        %s::vector,
                        %s,
                        %s
                    )
                    WHERE content_type = %s
                """, (query_embedding, threshold, top_k, content_type))
            else:
                cur.execute("""
                    SELECT * FROM search_similar_content(
                        %s::vector,
                        %s,
                        %s
                    )
                """, (query_embedding, threshold, top_k))
            
            results = []
            for row in cur.fetchall():
                results.append({
                    'id': row[0],
                    'content': row[1],
                    'content_type': row[2],
                    'similarity': float(row[3]),
                    'metadata': row[4]
                })
        
        return results
    
    def add_content_embedding(
        self,
        content: str,
        content_type: str = "text",
        metadata: dict = None
    ) -> int:
        """콘텐츠 임베딩 추가"""
        
        embedding = self.ollama.embed(content)
        
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO embeddings (content, content_type, embedding, metadata)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (content, content_type, embedding, metadata))
            
            content_id = cur.fetchone()[0]
        
        self.conn.commit()
        return content_id
    
    def close(self):
        """연결 종료"""
        if self.conn:
            self.conn.close()


    def get_graph_stats(self) -> dict:
        """그래프 통계 조회"""
        with self.conn.cursor() as cur:
            # 노드 수
            cur.execute("SELECT COUNT(*) FROM knowledge_graph")
            node_count = cur.fetchone()[0]
            
            # 엣지 수
            cur.execute("SELECT COUNT(*) FROM knowledge_relationships")
            edge_count = cur.fetchone()[0]
            
            # 엔티티 타입 수
            cur.execute("SELECT COUNT(DISTINCT entity_type) FROM knowledge_graph")
            type_count = cur.fetchone()[0]
        
        return {
            'node_count': node_count,
            'edge_count': edge_count,
            'type_count': type_count
        }
    
    def get_entity_relationships(self, entity: str, max_depth: int = 1) -> list:
        """엔티티 관계 조회"""
        relationships = []
        
        with self.conn.cursor() as cur:
            # 엔티티 ID 조회
            cur.execute("""
                SELECT id FROM knowledge_graph WHERE entity = %s
            """, (entity,))
            
            result = cur.fetchone()
            if not result:
                return relationships
            
            entity_id = result[0]
            
            # 관계 조회
            cur.execute("""
                SELECT 
                    kg1.entity as source,
                    kg2.entity as target,
                    kr.relationship_type as type,
                    kr.confidence
                FROM knowledge_relationships kr
                JOIN knowledge_graph kg1 ON kr.source_id = kg1.id
                JOIN knowledge_graph kg2 ON kr.target_id = kg2.id
                WHERE kr.source_id = %s OR kr.target_id = %s
                LIMIT 50
            """, (entity_id, entity_id))
            
            for row in cur.fetchall():
                relationships.append({
                    'source': row[0],
                    'target': row[1],
                    'type': row[2],
                    'confidence': float(row[3]) if row[3] else 1.0
                })
        
        return relationships
    
    def get_recent_entities(self, limit: int = 10) -> list:
        """최근 추가된 엔티티 조회"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    id,
                    entity,
                    entity_type,
                    metadata,
                    created_at
                FROM knowledge_graph
                ORDER BY created_at DESC
                LIMIT %s
            """, (limit,))
            
            results = []
            for row in cur.fetchall():
                results.append({
                    'id': row[0],
                    'entity': row[1],
                    'entity_type': row[2],
                    'metadata': row[3],
                    'created_at': row[4].isoformat() if row[4] else None
                })
        
        return results


# 싱글톤 인스턴스
_knowledge_graph = None

def get_knowledge_graph() -> KnowledgeGraph:
    """지식 그래프 싱글톤"""
    global _knowledge_graph
    if _knowledge_graph is None:
        _knowledge_graph = KnowledgeGraph()
    return _knowledge_graph
