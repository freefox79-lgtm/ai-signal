import os

# 프로젝트 루트 디렉토리 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SETTINGS = {
    "gemini_api_key": "AIzaSyCEcrkXKrfI3aehjLAZ7oMm2Ovrx54jIVk",
    "elevenlabs_api_key": "sk_0949db95c4b5bbd85e4da44f244b567d7066d4d8baf86991",
    "output_path": os.path.join(BASE_DIR, "outputs"),
    "jwem_voice_id": "O9O7ajUbTTkGHDhYAuba",  # 안정성 80% 권장
    "jfit_voice_id": "YPNGufGiEwSx2mXlRxky"   # 과장성 90% 권장
}
