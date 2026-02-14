# n8n Workflows for AI Signal

이 디렉토리에는 AI Signal 프로젝트의 자동 데이터 수집을 위한 n8n 워크플로우가 포함되어 있습니다.

## 📁 워크플로우 파일

### 1. `economic_indicators_daily.json`
- **스케줄**: 매일 09:00 KST
- **기능**: FRED API + Naver Finance 경제 지표 수집
- **데이터**: 금리, 인플레이션, 실업률, KOSPI, USD/KRW

### 2. `market_data_hourly.json`
- **스케줄**: 매시간 (시장 시간 체크)
- **기능**: 시장 지수 수집
- **데이터**: S&P 500, NASDAQ, KOSPI, Bitcoin
- **조건부 실행**: 한국장/미국장 개장 시간만 실행

### 3. `trend_collection_4h.json`
- **스케줄**: 4시간마다
- **기능**: SNS 및 커뮤니티 트렌드 수집
- **데이터**: 
  - SNS (4시간): X, Instagram
  - 커뮤니티 (6시간): DCInside, FMKorea, 더쿠, 루리웹, 클리앙
  - 쇼핑 (12시간): Hypebeast, Kream

## 🚀 n8n 설치 및 설정

### Docker로 n8n 실행
```bash
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### 워크플로우 import
1. n8n 웹 인터페이스 접속: http://localhost:5678
2. 좌측 메뉴에서 "Workflows" 클릭
3. "Import from File" 선택
4. 각 JSON 파일 import

## ⚙️ 환경 설정

### 1. Telegram 알림 설정 (선택사항)
n8n에서 Telegram credentials 추가:
- Bot Token: Telegram BotFather에서 생성
- Chat ID: 알림 받을 채팅방 ID

### 2. Redis 연결 확인
워크플로우는 Redis 캐시를 자동으로 삭제합니다:
```bash
redis-cli -a aisignal2026_secure PING
```

### 3. Python 스크립트 경로 수정
각 워크플로우의 "Execute Command" 노드에서 경로 확인:
```
/Users/freefox79gmail.com/개발프로젝트/ai/aisignal
```

## 📊 수집 스케줄 요약

| 시간 | 작업 |
|------|------|
| 00:00 | SNS 트렌드, 커뮤니티 트렌드 |
| 04:00 | SNS 트렌드 |
| 06:00 | 커뮤니티 트렌드 |
| 08:00 | SNS 트렌드 |
| 09:00 | **경제 지표 (FRED + Naver)**, 쇼핑 트렌드 |
| 10:00-15:00 | 시장 데이터 (매시간) |
| 12:00 | SNS 트렌드, 커뮤니티 트렌드 |
| 16:00 | SNS 트렌드 |
| 18:00 | 커뮤니티 트렌드 |
| 20:00 | SNS 트렌드 |
| 21:00 | 쇼핑 트렌드 |
| 23:00-06:00 | 시장 데이터 (매시간, 미국장) |

## 🧪 테스트

### 워크플로우 수동 실행
n8n에서 각 워크플로우의 "Execute Workflow" 버튼 클릭

### Python 스크립트 직접 실행
```bash
cd /Users/freefox79gmail.com/개발프로젝트/ai/aisignal
source venv/bin/activate

# 경제 지표
python scripts/collect_economic_data.py

# 시장 데이터
python scripts/collect_market_data.py

# SNS 트렌드
python scripts/collect_sns_trends.py

# 커뮤니티 트렌드
python scripts/collect_community_trends.py

# 쇼핑 트렌드
python scripts/collect_shopping_trends.py
```

## 📈 모니터링

### n8n 실행 로그
n8n 웹 인터페이스에서 각 워크플로우의 "Executions" 탭 확인

### Telegram 알림
성공/실패 알림이 Telegram으로 전송됨

### Redis 캐시 확인
```bash
redis-cli -a aisignal2026_secure KEYS "*"
redis-cli -a aisignal2026_secure GET "economic_indicators:20260214"
```

## ⚠️ 주의사항

1. **API Rate Limiting**
   - Alpha Vantage: 25 requests/day
   - FRED: 120 requests/min
   - 제한 초과 시 워크플로우 자동 중지

2. **서버 리소스**
   - Stealth Crawler는 CPU/메모리 사용
   - 동시 실행 제한 권장

3. **에러 처리**
   - 각 스크립트는 exit code 반환
   - 실패 시 Telegram 알림 발송

## 💡 향후 개선

- [ ] 데이터베이스 저장 추가
- [ ] 대시보드 통계 연동
- [ ] 에러 재시도 로직
- [ ] 성능 메트릭 수집
