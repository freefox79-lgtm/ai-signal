from moviepy import VideoFileClip, concatenate_videoclips
import os

def merge_scenes():
    video_dir = "outputs/videos"
    scene_files = ["scene_1.mp4", "scene_2.mp4", "scene_3.mp4", "scene_4.mp4"]
    
    clips = []
    for f in scene_files:
        path = os.path.join(video_dir, f)
        if os.path.exists(path):
            clips.append(VideoFileClip(path))
            print(f"📦 클립 로드 완료: {f}")

    if not clips:
        print("[에러] 합칠 영상이 없습니다!")
        return

    print("🎬 '쥄과쥐핏 EP.01' 통합본 렌더링 시작...")
    # method="compose"를 사용하면 오디오 레이어까지 안전하게 합쳐집니다. [cite: 2026-02-07]
    final_video = concatenate_videoclips(clips, method="compose")

    output_name = "쥄과쥐핏_EP01_최종본.mp4"
    final_video.write_videofile(
        output_name, 
        codec="libx264", 
        audio_codec="aac", 
        threads=8 # 안티그래비티 M4의 성능을 끝까지 활용합니다. [cite: 2026-02-02]
    )
    
    print(f"\n✨ [성공] 데뷔작이 완성되었습니다: {output_name}")

if __name__ == "__main__":
    merge_scenes()