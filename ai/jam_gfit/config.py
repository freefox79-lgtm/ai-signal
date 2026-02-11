import os

# 1. 경로 설정
OUT_DIR = "outputs"
EV_DIR = os.path.join(OUT_DIR, "evidence")
VOICE_DIR = os.path.join(OUT_DIR, "new_voices")
BGM_PATH = os.path.join(OUT_DIR, "bgm.mp3")

# 2. 폰트 설정 (안정적인 한글 렌더링을 위해 풀 경로 사용)
KOREAN_FONT = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"