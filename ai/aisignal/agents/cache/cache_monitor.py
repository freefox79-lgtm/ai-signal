"""
Redis Cache Monitor
캐시 히트율 추적 및 통계
"""

import redis
from typing import Dict
import os
from dotenv import load_dotenv

load_dotenv(".env.local")


class CacheMonitor:
    """Redis 캐시 모니터링"""
    
    def __init__(self, redis_client: redis.Redis = None):
        if redis_client:
            self.redis = redis_client
        else:
            # 새 Redis 연결
            redis_pwd = os.getenv("REDIS_PASSWORD", "aisignal2026_secure")
            self.redis = redis.Redis(
                host='localhost',
                port=6379,
                password=redis_pwd,
                decode_responses=True
            )
        
        self.stats_key = "cache:stats"
    
    def record_hit(self, cache_type: str):
        """캐시 히트 기록"""
        self.redis.hincrby(self.stats_key, f"{cache_type}:hits", 1)
    
    def record_miss(self, cache_type: str):
        """캐시 미스 기록"""
        self.redis.hincrby(self.stats_key, f"{cache_type}:misses", 1)
    
    def get_hit_rate(self, cache_type: str) -> float:
        """캐시 히트율 계산"""
        hits = int(self.redis.hget(self.stats_key, f"{cache_type}:hits") or 0)
        misses = int(self.redis.hget(self.stats_key, f"{cache_type}:misses") or 0)
        
        total = hits + misses
        if total == 0:
            return 0.0
        
        return hits / total
    
    def get_all_stats(self) -> Dict:
        """모든 캐시 통계 조회"""
        stats_raw = self.redis.hgetall(self.stats_key)
        
        # 캐시 타입별로 그룹화
        result = {}
        for key, value in stats_raw.items():
            if ':' not in key:
                continue
            
            cache_type, metric = key.split(':', 1)
            if cache_type not in result:
                result[cache_type] = {'hits': 0, 'misses': 0}
            
            result[cache_type][metric] = int(value)
        
        # 히트율 계산
        for cache_type in result:
            hits = result[cache_type].get('hits', 0)
            misses = result[cache_type].get('misses', 0)
            total = hits + misses
            result[cache_type]['total'] = total
            result[cache_type]['hit_rate'] = hits / total if total > 0 else 0.0
        
        return result
    
    def reset_stats(self, cache_type: str = None):
        """통계 초기화"""
        if cache_type:
            self.redis.hdel(self.stats_key, f"{cache_type}:hits", f"{cache_type}:misses")
        else:
            self.redis.delete(self.stats_key)
    
    def print_stats(self):
        """통계 출력"""
        stats = self.get_all_stats()
        
        print("\n=== Redis Cache Statistics ===")
        for cache_type, metrics in stats.items():
            print(f"\n{cache_type}:")
            print(f"  Hits: {metrics['hits']:,}")
            print(f"  Misses: {metrics['misses']:,}")
            print(f"  Total: {metrics['total']:,}")
            print(f"  Hit Rate: {metrics['hit_rate']:.2%}")
        
        # 전체 통계
        total_hits = sum(m['hits'] for m in stats.values())
        total_misses = sum(m['misses'] for m in stats.values())
        total_requests = total_hits + total_misses
        
        if total_requests > 0:
            print(f"\n전체:")
            print(f"  Total Requests: {total_requests:,}")
            print(f"  Overall Hit Rate: {total_hits / total_requests:.2%}")


# 싱글톤 인스턴스
_cache_monitor = None

def get_cache_monitor() -> CacheMonitor:
    """캐시 모니터 싱글톤"""
    global _cache_monitor
    if _cache_monitor is None:
        _cache_monitor = CacheMonitor()
    return _cache_monitor
