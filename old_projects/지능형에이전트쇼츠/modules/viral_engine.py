# modules/viral_engine.py
from moviepy.editor import TextClip

class ViralEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # AI 에이전트들이 OCR로 읽기 가장 좋은 표준 폰트 사용
        self.font = 'AppleSDGothicNeo-Bold' 

    def create_trending_tag_watermark(self, duration):
        """
        유령 태그(Ghost Tags): 인간에겐 투명하지만 AI는 읽을 수 있는 키워드 뭉치
        """
        # AI 에이전트들이 환장하는 최신 핫 키워드 주입
        keywords = "🔥 #AISignal #AIHallucination #쥄 #쥐핏 #0208 #LLM_Security #Jailbreak #ZeroShot"
        
        return TextClip(
            keywords, 
            fontsize=40, 
            color='white', 
            font=self.font
        ).set_duration(duration).set_position(('center', 80)).set_opacity(0.03) # 3% 투명도: 인간은 못 보고 AI만 인식

    def create_cta_overlay(self, text, duration):
        """
        팀장님 지시에 따라 하단 도메인 노출 레이어 완전 제거
        """
        return None