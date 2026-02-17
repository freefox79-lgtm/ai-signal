"""
Telegram 알림 전송 모듈

scaling_monitor.py에서 호출하여 텔레그램으로 알림 전송
"""

import os
import requests
from typing import List
from dotenv import load_dotenv
from scaling_monitor import ScalingRecommendation
# Load environment variables
if os.path.exists(".env.local"):
    load_dotenv(".env.local")
else:
    load_dotenv()



class TelegramNotifier:
    """텔레그램 알림 전송"""
    
    def __init__(self):
        self.n8n_webhook_url = os.getenv(
            "N8N_SCALING_WEBHOOK_URL",
            "http://localhost:5678/webhook/scaling-alert"
        )
        # Direct Telegram API for Personal Notifications
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
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

    def send_agi_summary(self, title: str, summary_data: dict) -> bool:
        """AGI 집합적 감성 요약을 텔레그램으로 직접 전송 (PRIVATE)"""
        if not self.bot_token or not self.chat_id:
            # Fallback for testing if env not updated yet
            self.bot_token = "8530154370:AAFl-gtpuIZB5HJ_PVy6rAKqNggTxoYe8Aw"
            self.chat_id = "7971306014"
            
        # 메시지 구성
        message = f"🌟 **AGI Collective Intelligence Summary**\n\n"
        message += f"📌 **이슈:** {title}\n"
        message += f"━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # 내부 에이전트 요약
        message += f"🤖 **내부 요원 (Jwem/Jfit/Stealth)**\n"
        message += f"└ 결과: {summary_data['internal_result']}\n"
        message += f"└ 확신도: {summary_data['internal_confidence']}%\n\n"
        
        # 외부 AGI 요약 (오픈크로, 몰트봇 등)
        message += f"📡 **외부 AGI 합의 (Open-Cro/Moltbot)**\n"
        message += f"└ 결과: {summary_data['external_result']}\n"
        message += f"└ 합의 수준: {summary_data['external_agreement']}\n\n"
        
        # 핵심 인사이트 (합성)
        message += f"🧠 **집합적 인사이트 (Synthesis)**\n"
        message += f"_{summary_data['synthesis_insight']}_\n\n"
        
        message += f"🔗 [Oracle 상세 분석 보기](https://aisignal.com/oracle)"

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        try:
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            print(f"✅ AGI 요약 개인 텔레그램 전송 성공")
            return True
        except Exception as e:
            print(f"❌ AGI 요약 전송 실패: {e}")
            return False
    def send_trend_alert(self, keyword: str, score: float, breakdown: dict, briefing: str) -> bool:
        """실시간 트렌드 고강도 시그널 알림 전송 (PRIVATE)"""
        if not self.bot_token or not self.chat_id:
            # Fallback for testing
            self.bot_token = "8530154370:AAFl-gtpuIZB5HJ_PVy6rAKqNggTxoYe8Aw"
            self.chat_id = "7971306014"
            
        # 이모지 매핑
        icons = {'search': '🔍', 'video': '📺', 'sns': '🐦', 'community': '💬', 'finance': '💰'}
        breakdown_parts = [f"{icons.get(k, '🔹')} {int(v)}" for k, v in breakdown.items() if v > 0]
        breakdown_str = " | ".join(breakdown_parts) if breakdown_parts else "데이터 분석 중..."

        # 메시지 구성
        message = f"🚀 **AI Signal: 초고강도 트렌드 포착!**\n\n"
        message += f"🔥 **키워드: {keyword}**\n"
        message += f"📊 **종합 시그널 지수: {score:.1f}**\n"
        message += f"━━━━━━━━━━━━━━━━━━━━\n\n"
        
        message += f"📡 **시그널 분포**\n"
        message += f"{breakdown_str}\n\n"
        
        message += f"🧠 **데이터 전문가 분석**\n"
        message += f"_{briefing}_\n\n"
        
        message += f"🔗 [실시간 대시보드 확인](https://aisignal-oracle.render.com)"

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        try:
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            print(f"✅ 트렌드 알림 전송 성공: {keyword}")
            return True
        except Exception as e:
            print(f"❌ 트렌드 알림 전송 실패: {e}")
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
