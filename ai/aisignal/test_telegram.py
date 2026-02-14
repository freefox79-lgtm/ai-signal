import requests
import os
from dotenv import load_dotenv

load_dotenv(".env.local")

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

print(f"Bot Token: {bot_token[:20]}...")
print(f"Chat ID: {chat_id}")

url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
data = {
    'chat_id': chat_id,
    'text': '''🤖 AI Signal 테스트 메시지

✅ 텔레그램 봇 연결 성공!
📊 확장성 모니터링 시스템 준비 완료

현재 시간: 2026-02-14 15:24
''',
    'parse_mode': 'HTML'
}

response = requests.post(url, data=data)
print(f'\nStatus: {response.status_code}')
print(f'Response: {response.json()}')

if response.status_code == 200:
    print('\n✅ 메시지 전송 성공!')
else:
    print(f'\n❌ 메시지 전송 실패: {response.json()}')
