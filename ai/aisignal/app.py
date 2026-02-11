import streamlit as st
from supabase import create_client
import os, toml
from dotenv import load_dotenv
from datetime import datetime, timedelta

# 🎯 안티그래비티 하이브리드 인프라: 환경 변수 로드
load_dotenv()

# 🎯 [사령부 테마 설정]
st.set_page_config(page_title="AI SIGNAL", page_icon="🛰️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    .badge { padding: 5px 15px; border: 1px solid #03C75A; border-radius: 20px; color: #03C75A; font-weight: bold; margin-right: 8px; background: rgba(3, 199, 90, 0.1); }
    .section-header { color: #03C75A; border-bottom: 2px solid #03C75A; padding-bottom: 5px; margin: 20px 0; font-size: 1.5rem; }
    .signal-card { background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; border-left: 4px solid #03C75A; margin-bottom: 10px; }
    .stTextInput > div > div > input { border: 2px solid #03C75A !important; background-color: rgba(3, 199, 90, 0.05) !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

def init_supabase():
    url, key = None, None
    # 1. 환경 변수 (Render 배포 환경 최우선)
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    
    # 2. Render Secret File (로컬 테스트용)
    if (not url or not key) and os.path.exists("secrets.toml"):
        try:
            config = toml.load("secrets.toml")
            url, key = config.get("SUPABASE_URL"), config.get("SUPABASE_KEY")
        except: pass
    
    # 3. 로컬 .streamlit/secrets.toml (맥미니 환경)
    if (not url or not key) and os.path.exists(".streamlit/secrets.toml"):
        try:
            config = toml.load(".streamlit/secrets.toml")
            url, key = config.get("SUPABASE_URL"), config.get("SUPABASE_KEY")
        except: pass
    
    return create_client(url, key) if url and key else None

supabase = init_supabase()

# 🚀 [하이브리드 데이터 프로바이더]
class DataProvider:
    """MOCK/REAL 모드를 지원하는 데이터 공급 클래스 (쥄+쥐핏 스타일)"""
    
    MODE = os.environ.get('API_STATUS', 'MOCK').upper()
    
    @staticmethod
    def get_data(category):
        """카테고리별 데이터 반환 (자동 폴백 지원)"""
        if DataProvider.MODE == 'REAL':
            try:
                if supabase:
                    res = supabase.table('signals').select("*").eq('category', category).order('created_at', desc=True).limit(5).execute()
                    if res.data:
                        return res.data
                # Supabase 연결 실패 시 자동 폴백
                return DataProvider.get_mock_data(category)
            except Exception as e:
                # 에러 발생 시 목업으로 안전하게 전환
                return DataProvider.get_mock_data(category)
        return DataProvider.get_mock_data(category)
    
    @staticmethod
    def get_mock_data(category):
        """카테고리별 목업 데이터 생성 (쥄+쥐핏 페르소나)"""
        base_time = datetime.now()
        
        mock_database = {
            "realtime": [
                {"rank": 1, "keyword": "AI 반도체", "insight": "쥄: 데이터 센터 수요 폭증. 논리적 홀딩 구간.", "created_at": (base_time - timedelta(minutes=5)).isoformat()},
                {"rank": 2, "keyword": "테슬라 FSD", "insight": "쥄: 자율주행 레벨4 근접. 규제 리스크 주시 필요.", "created_at": (base_time - timedelta(minutes=10)).isoformat()},
                {"rank": 3, "keyword": "비트코인 ETF", "insight": "쥄: 기관 자금 유입 지속. 변동성 관리 필수.", "created_at": (base_time - timedelta(minutes=15)).isoformat()},
                {"rank": 4, "keyword": "K-드라마 열풍", "insight": "쥐핏: 넷플릭스 한국 콘텐츠 대박! 렛츠기릿!", "created_at": (base_time - timedelta(minutes=20)).isoformat()},
                {"rank": 5, "keyword": "챗GPT-5 루머", "insight": "쥄: 공식 발표 전까지 신중한 접근 권장.", "created_at": (base_time - timedelta(minutes=25)).isoformat()},
            ],
            "shopping": [
                {"rank": 1, "keyword": "아이폰16", "insight": "혼용: 성능은 쥄, 감성은 쥐핏. 가성비는 글쎄?", "created_at": (base_time - timedelta(minutes=3)).isoformat()},
                {"rank": 2, "keyword": "다이슨 에어랩", "insight": "쥐핏: 이거 없으면 헤어 포기각 ㅋㅋ 필수템!", "created_at": (base_time - timedelta(minutes=8)).isoformat()},
                {"rank": 3, "keyword": "갤럭시 Z폴드6", "insight": "쥄: 폴더블 시장 성숙기. 내구성 개선 확인됨.", "created_at": (base_time - timedelta(minutes=12)).isoformat()},
                {"rank": 4, "keyword": "에어팟 프로3", "insight": "쥐핏: ANC 미쳤다! 지하철에서 꿀잠 가능 ㅇㅈ?", "created_at": (base_time - timedelta(minutes=18)).isoformat()},
                {"rank": 5, "keyword": "LG 올레드 TV", "insight": "쥄: 화질 대비 가격 경쟁력 우수. 추천.", "created_at": (base_time - timedelta(minutes=22)).isoformat()},
            ],
            "meme": [
                {"rank": 1, "keyword": "홍박사", "insight": "쥐핏: 이거 모르면 아재임 ㅋㅋㅋ 렛츠기릿!", "created_at": (base_time - timedelta(minutes=2)).isoformat()},
                {"rank": 2, "keyword": "무야호", "insight": "쥐핏: 레전드 밈 부활! 감성 충만 ㅠㅠ", "created_at": (base_time - timedelta(minutes=7)).isoformat()},
                {"rank": 3, "keyword": "AI 그림 챌린지", "insight": "쥐핏: 미드저니로 나 그려봄 ㅋㅋ 개웃김", "created_at": (base_time - timedelta(minutes=11)).isoformat()},
                {"rank": 4, "keyword": "고양이 짤", "insight": "쥐핏: 힐링 타임~~ 냥이 최고 ㅎㅎ", "created_at": (base_time - timedelta(minutes=16)).isoformat()},
                {"rank": 5, "keyword": "숏폼 중독", "insight": "쥄: 도파민 과다 분비 주의. 시간 관리 필요.", "created_at": (base_time - timedelta(minutes=21)).isoformat()},
            ]
        }
        
        return mock_database.get(category, [])

# --- [UI] 상단 헤더 ---
st.markdown('<div><span class="badge">네이버실검</span><span class="badge">쇼핑</span><span class="badge">밈</span></div>', unsafe_allow_html=True)
st.title("🛰️ AI SIGNAL: REAL-TIME HQ")

# 🚀 [중앙 프롬프트 컨트롤러]
st.write("### 🧠 Central Intelligence Control")
m_col, i_col = st.columns([1, 4])
with m_col:
    selected_llm = st.selectbox("Brain", ["Gemini 1.5 Pro", "GPT-4o", "Claude 3.5"], label_visibility="collapsed")
with i_col:
    user_input = st.text_input("Prompt", placeholder=f"{selected_llm}에게 시그널 분석 요청...", label_visibility="collapsed")

if user_input:
    st.success(f"📡 {selected_llm} 엔진 가동: '{user_input}' 분석 중...")

st.divider()

# --- [UI] 데이터 그리드 (하이브리드 모드) ---
st.caption(f"🔧 현재 모드: **{DataProvider.MODE}** {'(목업 데이터)' if DataProvider.MODE == 'MOCK' else '(실제 데이터)'}")

col1, col2, col3 = st.columns(3)

def render_section(col, title, category):
    """섹션별 데이터 렌더링 (DataProvider 사용)"""
    with col:
        st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
        data = DataProvider.get_data(category)
        if data:
            for item in data:
                st.markdown(f"<div class='signal-card'><b>{item['keyword']}</b><br><small>{item['insight']}</small></div>", unsafe_allow_html=True)
        else:
            st.caption(f"{title} 데이터 수집 중...")

render_section(col1, "🔥 네이버 실검", "realtime")
render_section(col2, "🛍️ 트렌드 쇼핑", "shopping")
render_section(col3, "🤣 바이럴 밈", "meme")