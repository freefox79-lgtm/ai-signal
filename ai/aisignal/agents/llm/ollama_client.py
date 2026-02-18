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
from typing import List, Optional, Union, Dict, Any
from dotenv import load_dotenv
# Load environment variables (WITHOUT OVERRIDE to respect Docker/System env)
if os.path.exists(".env.local"):
    load_dotenv(".env.local", override=False)
else:
    load_dotenv(override=False)


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
    
    # 모델 상수 (Mac Mini 최적화용)
    MODEL_FAST = "llama3.2:3b"       # 고속 처리, 요약용
    MODEL_ANALYTIC = "llama3.2:3b"   # (임시) Qwen 부재로 Llama로 대체
    MODEL_REASONING = "gemma3:12b"    # 심층 추론, 페르소나 합성용
    MODEL_BALANCED = "llama3.2:3b"    # 범용 모델
    MODEL_EMBED = "nomic-embed-text" # 임베딩 전용
    
    def __init__(
        self, 
        base_url: str = None,
        default_model: str = "llama3.2:3b"
    ):
        # Try multiple environment variables (Priority: OLLAMA_BASE_URL > OLLAMA_HOST)
        env_url = os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_HOST")
        self.base_url = base_url or env_url or "http://host.docker.internal:11434"
        self.default_model = default_model
        
        # Redis 캐싱
        try:
            redis_pwd = os.getenv("REDIS_PASSWORD", "aisignal2026_secure")
            self.redis = redis.Redis(
                host=os.getenv("REDIS_HOST", "aisignal-redis"),
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
            
        # GPU / Metal Status
        self.gpu_accelerated = self.check_gpu_status()

    def check_gpu_status(self) -> bool:
        """
        Checks if GPU acceleration (Metal) is active for the current model.
        Uses 'ollama ps' command for verification.
        """
        import subprocess
        try:
            result = subprocess.run(['ollama', 'ps'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                output = result.stdout.lower()
                # Pattern: Look for 100% GPU or Metal mentions
                is_gpu = "100% gpu" in output or "metal" in output
                if is_gpu:
                    print(f"🚀 [Ollama] M4 Metal Acceleration confirmed active.")
                else:
                    print(f"⚠️ [Ollama] GPU acceleration not detected in current status.")
                return is_gpu
        except Exception as e:
            print(f"ℹ️ [Ollama] GPU status check skip (Host access needed): {e}")
        return False
    
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
        use_cache: bool = True,
        options: Optional[Dict[str, Any]] = None,
        keep_alive: str = "5m"
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
        
        # Default options
        final_options = {
            "num_predict": max_tokens,
            "temperature": temperature
        }
        
        # Merge user options (e.g. num_ctx, num_gpu)
        if options:
            final_options.update(options)

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": final_options,
            "keep_alive": keep_alive
        }
        
        try:
            # Optional: Log GPU check before heavy generation
            if model == self.MODEL_REASONING:
                self.check_gpu_status()
                
            # Increased timeout for heavy models (12B+)
            request_timeout = 180 if model == self.MODEL_REASONING else 60
            
            try:
                response = requests.post(url, json=payload, timeout=request_timeout)
                response.raise_for_status()
            except requests.exceptions.HTTPError as he:
                # Automatic Fallback for Reasoning Model (Gemma 3 -> Llama 3)
                if model == self.MODEL_REASONING:
                    print(f"⚠️ [Ollama] {model} failed (500), falling back to {self.MODEL_FAST}...")
                    payload['model'] = self.MODEL_FAST
                    response = requests.post(url, json=payload, timeout=60)
                    response.raise_for_status()
                else:
                    raise he
            
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
            
    def warmup(self, models: List[str] = None):
        """모델 예열 (메모리에 로드)"""
        models = models or [self.default_model, "mistral:7b"]
        print(f"[Ollama] Warming up models: {models}")
        for model in models:
            try:
                # keep_alive: -1 maintains the model in memory indefinitely/long-term
                requests.post(
                    f"{self.base_url}/api/generate",
                    json={"model": model, "keep_alive": -1},
                    timeout=5 # Trigger only
                )
            except Exception as e:
                # We expect a possible timeout if we don't wait for the full load,
                # but the server will continue loading it.
                pass


# 싱글톤 인스턴스
_ollama_client = None

def get_ollama_client() -> OllamaClient:
    """Ollama 클라이언트 싱글톤"""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client
