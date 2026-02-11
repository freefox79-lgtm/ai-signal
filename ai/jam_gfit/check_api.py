import requests
from env_config import SETTINGS

def check_elevenlabs_api():
    """ElevenLabs API 키 상태를 확인합니다."""
    api_key = SETTINGS["elevenlabs_api_key"]
    
    # 1. 사용자 정보 확인 (권한 확인)
    print("🔍 ElevenLabs API 키 확인 중...\n")
    
    headers = {
        "xi-api-key": api_key
    }
    
    # 사용자 정보 조회
    user_url = "https://api.elevenlabs.io/v1/user"
    response = requests.get(user_url, headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        print("✅ API 키가 유효합니다!")
        print(f"\n📊 계정 정보:")
        print(f"   - 구독 플랜: {user_data.get('subscription', {}).get('tier', 'Unknown')}")
        print(f"   - 남은 문자 수: {user_data.get('subscription', {}).get('character_count', 0):,}")
        print(f"   - 문자 제한: {user_data.get('subscription', {}).get('character_limit', 0):,}")
        
        # 2. 사용 가능한 음성 목록 확인
        voices_url = "https://api.elevenlabs.io/v1/voices"
        voices_response = requests.get(voices_url, headers=headers)
        
        if voices_response.status_code == 200:
            voices = voices_response.json().get('voices', [])
            print(f"\n🎤 사용 가능한 음성: {len(voices)}개")
            
            # 설정된 voice_id가 있는지 확인
            jwem_id = SETTINGS["jwem_voice_id"]
            jfit_id = SETTINGS["jfit_voice_id"]
            
            voice_ids = [v['voice_id'] for v in voices]
            
            if jwem_id in voice_ids:
                print(f"   ✅ 쥄 음성 ID 확인됨: {jwem_id}")
            else:
                print(f"   ❌ 쥄 음성 ID 없음: {jwem_id}")
                
            if jfit_id in voice_ids:
                print(f"   ✅ 쥐핏 음성 ID 확인됨: {jfit_id}")
            else:
                print(f"   ❌ 쥐핏 음성 ID 없음: {jfit_id}")
                
    else:
        print(f"❌ API 키 오류!")
        print(f"   상태 코드: {response.status_code}")
        print(f"   응답: {response.text}")
        
        if response.status_code == 401:
            print("\n💡 해결 방법:")
            print("   1. ElevenLabs 대시보드에서 새 API 키를 발급받으세요")
            print("   2. https://elevenlabs.io/app/settings/api-keys")
            print("   3. env_config.py의 'elevenlabs_api_key'를 업데이트하세요")

if __name__ == "__main__":
    check_elevenlabs_api()
