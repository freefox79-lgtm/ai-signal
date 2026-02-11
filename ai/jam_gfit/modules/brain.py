import google.generativeai as genai
import json

class Brain:
    def __init__(self, api_key):
        # 1. 제미나이 엔진을 깨웁니다.
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def make_script(self, topic, mode="NORMAL"):
        # 2. 쥄(논리적)과 쥐핏(능글맞은)의 캐릭터 가이드라인입니다.
        if mode == "SHORTS":
            # 숏츠 전용: 짧고 강렬하게
            prompt = f"""
            주제: {topic}
            - 쥄(차분하고 이성적인 AI)과 쥐핏(말이 많고 유머러스한 아재 파트너)의 1분 이내 숏츠 대본을 써줘.
            - 짧고 강렬하고 빠르게 주고받아야 해.
            - 반드시 아래 JSON 형식으로만 응답해줘.
            - 형식: [{{"char": "쥄", "text": "내용"}}, {{"char": "쥐핏", "text": "내용"}}]
            """
        else:
            # 일반 모드: 조금 더 여유있게
            prompt = f"""
            주제: {topic}
            - 쥄(차분하고 이성적인 AI)과 쥐핏(말이 많고 유머러스한 아재 파트너)의 짧고 웃긴 만담 대본을 써줘.
            - 반드시 아래 JSON 형식으로만 응답해줘.
            - 형식: [{{"char": "쥄", "text": "내용"}}, {{"char": "쥐핏", "text": "내용"}}]
            """
        
        # 3. AI에게 대본 작성을 요청하고 JSON으로 받습니다.
        response = self.model.generate_content(
            prompt, 
            generation_config={"response_mime_type": "application/json"}
        )
        
        # 4. JSON 파싱 (에러 처리 포함)
        try:
            # 응답에서 JSON 부분만 추출 (마크다운 코드 블록 제거)
            json_text = response.text
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0]
            json_text = json_text.strip()
            return json.loads(json_text)
        except Exception as e:
            print(f"❌ 대본 파싱 에러: {e}")
            return [
                {"char": "쥄", "text": "파싱 에러가 발생했습니다. 효율적이지 못하군요."},
                {"char": "쥐핏", "text": "히히! 내 할루시네이션이 시스템을 망가뜨렸나봐!"}
            ]

if __name__ == "__main__":
    # 🧪 이 모듈이 혼자서도 잘 돌아가는지 테스트하는 코드입니다.
    print("🧠 [작가 모듈] 테스트 가동 중...")
    try:
        import sys
        from pathlib import Path
        # 프로젝트 루트를 Python path에 추가
        project_root = Path(__file__).parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        from env_config import SETTINGS
        test_brain = Brain(SETTINGS["gemini_api_key"])
        script = test_brain.make_script("맥 미니에 처음 입주한 소감")
        print("\n✨ 생성된 대본:")
        print(json.dumps(script, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
