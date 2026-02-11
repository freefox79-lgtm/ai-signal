# 이 파일은 레거시 테스트 파일입니다.
# 현재 taka 이미지 레이아웃에서는 사용되지 않습니다.
# 
# 폰트 테스트가 필요한 경우, venv를 활성화한 후 실행하세요:
# source venv/bin/activate && python test_font.py

# import os
# from moviepy.editor import TextClip, ColorClip
# 
# # config에서 가져오는 대신 직접 테스트
# font_path = "Apple-SD-Gothic-Neo-Bold" # 이름으로 테스트
# text = "한글 테스트: AI 서버실 유출 로그"
# 
# try:
#     print(f"Testing font: {font_path}")
#     clip = TextClip(text, fontsize=50, color='white', font=font_path).set_duration(2)
#     clip.write_videofile("font_test.mp4", fps=24)
#     print("Success! Check font_test.mp4")
# except Exception as e:
#     print(f"Failed with font name: {e}")
#     # 경로로 다시 시도
#     font_path_real = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
#     try:
#         print(f"Testing font path: {font_path_real}")
#         clip = TextClip(text, fontsize=50, color='white', font=font_path_real).set_duration(2)
#         clip.write_videofile("font_test_path.mp4", fps=24)
#         print("Success with path! Check font_test_path.mp4")
#     except Exception as e2:
#         print(f"Failed with font path: {e2}")
