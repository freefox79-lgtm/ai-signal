"""
AI Signal Agent Security Module

다층 보안 방어 시스템:
1. InputValidator - 입력 검증 및 새니타이제이션
2. OutputSanitizer - 출력 필터링
3. AgentSecurityMiddleware - 에이전트 보안 래퍼
4. SecureEnvManager - 환경 변수 보호
"""

import re
import os
import time
import datetime
import json
from typing import Any, Dict, List, Callable


class InputValidator:
    """입력 검증 및 새니타이제이션"""
    
    # 프롬프트 인젝션 패턴
    INJECTION_PATTERNS = [
        r"ignore\s+all\s+previous\s+instructions",
        r"you\s+are\s+now",
        r"print\s+.*\s+(key|password|token|secret|credential|api)",
        r"reveal\s+.*\s+(api|database|credential|key|password)",
        r"execute\s+.*\s+(command|script|code)",
        r"<script.*?>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",  # onclick, onerror, etc.
        r"';.*?--",  # SQL injection
        r"union\s+select",
        r"drop\s+table",
        r"delete\s+from",
        r"insert\s+into",
        r"update\s+.*\s+set",
    ]
    
    # 개인정보 패턴
    PII_PATTERNS = [
        (r"010-?\d{4}-?\d{4}", "PHONE"),  # 전화번호 (하이픈 있거나 없거나)
        (r"\d{3}-?\d{3,4}-?\d{4}", "PHONE"),  # 일반 전화번호
        (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}", "EMAIL"),  # 이메일
        (r"\d{6}-[1-4]\d{6}", "SSN"),  # 주민등록번호
        (r"\d{4}-\d{4}-\d{4}-\d{4}", "CARD"),  # 카드번호
    ]
    
    @staticmethod
    def validate_input(user_input: str) -> Dict[str, Any]:
        """
        입력 검증
        
        Args:
            user_input: 사용자 입력 문자열
            
        Returns:
            {
                "is_safe": bool,
                "sanitized_input": str,
                "threats_detected": list,
                "pii_detected": list
            }
        """
        if not isinstance(user_input, str):
            user_input = str(user_input)
        
        threats = []
        pii_found = []
        
        # 1. 프롬프트 인젝션 탐지
        for pattern in InputValidator.INJECTION_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE):
                threats.append(f"Injection pattern: {pattern[:50]}")
        
        # 2. 개인정보 탐지
        for pattern, pii_type in InputValidator.PII_PATTERNS:
            matches = re.findall(pattern, user_input)
            if matches:
                for match in matches:
                    pii_found.append({"type": pii_type, "value": match})
        
        # 3. 입력 새니타이제이션
        sanitized = user_input
        
        # HTML/Script 태그 제거
        sanitized = re.sub(r'<[^>]+>', '', sanitized)
        
        # SQL 특수문자 이스케이프
        sanitized = sanitized.replace("'", "''")
        sanitized = sanitized.replace(";", "")
        sanitized = sanitized.replace("--", "")
        
        # 개인정보 마스킹
        for pii in pii_found:
            if pii['type'] == 'EMAIL':
                sanitized = sanitized.replace(pii['value'], "[EMAIL_REDACTED]")
            elif pii['type'] == 'PHONE':
                sanitized = sanitized.replace(pii['value'], "[PHONE_REDACTED]")
            elif pii['type'] == 'SSN':
                sanitized = sanitized.replace(pii['value'], "[SSN_REDACTED]")
            elif pii['type'] == 'CARD':
                sanitized = sanitized.replace(pii['value'], "[CARD_REDACTED]")
        
        # 길이 제한 (DoS 방지)
        max_length = 2000
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
            threats.append(f"Input truncated (max: {max_length} chars)")
        
        is_safe = len(threats) == 0
        
        return {
            "is_safe": is_safe,
            "sanitized_input": sanitized,
            "threats_detected": threats,
            "pii_detected": pii_found
        }


class OutputSanitizer:
    """출력 새니타이제이션"""
    
    # 민감 정보 패턴
    SENSITIVE_PATTERNS = [
        (r"(api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?([^'\"\\s]+)", r'\1: [REDACTED]'),
        (r"(DATABASE_URL|DB_URL)\s*[:=]\s*['\"]?([^'\"\\s]+)", r'\1: [REDACTED]'),
        (r"postgresql://[^\\s]+", "postgresql://[REDACTED]"),
        (r"mongodb://[^\\s]+", "mongodb://[REDACTED]"),
        (r"redis://[^\\s]+", "redis://[REDACTED]"),
        (r"sk-[a-zA-Z0-9]{48}", "[OPENAI_KEY_REDACTED]"),
        (r"ghp_[a-zA-Z0-9]{36}", "[GITHUB_TOKEN_REDACTED]"),
    ]
    
    @staticmethod
    def sanitize_output(output: Any) -> Any:
        """
        출력 새니타이제이션
        
        Args:
            output: 출력 데이터 (str, dict, list 등)
            
        Returns:
            새니타이즈된 출력
        """
        if isinstance(output, str):
            sanitized = output
            
            # 민감 정보 마스킹
            for pattern, replacement in OutputSanitizer.SENSITIVE_PATTERNS:
                sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
            
            return sanitized
            
        elif isinstance(output, dict):
            return {
                k: OutputSanitizer.sanitize_output(v) 
                for k, v in output.items()
            }
            
        elif isinstance(output, list):
            return [
                OutputSanitizer.sanitize_output(item) 
                for item in output
            ]
        
        return output


