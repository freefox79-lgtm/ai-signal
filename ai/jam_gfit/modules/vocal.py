import os
from elevenlabs.client import ElevenLabs

class Vocal:
    def __init__(self, api_key, jwem_id, jfit_id):
        self.client = ElevenLabs(api_key=api_key)
        self.voices = {
            "쥄": jwem_id,
            "쥐핏": jfit_id
        }

    def generate_voice(self, script, output_path):
        audio_paths = []
        print("🎙️ [쥄과쥐핏] 커스텀 보이스 합성 시작...")
        
        for i, line in enumerate(script):
            char = line["char"]
            text = line["text"]
            voice_id = self.voices.get(char)
            
            # 보이스별 최적 설정 적용
            stability = 0.8 if char == "쥄" else 0.35
            similarity = 0.75
            style = 0.0 if char == "쥄" else 0.9
            
            # ElevenLabs SDK의 올바른 API 사용
            audio_generator = self.client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id="eleven_multilingual_v2",
                voice_settings={
                    "stability": stability,
                    "similarity_boost": similarity,
                    "style": style
                }
            )
            
            # 오디오 스트림을 파일로 저장
            file_name = f"line_{i}_{char}.mp3"
            full_path = os.path.join(output_path, file_name)
            
            with open(full_path, 'wb') as f:
                for chunk in audio_generator:
                    f.write(chunk)
            
            audio_paths.append(full_path)
            print(f"✅ {char} 보이스 생성 완료: {file_name}")
            
        return audio_paths