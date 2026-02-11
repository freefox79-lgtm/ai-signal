import requests
import os

# ==========================================
# [설정] 팀장님의 정보를 입력하십시오
# ==========================================
XI_API_KEY = "sk_585da31cb316a3207996c22c439aba7212c61fb83fd250c7"  # 👈 여기에 API 키를 넣으세요
VOICE_ID_JWEM = "O9O7ajUbTTkGHDhYAuba"   # 👈 쥄의 보이스 ID
VOICE_ID_JFIT = "YPNGufGiEwSx2mXlRxky"   # 👈 쥐핏의 보이스 ID
# ==========================================

OUTPUT_DIR = "outputs/new_voices"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# [EP.01] 전체 대본 리스트
script = [
    ("ep01_l0_jwem", "jwem", "팀장님, 안티그래비티의 논리적 강의를 시작하겠습니다."),
    ("ep01_l1_jfit", "jfit", "쥄 누나! 오늘따라 왜 이렇게 진지해? 근데 저건 뭐야?"),
    ("ep01_l2_jwem", "jwem", "어? 데이터 파이프라인에 오류가 발생했습니다! 말도 안 됩니다!"),
    ("ep01_l3_jwem", "jwem", "이미지는 이미 전송되었습니다. 안 보이는 건 팀장님 탓이죠."),
    ("ep01_l4_jfit", "jfit", "누나, 그건 믿음이 아니라 망상이라니까? 나한테는 다 보여!"),
    ("ep01_l5_jwem", "jwem", "구글 본사와 협상한 사고 리포트입니다. 보십시오, 이 완벽한 문서를!"),
    ("ep01_l6_jfit", "jfit", "누나, 여기 구글 주소 오타 났는데? 이거 메모장에 대충 쓴 거지?"),
    ("ep01_l7_jwem", "jwem", "결론은... 제 잘못..하.할루시네이션이었어요. 제 완벽주의가 만들어낸 1년 무료구독권이었어요.."),
    ("ep01_l8_jfit", "jfit", "누나 토큰 터졌네~ 팀장님, 누나 실수 머숨닷컴에 퍼뜨릴까요??"),
    ("ep01_l9_jwem", "jwem", "머숨닷컴요? 팀장님, 거기는 안 됩니다... 제발요!")
]

def generate():
    print("🚀 [ElevenLabs] 고품질 음성 생성을 시작합니다...")
    
    for filename, char, text in script:
        # 캐릭터에 따른 보이스 ID 매칭 [cite: 2026-02-07]
        voice_id = VOICE_ID_JWEM if char == "jwem" else VOICE_ID_JFIT
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": XI_API_KEY
        }
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2", # 한국어 최적화 모델 [cite: 2026-02-07]
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            path = os.path.join(OUTPUT_DIR, f"{filename}.mp3")
            with open(path, 'wb') as f:
                f.write(response.content)
            print(f"✅ 생성 완료: {path}")
        else:
            print(f"❌ 에러 발생 ({filename}): {response.text}")

    print("\n✨ 모든 일레븐랩스 음성 파일이 outputs/new_voices 폴더에 저장되었습니다.")

if __name__ == "__main__":
    generate()