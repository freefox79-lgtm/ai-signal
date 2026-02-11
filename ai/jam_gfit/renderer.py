import os
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip, ColorClip, AudioFileClip
from config import KOREAN_FONT, OUT_DIR, VOICE_DIR

def build_scene(entry):
    """단순화된 씬 빌더: taka 이미지를 9:16 화면에 표시"""
    voice_path = os.path.join(VOICE_DIR, entry.get('audio', ''))
    audio = AudioFileClip(voice_path) if os.path.exists(voice_path) else None
    dur = audio.duration if audio else 3.0

    # 1. Taka 이미지 로드 (9:16 비율로 리사이즈)
    img_path = os.path.join(OUT_DIR, entry.get('img', 'take1.png'))
    
    if os.path.exists(img_path):
        # 이미지를 1080x1920 (9:16) 크기에 맞춰 리사이즈
        main_image = ImageClip(img_path).set_duration(dur)
        
        # 이미지 비율 유지하며 화면에 맞추기
        img_w, img_h = main_image.w, main_image.h
        target_w, target_h = 1080, 1920
        
        # 화면을 꽉 채우도록 리사이즈 (crop 방식)
        scale = max(target_w / img_w, target_h / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        
        # width 또는 height 파라미터를 사용하여 리사이즈 (PIL 호환성 개선)
        if new_w > new_h:
            main_image = main_image.resize(width=new_w)
        else:
            main_image = main_image.resize(height=new_h)
        
        # 중앙 정렬
        main_image = main_image.set_position('center')
    else:
        # 이미지가 없으면 검은 배경
        main_image = ColorClip(size=(1080, 1920), color=(0, 0, 0)).set_duration(dur)

    # 2. 배경 (검은색)
    bg = ColorClip(size=(1080, 1920), color=(0, 0, 0)).set_duration(dur)

    # 3. 상단 타이틀
    title = TextClip("AI 서버실 유출 로그 EP.01", fontsize=60, color='white', font=KOREAN_FONT,
                     method='caption', size=(1000, None), align='center',
                     stroke_color='#00FFFF', stroke_width=2).set_duration(dur).set_position(('center', 100))

    # 4. 하단 자막
    subtitle = TextClip(entry.get('txt', ''), fontsize=52, color='white', font=KOREAN_FONT,
                       method='caption', size=(1000, None), align='center',
                       stroke_color='black', stroke_width=2).set_duration(dur).set_position(('center', 1700))

    # 5. 최종 합성
    final_clip = CompositeVideoClip([
        bg,
        main_image,
        title,
        subtitle
    ], size=(1080, 1920))

    return final_clip.set_audio(audio) if audio else final_clip