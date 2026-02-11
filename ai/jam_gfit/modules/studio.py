import os
from moviepy import ImageClip, CompositeVideoClip, AudioFileClip, TextClip, ColorClip, concatenate_audioclips

class Studio:
    def __init__(self, output_path):
        self.output_path = output_path

    def create_video(self, script, audio_files, final_name, mode="SHORTS"):
        # 1. 규격 설정 (9:16 쇼츠 vs 16:9 정보성)
        target_size = (1080, 1920) if mode == "SHORTS" else (1920, 1080)
        clips = []
        
        # 2. 오디오 클립들을 미리 로드
        audio_clips = [AudioFileClip(a) for a in audio_files]
        total_duration = sum([a.duration for a in audio_clips])
        
        # 3. 배경 생성 (어두운 배경)
        bg = ColorClip(size=target_size, color=(15, 15, 25)).with_duration(total_duration)
        clips.append(bg)

        current_time = 0
        for i, (line, audio_clip) in enumerate(zip(script, audio_clips)):
            dur = audio_clip.duration
            char = line["char"]
            text = line["text"]

            # 4. 캐릭터 이미지 로드 (프로젝트 루트 또는 outputs 폴더)
            img_name = "jwem.png" if char == "쥄" else "jfit.png"
            
            # 여러 위치에서 이미지 찾기
            possible_paths = [
                img_name,  # 프로젝트 루트
                os.path.join(self.output_path, img_name),  # outputs 폴더
                os.path.join(os.path.dirname(os.path.dirname(__file__)), img_name)  # 상위 폴더
            ]
            
            img_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    img_path = path
                    break
            
            if not img_path:
                print(f"⚠️ {img_name} 이미지를 찾을 수 없습니다! 다음 위치를 확인하세요:")
                for p in possible_paths:
                    print(f"   - {p}")
                current_time += dur
                continue

            char_clip = ImageClip(img_path).with_duration(dur).with_start(current_time)

            # 5. 만화적 연출(FX) 적용
            if char == "쥄":
                # 쥄: 논리적 줌인 (서서히 커짐)
                char_clip = char_clip.resized(lambda t: 1.0 + 0.05 * t).with_position(('center', 450))
            else:
                # 쥐핏: 킹받는 글리치 셰이크 (좌우 흔들림)
                char_clip = char_clip.with_position(lambda t: ('center', 450 + (10 if (t*10)%2 < 1 else -10)))

            # 6. 말풍선 스타일 자막 연출 (한글 지원)
            # macOS에서 한글을 지원하는 폰트 사용
            txt_clip = TextClip(
                text=text,
                font_size=60,
                color='yellow' if char=="쥐핏" else 'white',
                font='AppleGothic',  # macOS 기본 한글 폰트
                method='caption',
                size=(950, None),
                stroke_color='black',
                stroke_width=3
            )
            txt_clip = txt_clip.with_duration(dur).with_start(current_time).with_position(('center', 1500))

            clips.extend([char_clip, txt_clip])
            current_time += dur

        # 7. 최종 렌더링
        final_video = CompositeVideoClip(clips, size=target_size)
        
        # 8. 오디오 합성
        final_audio = concatenate_audioclips(audio_clips)
        final_video = final_video.with_audio(final_audio)
        
        output_full_path = os.path.join(self.output_path, final_name)
        final_video.write_videofile(output_full_path, fps=24, codec="libx264", audio_codec="aac")
        
        print(f"✅ [쥄과쥐핏] 영상 제작 완료: {output_full_path}")