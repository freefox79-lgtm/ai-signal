from moviepy import ImageClip, TextClip, CompositeVideoClip, ColorClip, AudioFileClip, CompositeAudioClip
from moviepy.audio.fx.MultiplyVolume import MultiplyVolume
import os

class VisualEngine:
    def __init__(self, folder="outputs/"):
        self.folder = folder
        self.width = 1920
        self.height = 1080
        # 3x3 그리드 계산 (1920/3 = 640, 1080/3 = 360)
        self.cell_w = self.width // 3
        self.cell_h = self.height // 3
        self.margin = 0.15  # 팀장님이 강조하신 15% 여백 [cite: 2026-02-07]
        self.default_font = '/System/Library/Fonts/Supplemental/AppleGothic.ttf'

    def find_file(self, filename):
        search_paths = [self.folder, os.path.join(self.folder, "evidence"), 
                        os.path.join(self.folder, "new_voices"), "assets/bgm", "./"]
        for path in search_paths:
            full_path = os.path.join(path, filename)
            if os.path.exists(full_path): return full_path
        return None

    def apply_zoom_effect(self, clip, duration):
        """증거 이미지를 강조하기 위해 서서히 줌인되는 효과를 줍니다. [cite: 2026-02-07]"""
        return clip.resize(lambda t: 1.0 + 0.2 * (t / duration)).set_position('center')

    def render_scene(self, scene_id, script_data):
        clips = []
        audio_clips = []
        
        # 1. 배경 (서버룸 bg.jpg) [cite: 2026-02-07]
        bg_path = self.find_file("bg.jpg")
        bg = ImageClip(bg_path).set_duration(30).resize(newsize=(self.width, self.height))
        clips.append(bg)

        # 2. BGM
        bgm_path = self.find_file(script_data.get("bgm", ""))
        if bgm_path:
            audio_clips.append(AudioFileClip(bgm_path).with_effects([MultiplyVolume(0.2)]).with_duration(30))

        for event in script_data.get("events", []):
            img_path = self.find_file(event["img"])
            voice_path = self.find_file(event["audio"])
            
            if img_path and voice_path:
                voice = AudioFileClip(voice_path).set_start(event["t"])
                audio_clips.append(voice)
                dur = voice.duration
                
                # [9분할 레이아웃 배치] [cite: 2026-02-07]
                if event["char"] == "evidence":
                    # 상단 6칸(2/3 지점)에 크게 배치 및 줌인 이펙트 [cite: 2026-02-07]
                    ev_w = int(self.width * (1 - self.margin))
                    ev_h = int((self.height * 2/3) * (1 - self.margin))
                    ev = ImageClip(img_path).set_start(event["t"]).set_duration(dur).resize(height=ev_h)
                    
                    # 줌인 효과 적용 [cite: 2026-02-07]
                    ev = self.apply_zoom_effect(ev, dur)
                    # 상단 2/3 영역의 중앙에 배치
                    clips.append(ev.set_position(('center', self.height * 0.05)))
                    
                elif event["char"] == "jwem":
                    # 가장 왼쪽 하단 (Grid: 2,0) [cite: 2026-02-07]
                    jwem = ImageClip(img_path).set_start(event["t"]).set_duration(dur).resize(width=self.cell_w * 0.8)
                    clips.append(jwem.set_position((self.cell_w * 0.1, self.cell_h * 2 + 20)))
                    
                elif event["char"] == "jfit":
                    # 가장 오른쪽 하단 (Grid: 2,2) [cite: 2026-02-07]
                    jfit = ImageClip(img_path).set_start(event["t"]).set_duration(dur).resize(width=self.cell_w * 0.8)
                    clips.append(jfit.set_position((self.cell_w * 2.1, self.cell_h * 2 + 20)))
                
                # 자막 (하단 중앙 칸 Grid: 2,1) [cite: 2026-02-07]
                txt = TextClip(event["txt"], fontsize=45, color='white', font=self.default_font,
                               method='caption', size=(self.cell_w * 0.9, None), bg_color='black').set_opacity(0.8)
                clips.append(txt.set_duration(dur).set_start(event["t"]).set_position(('center', 0.82), relative=True))

        final = CompositeVideoClip(clips, size=(self.width, self.height))
        if audio_clips: final = final.set_audio(CompositeAudioClip(audio_clips))
        return final