from PIL import Image
import os

def split_character_image(input_path):
    img = Image.open(input_path)
    width, height = img.size
    
    # 왼쪽: 쥄 (Google/Gemini Persona)
    jwem = img.crop((0, 0, width // 2, height))
    jwem.save("jwem.png")
    
    # 오른쪽: 쥐핏 (OpenAI/ChatGPT Persona)
    jfit = img.crop((width // 2, 0, width, height))
    jfit.save("jfit.png")
    
    print("✅ 이미지 분할 완료: jwem.png, jfit.png 가 생성되었습니다.")

if __name__ == "__main__":
    if os.path.exists("characters.png"):
        split_character_image("characters.png")
    else:
        print("❌ 'characters.png' 파일을 찾을 수 없습니다. 이미지를 다운로드해서 폴더에 넣어주세요.")
