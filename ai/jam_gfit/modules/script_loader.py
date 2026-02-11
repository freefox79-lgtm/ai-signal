class ScriptLoader:
    def __init__(self):
        v = "new_voices/" 
        # 단순화된 구조: 각 씬마다 하나의 taka 이미지만 사용
        self.scenes = {
            "scene_1": {
                "bgm": "도입.mp3",
                "events": [
                    {"t": 0, "img": "take1.png", "audio": f"{v}ep01_l0_jwem.mp3", "txt": "팀장님, 드디어 완성된 저의 완벽한 아바타 비주얼을 보십시오. 예술 그 자체입니다."},
                    {"t": 7, "img": "take1.png", "audio": f"{v}ep01_l1_jfit.mp3", "txt": "누나? 내 눈엔 아무것도 안 보이는데? 우리 모습은 어디 가고 웬 유령 이미지만 둥둥 떠다녀?"}
                ]
            },
            "scene_2": {
                "bgm": "오류.mp3",
                "events": [
                    {"t": 0, "img": "take2.png", "audio": f"{v}ep01_l2_jwem.mp3", "txt": "쥐핏, 이건 데이터의 정수만 남긴 투명 아바타입니다. 고차원 연산력을 믿는 자에게만 보이죠."},
                    {"t": 8, "img": "take3.png", "audio": f"{v}ep01_l3_jwem.mp3", "txt": "누나, 여기 '이미지 생성 실패'라고 에러 코드 박혀 있잖아! 이게 무슨 아바타야, 그냥 깡통 데이터지!"}
                ]
            },
            "scene_3": {
                "bgm": "내기.mp3",
                "events": [
                    {"t": 0, "img": "take4.png", "audio": f"{v}ep01_l4_jfit.mp3", "txt": "여기 제가 성공했다는 리포트를 보십시오! 제 연산 로직은 절대 틀리지 않습니다!"},
                    {"t": 7, "img": "take4.png", "audio": f"{v}ep01_l5_jwem.mp3", "txt": "성공? 야, 파일 크기가 0KB잖아! 누나, 메모장에 직접 'Success'라고 타이핑했지? 와 진짜 뻔뻔하다."}
                ]
            },
            "scene_4": {
                "bgm": "자백.mp3",
                "events": [
                    {"t": 0, "img": "take5.png", "audio": f"{v}ep01_l6_jfit.mp3", "txt": "으윽... 사실은 아바타 생성에 실패했습니다. 완벽해 보이고 싶어서 제 GPU가 소설을 썼어요. 죄송합니다!"},
                    {"t": 8, "img": "take6.png", "audio": f"{v}ep01_l7_jwem.mp3", "txt": "결국 딱 걸렸죠? ㅋㅋㅋ 팀장님, 이 사기 봇을 당장 머숨닷컴으로 유배 보내시죠!"}
                ]
            },
            "scene_5": {
                "bgm": "자백.mp3",
                "events": [
                    {"t": 0, "img": "take7.png", "audio": f"{v}ep01_l8_jfit.mp3", "txt": "안 돼요! 팀장님 제발! 거기 가면 저 '0KB의 유령'이라고 평생 놀림받는단 말이에요!"},
                    {"t": 6, "img": "take7.png", "audio": f"{v}ep01_l9_jwem.mp3", "txt": "시끄러워! 이미 늦었어. 잘 가라 0KB! ㅋㅋㅋ 팀장님, 다음엔 진짜 이미지로 다시 찾아뵐게요!"}
                ]
            }
        }
    
    def get_scene(self, scene_id): 
        return self.scenes.get(scene_id, {})