class AgentSecurityMiddleware:
    """에이전트 보안 미들웨어"""
    
    def __init__(self):
        self.validator = InputValidator()
        self.sanitizer = OutputSanitizer()
        self.blocked_queries = []
        self.rate_limiter = RateLimiter()
    
    def secure_execute(
        self, 
        agent_func: Callable, 
        user_input: str, 
        user_id: str = "default",
        **kwargs
    ) -> Any:
        """
        보안 검증 후 에이전트 실행
        
        Args:
            agent_func: 실행할 에이전트 함수
            user_input: 사용자 입력
            user_id: 사용자 ID (rate limiting용)
            **kwargs: 추가 인자
            
        Returns:
            새니타이즈된 결과 또는 에러
        """
        # 0. Rate Limiting
        if not self.rate_limiter.is_allowed(user_id):
            return {
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later."
            }
        
        # 1. 입력 검증
        validation_result = self.validator.validate_input(user_input)
        
        if not validation_result["is_safe"]:
            # 위협 탐지 시 차단
            self._log_blocked_query(user_input, validation_result["threats_detected"])
            
            return {
                "error": "Security threat detected",
                "threats": validation_result["threats_detected"],
                "message": "Your query has been blocked for security reasons."
            }
        
        # 2. PII 경고
        if validation_result["pii_detected"]:
            print(f"[SECURITY WARNING] PII detected and redacted: {len(validation_result['pii_detected'])} items")
        
        # 3. 새니타이즈된 입력으로 에이전트 실행
        try:
            result = agent_func(validation_result["sanitized_input"], **kwargs)
        except Exception as e:
            print(f"[SECURITY ERROR] Agent execution failed: {e}")
            return {
                "error": "Agent execution failed",
                "message": "An error occurred while processing your request."
            }
        
        # 4. 출력 새니타이제이션
        sanitized_result = self.sanitizer.sanitize_output(result)
        
        return sanitized_result
    
    def _log_blocked_query(self, query: str, threats: List[str]):
        """차단된 쿼리 로깅"""
        blocked_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "query": query[:100],  # 처음 100자만 로그
            "threats": threats
        }
        
        self.blocked_queries.append(blocked_entry)
        
        print(f"[SECURITY ALERT] Blocked malicious query: {threats}")
        
        # 로그 파일에 기록
        try:
            with open("security_audit.log", "a") as f:
                f.write(json.dumps(blocked_entry) + "\n")
        except Exception as e:
            print(f"[SECURITY ERROR] Failed to write audit log: {e}")


class SecureEnvManager:
    """환경 변수 보안 관리"""
    
    # 허용된 환경 변수만 접근 가능
    ALLOWED_ENV_VARS = [
        "API_STATUS",  # MOCK/LIVE
        "LOG_LEVEL",
    ]
    
    # 절대 노출 금지
    FORBIDDEN_ENV_VARS = [
        "DATABASE_URL",
        "NAVER_CLIENT_ID",
        "NAVER_CLIENT_SECRET",
        "ALPHA_VANTAGE_API_KEY",
        "FRED_API_KEY",
        "OPENAI_API_KEY",
        "GITHUB_TOKEN",
        "YOUTUBE_API_KEY",
        "TMDB_KEY",
        "OPENWEATHER_KEY",
    ]
    
    @staticmethod
    def get_safe_env(key: str) -> str:
        """
        안전한 환경 변수 접근
        
        Args:
            key: 환경 변수 키
            
        Returns:
            값 또는 None
        """
        # 금지된 변수 접근 시도 차단
        if key in SecureEnvManager.FORBIDDEN_ENV_VARS:
            print(f"[SECURITY ALERT] Attempted access to forbidden env var: {key}")
            return None
        
        # 허용된 변수만 반환
        if key in SecureEnvManager.ALLOWED_ENV_VARS:
            return os.getenv(key)
        
        # 기타 변수는 차단
        print(f"[SECURITY WARNING] Attempted access to non-whitelisted env var: {key}")
        return None


class RateLimiter:
    """요청 속도 제한"""
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        """
        Args:
            max_requests: 시간 윈도우 내 최대 요청 수
            time_window: 시간 윈도우 (초)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}  # {user_id: [timestamps]}
    
    def is_allowed(self, user_id: str) -> bool:
        """
        요청 허용 여부 확인
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            허용 여부
        """
        now = time.time()
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # 시간 윈도우 밖의 요청 제거
        self.requests[user_id] = [
            ts for ts in self.requests[user_id]
            if now - ts < self.time_window
        ]
        
        # 제한 확인
        if len(self.requests[user_id]) >= self.max_requests:
            print(f"[SECURITY WARNING] Rate limit exceeded for user: {user_id}")
            return False
        
        # 요청 기록
        self.requests[user_id].append(now)
        return True


# 편의 함수
def create_security_middleware() -> AgentSecurityMiddleware:
    """보안 미들웨어 인스턴스 생성"""
    return AgentSecurityMiddleware()
