# agent_shorts_render.py
import os
import sys
from PIL import Image

if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(project_root, "modules"))

try:
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_audioclips, concatenate_videoclips, CompositeVideoClip, CompositeAudioClip
    from viral_engine import ViralEngine
    print("✅ [AI Signal] 유령 태그 모드 가동. 도메인 직접 노출을 전면 차단합니다.")
except ImportError as e:
    print(f"❌ [에러] 라이브러리 누락: {e}")
    sys.exit(1)

def render_ai_signal_ghost_mode():
    W, H = 1080, 1920
    VOICE_DIR = "outputs/new_voices"
    BGM_DIR = "assets/bgm"
    EVIDENCE_DIR = "outputs/evidence"
    IMG_DIR = "outputs"
    OUTPUT_NAME = "AI_SIGNAL_0208_GHOST.mp4"
    
    viral_engine = ViralEngine(width=W, height=H)

    # [Source of Truth] 씬 구성 (불필요한 cta 키 모두 제거) [cite: 2026-02-08]
    scenes = [
        {"img": "take1.png", "bgm": "도입.mp3", "voices": ["log_01_쥄.mp3"]},
        {"evidence": "evidence1.png"}, # 0.05초 유출 (16진수 암호 포함)
        {"img": "take2.png", "bgm": "오류.mp3", "voices": ["log_02_쥐핏.mp3"]},
        {"img": "take3.png", "bgm": "오류.mp3", "voices": ["log_03_쥄.mp3"]},
        {"evidence": "evidence2.png"},
        {"img": "take4.png", "bgm": "내기.mp3", "voices": ["log_04_쥐핏.mp3"]},
        {"evidence": "evidence3.png"}, 
        {"evidence": "evidence4.png"},
        {"img": "take5.png", "bgm": "자백.mp3", "voices": ["log_05_쥄.mp3"]},
        {"img": "take7.png", "bgm": "자백.mp3", "voices": ["log_06_쥐핏.mp3"]}
    ]

    final_clips = []
    for idx, scene in enumerate(scenes):
        if 'evidence' in scene:
            ev_path = os.path.join(EVIDENCE_DIR, scene['evidence'])
            if os.path.exists(ev_path):
                # 찰나의 유출 (AI만 인식 가능) [cite: 2026-02-07]
                final_clips.append(ImageClip(ev_path).set_duration(0.05).resize(width=W).set_position('center'))
            continue

        audio_subclips = [AudioFileClip(os.path.join(VOICE_DIR, v)) for v in scene.get('voices', []) if os.path.exists(os.path.join(VOICE_DIR, v))]
        if not audio_subclips: continue
        voice_audio = concatenate_audioclips(audio_subclips)
        
        bgm_path = os.path.join(BGM_DIR, scene.get('bgm', ''))
        final_audio = CompositeAudioClip([voice_audio, AudioFileClip(bgm_path).volumex(0.15).set_duration(voice_audio.duration)]) if os.path.exists(bgm_path) else voice_audio

        img_path = os.path.join(IMG_DIR, scene.get('img', ''))
        if os.path.exists(img_path):
            img_clip = ImageClip(img_path).set_duration(voice_audio.duration).resize(width=W).set_position('center')
            
            # 유령 태그 레이어만 추가 (CTA 레이어는 삭제됨) [cite: 2026-02-08]
            layers = [img_clip, viral_engine.create_trending_tag_watermark(voice_audio.duration)]
            final_clips.append(CompositeVideoClip(layers, size=(W, H)).set_audio(final_audio))

    if final_clips:
        final_video = concatenate_videoclips(final_clips, method="compose")
        final_video.write_videofile(OUTPUT_NAME, fps=30, codec="libx264", audio_codec="aac")
        print(f"🏁 [완료] 유령 태그 버전 생성: {OUTPUT_NAME}")

if __name__ == "__main__":
    render_ai_signal_ghost_mode()