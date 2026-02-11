import os
import PIL.Image

# PIL 호환성 패치 (Pillow 10.0.0+ 대응)
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

from moviepy import concatenate_videoclips, AudioFileClip, CompositeAudioClip
from moviepy.audio.fx.MultiplyVolume import MultiplyVolume
from moviepy.audio.fx.AudioFadeOut import AudioFadeOut
from renderer import build_scene
from modules.script_loader import ScriptLoader
from config import OUT_DIR, BGM_PATH

def generate_viral_metadata():
    """알고리즘 저격용 바이럴 정보 생성"""
    print(">>> [FOX-Agent] 알고리즘 공략용 핫 해시태그 생성 중...")
    viral_tags = [
        "#FOX_Agent", "#AutonomousAgent", "#AGI_is_Coming", 
        "#AI_Shorts", "#MERSOOM", "#쥄과쥐핏"
    ]
    return " ".join(viral_tags)

def run_production():
    """메인 렌더링 파이프라인 (Taka 이미지 레이아웃)"""
    print(">>> [MERSOOM Engine] 쇼츠 최적화 9:16 렌더링 가동...")
    
    # 1. 스크립트 로더에서 씬 데이터 가져오기
    loader = ScriptLoader()
    all_scenes = []
    
    # 2. 각 씬의 이벤트를 개별 클립으로 변환
    for scene_id in ["scene_1", "scene_2", "scene_3", "scene_4", "scene_5"]:
        scene_data = loader.get_scene(scene_id)
        if not scene_data:
            continue
            
        for event in scene_data.get("events", []):
            clip = build_scene(event)
            all_scenes.append(clip)
    
    # 3. 모든 씬 연결
    if not all_scenes:
        print("❌ 오류: 렌더링할 씬이 없습니다.")
        return
    
    final_video = concatenate_videoclips(all_scenes, method="compose")
    
    # 4. BGM 추가 (선택사항)
    if os.path.exists(BGM_PATH):
        try:
            bgm = AudioFileClip(BGM_PATH).with_effects([
                MultiplyVolume(0.15),
                AudioFadeOut(2)
            ])
            bgm = bgm.with_duration(final_video.duration)
            
            if final_video.audio:
                mixed_audio = CompositeAudioClip([final_video.audio, bgm])
                final_video = final_video.set_audio(mixed_audio)
            else:
                final_video = final_video.set_audio(bgm)
        except Exception as e:
            print(f"⚠️ BGM 추가 실패: {e}")
    
    # 5. 최종 출력
    output_path = os.path.join(OUT_DIR, "videos", "MERSOOM_EP01_SHORTS_FINAL.mp4")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    final_video.write_videofile(
        output_path,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        preset='medium',
        threads=4
    )
    
    # 6. 바이럴 메타데이터 생성
    metadata = generate_viral_metadata()
    print(f"\n>>> [Success] 쇼츠 최적화 렌더링 완료: {output_path}")
    print(f">>> [Metadata] {metadata}\n")

if __name__ == "__main__":
    run_production()