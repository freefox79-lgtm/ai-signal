"""
AI Signal 확장성 모니터링 시스템

사용자 수, 리소스 사용량을 모니터링하고
인프라 확장이 필요한 시점에 알림 및 제안 제공
"""

import os
import psutil
import redis
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from db_utils import get_db_connection

load_dotenv(".env.local")


@dataclass
class ScalingThreshold:
    """확장 임계값"""
    users: int
    cpu_percent: float
    memory_percent: float
    redis_memory_mb: float
    db_size_mb: float
    bandwidth_gb: float


@dataclass
class ScalingRecommendation:
    """확장 제안"""
    level: str  # "warning", "critical", "urgent"
    title: str
    description: str
    actions: List[str]
    estimated_cost: str
    timeline: str


class ScalingMonitor:
    """확장성 모니터링"""
    
    # 확장 단계별 임계값
    THRESHOLDS = {
        "beta": ScalingThreshold(
            users=100,
            cpu_percent=70,
            memory_percent=70,
            redis_memory_mb=100,
            db_size_mb=400,
            bandwidth_gb=4
        ),
        "growth": ScalingThreshold(
            users=1000,
            cpu_percent=80,
            memory_percent=80,
            redis_memory_mb=500,
            db_size_mb=7000,
            bandwidth_gb=40
        ),
        "scale": ScalingThreshold(
            users=10000,
            cpu_percent=85,
            memory_percent=85,
            redis_memory_mb=2000,
            db_size_mb=50000,
            bandwidth_gb=400
        )
    }
    
    def __init__(self):
        self.redis_client = self._init_redis()
        self.current_stage = self._detect_current_stage()
    
    def _init_redis(self) -> Optional[redis.Redis]:
        """Redis 연결"""
        try:
            r = redis.Redis(
                host='localhost',
                port=6379,
                password=os.getenv("REDIS_PASSWORD", "aisignal2026_secure"),
                decode_responses=True
            )
            r.ping()
            return r
        except Exception as e:
            print(f"[ScalingMonitor] Redis 연결 실패: {e}")
            return None
    
    def _detect_current_stage(self) -> str:
        """현재 단계 감지"""
        users = self.get_user_count()
        
        if users < 100:
            return "development"
        elif users < 1000:
            return "beta"
        elif users < 10000:
            return "growth"
        else:
            return "scale"
    
    def get_user_count(self) -> int:
        """사용자 수 조회 (Supabase)"""
        try:
            conn = get_db_connection(routing='cloud')
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM users")
                count = cur.fetchone()[0]
            return count
        except Exception as e:
            print(f"[ScalingMonitor] 사용자 수 조회 실패: {e}")
            return 0
    
    def get_system_metrics(self) -> Dict:
        """시스템 메트릭 수집"""
        # 기본 시스템 정보
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "users": self.get_user_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "cpu_count": psutil.cpu_count(),
            "memory_percent": vm.percent,
            "memory_total_gb": vm.total / (1024**3),
            "memory_used_gb": vm.used / (1024**3),
            "disk_percent": disk.percent,
            "disk_total_gb": disk.total / (1024**3),
            "disk_used_gb": disk.used / (1024**3),
        }
        
        # CPU 온도 (Mac Mini)
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Mac의 경우 'coretemp' 또는 'cpu_thermal' 사용
                for name, entries in temps.items():
                    if entries:
                        metrics["cpu_temp"] = entries[0].current
                        break
        except:
            metrics["cpu_temp"] = None
        
        # Redis 메모리
        if self.redis_client:
            try:
                info = self.redis_client.info("memory")
                metrics["redis_memory_mb"] = info["used_memory"] / (1024 * 1024)
            except:
                metrics["redis_memory_mb"] = 0
        
        return metrics
    
    def check_scaling_needs(self) -> List[ScalingRecommendation]:
        """확장 필요성 체크"""
        metrics = self.get_system_metrics()
        recommendations = []
        
        # 사용자 수 기반 체크
        users = metrics["users"]
        
        if users >= 100 and self.current_stage == "development":
            recommendations.append(ScalingRecommendation(
                level="warning",
                title="베타 단계 전환 권장",
                description=f"사용자 {users}명 도달. Render 배포 고려 필요.",
                actions=[
                    "Render.com에 배포 (1 instance)",
                    "Supabase Free 플랜 유지",
                    "Ollama → OpenAI API 전환 고려",
                    "모니터링 도구 추가 (Sentry)"
                ],
                estimated_cost="$21/월",
                timeline="1주일 내"
            ))
        
        if users >= 1000 and self.current_stage == "beta":
            recommendations.append(ScalingRecommendation(
                level="critical",
                title="성장 단계 전환 필요",
                description=f"사용자 {users}명 도달. 인프라 확장 필요.",
                actions=[
                    "Render 인스턴스 2개로 증설",
                    "Supabase Pro 플랜 업그레이드 ($25/월)",
                    "Redis Cloud 추가 ($10/월)",
                    "CDN 설정 (Cloudflare)",
                    "로드 밸런싱 구성"
                ],
                estimated_cost="$67/월",
                timeline="3일 내"
            ))
        
        if users >= 10000 and self.current_stage == "growth":
            recommendations.append(ScalingRecommendation(
                level="urgent",
                title="스케일 단계 전환 긴급",
                description=f"사용자 {users}명 도달. 즉시 확장 필요.",
                actions=[
                    "Render 인스턴스 3개 이상으로 증설",
                    "Database Read Replicas 추가",
                    "Redis Cluster 구성",
                    "Auto-scaling 설정",
                    "성능 모니터링 강화 (DataDog)"
                ],
                estimated_cost="$148/월",
                timeline="즉시"
            ))
        
        # CPU 사용률 체크
        if metrics["cpu_percent"] > 85:
            recommendations.append(ScalingRecommendation(
                level="critical",
                title="CPU 사용률 임계치 초과",
                description=f"CPU 사용률 {metrics['cpu_percent']:.1f}% (임계치: 85%)",
                actions=[
                    "서버 인스턴스 추가",
                    "로드 밸런싱 구성",
                    "코드 최적화 검토"
                ],
                estimated_cost="인스턴스당 $21/월",
                timeline="24시간 내"
            ))
        
        # 메모리 사용률 체크
        if metrics["memory_percent"] > 85:
            recommendations.append(ScalingRecommendation(
                level="critical",
                title="메모리 사용률 임계치 초과",
                description=f"메모리 사용률 {metrics['memory_percent']:.1f}% (임계치: 85%)",
                actions=[
                    "메모리 증설 또는 인스턴스 업그레이드",
                    "캐싱 전략 최적화",
                    "메모리 누수 점검"
                ],
                estimated_cost="$10-30/월 추가",
                timeline="24시간 내"
            ))
        
        # Mac Mini 하드웨어 한계 체크
        hw_recommendations = self._check_hardware_limits(metrics)
        recommendations.extend(hw_recommendations)
        
        return recommendations
    
    def _check_hardware_limits(self, metrics: Dict) -> List[ScalingRecommendation]:
        """Mac Mini 하드웨어 한계 체크 및 업그레이드 제안"""
        recommendations = []
        
        # Mac Mini 사양 (예: M2, 8GB RAM, 256GB SSD)
        # 실제 사양은 자동 감지된 값 사용
        total_ram_gb = metrics.get("memory_total_gb", 8)
        total_disk_gb = metrics.get("disk_total_gb", 256)
        cpu_count = metrics.get("cpu_count", 8)
        
        # 1. RAM 한계 체크 (8GB Mac Mini)
        if total_ram_gb <= 8 and metrics["memory_percent"] > 75:
            recommendations.append(ScalingRecommendation(
                level="warning",
                title="🖥️ Mac Mini RAM 용량 부족",
                description=f"현재 RAM: {total_ram_gb:.0f}GB, 사용률: {metrics['memory_percent']:.1f}%\n8GB RAM은 개발 환경에만 적합합니다.",
                actions=[
                    "Mac Mini 16GB 또는 24GB 모델로 업그레이드",
                    "또는 Render.com 클라우드로 마이그레이션",
                    "메모리 집약적 작업 최적화 (Ollama 모델 경량화)",
                    "Redis 메모리 제한 설정"
                ],
                estimated_cost="Mac Mini 16GB: $799 / Render: $21/월",
                timeline="사용자 50명 도달 전"
            ))
        
        # 2. 디스크 용량 체크 (256GB SSD)
        if total_disk_gb <= 256 and metrics["disk_percent"] > 70:
            recommendations.append(ScalingRecommendation(
                level="warning",
                title="💾 Mac Mini 디스크 용량 부족",
                description=f"현재 디스크: {total_disk_gb:.0f}GB, 사용률: {metrics['disk_percent']:.1f}%\n로그, 캐시, 모델 파일로 빠르게 소진됩니다.",
                actions=[
                    "Mac Mini 512GB 이상 모델로 업그레이드",
                    "외장 SSD 추가 (Thunderbolt)",
                    "로그 로테이션 설정",
                    "Ollama 모델을 외장 디스크로 이동",
                    "클라우드 스토리지 활용 (S3, Supabase Storage)"
                ],
                estimated_cost="512GB 모델: $999 / 외장 SSD: $100-200",
                timeline="디스크 80% 도달 전"
            ))
        
        # 3. CPU 온도 체크 (과열 경고)
        cpu_temp = metrics.get("cpu_temp")
        if cpu_temp and cpu_temp > 80:
            recommendations.append(ScalingRecommendation(
                level="critical",
                title="🌡️ Mac Mini CPU 과열 경고",
                description=f"CPU 온도: {cpu_temp:.1f}°C (정상: 60-70°C)\n지속적인 고부하로 인한 과열 위험.",
                actions=[
                    "Mac Mini 쿨링 패드 사용",
                    "통풍이 잘 되는 곳으로 이동",
                    "CPU 집약적 작업을 클라우드로 오프로드",
                    "Ollama 추론을 GPU 서버로 이전 (Render + GPU)",
                    "백그라운드 프로세스 최적화"
                ],
                estimated_cost="쿨링 패드: $30 / GPU 서버: $50/월",
                timeline="즉시"
            ))
        
        # 4. 종합 업그레이드 제안 (사용자 100명 이상)
        if metrics["users"] >= 100 and (total_ram_gb <= 8 or total_disk_gb <= 256):
            recommendations.append(ScalingRecommendation(
                level="urgent",
                title="🚀 Mac Mini 한계 도달 - 클라우드 마이그레이션 권장",
                description=f"사용자 {metrics['users']}명 도달. Mac Mini는 개발/테스트 환경에 적합하며, 프로덕션 환경으로는 부적합합니다.",
                actions=[
                    "Render.com으로 완전 마이그레이션 (권장)",
                    "또는 Mac Mini M2 Pro (16GB+ RAM, 512GB+ SSD) 업그레이드",
                    "하이브리드: Mac Mini (개발) + Render (프로덕션)",
                    "로드 밸런싱: Mac Mini + 클라우드 인스턴스",
                    "모니터링 강화: Uptime, 성능 추적"
                ],
                estimated_cost="Render 마이그레이션: $21/월 / Mac Mini M2 Pro: $1,299",
                timeline="1주일 내"
            ))
        
        # 5. 디스크 I/O 병목 체크
        if metrics["disk_percent"] > 85:
            recommendations.append(ScalingRecommendation(
                level="critical",
                title="⚠️ 디스크 용량 임계치 초과",
                description=f"디스크 사용률: {metrics['disk_percent']:.1f}%\n시스템 불안정 위험.",
                actions=[
                    "즉시 불필요한 파일 삭제",
                    "로그 파일 정리 (Docker, n8n, Streamlit)",
                    "Ollama 모델 캐시 정리",
                    "외장 SSD로 데이터 이동",
                    "클라우드 마이그레이션 고려"
                ],
                estimated_cost="외장 SSD: $100-200",
                timeline="24시간 내"
            ))
        
        return recommendations
    
    def save_metrics_history(self):
        """메트릭 히스토리 저장 (Redis)"""
        if not self.redis_client:
            return
        
        metrics = self.get_system_metrics()
        key = f"metrics:{datetime.now().strftime('%Y%m%d%H')}"
        
        try:
            self.redis_client.setex(
                key,
                86400 * 7,  # 7일 보관
                str(metrics)
            )
        except Exception as e:
            print(f"[ScalingMonitor] 메트릭 저장 실패: {e}")
    
    def generate_report(self) -> str:
        """확장성 보고서 생성"""
        metrics = self.get_system_metrics()
        recommendations = self.check_scaling_needs()
        
        report = f"""
# AI Signal 확장성 보고서
**생성 시간**: {metrics['timestamp']}
**현재 단계**: {self.current_stage.upper()}

## 📊 현재 메트릭

### 비즈니스 메트릭
- **사용자 수**: {metrics['users']:,}명

### 시스템 리소스
- **CPU 사용률**: {metrics['cpu_percent']:.1f}% (코어: {metrics.get('cpu_count', 'N/A')}개)
- **메모리 사용률**: {metrics['memory_percent']:.1f}% ({metrics.get('memory_used_gb', 0):.1f}GB / {metrics.get('memory_total_gb', 0):.1f}GB)
- **디스크 사용률**: {metrics['disk_percent']:.1f}% ({metrics.get('disk_used_gb', 0):.1f}GB / {metrics.get('disk_total_gb', 0):.1f}GB)
- **Redis 메모리**: {metrics.get('redis_memory_mb', 0):.1f} MB
"""
        
        if not recommendations:
            report += "\n✅ 현재 인프라로 충분합니다.\n"
        else:
            for i, rec in enumerate(recommendations, 1):
                level_emoji = {
                    "warning": "⚠️",
                    "critical": "🔴",
                    "urgent": "🚨"
                }
                
                report += f"""
### {level_emoji[rec.level]} {rec.title}
**심각도**: {rec.level.upper()}
**설명**: {rec.description}

**권장 조치**:
"""
                for action in rec.actions:
                    report += f"- {action}\n"
                
                report += f"""
**예상 비용**: {rec.estimated_cost}
**타임라인**: {rec.timeline}
---
"""
        
        return report


def main():
    """메인 실행"""
    monitor = ScalingMonitor()
    
    # 메트릭 수집 및 저장
    monitor.save_metrics_history()
    
    # 확장 제안 체크
    metrics = monitor.get_system_metrics()
    recommendations = monitor.check_scaling_needs()
    
    # 텔레그램 알림 전송 (제안이 있을 경우)
    if recommendations:
        try:
            from telegram_notifier import send_scaling_alert
            send_scaling_alert(metrics, recommendations)
        except Exception as e:
            print(f"[ScalingMonitor] 텔레그램 알림 실패: {e}")
    
    # 보고서 생성
    report = monitor.generate_report()
    print(report)
    
    # 파일로 저장
    report_path = f"scaling_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 보고서 저장: {report_path}")


if __name__ == "__main__":
    main()
