"""
Cache TTL Constants
데이터 타입별 캐시 TTL 전략
"""


class CacheTTL:
    """캐시 TTL 상수"""
    
    # Ollama 관련
    EMBEDDING = 7 * 24 * 3600  # 7일 (임베딩은 결정론적)
    LLM_GENERATION = 3600  # 1시간 (생성 결과는 변할 수 있음)
    
    # 시장 데이터
    MARKET_DATA_ACTIVE = 15 * 60  # 15분 (시장 개장 시간)
    MARKET_DATA_INACTIVE = 4 * 3600  # 4시간 (시장 폐장 시간)
    
    # 경제 데이터
    ECONOMIC_DATA = 24 * 3600  # 24시간 (일일 업데이트)
    
    # 트렌드 데이터
    TREND_DATA = 4 * 3600  # 4시간 (빠르게 변함)
    SNS_TREND = 2 * 3600  # 2시간 (더 빠름)
    
    # 사용자 쿼리
    USER_QUERY = 30 * 60  # 30분 (최근 쿼리 재사용)
    
    # API 응답
    API_RESPONSE = 3600  # 1시간 (기본값)
    
    @classmethod
    def get_market_ttl(cls, is_market_hours: bool = True) -> int:
        """시장 시간에 따른 TTL 반환"""
        return cls.MARKET_DATA_ACTIVE if is_market_hours else cls.MARKET_DATA_INACTIVE
