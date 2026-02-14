#!/usr/bin/env python3
"""
Telegram API 직접 테스트
n8n을 거치지 않고 Telegram API로 직접 메시지 전송
"""
import requests

BOT_TOKEN = "8530154370:AAFl-gtpuIZB5HJ_PVy6rAKqNggTxoYe8Aw"
CHAT_ID = "7971306014"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
data = {
    "chat_id": CHAT_ID,
    "text": "✅ **Telegram API 직접 테스트**\n\nn8n을 거치지 않고 직접 전송된 메시지입니다.",
    "parse_mode": "Markdown"
}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("\n✅ Telegram API 직접 전송 성공!")
        print("Telegram 앱에서 메시지를 확인하세요.")
    else:
        print(f"\n❌ 전송 실패: {response.json()}")
except Exception as e:
    print(f"❌ 에러: {e}")
