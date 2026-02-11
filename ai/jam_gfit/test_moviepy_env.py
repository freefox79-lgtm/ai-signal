#!/usr/bin/env python3
"""MoviePy 환경 진단 스크립트 - 맥미니 전용"""

import sys
import os

print("=" * 60)
print("🔍 MoviePy 환경 진단 (Mac Mini)")
print("=" * 60)

# 1. Python 버전
print(f"\n✓ Python: {sys.version}")

# 2. MoviePy 버전 및 위치
try:
    import moviepy
    print(f"✓ MoviePy: {moviepy.__version__}")
    print(f"  위치: {moviepy.__file__}")
except ImportError as e:
    print(f"❌ MoviePy import 실패: {e}")
    sys.exit(1)

# 3. FFmpeg 확인
try:
    from moviepy.config import FFMPEG_BINARY
    print(f"✓ FFmpeg: {FFMPEG_BINARY}")
    if not os.path.exists(FFMPEG_BINARY):
        print(f"  ⚠️  경고: FFmpeg 파일이 존재하지 않습니다!")
except Exception as e:
    print(f"❌ FFmpeg 설정 오류: {e}")

# 4. ImageMagick 확인 (TextClip용)
try:
    from moviepy.config import IMAGEMAGICK_BINARY
    print(f"✓ ImageMagick: {IMAGEMAGICK_BINARY}")
    if IMAGEMAGICK_BINARY == "auto-detect":
        print("  ⚠️  ImageMagick이 자동 감지 모드입니다. TextClip 사용 시 오류 가능성 있음")
except Exception as e:
    print(f"⚠️  ImageMagick 설정 확인 불가: {e}")

# 5. 기본 클립 생성 테스트
print("\n--- 기능 테스트 ---")

try:
    from moviepy import ColorClip
    clip = ColorClip(size=(100, 100), color=(255, 0, 0), duration=1)
    print("✅ ColorClip 생성 성공")
    clip.close()
except Exception as e:
    print(f"❌ ColorClip 생성 실패: {e}")

# 6. Import 방식 확인
print("\n--- Import 방식 확인 ---")

# MoviePy 2.x 방식
try:
    from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
    print("✅ MoviePy 2.x 방식 import 성공")
except ImportError as e:
    print(f"❌ MoviePy 2.x import 실패: {e}")

# MoviePy 1.x 방식 (호환성 확인)
try:
    from moviepy.editor import VideoFileClip as VFC_old
    print("✅ MoviePy 1.x (moviepy.editor) 방식도 지원됨")
except ImportError:
    print("⚠️  moviepy.editor 모듈 없음 (MoviePy 2.x 전용)")

# 7. PIL/Pillow 확인
try:
    import PIL.Image
    print(f"\n✓ Pillow: {PIL.__version__}")
    if hasattr(PIL.Image, 'ANTIALIAS'):
        print("  ✓ ANTIALIAS 속성 존재 (패치 적용됨 또는 구버전)")
    else:
        print("  ⚠️  ANTIALIAS 속성 없음 (Pillow 10.0+, 패치 필요)")
except ImportError as e:
    print(f"❌ Pillow import 실패: {e}")

print("\n" + "=" * 60)
print("진단 완료!")
print("=" * 60)
