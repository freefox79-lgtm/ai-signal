# 🛰️ AI SIGNAL: REAL-TIME HQ

네이버 실검, 쇼핑 트렌드, 바이럴 밈을 실시간으로 분석하는 AI 시그널 대시보드

## 🚀 주요 기능

- **하이브리드 인프라**: MOCK/REAL 데이터 소스 자동 전환
- **자동 폴백**: Supabase 연결 실패 시 목업 데이터로 안전하게 전환
- **실시간 대시보드**: 3개 카테고리(실검/쇼핑/밈) 동시 모니터링
- **AI 인사이트**: 쥄(논리적) + 쥐핏(감성적) 페르소나 분석

## 🛠️ 로컬 개발

```bash
# 1. 가상환경 활성화
source venv/bin/activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경 변수 설정 (.env 파일)
API_STATUS=MOCK  # 또는 REAL

# 4. 앱 실행
streamlit run app.py
```

## 📦 Render 배포

### 자동 배포 (render.yaml 사용)

1. GitHub 저장소 연결
2. Render가 자동으로 `render.yaml` 감지
3. 환경 변수 설정:
   - `API_STATUS`: `MOCK` 또는 `REAL`
   - `SUPABASE_URL`: Supabase 프로젝트 URL (REAL 모드 시)
   - `SUPABASE_KEY`: Supabase Anon Key (REAL 모드 시)

### 수동 배포

- **Root Directory**: `ai/aisignal`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`

## 🗄️ 데이터베이스 스키마

Supabase `signals` 테이블 구조:

```sql
CREATE TABLE signals (
  id BIGSERIAL PRIMARY KEY,
  category TEXT NOT NULL,  -- 'realtime', 'shopping', 'meme'
  keyword TEXT NOT NULL,
  insight TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_signals_category ON signals(category);
CREATE INDEX idx_signals_created_at ON signals(created_at DESC);
```

## 🔧 환경 변수

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `API_STATUS` | 데이터 소스 모드 (`MOCK` 또는 `REAL`) | `MOCK` |
| `SUPABASE_URL` | Supabase 프로젝트 URL | - |
| `SUPABASE_KEY` | Supabase Anon Key | - |

## 📝 라이선스

MIT License
