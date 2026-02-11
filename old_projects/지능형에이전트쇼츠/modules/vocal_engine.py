# modules/vocal_engine.py
import os
import requests
from env_config import ELEVENLABS_API_KEY, VOICE_IDS

class VocalEngine:
    def __init__(self):
        self.api_key = ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1/text-to-speech"

    def generate_voice(self, text, speaker, output_path):
        """
        ElevenLabs API를 호출하여 텍스트를 음성 파일로 변환합니다.
        """
        voice_id = VOICE_IDS.get(speaker)
        if not voice_id:
            print(f"❌ 오류: {speaker}에 해당하는 보이스 ID가 없습니다.")
            return

        url = f"{self.base_url}/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5, 
                "similarity_boost": 0.75
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ 생성 완료: {output_path}")
            else:
                print(f"❌ API 오류 ({speaker}): {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ 시스템 오류 발생: {e}")