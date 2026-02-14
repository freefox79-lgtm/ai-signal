"""
Telegram 알림 전송 모듈

scaling_monitor.py에서 호출하여 텔레그램으로 알림 전송
"""

import os
import requests
from typing import List
from scaling_monitor import ScalingRecommendation
from dotenv import load_dotenv

load_dotenv(".env.local")


class TelegramNotifier:
    """텔레그램 알림 전송"""
    
    def __init__(self):
        self.n8n_webhook_url = os.getenv(
            "N8N_SCALING_WEBHOOK_URL",
            "http://localhost:5678/webhook/scaling-alert"
        )
    
    def format_message(
        self,
        metrics: dict,
        recommendations: List[ScalingRecommendation]
    ) -> str:
        """알림 메시지 포맷"""
        
        # 이모지 매핑
        level_emoji = {
            "warning": "⚠️",
            "critical": "🔴",
            "urgent": "🚨"
        }
        
        message = f"""
🤖 **AI Signal 확장성 알림**

📊 **현재 상태**
👥 사용자: {metrics['users']:,}명
💻 CPU: {metrics['cpu_percent']:.1f}%
🧠 메모리: {metrics['memory_percent']:.1f}%
💾 Redis: {metrics.get('redis_memory_mb', 0):.1f} MB
"""
        
        if not recommendations:
            message += "\n✅ 모든 시스템 정상 작동 중"
        else:
            message += f"\n⚡ **{len(recommendations)}개의 확장 제안**\n"
            
            for i, rec in enumerate(recommendations, 1):
                emoji = level_emoji.get(rec.level, "ℹ️")
                message += f"""
{emoji} **{rec.title}**
심각도: {rec.level.upper()}
예상 비용: {rec.estimated_cost}
타임라인: {rec.timeline}
"""
                
                if i < len(recommendations):
                    message += "\n---\n"
        
        return message.strip()
    
    def send_to_telegram(
        self,
        metrics: dict,
        recommendations: List[ScalingRecommendation]
    ) -> bool:
        """n8n 웹훅을 통해 텔레그램 전송"""
        
        message = self.format_message(metrics, recommendations)
        
        payload = {
            "message": message,
            "metrics": metrics,
            "recommendations": [
                {
                    "level": rec.level,
                    "title": rec.title,
                    "description": rec.description,
                    "cost": rec.estimated_cost,
                    "timeline": rec.timeline
                }
                for rec in recommendations
            ]
        }
        
        try:
            response = requests.post(
                self.n8n_webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            print(f"✅ 텔레그램 알림 전송 성공")
            return True
        except Exception as e:
            print(f"❌ 텔레그램 알림 전송 실패: {e}")
            return False


def send_scaling_alert(metrics: dict, recommendations: List[ScalingRecommendation]):
    """확장성 알림 전송 (메인 함수)"""
    notifier = TelegramNotifier()
    return notifier.send_to_telegram(metrics, recommendations)


if __name__ == "__main__":
    # 테스트
    from scaling_monitor import ScalingMonitor
    
    monitor = ScalingMonitor()
    metrics = monitor.get_system_metrics()
    recommendations = monitor.check_scaling_needs()
    
    send_scaling_alert(metrics, recommendations)
