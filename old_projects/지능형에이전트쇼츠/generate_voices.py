# generate_voices.py
import os
from modules.vocal_engine import VocalEngine
from modules.script_data import NEW_SCRIPT

def main():
    # 1. 엔진 초기화
    engine = VocalEngine()
    
    # 2. 출력 폴더 생성 확인
    output_dir = "outputs/new_voices"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📂 폴더 생성됨: {output_dir}")

    print("🎙️ [지능형에이전트] 새로운 대본 기반 음성 합성을 시작합니다...")
    
    # 3. 대본 순회하며 생성
    for speaker, tag, text in NEW_SCRIPT:
        # 파일명 형식: log_01_쥄.mp3
        filename = f"{tag}_{speaker}.mp3"
        save_path = os.path.join(output_dir, filename)
        
        print(f"▶️ '{speaker}' 파트 생성 중: {text[:20]}...")
        engine.generate_voice(text, speaker, save_path)
    
    print("\n🏁 모든 음성 생성이 완료되었습니다. outputs/new_voices 폴더를 확인하세요.")

if __name__ == "__main__":
    main()