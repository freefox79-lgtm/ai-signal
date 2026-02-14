#!/usr/bin/env python3
"""
Telegram 알림 테스트 스크립트
n8n Webhook을 통해 Telegram으로 메시지 전송
"""
import requests

# n8n Webhook URL
webhook_url = "http://localhost:5678/webhook/scaling-alert"

# 테스트 메시지
test_message = """
🎉 **AI Signal 모니터링 시스템 테스트**

✅ Telegram Bot 연결 성공!
✅ n8n 워크플로우 활성화 완료!
✅ 하드웨어 모니터링 준비 완료!

**시스템 정보**:
- Mac Mini 하드웨어 모니터링: 활성
- 데이터 수집 워크플로우: 3개 활성화
- 알림 시스템: Telegram 연동 완료

다음 단계: scaling_monitor.py 실행 시 자동 알림 전송!
"""

# Webhook 호출
try:
    response = requests.post(webhook_url, json={"message": test_message})
    
    if response.status_code == 200:
        print("✅ Telegram 알림 전송 성공!")
        print(f"응답: {response.json()}")
    else:
        print(f"❌ 알림 전송 실패: {response.status_code}")
        print(f"응답: {response.text}")
except Exception as e:
    print(f"❌ 에러 발생: {e}")
