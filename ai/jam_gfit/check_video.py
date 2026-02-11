#!/usr/bin/env python3
"""
영상 파일의 오디오 트랙을 확인하고 테스트하는 스크립트
"""
from moviepy import VideoFileClip
import os

def check_video_audio(video_path):
    """영상 파일의 오디오 정보를 확인합니다."""
    print(f"🔍 영상 파일 분석 중: {video_path}\n")
    
    if not os.path.exists(video_path):
        print(f"❌ 파일을 찾을 수 없습니다: {video_path}")
        return
    
    try:
        # 영상 파일 로드
        video = VideoFileClip(video_path)
        
        print("📊 영상 정보:")
        print(f"   - 파일 크기: {os.path.getsize(video_path) / 1024 / 1024:.2f} MB")
        print(f"   - 영상 길이: {video.duration:.2f}초")
        print(f"   - 해상도: {video.size}")
        print(f"   - FPS: {video.fps}")
        
        # 오디오 트랙 확인
        if video.audio is None:
            print("\n❌ 오디오 트랙이 없습니다!")
            print("   → 영상 파일에 오디오가 포함되지 않았습니다.")
            print("   → 이것은 파일 오류입니다 (스피커 문제 아님)")
        else:
            print("\n✅ 오디오 트랙이 존재합니다!")
            print(f"   - 오디오 길이: {video.audio.duration:.2f}초")
            print(f"   - 샘플레이트: {video.audio.fps} Hz")
            print(f"   - 채널 수: {video.audio.nchannels}")
            
            # 오디오 추출 테스트
            print("\n🎵 오디오 추출 테스트 중...")
            test_audio_path = "./outputs/test_extracted_audio.mp3"
            video.audio.write_audiofile(test_audio_path)
            
            if os.path.exists(test_audio_path):
                test_size = os.path.getsize(test_audio_path)
                print(f"✅ 오디오 추출 성공: {test_audio_path} ({test_size / 1024:.2f} KB)")
                print(f"\n💡 테스트 방법:")
                print(f"   1. 추출된 오디오 파일을 재생해보세요:")
                print(f"      open {test_audio_path}")
                print(f"   2. 이 파일에서 소리가 들리면 → 원본 영상의 오디오는 정상입니다")
                print(f"   3. 이 파일에서도 소리가 안 들리면 → 스피커/볼륨 문제일 수 있습니다")
            else:
                print("❌ 오디오 추출 실패")
        
        video.close()
        
    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    video_file = "./outputs/쥄과쥐핏_만담.mp4"
    check_video_audio(video_file)
    
    # 개별 오디오 파일도 확인
    print("\n" + "="*60)
    print("📁 개별 음성 파일 확인:")
    print("="*60)
    
    audio_files = [f"./outputs/line_{i}.mp3" for i in range(6)]
    for audio_file in audio_files:
        if os.path.exists(audio_file):
            size = os.path.getsize(audio_file) / 1024
            print(f"✅ {audio_file}: {size:.2f} KB")
        else:
            print(f"❌ {audio_file}: 파일 없음")
