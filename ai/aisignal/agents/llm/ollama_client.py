"""
Ollama 로컬 LLM 클라이언트

Mac Mini 최적화:
- 로컬 Ollama 서버 사용 (GPU 가속)
- 임베딩 캐싱 (Redis)
- LLM 생성 캐싱 (Redis)
- 캐시 히트율 모니터링
- 배치 처리 지원
"""

import os
import requests
import json
import hashlib
import redis
from typing import List, Optional, Union, Dict
from dotenv import load_dotenv

load_dotenv(".env.local")

# TTL 상수 import
try:
    from agents.cache.cache_ttl import CacheTTL
except ImportError:
    # Fallback if cache module not available
    class CacheTTL:
        EMBEDDING = 7 * 24 * 3600
        LLM_GENERATION = 3600


class OllamaClient:
    """Ollama 로컬 LLM 클라이언트"""
    
    def __init__(
        self, 
        base_url: str = None,
        default_model: str = "llama3.2:3b"
    ):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.default_model = default_model
        
        # Redis 캐싱
        try:
            redis_pwd = os.getenv("REDIS_PASSWORD", "aisignal2026_secure")
            self.redis = redis.Redis(
                host='localhost',
                port=6379,
                password=redis_pwd,
                decode_responses=False
            )
            self.redis.ping()
            print("[Ollama] Redis 캐싱 활성화 (임베딩 + 생성)")
        except Exception as e:
            print(f"[Ollama] Redis 연결 실패, 캐싱 비활성화: {e}")
            self.redis = None
        
        # 캐시 모니터 (선택적)
        self.cache_monitor = None
        try:
            from agents.cache.cache_monitor import get_cache_monitor
            self.cache_monitor = get_cache_monitor()
        except ImportError:
            pass
    
    def _get_cache_key(self, text: str, model: str) -> str:
        """캐시 키 생성 (텍스트 + 모델 해시)"""
        content = f"{text}:{model}"
        return f"ollama:embed:{hashlib.md5(content.encode()).hexdigest()}"
    
    def generate(
        self,
        prompt: str,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        stream: bool = False,
        use_cache: bool = True
    ) -> str:
        """텍스트 생성 (캐싱 지원)"""
        model = model or self.default_model
        
        # 캐싱 (스트리밍 제외, temperature < 0.3만)
        if use_cache and not stream and temperature < 0.3 and self.redis:
            cache_key = self._get_generation_cache_key(prompt, model, temperature, max_tokens)
            
            try:
                cached = self.redis.get(cache_key)
                if cached:
                    if self.cache_monitor:
                        self.cache_monitor.record_hit('llm_generation')
                    return cached.decode('utf-8')
            except Exception as e:
                print(f"[Ollama] Cache read error: {e}")
        
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": stream,
            "options": {
                "num_predict": max_tokens
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            if stream:
                return response.iter_lines()
            else:
                result = response.json()
                response_text = result.get("response", "")
                
                # 캐싱
                if use_cache and temperature < 0.3 and self.redis:
                    try:
                        self.redis.setex(cache_key, CacheTTL.LLM_GENERATION, response_text)
                        if self.cache_monitor:
                            self.cache_monitor.record_miss('llm_generation')
                    except Exception as e:
                        print(f"[Ollama] Cache write error: {e}")
                
                return response_text
                
        except Exception as e:
            print(f"[Ollama] Generate error: {e}")
            raise
    
    def _get_generation_cache_key(self, prompt: str, model: str, temperature: float, max_tokens: int) -> str:
        """생성 캐시 키 생성"""
        cache_data = {
            'prompt': prompt,
            'model': model,
            'temperature': temperature,
            'max_tokens': max_tokens
        }
        content_hash = hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()
        return f"ollama:gen:{content_hash}"
    
    def embed(self, text: str, model: str = "nomic-embed-text") -> List[float]:
        """텍스트 임베딩 (GraphRAG용, 캐싱 지원)"""
        if self.redis:
            cache_key = self._get_cache_key(text, model)
            try:
                cached_embedding = self.redis.get(cache_key)
                if cached_embedding:
                    if self.cache_monitor:
                        self.cache_monitor.record_hit('embedding')
                    return json.loads(cached_embedding.decode('utf-8'))
            except Exception as e:
                print(f"[Ollama] Cache read error: {e}")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": model,
                    "prompt": text
                },
                timeout=30
            )
            response.raise_for_status()
            embedding = response.json()["embedding"]
            
            # 캐싱 (7일, 임베딩은 결정론적)
            if self.redis:
                try:
                    self.redis.setex(
                        self._get_cache_key(text, model),
                        CacheTTL.EMBEDDING,
                        json.dumps(embedding)
                    )
                    if self.cache_monitor:
                        self.cache_monitor.record_miss('embedding')
                except Exception as e:
                    print(f"[Ollama] Cache write error: {e}")
            
            return embedding
        except Exception as e:
            print(f"[Ollama] 임베딩 오류: {e}")
            # 768차원 제로 벡터 반환 (fallback)
            return [0.0] * 768
    
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: str = None,
        temperature: float = 0.7
    ) -> str:
        """채팅 (대화형)"""
        model = model or self.default_model
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature
                    }
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()["message"]["content"]
        except Exception as e:
            print(f"[Ollama] 채팅 오류: {e}")
            return f"Error: {str(e)}"
    
    def list_models(self) -> List[str]:
        """설치된 모델 목록"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            models = response.json().get("models", [])
            return [m["name"] for m in models]
        except Exception as e:
            print(f"[Ollama] 모델 목록 조회 오류: {e}")
            return []
    
    def is_available(self) -> bool:
        """Ollama 서비스 사용 가능 여부"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False


# 싱글톤 인스턴스
_ollama_client = None

def get_ollama_client() -> OllamaClient:
    """Ollama 클라이언트 싱글톤"""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client
