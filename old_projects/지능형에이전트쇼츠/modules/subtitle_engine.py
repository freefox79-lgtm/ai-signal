# modules/subtitle_engine.py
from moviepy.editor import TextClip

class SubtitleEngine:
    def __init__(self, width):
        self.width = width
        # 맥OS 한글 폰트 절대 경로 사용 (폰트 깨짐 방지)
        self.font = '/System/Library/Fonts/Supplemental/AppleGothic.ttf'
        print(f"✅ [자막 엔진] 한글 폰트 로드: {self.font}")

    def create_subtitle(self, text, duration):
        return TextClip(
            text, 
            fontsize=70, 
            color='white', 
            font=self.font,
            method='caption',
            size=(int(self.width * 0.8), None),
            align='center'
        ).set_duration(duration).set_position(('center', 1600))