#!/usr/bin/env python3
"""
사용자가 제공한 캐릭터 시트 이미지를 직접 처리하여 9개로 분리
"""

from PIL import Image
import os
import sys

# 프로젝트 디렉토리
project_dir = "/Users/freefox79gmail.com/Desktop/프로젝트/쥄과쥐핏"

# 사용자에게 이미지 경로 안내
print("=" * 60)
print("캐릭터 시트 이미지 분리 스크립트")
print("=" * 60)
print()

# 가능한 입력 파일 경로들
possible_paths = [
    os.path.join(project_dir, "character_sheet.png"),
    os.path.join(project_dir, "characters.png"),
    os.path.join(project_dir, "sheet.png"),
    os.path.join(project_dir, "jwem_jfit.png"),
]

# 다운로드 폴더도 확인
downloads_dir = os.path.expanduser("~/Downloads")
download_images = [f for f in os.listdir(downloads_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
if download_images:
    # 가장 최근 이미지 파일 찾기
    download_images.sort(key=lambda x: os.path.getmtime(os.path.join(downloads_dir, x)), reverse=True)
    possible_paths.insert(0, os.path.join(downloads_dir, download_images[0]))

# 입력 파일 찾기
input_image = None
for path in possible_paths:
    if os.path.exists(path):
        input_image = path
        print(f"✅ 이미지 발견: {path}")
        break

if not input_image:
    print("❌ 캐릭터 시트 이미지를 찾을 수 없습니다!")
    print()
    print("다음 중 하나로 이미지를 저장해주세요:")
    for path in possible_paths[1:]:  # 다운로드 폴더 제외
        print(f"  - {path}")
    print()
    print("또는 명령줄 인자로 이미지 경로를 지정하세요:")
    print(f"  python {sys.argv[0]} <이미지_경로>")
    sys.exit(1)

# 명령줄 인자로 경로가 제공된 경우
if len(sys.argv) > 1:
    input_image = sys.argv[1]
    if not os.path.exists(input_image):
        print(f"❌ 오류: 파일을 찾을 수 없습니다: {input_image}")
        sys.exit(1)

# 출력 디렉토리
output_dir = os.path.join(project_dir, "character_actions")

# 이미지 로드
try:
    img = Image.open(input_image)
    width, height = img.size
    print(f"원본 이미지 크기: {width}x{height}")
except Exception as e:
    print(f"❌ 이미지 로드 실패: {e}")
    sys.exit(1)

# 3x3 그리드이므로 각 셀의 크기 계산
cell_width = width // 3
cell_height = height // 3

print(f"각 셀 크기: {cell_width}x{cell_height}")
print()

# 출력 디렉토리 생성
os.makedirs(output_dir, exist_ok=True)

# 9개 이미지 추출 (왼쪽에서 오른쪽, 위에서 아래)
act_num = 1
for row in range(3):
    for col in range(3):
        # 크롭 영역 계산
        left = col * cell_width
        top = row * cell_height
        right = left + cell_width
        bottom = top + cell_height
        
        # 이미지 크롭
        cropped = img.crop((left, top, right, bottom))
        
        # 파일명 생성 및 저장
        output_path = os.path.join(output_dir, f"act{act_num}.png")
        cropped.save(output_path, "PNG")
        
        print(f"✅ act{act_num}.png 저장 완료")
        act_num += 1

print()
print("=" * 60)
print(f"🎉 총 9개 이미지 분리 완료!")
print(f"📁 저장 위치: {output_dir}")
print("=" * 60)
print()
print("생성된 파일:")
for i in range(1, 10):
    print(f"  - act{i}.png")
